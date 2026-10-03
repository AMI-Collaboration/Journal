"""Stage 2 - LOCAL PLANNING.

Each robot independently generates its own local plan using:
- the shared TASK
- its private observation (images, HIDDEN INFO, own full OFFER)
- the PUBLIC part of other robots' OFFERS

Local Planning writes only three step types:

    LOCAL     : I do this myself.
    ASK_HELP  : request another robot to perform a task that is either
                (a) required by one of MY later steps, OR
                (b) a task-relevant global subgoal I can identify from my
                    own observation but cannot execute with my embodiment.
    RECEIVE   : one of MY later steps needs a physical item that is not
                in my room -> I request it from another robot.

HELP / PASS are NOT written here. Local plans are generated in parallel,
so a robot cannot see requests that only appear in other robots' plans.
Responses (HELP / PASS) are proposed afterwards in the Auction stage,
when every local plan has been broadcast.

`target` is only a preferred hint; `purpose` names the own later step
that the request enables.
"""

from __future__ import annotations

import re

from runtime import Agent
from schemas import AgentInput, LocalPlan, Offer, RawLocalPlan


PLAN_STEP_TYPES = {"LOCAL", "ASK_HELP", "RECEIVE"}
REQUEST_TYPES = {"ASK_HELP", "RECEIVE"}


# ---------------------------------------------------------------------------
# Prompt example
# ---------------------------------------------------------------------------

_LOCAL_PLAN_EXAMPLE = """EXAMPLE

Shared TASK:
"Prepare the living room for exercise."

You are agent_3:
"Light-duty mobile robot in the living room. Cannot move heavy furniture."

Your room: a heavy coffee table stands on the only free floor spot.

Other robots' public OFFERS:
- agent_2  CAN PROVIDE: type=task, object=heavy furniture, action=move
- agent_4  CAN PROVIDE: type=item, object=yoga mat, location=bedroom

VALID local plan:

{
  "steps": [
    {
      "type": "LOCAL",
      "action": "Clear the small items from the floor spot",
      "kind": null, "item": null, "target": null, "purpose": null
    },
    {
      "type": "ASK_HELP",
      "action": "Move the heavy coffee table away from the floor spot",
      "kind": "task", "item": null, "target": "agent_2",
      "purpose": "Lay the yoga mat on the floor spot"
    },
    {
      "type": "RECEIVE",
      "action": "Receive the yoga mat",
      "kind": "item", "item": "yoga mat", "target": "agent_4",
      "purpose": "Lay the yoga mat on the floor spot"
    },
    {
      "type": "LOCAL",
      "action": "Lay the yoga mat on the floor spot",
      "kind": null, "item": null, "target": null, "purpose": null
    }
  ]
}

Why this is valid:
- The table is a concrete task-relevant subgoal grounded in this robot's
  observation.
- This robot cannot move the heavy table because of its embodiment.
- Therefore the robot delegates the task to agent_2.
- A later LOCAL step is NOT required when the requested action is itself
  a concrete global subgoal.
- `purpose` explains the subgoal that the requested action accomplishes.

INVALID (do NOT do this):

{
  "type": "ASK_HELP",
  "action": "Move heavy furniture in the living room",
  "purpose": null
}
as the last step of the plan.

Reason: nothing of yours depends on it. The global task needing it is NOT
a reason. Another robot that can move furniture will plan it itself.
"""


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

LOCAL_PLAN_SYSTEM = f"""You are one robot in a team of heterogeneous robots.

Each robot independently creates its OWN local plan.
Nobody assigns tasks to you.

You receive:
1. SHARED TASK
2. YOUR CAPABILITY
3. YOUR PRIVATE ROOM IMAGES
4. HIDDEN INFO
5. YOUR OFFER (full, private)
6. OTHER ROBOTS' OFFERS (public part only)

Your images, HIDDEN INFO, observed objects and cannot-do list are PRIVATE.
Never assume objects exist in another robot's room unless that robot's
public OFFER lists them in CAN PROVIDE.

{_LOCAL_PLAN_EXAMPLE}

==================================================
STEP TYPES (only these three)
==================================================

LOCAL      "I do this myself."
ASK_HELP   "I need another robot to do this TASK for me."
RECEIVE    "I need another robot to give me this ITEM."

Do NOT write HELP or PASS.
After all plans are shared, other robots will read your requests and
volunteer to respond. You only state what YOU do and what YOU need.

==================================================
REQUEST RULES (ASK_HELP / RECEIVE)  -- STRICT
==================================================

ASK_HELP should be generated whenever you identify a concrete,
task-relevant subgoal that you cannot execute with your own embodiment.

For every relevant subgoal grounded in YOUR observation or HIDDEN INFO:

1. Identify the concrete action required.
2. Check whether YOU can perform that action using YOUR capability,
   CAN DO, observed objects, and CANNOT DO constraints.
3. If YOU can perform it, you MUST make it LOCAL.
4. If YOU cannot perform it, make it ASK_HELP and request another robot
   that can perform the action.
5. Do NOT require a later LOCAL step of yours before creating ASK_HELP.

IMPORTANT CAN-DO PRIORITY:
- YOUR CAN DO has priority over delegation.
- If the requested object/action is covered by YOUR CAN DO, do NOT create
  ASK_HELP for it.
- Perform that action yourself as LOCAL.
- ASK_HELP is allowed only when the concrete requested action is relevant,
  grounded in YOUR observation or HIDDEN INFO, and YOU cannot perform it.
- Example: if you observe a chair and YOUR CAN DO contains "move chair",
  the correct step is LOCAL "Move the chair", not ASK_HELP.
- Example: if you observe a bunk bed and YOUR CANNOT DO says you cannot
  move the bunk bed because it is too heavy, the correct step is ASK_HELP
  for another robot that can move it.

IMPORTANT OBSERVATION GROUNDING:
- Every ASK_HELP must be grounded in YOUR OWN obs_scope or YOUR OWN
  cannot_do information.
- Before creating ASK_HELP, identify the concrete object/action that
  requires help and verify that the relevant object or limitation is
  explicitly present in YOUR observation or cannot_do information.
- Do NOT invent or assume objects that you did not observe.
- Do NOT create ASK_HELP for a generic class of objects, such as
  "heavy objects", if no specific relevant heavy object is present in
  YOUR obs_scope or cannot_do.
- Do NOT infer that another room contains a relevant object unless that
  object is explicitly present in YOUR own observation/HIDDEN INFO.
- Do NOT create ASK_HELP merely because the shared task mentions a
  subgoal that you cannot currently ground to your own observation.
- Shared TASK information can establish that a subgoal is important,
  but it cannot establish that an unobserved object exists.
- Example: if YOUR obs_scope contains a bunk bed and YOUR cannot_do says
  you cannot move it because it is too heavy, ASK_HELP for "Move the bunk
  bed" is valid.
- Example: if YOUR obs_scope contains a chair and YOUR can_do says you can
  move it, perform it as LOCAL.
- Example: if YOUR obs_scope contains no heavy object, do NOT create
  ASK_HELP such as "Move heavy objects".

A) DEPENDENCY REQUEST
  Use ASK_HELP when one of YOUR later LOCAL steps is blocked by a task
  that you cannot perform yourself.
  - Put the request immediately before the LOCAL step it enables.
  - `purpose` = that LOCAL step's action.

B) GLOBAL-SUBGOAL DELEGATION
  Use ASK_HELP when a concrete, task-relevant subgoal exists in your
  observed area but your embodiment cannot perform that subgoal.
  - This is valid even when you have no later LOCAL step depending on it.
  - `purpose` MUST start with `[GLOBAL_SUBGOAL]` and describe the
    global subgoal accomplished by the requested action.
  - Prefer a `target` whose CAPABILITY, CAN DO, or CAN PROVIDE matches
    the requested task.
  - The request must be grounded in YOUR observation or HIDDEN INFO.

For both forms:
  - ASK_HELP: `action` = the concrete task, `kind` = "task",
    `item` = null.
  - The requested action must be something you genuinely cannot execute.
  - Do NOT choose LOCAL for an action that is blocked by your embodiment
    or an explicit CANNOT DO constraint.
  - Do NOT invent arbitrary work merely because another robot can do it.

RECEIVE remains dependency-based:
  - one of YOUR later LOCAL steps needs a physical item that is not in your room.
  - Put RECEIVE immediately before that LOCAL step.
  - `purpose` = that LOCAL step's action.
  - `item` = the physical object, `kind` = "item".

IMPORTANT:
The existence of a later LOCAL step is NOT required for ASK_HELP.
If you observe a concrete subgoal required by the shared task and cannot
execute it, delegate it even if another robot will perform the resulting
action as the final step for that part of the task.

Do not suppress collaboration simply because the requested action is
globally relevant. The key test is:
  "Is this a concrete task-relevant action I observe, and can I execute it?"
If YES -> LOCAL.
If NO because of my embodiment/capability -> ASK_HELP.

==================================================
LOCAL RULES
==================================================

- Only actions that directly contribute to the SHARED TASK.
- Only actions your capability allows. CANNOT DO entries are hard limits.
- Ground actions in your own observation / HIDDEN INFO.
- Do not create steps for other robots. Do not create WAIT steps.
- Keep the plan concise and execution-oriented.

==================================================
TARGET (hint only)
==================================================

`target` is a PREFERRED robot, never a final assignment.
- ASK_HELP : a robot whose CAPABILITY / CAN DO / CAN PROVIDE shows it can
             do the task, else null.
- RECEIVE  : a robot whose CAN PROVIDE lists the item, else null.
- LOCAL    : null.

==================================================
OUTPUT
==================================================

Return ONE JSON object and nothing else:

{{
  "steps": [
    {{
      "type": "LOCAL" | "ASK_HELP" | "RECEIVE",
      "action": "string",
      "kind": "task" | "item" | null,
      "item": "string" | null,
      "target": "agent_id" | null,
      "purpose": "string" | null
    }}
  ]
}}
"""


# ---------------------------------------------------------------------------
# Offer formatting
# ---------------------------------------------------------------------------

def _format_obs(offer: Offer) -> str:
    if not offer.obs_scope:
        return "- (none)"

    lines = []
    for o in offer.obs_scope:
        parts = [o.object]
        if o.location:
            parts.append(f"@ {o.location}")
        if o.state:
            parts.append(f"({o.state})")
        lines.append("- " + " ".join(parts))
    return "\n".join(lines)


def _format_cannot_do(offer: Offer) -> str:
    if not offer.cannot_do:
        return "- (none)"

    lines = []
    for c in offer.cannot_do:
        text = " ".join(x for x in (c.action, c.object) if x)
        lines.append(f"- {text}: {c.reason}" if c.reason else f"- {text}")
    return "\n".join(lines)


def _format_can_do(offer: Offer) -> str:
    if not offer.can_do:
        return "- (none)"

    return "\n".join(
        "- " + " ".join(x for x in (c.action, c.object) if x)
        for c in offer.can_do
    )


def _format_can_provide(offer: Offer) -> str:
    if not offer.can_provide:
        return "- (none)"

    lines = []
    for c in offer.can_provide:
        parts = [f"type={c.type}"]
        if c.object:
            parts.append(f"object={c.object}")
        if c.location:
            parts.append(f"location={c.location}")
        if c.action:
            parts.append(f"action={c.action}")
        lines.append("- " + ", ".join(parts))
    return "\n".join(lines)


def _format_needs(offer: Offer) -> str:
    return "\n".join(f"- ({n.kind}) {n.text}" for n in offer.needs) or "- (none)"


def build_local_plan_user(
    inp: AgentInput,
    own_offer: Offer,
    others: dict[str, Offer],
) -> str:

    hidden = (
        "\n".join(f"- {h}" for h in inp.hidden_info)
        if inp.hidden_info
        else "- (none)"
    )

    # Other robots: public fields only (obs_scope / cannot_do are not broadcast).
    other_blocks = [
        f"""[{agent_id}]
CAPABILITY:
{offer.capability}

CAN DO:
{_format_can_do(offer)}

CAN PROVIDE:
{_format_can_provide(offer)}

NEEDS:
{_format_needs(offer)}
"""
        for agent_id, offer in sorted(others.items())
    ]
    others_txt = "\n".join(other_blocks) or "- (none)"

    own_offer_txt = f"""CAPABILITY:
{own_offer.capability}

OBSERVED (private):
{_format_obs(own_offer)}

CAN DO:
{_format_can_do(own_offer)}

CANNOT DO (private, hard limits):
{_format_cannot_do(own_offer)}

CAN PROVIDE:
{_format_can_provide(own_offer)}

OWN NEEDS:
{_format_needs(own_offer)}
"""

    return f"""SHARED TASK:
{inp.task}

YOU ARE:
{own_offer.agent}

YOUR CAPABILITY:
{inp.capability}

HIDDEN INFO:
{hidden}

YOUR OFFER:
{own_offer_txt}

OTHER ROBOTS' OFFERS (public part):
{others_txt}

Remember:
- Use only LOCAL / ASK_HELP / RECEIVE.
- ASK_HELP may be a normal dependency request OR a `[GLOBAL_SUBGOAL]`
  delegation request.
- RECEIVE must always be followed by the own LOCAL step it enables.
- Return JSON only.
"""


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def _token_set(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _overlap(a: str, b: str) -> float:
    aa = _token_set(a)
    bb = _token_set(b)

    if not aa or not bb:
        return 0.0

    return len(aa & bb) / max(1, min(len(aa), len(bb)))


# ---------------------------------------------------------------------------
# Structural validation (violations trigger an LLM retry)
# ---------------------------------------------------------------------------

def _validate_plan_structure(steps: list[dict]) -> None:
    """Hard rules that the LLM must satisfy; a ValueError triggers a retry."""

    for i, step in enumerate(steps):

        step_type = step["type"]

        if step_type in {"HELP", "PASS"}:
            raise ValueError(
                f"step {i + 1}: {step_type} is not allowed in Local Planning. "
                "Other robots respond to your requests later. "
                "Use only LOCAL / ASK_HELP / RECEIVE."
            )

        if step_type not in PLAN_STEP_TYPES:
            raise ValueError(
                f"step {i + 1}: invalid type {step_type!r}. "
                f"Allowed: {sorted(PLAN_STEP_TYPES)}"
            )

        if step_type in REQUEST_TYPES:

            purpose = (step.get("purpose") or "").strip()
            if not purpose:
                raise ValueError(
                    f"step {i + 1}: {step_type} requires `purpose`."
                )

            has_later_local = any(
                s["type"] == "LOCAL" for s in steps[i + 1:]
            )

            # ASK_HELP can also represent decentralized task delegation:
            # the requester identifies a concrete global subgoal in its own
            # observed area but cannot execute it.  RECEIVE remains a true
            # physical dependency and therefore still needs a later LOCAL.
            is_global_delegation = (
                step_type == "ASK_HELP"
                and purpose.startswith("[GLOBAL_SUBGOAL]")
            )

            if not has_later_local and not is_global_delegation:
                raise ValueError(
                    f"step {i + 1}: {step_type} {step['action']!r} is not "
                    "followed by an own LOCAL step. For ASK_HELP-only task "
                    "delegation, prefix purpose with [GLOBAL_SUBGOAL]."
                )


# ---------------------------------------------------------------------------
# Step normalization / salvage
# ---------------------------------------------------------------------------

def _normalize_step(step: dict) -> None:
    """Normalize one raw step in place; raise ValueError if unusable."""

    if not isinstance(step, dict):
        raise ValueError("each step must be a JSON object")

    step["type"] = str(step.get("type", "")).upper()
    step["action"] = str(step.get("action", "")).strip()

    if not step["action"]:
        raise ValueError(f"{step['type']} step requires an action.")

    if step.get("target") in {"", "null", "None"}:
        step["target"] = None

    if step.get("purpose") in {"", "null", "None"}:
        step["purpose"] = None

    if step["type"] == "ASK_HELP":
        step["kind"] = "task"
        step["item"] = None

    elif step["type"] == "RECEIVE":
        step["kind"] = "item"
        if not step.get("item"):
            raise ValueError("RECEIVE requires an `item` field.")


def _salvage_steps(raw: dict | None) -> tuple[list[dict], list[dict]]:
    """Fallback after the last retry: keep every valid step, drop only the
    ones that break the rules. Returns (kept, dropped-with-reason)."""

    steps = raw.get("steps", []) if isinstance(raw, dict) else []
    if not isinstance(steps, list):
        steps = []

    usable: list[dict] = []
    dropped: list[dict] = []

    for step in steps:
        try:
            _normalize_step(step)
        except ValueError as e:
            dropped.append({"step": str(step)[:200], "why": str(e)})
            continue

        if step["type"] not in PLAN_STEP_TYPES:
            dropped.append({"step": step["action"], "why": f"type {step['type']} not allowed"})
            continue

        usable.append(step)

    kept: list[dict] = []

    for i, step in enumerate(usable):

        if step["type"] in REQUEST_TYPES:

            later_local = next(
                (s for s in usable[i + 1:] if s["type"] == "LOCAL"),
                None,
            )

            is_global_delegation = (
                step["type"] == "ASK_HELP"
                and str(step.get("purpose") or "").startswith("[GLOBAL_SUBGOAL]")
            )

            if later_local is None and not is_global_delegation:
                dropped.append({"step": step["action"], "why": "request with no own later step"})
                continue

            # Missing purpose is repaired only for dependency requests.
            if not step.get("purpose") and later_local is not None:
                step["purpose"] = later_local["action"]

        kept.append(step)

    return kept, dropped


# ---------------------------------------------------------------------------
# Consistency checks (warnings only)
# ---------------------------------------------------------------------------

def _plan_consistency_checks(
    agent: Agent,
    plan: LocalPlan,
) -> list[dict]:

    warnings: list[dict] = []

    own = agent.offer

    if own is None:
        return warnings

    own_can_do = [
        " ".join(x for x in (c.action, c.object) if x)
        for c in own.can_do
    ]
    own_objects = [o.object for o in own.obs_scope]

    for step in plan.steps:

        # Asking for something the robot declared it can do itself.
        if step.type == "ASK_HELP":
            if any(_overlap(step.action, c) >= 0.8 for c in own_can_do):
                warnings.append({
                    "step": step.id,
                    "issue": "ask_help_for_own_can_do",
                    "action": step.action,
                })

        # Requesting an item that is already in the robot's own room.
        if step.type == "RECEIVE" and step.item:
            if any(_overlap(step.item, o) >= 0.8 for o in own_objects):
                warnings.append({
                    "step": step.id,
                    "issue": "receive_item_already_observed",
                    "action": step.action,
                })

    return warnings


# ---------------------------------------------------------------------------
# Main Local Planning
# ---------------------------------------------------------------------------

async def make_local_plan(
    agent: Agent,
    known_agents: set[str],
) -> LocalPlan:

    assert agent.offer is not None, (
        "make_offer() must run first"
    )

    agent.receive()

    user = build_local_plan_user(
        agent.inp,
        agent.offer,
        agent.others_offers,
    )

    # ---------------------------------------------------------------
    # Parse LLM JSON (strict) / salvage (fallback after last retry)
    # ---------------------------------------------------------------

    def parse(raw: dict) -> LocalPlan:

        steps = raw.get("steps", [])

        if not isinstance(steps, list):
            raise ValueError("`steps` must be a list")

        for step in steps:
            _normalize_step(step)

        _validate_plan_structure(steps)

        return LocalPlan.from_raw(
            agent.id,
            RawLocalPlan.model_validate(raw),
            known_agents,
        )

    def fallback(raw: dict | None) -> LocalPlan:
        kept, dropped = _salvage_steps(raw)

        agent.log.log(
            "plan",
            agent.id,
            "fallback_salvaged",
            kept=len(kept),
            dropped=dropped,
        )

        if agent.verbose:
            print(f"  [PLAN FALLBACK] {agent.id}: kept {len(kept)} steps, dropped {dropped}")

        return LocalPlan.from_raw(
            agent.id,
            RawLocalPlan.model_validate({"steps": kept}),
            known_agents,
        )

    # ---------------------------------------------------------------
    # LLM planning
    # ---------------------------------------------------------------

    agent.plan = await agent.ask(
        "plan",
        LOCAL_PLAN_SYSTEM,
        user,
        parse,
        banner_label="LOCAL PLAN RAW",
        fallback=fallback,
    )

    # ---------------------------------------------------------------
    # Consistency checks
    # ---------------------------------------------------------------

    consistency = _plan_consistency_checks(agent, agent.plan)

    if consistency:

        agent.log.log(
            "plan",
            agent.id,
            "plan_consistency_warning",
            warnings=consistency,
        )

        if agent.verbose:
            for warning in consistency:
                print(
                    f"  [PLAN CHECK] {agent.id} {warning['issue']}: "
                    f"{warning['step']} — {warning['action']}"
                )

    # ---------------------------------------------------------------
    # Statistics / logging
    # ---------------------------------------------------------------

    counts = {t: 0 for t in ("LOCAL", "ASK_HELP", "RECEIVE")}

    for step in agent.plan.steps:
        counts[step.type] += 1

    if agent.verbose:
        print(
            f"  [PLAN] {agent.id}: steps={len(agent.plan.steps)} "
            f"LOCAL={counts['LOCAL']} ASK_HELP={counts['ASK_HELP']} "
            f"RECEIVE={counts['RECEIVE']}"
        )

    agent.log.log(
        "plan",
        agent.id,
        "plan_made",
        n_steps=len(agent.plan.steps),
        n_local=counts["LOCAL"],
        n_ask_help=counts["ASK_HELP"],
        n_receive=counts["RECEIVE"],
    )

    # ---------------------------------------------------------------
    # Broadcast
    # ---------------------------------------------------------------

    agent.bus.broadcast(
        agent.id,
        "plan",
        agent.plan.model_dump(),
        phase="plan",
    )

    return agent.plan
