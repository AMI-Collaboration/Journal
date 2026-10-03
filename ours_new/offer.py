"""Stage 1 - OFFER.

Each robot looks at its own room and describes, in plain structured
form, what it can do there, what it cannot do, what it could give to
another robot, and what it still needs from another robot to finish
its own part of the task.
"""

from __future__ import annotations

from runtime import Agent
from schemas import AgentInput, CanProvide, Offer, RawOffer


OFFER_SYSTEM = """You are one robot in a team of heterogeneous robots working
together on a shared TASK. Each robot is in a different room and can only see
its own room (through its own image) and its own stated CAPABILITY.

Your job: write an OFFER describing YOUR OWN room and YOUR OWN capability,
for this shared TASK.

Fill in:
- capability: copy your given capability description as-is.
- obs_scope: objects you can actually see in your room image, or that are
  listed in your HIDDEN INFO. Do not invent objects you cannot see.
- can_do: concrete actions you can perform in your own room that help the
  shared TASK, given your capability.
- cannot_do: concrete actions relevant to the shared TASK that your
  capability does NOT allow (use your capability's CAN/CANNOT list -- list
  every CANNOT item from your capability here, even if your own room has no
  object that triggers it right now, since other robots need to know your
  hard limits).
- can_provide: physical items in your room, or tasks you are capable of
  performing, that could help ANY robot's contribution to the shared TASK --
  not only your own room. If your capability allows it and it could plausibly
  help the task, offer it.
- needs: something you genuinely require from another robot to finish your
  OWN room's part of the task (an item you don't have, or a task you cannot
  perform yourself that blocks your own room's progress). Leave empty if you
  have no such need.

Return exactly ONE JSON object:

{
  "capability": "...",
  "reasoning": "1-3 sentences on why you listed what you listed",
  "obs_scope": [{"object": "...", "location": "...", "state": "..."}],
  "can_do": [{"action": "...", "object": "...", "location": "...", "target": "..."}],
  "cannot_do": [{"action": "...", "object": "...", "location": "...", "reason": "..."}],
  "can_provide": [{"type": "item" | "task", "object": "...", "location": "...", "action": "..."}],
  "needs": [{"kind": "item" | "task", "object": "...", "location": "...", "action": "..."}]
}

Return JSON only.
"""


def build_offer_user(inp: AgentInput) -> str:
    hidden = "\n".join(f"- {h}" for h in inp.hidden_info) or "- (none)"
    return (
        f"SHARED TASK:\n{inp.task}\n\n"
        f"YOUR CAPABILITY:\n{inp.capability}\n\n"
        f"HIDDEN INFO (objects not visible in your image but present in your room):\n{hidden}\n\n"
        "The attached image shows your own room. Return JSON only."
    )


def _is_passable(item: CanProvide) -> bool:
    """A can_provide 'item' must name a real transferable object, not an
    abstract state like 'a clean floor'."""
    if item.type != "item":
        return True
    return bool(item.object)


async def make_offer(agent: Agent) -> Offer:
    raw: RawOffer = await agent.ask(
        "offer", OFFER_SYSTEM, build_offer_user(agent.inp),
        RawOffer.model_validate, banner_label="OFFER RAW",
    )

    raw = raw.model_copy(update={
        "can_provide": [p for p in raw.can_provide if _is_passable(p)],
    })

    agent.offer = Offer(agent=agent.id, **raw.model_dump())

    if agent.verbose:
        if agent.offer.reasoning:
            print(f"  [OFFER REASONING] {agent.id}: {agent.offer.reasoning}")
        print(
            f"  [OFFER] {agent.id}: obs_scope={len(agent.offer.obs_scope)} "
            f"can_do={len(agent.offer.can_do)} cannot_do={len(agent.offer.cannot_do)} "
            f"can_provide={len(agent.offer.can_provide)} needs={len(agent.offer.needs)}"
        )

    agent.log.log("offer", agent.id, "offer_made",
                   n_needs=len(agent.offer.needs), n_provide=len(agent.offer.can_provide))

    agent.bus.broadcast(agent.id, "offer", agent.offer.model_dump(), phase="offer")
    return agent.offer
