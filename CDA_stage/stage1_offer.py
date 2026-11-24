"""Stage 1 - Offer. Each robot, in parallel, tells the team what it brings to THIS task.

    from code : room, mobile (can_navigate), capability (robot.json)
    from LLM  : can_do    - actions my body and my room allow, many and varied ("slice bread")
                can_help  - work I can do for other robots ("bring food"; fixed: usually none)
                need_from_others - what the task needs that I cannot do or get myself ("bring lettuce"),
                            by object or action only, never by robot
                has_items - movable task-related objects in my room (no furniture / appliances)
                reasoning - short, private
Every list entry is a plain string "verb object" (optionally "... to place"). The verb comes from the
robots' capability lists (CAPABILITY_VERBS): can_do / can_help use the robot's own verbs, need_from_others
the verbs of the whole team. The entries become JSON values in later stages. Stage 1 lists broadly and does
not filter by room or usefulness; a later stage does that.
The offers are broadcast, so in Stage 2 each robot can plan with them ("get the apple from R2").
An offer is not a plan: it says what is possible, not what will be done.
"""
from __future__ import annotations

import re

from .core import AgentInput, EventLog, Offer, TaskConfig, as_list
from .llm import BaseLLM

# Limits live here so that other values can be tried later without touching the prompt.
CAN_DO_MAX = 10
CAN_HELP_MAX = 2
NEED_MAX = 5

# The verbs a robot may write come from ITS OWN capability list (robot.json "robot_can"), not from one
# global list: each capability name maps to the verbs it allows. "can_navigate" (= mobile) allows "bring".
# A verb that no capability maps to (open, turn_on, cook, clean, ...) is therefore never offered.
CAPABILITY_VERBS = {
    "PickupLightObject": ("pick_up", "put_down"),
    "PickupHeavyObject": ("pick_up", "put_down"),
    "PushFurniture": ("push",),
    "SliceObject": ("slice",),
    "PourObject": ("pour", "fill"),
    "PassReceiveObject": ("pass",),
    "OpenCloseObject": ("open", "close"),
    "ToggleObject": ("turn_on", "turn_off"),
    "CleanObject": ("clean",),
    "CookObject": ("cook",),
    "can_navigate": ("bring",),
}
BASE_VERBS: tuple[str, ...] = ()   # verbs every robot may use whatever its capabilities (none for now)


def robot_verbs(embodiment: str, mobile: bool) -> list[str]:
    """Verbs this robot may write: its own CAN list (read from the capability text) mapped to verbs."""
    m = re.search(r"CAN:\s*(.*?)\.\s*CANNOT", embodiment or "", flags=re.S)
    caps = [c.strip() for c in m.group(1).split(",") if c.strip()] if m else []
    if mobile:
        caps.append("can_navigate")          # the loader leaves can_navigate out of the CAN text
    verbs: list[str] = list(BASE_VERBS)
    for c in caps:
        for v in CAPABILITY_VERBS.get(c, ()):
            if v not in verbs:
                verbs.append(v)
    return verbs


def team_verbs(cfg: TaskConfig) -> list[str]:
    """Verbs that SOME robot of the team can do: what need_from_others may ask for."""
    verbs: list[str] = []
    for ag in cfg.agents:
        for v in robot_verbs(ag.profile.embodiment, ag.profile.mobile):
            if v not in verbs:
                verbs.append(v)
    return verbs

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

WHAT YOU KNOW ABOUT OBJECTS: only two sources.
 1) Your images: name only objects you actually see in them. Never guess or infer an object.
 2) "ABOUT AREAS YOU CANNOT SEE" (in the task message below): objects that exist in your room but are
    hidden from your view (for example inside a closed cabinet or drawer). You may count on them as
    objects you can reach, and name them like the ones you see.
There is no other list of objects. If you neither see an object nor were told about it, leave it out
of has_items.

FORMAT OF EVERY ENTRY in can_do, can_help and need_from_others: one short plain string,
    "<verb> <object>"   or   "<verb> <object> to <place>"
- the verbs come from the robots' capability lists, so each field has its own verbs:
    can_do and can_help use YOUR verbs only:  {my_verbs}
    need_from_others uses the TEAM's verbs (verbs that some robot of the team can do):  {team_verbs}
- one entry = one action on one object. No adjectives, no "and", no sentences.
  CORRECT (format only): "pick_up apple", "put_down plate to dining_table"
  WRONG: "make a delicious sandwich with the bread and lettuce", "help with the food"

Fill these fields (all related to the task):
- can_do: up to {can_do_max} actions that your body and your room allow, written with YOUR verbs. Be
  BROAD and VARIED: break the task into small actions you could do (one entry per object and per
  verb). Think of what your body can do (the CAN list in "capability"; a FIXED robot lists actions it
  can do from its own spot) and of what the task needs. An action on an object that is not in your
  room is fine when it belongs to this task: another robot may bring that object to you later. A later
  stage filters out what is impossible or not useful, so do not hold back, but stay related to the task.
- can_help: up to {can_help_max} actions you can do FOR other robots, written with YOUR verbs. A fixed
  robot usually writes nothing here.
- need_from_others: up to {need_max} things this task needs that you cannot do or get yourself, each
  as "<verb> <object>" with a TEAM verb: work your body cannot do (a verb that is not in YOUR verbs) or
  an object that must come from elsewhere. Name the object or the action ONLY. Never name a robot and
  never say who should do it. Several entries are welcome when the task really needs them; empty list
  if you need nothing. Do not ask for something that no verb of the team covers.
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
    system = OFFER_SYSTEM.format(agent=a.id, room=p.room, mobility=mobility_text(p.mobile),
                                 capability=p.embodiment,
                                 my_verbs=", ".join(robot_verbs(p.embodiment, p.mobile)) or "(none)",
                                 team_verbs=", ".join(team_verbs(cfg)) or "(none)",
                                 can_do_max=CAN_DO_MAX, can_help_max=CAN_HELP_MAX, need_max=NEED_MAX)
    user = OFFER_USER.format(task=cfg.task, deadline=cfg.deadline_min, instruction=a.instruction or "(none)",
                             n_img=len(a.images))
    d = await llm.complete(system, user, key=f"offer:{a.id}", images=a.images)
    names = lambda k: [x.split("(")[0].strip() for x in as_list(d.get(k))]
    offer = Offer(agent=a.id, room=p.room, mobile=p.mobile, capability=p.embodiment,
                  can_do=as_list(d.get("can_do"))[:CAN_DO_MAX],
                  can_help=as_list(d.get("can_help"))[:CAN_HELP_MAX],
                  need_from_others=as_list(d.get("need_from_others"))[:NEED_MAX],
                  has_items=names("has_items"), reasoning=str(d.get("reasoning", "")))
    log.log("offer", a.id, "broadcast", can_do=len(offer.can_do),
            can_help=len(offer.can_help), needs=len(offer.need_from_others), items=len(offer.has_items))
    return offer
