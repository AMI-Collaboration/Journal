"""Stage 2 - LOCAL PLANNING.

Each robot writes its own plan using three ideas:

1. Plan what YOU do in YOUR OWN room for the shared TASK.
2. Ground every action in YOUR OWN capability (CAN / CANNOT).
3. Collaboration: if your own room's progress is blocked by something you
   cannot do, ASK_HELP / RECEIVE for it. If another robot's broadcast OFFER
   shows a need (a task or item) that YOUR capability can satisfy, volunteer
   with HELP / PASS for it -- even if it is not in your own room.
"""

from __future__ import annotations

from runtime import Agent
from schemas import AgentInput, LocalPlan, Offer, RawLocalPlan


LOCAL_PLAN_SYSTEM = """You are one robot in a team of heterogeneous robots.
Each robot writes its own local plan independently.

You receive: the shared TASK, your own CAPABILITY, your own room image,
HIDDEN INFO, your own OFFER, and every other robot's broadcast OFFER
(capability, can_do, cannot_do, can_provide, needs).

Write your plan using only these step types:

LOCAL      You do this yourself, in your own room, using your own capability.
ASK_HELP   Your own room's progress on the shared TASK is blocked by a task
           you cannot perform yourself -- you request another robot do it.
HELP       Another robot's broadcast OFFER lists a need (a task), and YOUR
           capability can perform it -- you volunteer to do it for them,
           even if it is not in your own room.
RECEIVE    Your own room's progress depends on a physical item you don't
           have -- you request it from another robot.
PASS       Another robot's broadcast OFFER lists a need (an item), or your
           item could plausibly help the shared TASK -- you offer to give it,
           even if it is not needed in your own room.

Before writing your plan, go through EVERY other robot's broadcast
NEEDS one by one (not just the first one you notice) and check each
against your own CAN list. Do not stop after finding one match --
if your capability can satisfy more than one other robot's need, you
should volunteer (HELP/PASS) for each one you can genuinely perform.

Rules:
- Ground every action in your own CAPABILITY's CAN list; never do or
  volunteer (HELP/PASS) for something your CAPABILITY's CANNOT list rules
  out, no matter who the request came from or who you name as `target`.
  Before writing ANY HELP or PASS step, check your own CANNOT list first --
  if the action (or a close variant of it, e.g. "move furniture" vs "push
  furniture") appears there, do not write it, even if you think another
  robot would be better suited; simply do not create that step at all and
  let the actually capable robot volunteer on its own.
- ASK_HELP / RECEIVE must be about blocking your OWN room's progress on the
  shared TASK. Only the robot actually located in a room may write an
  ASK_HELP/RECEIVE about that room's state; do not write one about another
  room, and do not write one on another robot's behalf even if you share
  the same limitation.
- HELP / PASS must match a need or useful item you actually saw in another
  robot's broadcast OFFER; do not invent one.
- `target` is a preferred hint only (the robot you believe fits), never a
  final assignment. Leave it null if unsure.
- If a robot cannot navigate (its CAPABILITY says so), it can only
  PASS/HELP across its own room's boundary (e.g. hand an item to a robot
  that comes to it); it never writes a step moving itself elsewhere.
- A robot that can navigate may write a LOCAL step like "Go from <room A>
  to <room B>" when it is moving to RECEIVE something it needs, or to
  physically deliver a HELP/PASS it volunteered for.

Return exactly ONE JSON object:

{
  "reasoning": "1-3 sentences on your overall plan and why",
  "steps": [
    {
      "type": "LOCAL" | "ASK_HELP" | "HELP" | "RECEIVE" | "PASS",
      "action": "string",
      "kind": "task" | "item" | null,
      "item": "string" | null,
      "target": "agent_id" | null
    }
  ]
}

Return JSON only.
"""


def _format_offer_block(agent_id: str, offer: Offer) -> str:
    can_do = "\n".join(f"  - {c.action} {c.object or ''}".strip() for c in offer.can_do) or "  - (none)"
    cannot_do = "\n".join(f"  - {c.action} {c.object or ''}: {c.reason}".strip() for c in offer.cannot_do) or "  - (none)"
    can_provide = "\n".join(
        f"  - type={c.type}, object={c.object}, location={c.location}, action={c.action}"
        for c in offer.can_provide
    ) or "  - (none)"
    needs = "\n".join(
        f"  - kind={n.kind}, object={n.object}, location={n.location}, action={n.action}"
        for n in offer.needs
    ) or "  - (none)"

    return f"""[{agent_id}]
CAPABILITY: {offer.capability}
CAN DO:
{can_do}
CANNOT DO:
{cannot_do}
CAN PROVIDE:
{can_provide}
NEEDS:
{needs}
"""


def build_local_plan_user(inp: AgentInput, own_offer: Offer, others: dict[str, Offer]) -> str:
    hidden = "\n".join(f"- {h}" for h in inp.hidden_info) or "- (none)"
    others_txt = "\n".join(
        _format_offer_block(aid, offer) for aid, offer in sorted(others.items())
    ) or "- (none)"

    return f"""SHARED TASK:
{inp.task}

YOU ARE: {own_offer.agent}

YOUR OFFER:
{_format_offer_block(own_offer.agent, own_offer)}

HIDDEN INFO:
{hidden}

OTHER ROBOTS' BROADCAST OFFERS:
{others_txt}

Return JSON only.
"""


async def make_local_plan(agent: Agent, known_agents: set[str]) -> LocalPlan:
    assert agent.offer is not None, "make_offer() must run first"
    agent.receive()

    user = build_local_plan_user(agent.inp, agent.offer, agent.others_offers)

    def parse(raw: dict) -> LocalPlan:
        steps = raw.get("steps", [])
        if not isinstance(steps, list):
            raise ValueError("`steps` must be a list")

        allowed = {"LOCAL", "ASK_HELP", "HELP", "RECEIVE", "PASS"}
        for step in steps:
            t = str(step.get("type", "")).upper()
            if t not in allowed:
                raise ValueError(f"invalid step type {t!r}; allowed: {sorted(allowed)}")
            step["type"] = t

            if t in {"ASK_HELP", "HELP"}:
                step["kind"] = "task"
                step["item"] = None
            elif t in {"RECEIVE", "PASS"}:
                step["kind"] = "item"
                if not step.get("item"):
                    raise ValueError(f"{t} requires an `item` field")
            elif t == "LOCAL":
                if step.get("kind") not in {"task", "item", None}:
                    step["kind"] = "task"

            step["action"] = str(step.get("action", "")).strip()
            if not step["action"]:
                raise ValueError(f"{t} step requires a non-empty action")

            if step.get("target") in {"", "null", "None"}:
                step["target"] = None

        return LocalPlan.from_raw(agent.id, RawLocalPlan.model_validate(raw), known_agents)

    agent.plan = await agent.ask(
        "plan", LOCAL_PLAN_SYSTEM, user, parse, banner_label="LOCAL PLAN RAW",
    )

    if agent.verbose:
        if agent.plan.reasoning:
            print(f"  [PLAN REASONING] {agent.id}: {agent.plan.reasoning}")
        counts = {"LOCAL": 0, "ASK_HELP": 0, "HELP": 0, "RECEIVE": 0, "PASS": 0}
        for s in agent.plan.steps:
            if s.type in counts:
                counts[s.type] += 1
        print(
            f"  [PLAN] {agent.id}: steps={len(agent.plan.steps)} "
            f"LOCAL={counts['LOCAL']} ASK_HELP={counts['ASK_HELP']} HELP={counts['HELP']} "
            f"RECEIVE={counts['RECEIVE']} PASS={counts['PASS']}"
        )

    agent.log.log("plan", agent.id, "plan_made", n_steps=len(agent.plan.steps))
    agent.bus.broadcast(agent.id, "plan", agent.plan.model_dump(), phase="plan")
    return agent.plan
