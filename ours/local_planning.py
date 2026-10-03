"""Stage 2 - LOCAL PLANNING.

Each robot independently generates its own local plan using:
- the shared TASK
- its private observation
- its own OFFER
- broadcast OFFERS from other robots

The local planner produces explicit collaboration tags:

    LOCAL
    ASK_HELP
    HELP
    RECEIVE
    PASS

Semantics:
    ASK_HELP <-> HELP
    RECEIVE  <-> PASS

The planner does NOT perform final allocation.
`target` is only a preferred coordination hint.
Auction and Graph Reasoning determine the final collaboration relations.
"""

from __future__ import annotations

import json
import re

from runtime import Agent
from schemas import AgentInput, LocalPlan, Offer, RawLocalPlan


# ---------------------------------------------------------------------------
# Prompt example
# ---------------------------------------------------------------------------

_LOCAL_PLAN_EXAMPLE = """EXAMPLE

Shared TASK:
"Clear and prepare the living room for a home workout."

Your capability:
"You can move heavy furniture."

Your own room contains:
- sofa
- coffee table
- chairs

Another robot's OFFER contains:
- cannot_do: move heavy furniture
- needs:
    - kind: task
      text: move heavy furniture

A valid local plan is:

{
  "steps": [
    {
      "type": "LOCAL",
      "action": "Move the sofa to clear the living room",
      "kind": "task",
      "item": null,
      "target": null
    },
    {
      "type": "HELP",
      "action": "Move heavy furniture",
      "kind": "task",
      "item": null,
      "target": "agent_3"
    }
  ]
}

The HELP step means:
"I will perform this task for agent_3."

If you cannot perform a required task yourself, use:

{
  "type": "ASK_HELP",
  "action": "Move heavy furniture",
  "kind": "task",
  "item": null,
  "target": "agent_2"
}

The ASK_HELP step means:
"I need another robot to perform this task for me."

For physical item transfer:

{
  "type": "RECEIVE",
  "action": "Receive the table",
  "kind": "item",
  "item": "table",
  "target": "agent_2"
}

and:

{
  "type": "PASS",
  "action": "Pass the table to agent_1",
  "kind": "item",
  "item": "table",
  "target": "agent_1"
}

`target` is only a preferred target.
It is NOT a final assignment.

---

ADDITIONAL EXAMPLES (requesting robot's perspective):

Example A - requesting something for the GLOBAL TASK, not just your
own later step:

Shared TASK:
"Clear the living room and turn on the floor lamp for a home workout."

Your capability:
"Mobile robot in the living room. Can carry light objects but
cannot move heavy furniture."

Your own room contains:
- coffee table (heavy)
- floor lamp

Since the shared TASK explicitly requires the floor lamp to be on
and the room cleared, and clearing/lighting THIS room is part of
your own contribution, you may request help even when the blocking
object is in your OWN room:

{
  "type": "ASK_HELP",
  "action": "Move the heavy coffee table to clear the room",
  "kind": "task",
  "item": null,
  "target": null
}

Example B - do NOT request something that is simply "someone else's
job", even if the global task mentions it:

Shared TASK:
"Clear the living room and turn on the floor lamp for a home workout."

Your capability:
"Mobile robot in the bedroom. Can carry light objects."

Your own room contains:
- basketball
- pillow

Nothing in the shared TASK depends on this robot's bedroom
contribution being blocked by another robot. Requesting help with
the living room's coffee table here would be invalid -- that is not
this robot's own room or own contribution.

KEY DISTINCTION:
- Request when the task's OWN target area is YOUR OWN room and you
  are physically unable to complete part of it.
- Do NOT request just because the global task text mentions an
  object or action that lives in a different room from you.

---

CRITICAL SUMMARY -- READ BEFORE WRITING ASK_HELP / HELP
(this ties together every rule above into one check)

Two roles must NEVER be confused:

  ASK_HELP = "MY OWN required contribution is blocked, so I request help."
  HELP     = "ANOTHER robot's broadcast need matches what I can do, so I volunteer."

A very common mistake is this:

  WRONG: Robot X reads another robot's broadcast OFFER `needs`
  (e.g. agent_2 needs the living-room coffee table moved), and
  because Robot X also cannot move heavy furniture, Robot X ALSO
  writes its own ASK_HELP for "move the living-room coffee table."

  This is WRONG even though Robot X genuinely cannot push furniture.
  The reason: that need belongs to agent_2's own contribution (the
  living room), not to Robot X's own contribution (Robot X's own
  room). Robot X copying another robot's need as its own ASK_HELP
  creates a duplicate, spurious request for something Robot X was
  never responsible for.

BEFORE writing ANY ASK_HELP, ask yourself:
  1. Is the blocked action part of MY OWN room / MY OWN required
     contribution to the shared TASK? (Not just "the shared TASK
     mentions this room" -- literally your own assigned room.)
  2. If the answer is NO -- if this is really another robot's own
     room/contribution -- do NOT write ASK_HELP for it. That other
     robot already owns this request; duplicating it is invalid.

BEFORE setting `target` on ASK_HELP, ask yourself:
  3. Does the candidate robot's OWN broadcast CAPABILITY / CAN list
     actually support this action? Never target a robot whose
     CANNOT list (or capability description) rules this out (e.g.
     never target a Gripper, which cannot navigate or push
     furniture, for a "move heavy furniture" request). If unsure,
     leave `target` as null rather than guessing.

BEFORE writing ANY HELP, ask yourself:
  4. Check YOUR OWN CANNOT_DO list first. If the action you are
     about to volunteer for (or any close variant of it, e.g.
     "move furniture" vs "push furniture") appears in YOUR OWN
     CANNOT_DO, you must NOT write HELP for it -- no matter who the
     `target` is, and even if you privately intend the target robot
     to actually be the one who does it. HELP always means "I will
     personally perform this," so if you cannot, you must not write
     it, full stop. Setting `target` to a more capable robot does
     NOT excuse writing a HELP step you cannot fulfill.

     Common failure to avoid: you have "CANNOT: push furniture" and
     the request is "move heavy furniture in the living room." You
     might think "I can't do it myself, but agent_4 can, so I'll
     write HELP with target=agent_4 as a hint." This is WRONG. If
     you cannot perform it, write NOTHING for this request -- let
     the robot that CAN perform it (agent_4) write its own HELP
     directly, using the same OFFER-needs mechanism described above.

---

FULL WORKED EXAMPLE (different scenario, showing movement + relay):

Shared TASK:
"Prepare drinks and snacks for guests arriving soon."

Robots:
- agent_1: Gripper in the kitchen. Cannot navigate (fixed in place).
- agent_2: Mobile_Light in the dining room. Can navigate, carry light items.

agent_1's own room (kitchen) has:
- a tray of snacks
- a jug of water

agent_1's OFFER (own, private) shows:
- can_provide: [{{"type": "item", "object": "snack tray"}}, {{"type": "item", "object": "water jug"}}]
- cannot_do: [{{"action": "navigate", "reason": "fixed gripper"}}]

agent_2's broadcast OFFER shows:
- needs: [{{"kind": "item", "object": "snack tray", "location": "kitchen"}}]

VALID plan for agent_1 (the fixed Gripper -- it never "moves to" anywhere,
it only hands items across when another robot comes to it):

{{
  "steps": [
    {{
      "type": "PASS",
      "action": "Hand the snack tray to agent_2 at the kitchen doorway",
      "kind": "item", "item": "snack tray", "target": "agent_2"
    }},
    {{
      "type": "PASS",
      "action": "Hand the water jug to agent_2 at the kitchen doorway",
      "kind": "item", "item": "water jug", "target": "agent_2"
    }}
  ]
}}

VALID plan for agent_2 (mobile -- movement between rooms is written as
a LOCAL step naming the two rooms, e.g. "Go from X to Y"):

{{
  "steps": [
    {{
      "type": "LOCAL",
      "action": "Go from the dining room to the kitchen",
      "kind": null, "item": null, "target": null
    }},
    {{
      "type": "RECEIVE",
      "action": "Receive the snack tray",
      "kind": "item", "item": "snack tray", "target": "agent_1"
    }},
    {{
      "type": "RECEIVE",
      "action": "Receive the water jug",
      "kind": "item", "item": "water jug", "target": "agent_1"
    }},
    {{
      "type": "LOCAL",
      "action": "Go from the kitchen back to the dining room",
      "kind": null, "item": null, "target": null
    }},
    {{
      "type": "LOCAL",
      "action": "Arrange the snack tray and water jug on the dining table",
      "kind": null, "item": null, "target": null
    }}
  ]
}}

WHY THIS IS THE RIGHT PATTERN:
- A robot that CANNOT navigate never writes "go to another room" --
  it stays put and only PASSes/HELPs across whatever boundary it can
  reach (e.g. a doorway), exactly matching its CANNOT_DO.
- A robot that CAN navigate writes its own room-to-room movement as
  a plain LOCAL step: "Go from <room A> to <room B>". This makes the
  physical relay of items across rooms visible in the plan instead of
  being silently skipped.
- The relay item names (snack tray, water jug) are copied verbatim
  from the OFFER fields, never generalized to vague terms like
  "supplies".

CRITICAL BOUNDARY -- when is moving to another room valid?

Movement to another room (a LOCAL "Go from X to Y" step) is valid
ONLY in these two cases:

  (1) You are RECEIVING something there because YOUR OWN required
      contribution (in your own room) genuinely depends on that
      item -- exactly like agent_2 fetching the snack tray above.

  (2) You are the HELP/PASS PROVIDER for another robot's need, and
      you are physically capable of it (see rule 6 above) -- e.g. a
      Mobile_Heavy robot navigating into the living room specifically
      to perform the HELP it volunteered for.

Movement is NEVER valid merely to go create an ASK_HELP or otherwise
comment on another room's objects/furniture. If the task you are
thinking about belongs to another room and you are not the one
volunteering to physically HELP with it, do not move there and do
not write an ASK_HELP about it -- that is not your own room's
responsibility (see Example B above). Owning a room means you only
ASK_HELP for blockers inside THAT room; you do not travel elsewhere
to raise requests on another robot's behalf.

---

ROOM OWNERSHIP RULES (ASK_HELP vs PASS) -- FINAL CHECK

1. ASK_HELP about a room's state belongs ONLY to that room's robot.

   An ASK_HELP about the condition of a room (clearing it, preparing
   it, tidying it, etc.) may ONLY be written by the robot that is
   actually located in that room. A robot in a DIFFERENT room may
   NEVER write this ASK_HELP on that room's behalf -- not even if it
   shares the exact same limitation (e.g. it also cannot move heavy
   furniture). If you are not in that room, this ASK_HELP is not
   yours to make; leave it to the robot who is actually there.

2. PASS (physical item delivery) is NOT restricted by room ownership.

   Unlike ASK_HELP, a PASS step may be written by ANY robot, in ANY
   room, as long as the item is genuinely relevant to the shared
   TASK. You do not need to be in the task's target room to offer an
   item you have -- proactively PASS it if it could help, regardless
   of whose room the task is mainly about.
"""


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

LOCAL_PLAN_SYSTEM = f"""You are one robot in a team of heterogeneous robots.

Each robot independently creates its OWN local plan.

You receive:

1. SHARED TASK
2. YOUR CAPABILITY
3. YOUR PRIVATE ROOM IMAGE
4. HIDDEN INFO
5. YOUR OFFER
6. OTHER ROBOTS' OFFERS

Raw visual observations are PRIVATE.
Never assume objects exist in another robot's room unless they are explicitly
described in that robot's broadcast OFFER.

{_LOCAL_PLAN_EXAMPLE}


# OUTPUT FORMAT

Return ONE JSON object and NOTHING ELSE. Include a top-level
"reasoning" field (1-3 sentences) explaining your overall plan
strategy -- e.g. why you did or didn't request help, why you
targeted a specific robot, why you did or didn't volunteer a
HELP/PASS. This is for debugging/transparency only; it does not
affect scoring.

{{
  "reasoning": "string",
  "steps": [
    {{
      "type": "LOCAL" | "ASK_HELP" | "HELP" | "RECEIVE" | "PASS",
      "action": "string",
      "kind": "task" | "item" | null,
      "item": "string" | null,
      "target": "agent_id" | null
    }}
  ]
}}


# STEP SEMANTICS

## 1. LOCAL

You perform the action yourself.

Use LOCAL when:
- the task directly contributes to the shared TASK
- you have the required capability
- the action uses your own private observation

Example:

{{
  "type": "LOCAL",
  "action": "Move the sofa to clear the living room",
  "kind": "task",
  "item": null,
  "target": null
}}


## 2. ASK_HELP

You need another robot to perform a task that you cannot perform yourself.

ASK_HELP is a REQUEST.

Use ASK_HELP when:
- the shared TASK requires the action
- you cannot perform the action because of your capability or constraints
- another robot may be able to perform it

Example:

{{
  "type": "ASK_HELP",
  "action": "Move heavy furniture",
  "kind": "task",
  "item": null,
  "target": "agent_2"
}}

Do NOT write:
"Ask agent_2 to move heavy furniture"

The action itself should describe the required task:
"Move heavy furniture"


## 3. HELP

You volunteer to perform a task requested by another robot.

HELP is a PROVIDER action.

Use HELP only when:
- another robot has a concrete relevant need
- the need contributes to the shared TASK
- your capability supports the requested task

Example:

{{
  "type": "HELP",
  "action": "Move heavy furniture",
  "kind": "task",
  "item": null,
  "target": "agent_3"
}}


## 4. RECEIVE

You need to receive a physical item from another robot.

Example:

{{
  "type": "RECEIVE",
  "action": "Receive the table",
  "kind": "item",
  "item": "table",
  "target": "agent_2"
}}


## 5. PASS

You provide or physically pass an item to another robot.

Example:

{{
  "type": "PASS",
  "action": "Pass the table",
  "kind": "item",
  "item": "table",
  "target": "agent_1"
}}


# COLLABORATION PAIRING

The intended pairings are:

ASK_HELP <-> HELP

RECEIVE <-> PASS


# TASK-GROUNDED PLANNING

Follow these rules in order.

1. First understand the SHARED TASK. Re-read it carefully and
   identify EVERY distinct sub-goal it describes -- a shared TASK
   sentence can describe more than one thing that needs to happen.
   Do not let one sub-goal (e.g. clearing or tidying something)
   crowd out the others just because it is the easiest or most
   literal reading of the sentence. Check your own room against
   EACH sub-goal you found, not just the first one.

2. Only generate actions that directly contribute to the SHARED TASK.

3. Do NOT perform unrelated actions merely because objects are visible.

4. If your room contains objects that are irrelevant to the shared TASK,
   do not create LOCAL steps for them.

5. If your capability cannot perform a task required by the shared TASK,
   create ASK_HELP rather than pretending to perform it.

6. If another robot's broadcast OFFER `needs` names a task that is
   (a) relevant to the SHARED TASK, and
   (b) something YOUR capability can physically perform (check CAN list),
   you SHOULD create a HELP step for it, even if the task is not in
   your own room and even if it has nothing to do with your own
   room's objects. This is exactly how cross-room collaboration is
   supposed to happen: a robot with the right capability volunteers
   for a need it saw in another robot's broadcast OFFER.

   Example: another robot's OFFER needs = [{{"kind": "task", "object":
   "CoffeeTable", "location": "living_room", "action": "move"}}], and
   your own CAN list includes PushFurniture / PickupHeavyObject.
   -> You SHOULD add:
      {{"type": "HELP", "action": "Move the CoffeeTable in living_room",
       "kind": "task", "item": null, "target": "<that robot's id>"}}
   even though the CoffeeTable is not in your own room.

   IMPORTANT: when writing the HELP action, copy the specific object
   name from that need's `object` field verbatim (e.g. "CoffeeTable"),
   never generalize it to a vague phrase like "heavy objects" or
   "furniture". The action must name the exact object so downstream
   matching and rendering stay precise.

7. A robot's OFFER `needs` does NOT automatically become a task.
   Only use it when that need is relevant to the SHARED TASK.

8. Do not create HELP merely because another robot has a need.
   The need must be relevant to the shared TASK and compatible with your capability.

9. Do not create PASS unless another robot actually requires the item.

10. Do not create RECEIVE unless your own required task genuinely depends on
    receiving that physical item.

11. Never invent objects that are not visible in your own observation,
    stated in your HIDDEN INFO, or explicitly provided in the broadcast OFFER.

12. Respect `cannot_do` constraints.

13. Never generate an action that is explicitly listed in your own
    CANNOT-DO CONSTRAINTS.

14. Do not create WAIT steps.

15. Keep the plan concise and execution-oriented.


# TARGET RULES

`target` is only a PREFERRED TARGET.

It is NOT a final allocation.

For ASK_HELP:
- target may be the robot whose OFFER clearly provides the required capability.
- otherwise use null.

For HELP:
- target should normally be the robot whose OFFER contains the matching need.
- if there is no clear matching robot, do not create HELP.

For RECEIVE:
- target may be the robot whose OFFER explicitly provides the required item.
- otherwise use null.

For PASS:
- target should be the robot that explicitly needs the item.

Never choose a target simply because that robot exists.


# CANNOT-DO RULE

Your CANNOT-DO CONSTRAINTS are hard constraints.

If the OFFER says:

- move heavy furniture: insufficient payload

you MUST NOT generate:

{{
  "type": "LOCAL",
  "action": "Move the heavy sofa",
  ...
}}

Instead, if the shared TASK requires it, generate ASK_HELP.


# IMPORTANT DISTINCTION

ASK_HELP means:

"I need someone else to do this."

HELP means:

"I will do this for someone else."

RECEIVE means:

"I need to receive this item."

PASS means:

"I will provide/pass this item."

LOCAL means:

"I will do this myself."

Never mix these directions.


# OUTPUT RESTRICTION

Return JSON only.

Do not output explanations.
Do not output markdown.
Do not output natural-language commentary.
"""


# ---------------------------------------------------------------------------
# User prompt
# ---------------------------------------------------------------------------

def _format_cannot_do(offer: Offer) -> str:
    """Convert CannotDoAction objects into readable prompt text."""

    if not offer.cannot_do:
        return "- (none)"

    lines = []

    for c in offer.cannot_do:
        action = getattr(c, "action", None)
        reason = getattr(c, "reason", None)

        if action and reason:
            lines.append(f"- {action}: {reason}")
        elif action:
            lines.append(f"- {action}")
        else:
            lines.append(f"- {str(c)}")

    return "\n".join(lines)


def _format_can_do(offer: Offer) -> str:
    """Convert CanDoAction objects into readable prompt text."""

    if not offer.can_do:
        return "- (none)"

    lines = []

    for c in offer.can_do:
        action = getattr(c, "action", None)

        if action:
            lines.append(f"- {action}")
        else:
            lines.append(f"- {str(c)}")

    return "\n".join(lines)


def _format_can_provide(offer: Offer) -> str:
    """Convert CanProvide objects into readable prompt text."""

    if not offer.can_provide:
        return "- (none)"

    lines = []

    for c in offer.can_provide:
        item = getattr(c, "item", None)
        location = getattr(c, "location", None)
        action = getattr(c, "action", None)

        parts = []

        if item:
            parts.append(f"item={item}")

        if location:
            parts.append(f"location={location}")

        if action:
            parts.append(f"action={action}")

        lines.append("- " + ", ".join(parts) if parts else f"- {str(c)}")

    return "\n".join(lines)


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

    # ---------------------------------------------------------------
    # Other robots' offers
    # ---------------------------------------------------------------

    other_offer_blocks = []

    for agent_id, offer in sorted(others.items()):

        needs = "\n".join(
            f"  - ({n.kind}) {n.text}"
            for n in offer.needs
        ) or "  - (none)"

        other_offer_blocks.append(
            f"""[{agent_id}]
CAPABILITY:
{offer.capability}

OBSERVED SCOPE:
{offer.obs_scope}

CAN DO:
{_format_can_do(offer)}

CANNOT DO:
{_format_cannot_do(offer)}

CAN PROVIDE:
{_format_can_provide(offer)}

NEEDS:
{needs}
"""
        )

    others_txt = "\n".join(other_offer_blocks) or "- (none)"

    # ---------------------------------------------------------------
    # Own offer
    # ---------------------------------------------------------------

    own_needs = "\n".join(
        f"- ({n.kind}) {n.text}"
        for n in own_offer.needs
    ) or "- (none)"

    own_offer_txt = f"""CAPABILITY:
{own_offer.capability}

OBSERVED SCOPE:
{own_offer.obs_scope}

CAN DO:
{_format_can_do(own_offer)}

CANNOT DO:
{_format_cannot_do(own_offer)}

CAN PROVIDE:
{_format_can_provide(own_offer)}

OWN NEEDS:
{own_needs}
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

OTHER ROBOTS' OFFERS:
{others_txt}

Remember:
- Your images and hidden information are private.
- Generate only YOUR OWN plan.
- Use explicit step types:
  LOCAL / ASK_HELP / HELP / RECEIVE / PASS
- Do not use NEED.
- Do not use natural-language tags such as "[HELP]" inside the action.
- The `type` field itself is the semantic tag.
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
# Consistency checks
# ---------------------------------------------------------------------------

def _plan_consistency_checks(
    agent: Agent,
    plan: LocalPlan,
) -> list[dict]:

    warnings: list[dict] = []

    own = agent.offer

    if own is None:
        return warnings

    # ---------------------------------------------------------------
    # HELP must correspond to another robot's need
    # ---------------------------------------------------------------

    other_needs = [
        (agent_id, need)
        for agent_id, offer in agent.others_offers.items()
        for need in offer.needs
    ]

    for step in plan.steps:

        if step.type != "HELP":
            continue

        matched = False

        for agent_id, need in other_needs:

            if step.target == agent_id:
                score = _overlap(step.action, need.text)

                if score >= 0.20:
                    matched = True
                    break

        if not matched:

            candidates = [
                (agent_id, need, _overlap(step.action, need.text))
                for agent_id, need in other_needs
            ]

            if candidates:

                _, _, score = max(
                    candidates,
                    key=lambda x: x[2],
                )

                if score >= 0.35:
                    matched = True

        if not matched:
            warnings.append({
                "step": step.id,
                "issue": "help_without_matching_need",
                "action": step.action,
                "target": step.target,
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
    # Parse LLM JSON
    # ---------------------------------------------------------------

    def parse(raw: dict) -> LocalPlan:

        steps = raw.get("steps", [])

        if not isinstance(steps, list):
            raise ValueError(
                "`steps` must be a list"
            )

        # -----------------------------------------------------------
        # Strict tag validation
        # -----------------------------------------------------------

        allowed_types = {
            "LOCAL",
            "ASK_HELP",
            "HELP",
            "RECEIVE",
            "PASS",
        }

        for step in steps:

            step_type = str(
                step.get("type", "")
            ).upper()

            if step_type not in allowed_types:
                raise ValueError(
                    f"Invalid Local Planning step type: {step_type}. "
                    f"Allowed types: {sorted(allowed_types)}"
                )

            step["type"] = step_type

            # -------------------------------------------------------
            # ASK_HELP / HELP are task-level collaboration
            # -------------------------------------------------------

            if step_type in {"ASK_HELP", "HELP"}:

                step["kind"] = "task"
                step["item"] = None

            # -------------------------------------------------------
            # RECEIVE / PASS are item-level collaboration
            # -------------------------------------------------------

            elif step_type in {"RECEIVE", "PASS"}:

                step["kind"] = "item"

                if not step.get("item"):
                    raise ValueError(
                        f"{step_type} requires an `item` field."
                    )

            # -------------------------------------------------------
            # LOCAL
            # -------------------------------------------------------

            elif step_type == "LOCAL":

                if step.get("kind") not in {
                    "task",
                    "item",
                    None,
                }:
                    step["kind"] = "task"

            # -------------------------------------------------------
            # Clean action
            # -------------------------------------------------------

            step["action"] = str(
                step.get("action", "")
            ).strip()

            if not step["action"]:
                raise ValueError(
                    f"{step_type} step requires an action."
                )

            # -------------------------------------------------------
            # Target
            # -------------------------------------------------------

            target = step.get("target")

            if target in {"", "null", "None"}:
                step["target"] = None

        # -----------------------------------------------------------
        # IMPORTANT:
        # Do NOT convert HELP -> NEED.
        # Do NOT convert ASK_HELP -> NEED.
        # Do NOT inject [HELP] into action text.
        # -----------------------------------------------------------

        plan = LocalPlan.from_raw(
            agent.id,
            RawLocalPlan.model_validate(raw),
            known_agents,
        )

        return plan

    # ---------------------------------------------------------------
    # LLM planning
    # ---------------------------------------------------------------

    agent.plan = await agent.ask(
        "plan",
        LOCAL_PLAN_SYSTEM,
        user,
        parse,
        banner_label="LOCAL PLAN RAW",
    )

    if agent.verbose and agent.plan.reasoning:
        print(f"  [PLAN REASONING] {agent.id}: {agent.plan.reasoning}")

    # ---------------------------------------------------------------
    # Consistency checks
    # ---------------------------------------------------------------

    consistency = _plan_consistency_checks(
        agent,
        agent.plan,
    )

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
                    f"  [PLAN CHECK] "
                    f"{agent.id} "
                    f"{warning['issue']}: "
                    f"{warning['step']} — "
                    f"{warning['action']}"
                )

    # ---------------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------------

    counts = {
        "LOCAL": 0,
        "ASK_HELP": 0,
        "HELP": 0,
        "RECEIVE": 0,
        "PASS": 0,
    }

    for step in agent.plan.steps:

        if step.type in counts:
            counts[step.type] += 1

    if agent.verbose:

        print(
            f"  [PLAN] {agent.id}: "
            f"steps={len(agent.plan.steps)} "
            f"LOCAL={counts['LOCAL']} "
            f"ASK_HELP={counts['ASK_HELP']} "
            f"HELP={counts['HELP']} "
            f"RECEIVE={counts['RECEIVE']} "
            f"PASS={counts['PASS']}"
        )

    # ---------------------------------------------------------------
    # Logging
    # ---------------------------------------------------------------

    agent.log.log(
        "plan",
        agent.id,
        "plan_made",
        n_steps=len(agent.plan.steps),
        n_local=counts["LOCAL"],
        n_ask_help=counts["ASK_HELP"],
        n_help=counts["HELP"],
        n_receive=counts["RECEIVE"],
        n_pass=counts["PASS"],
        n_collab=len(
            agent.plan.collaboration_steps()
        ),
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
