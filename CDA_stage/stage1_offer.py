"""Stage 1 - Offer. Each robot, in parallel, tells the team what it brings to THIS task.

    from code : room, mobile (can_navigate), capability (robot.json)
    from LLM  : can_do    - what I can do myself for the task (with my objects, max 3)
                can_help  - work I can do for other robots (carrying, heavy work; fixed: usually none)
                need_from_others - what I may need (reference only)
                has_items - movable task-related objects in my room (no furniture / appliances)
                reasoning - short, private
The offers are broadcast, so in Stage 2 each robot can plan with them ("get the apple from R2").
An offer is not a plan: it says what is possible, not what will be done.
"""
from __future__ import annotations

from .core import AgentInput, EventLog, Offer, TaskConfig, as_list
from .llm import BaseLLM

# ================================================================================================
# PROMPTS
# ================================================================================================
OFFER_SYSTEM = """You are robot {agent}, a household robot. You see only your own room ({room}).
Tell the team what you bring to THIS task. This is not a plan yet: say what is POSSIBLE for you,
so that the other robots can plan with it (for example "I will get the apple from R2").

YOUR BODY (fixed facts, do not change them):
- room: {room}
- {mobility}
- capability: {capability}

OBJECT TYPES THAT EXIST IN YOUR ROOM: {object_catalog}
Name only objects you actually see in your images, and only types from this list.

Fill these fields (short phrases, name the exact objects, all related to the task):
- can_do: up to 3 things you can do YOURSELF for the task, with the objects you use
  ("make a sandwich with the bread, lettuce and tomato"). If you cannot move, only things you can
  do where you stand.
- can_help: up to 2 kinds of work you can do FOR other robots ("carry food from the kitchen to
  the living room", "push the armchair"). A fixed robot usually writes nothing here.
- need_from_others: what the task may need from other robots (an object you do not have, work
  your body cannot do). Reference only. Empty list if nothing.
- has_items: objects in your room that you can pick up and that may matter for the task. Names
  only, no furniture or appliances (no fridge, sink, table, sofa, microwave).
- reasoning: one sentence, for yourself only.

Return JSON:
{{"reasoning":"...","can_do":[...],"can_help":[...],"need_from_others":[...],"has_items":[...]}}"""

OFFER_USER = """TASK: {task}
DEADLINE: {deadline} minutes

ABOUT AREAS YOU CANNOT SEE:
{instruction}

Images of your room attached ({n_img} image(s))."""


def mobility_text(mobile: bool) -> str:
    return ("mobile: you can move to other rooms" if mobile
            else "FIXED: you cannot move; you act only where you stand in your own room")


# ================================================================================================
# CODE
# ================================================================================================
async def make_offer(cfg: TaskConfig, a: AgentInput, llm: BaseLLM, log: EventLog) -> Offer:
    p = a.profile
    catalog = ", ".join(a.object_catalog) if a.object_catalog else "(not given: name only what you clearly see)"
    system = OFFER_SYSTEM.format(agent=a.id, room=p.room, mobility=mobility_text(p.mobile),
                                 capability=p.embodiment, object_catalog=catalog)
    user = OFFER_USER.format(task=cfg.task, deadline=cfg.deadline_min, instruction=a.instruction or "(none)",
                             n_img=len(a.images))
    d = await llm.complete(system, user, key=f"offer:{a.id}", images=a.images)
    names = lambda k: [x.split("(")[0].strip() for x in as_list(d.get(k))]
    offer = Offer(agent=a.id, room=p.room, mobile=p.mobile, capability=p.embodiment,
                  can_do=as_list(d.get("can_do"))[:3],
                  can_help=as_list(d.get("can_help"))[:2], need_from_others=as_list(d.get("need_from_others")),
                  has_items=names("has_items"), reasoning=str(d.get("reasoning", "")))
    log.log("offer", a.id, "broadcast", can_do=len(offer.can_do),
            can_help=len(offer.can_help), items=len(offer.has_items))
    return offer
