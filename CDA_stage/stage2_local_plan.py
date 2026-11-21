"""Stage 2 - Local Plan. Each robot, in parallel, writes its goals, its own work and what it needs.

Stage 2 writes only three step types:
    LOCAL     work I do myself (a mobile robot may carry its own objects to another room)
    RECEIVE   "I want object o from robot i" (i is chosen from the offers)
    ASK_HELP  "I need this exact work done" (what, which object, where), with a condition, no robot named
PASS and HELP are NOT written here: they are answers to requests and are added in Stage 3 by the
robot that offers them. So every link answers a stated request.

No LLM self-correction. Code only tidies the format and goes straight on to Stage 3:
    - a step with an unknown type, or a PASS / HELP (Stage 3 only), is removed
    - a RECEIVE that names no existing other robot is removed
    - an enables / serves that does not point to a valid index is cleared
    - the room is set by code (own room)
Everything removed or cleared is recorded. Meaning problems are NOT removed here (Stage 4 judges).
"""
from __future__ import annotations

from .core import (ASK_HELP, HELP, PASS, RECEIVE, REQUEST_TYPES, STEP_TYPES, EventLog, Node, Offer, Plan,
                   TaskConfig, _j, as_int, as_list)

STAGE3_ONLY = (PASS, HELP)
from .llm import BaseLLM

# ================================================================================================
# PROMPTS
# ================================================================================================
PLAN_SYSTEM = """You are robot {agent} in the {room}. Write YOUR part of the team plan.

You are a HIGH-LEVEL planner. Write what gets done, not how you move: one step = one meaningful
piece of work, as one short sentence with the exact objects ("put the apples in the fruit bowl").
No separate move / pick up / put down steps, and no vague words ("any", "necessary items", "things").

YOUR PART. Every robot has broadcast its offer: can_do (what it does itself), has_items (objects it
has) and can_help (work it can do for others).
- Your own can_do is your work: do it yourself.
- Work that another robot offered in ITS can_do is its work: do not write it and do not request it.
  (If two robots offered the same work, you may both write it; it is sorted out later.)
- One of YOUR steps uses an object that another robot has -> RECEIVE it from that robot (the
  hand-over includes the carrying; do not ask someone to carry it). Receive only objects your own
  step uses (fill "enables"), never the result of other robots' work (a filled bathtub, a cleared
  table) and never objects you do not use.
- You need work your body cannot do -> ASK_HELP (say exactly what, which object, where).

THINK FIRST (fill these before the plan):
- "my_part": one sentence: what YOU contribute to the task.
- "left_to_others": the work you leave to other robots because they offered it ("set the table (R3)").

STEP TYPES (only these three):
- LOCAL:    work you do yourself. A FIXED robot works only at its spot; a mobile robot may also
            carry its own objects to another room ("carry the toast to the dining table").
            {{"type":"LOCAL","text":"...","serves":<goal index>}}
- RECEIVE:  an object another robot has (see its has_items or can_do) that your later step uses.
            {{"type":"RECEIVE","text":"...","item":"<object>","target":"R<n>","enables":<index of YOUR later step that uses it>,"serves":<goal index>}}
- ASK_HELP: work your body cannot do. Do NOT name a robot: describe who could do it.
            {{"type":"ASK_HELP","text":"<the exact work>","condition":"<what the helper must be able to do>","enables":<index of YOUR later step that needs it, or null>,"serves":<goal index>}}
You never write steps that give objects to others or help others (not even as a RECEIVE): the robot
that needs it will request it, and you answer requests in the next stage.

RULES:
- goals: 1-3 outcomes of YOUR part. "serves" is an index in your goals, "enables" an index in your
  steps (from 0) pointing to a LATER step; always fill "enables" for RECEIVE / ASK_HELP.
- Your LOCAL steps run in the order you write them; while waiting for a request you keep working.
- Two FIXED robots cannot give objects to each other. Every step takes 1 minute; stay in the deadline.

EXAMPLE. Task: "Make breakfast, bring it to the dining room, and put the newspaper there."
Offers: R1 (kitchen, FIXED) can_do "make toast with the bread", has_items "bread".
        R2 (kitchen, mobile) can_do "pour orange juice into the glass", can_help "carry food".
        R3 (dining room, FIXED) can_do "set the plates on the dining table".
        R4 (hallway, mobile) can_do "bring the newspaper to the dining table".
Answer of R2:
{{"reasoning":"Juice is mine. Toast is R1's, the table is R3's, the newspaper is R4's. I can move, so I bring the toast and juice.",
 "my_part":"I pour the juice and carry the toast and juice to the dining table.",
 "left_to_others":["make toast (R1)","set the plates (R3)","bring the newspaper (R4)"],
 "goals":["juice and toast are on the dining table"],
 "steps":[
  {{"type":"LOCAL","text":"pour orange juice into the glass","serves":0}},
  {{"type":"RECEIVE","text":"get the toast","item":"toast","target":"R1","enables":2,"serves":0}},
  {{"type":"LOCAL","text":"carry the toast and the glass of juice to the dining table","serves":0}}
 ]}}
(R1's answer would be one LOCAL "make toast with the bread" and nothing else: R2 receives it.)

Return JSON: {{"reasoning":"...","my_part":"...","left_to_others":[...],"goals":[...],"steps":[...]}}"""

PLAN_USER = """TASK: {task}
DEADLINE: {deadline} minutes

YOUR OFFER: {own_offer}

{others_block}"""

OTHERS_BLOCK = "OTHER ROBOTS' OFFERS: {offers}"
NO_OTHERS_BLOCK = ("OTHER ROBOTS (their offers are not shared; you know only who they are): {robots}")


# ================================================================================================
# CODE
# ================================================================================================
def tidy(raw_steps, agent: str, goals: list[str], cfg: TaskConfig) -> tuple[list[dict], list[dict]]:
    """Format-only tidy-up. Returns (kept step dicts with their raw index '_i', notes)."""
    me = cfg.agent(agent)
    others = [x for x in cfg.ids if x != agent]
    raw_steps = raw_steps if isinstance(raw_steps, list) else []
    notes: list[dict] = []
    kept: list[dict] = []
    for i, s in enumerate(raw_steps):
        s = s if isinstance(s, dict) else {}
        t = str(s.get("type", "")).upper().strip()
        text = str(s.get("text") or s.get("action") or "").strip()
        st = {"_i": i, "type": t, "text": text,
              "item": str(s["item"]).strip() if s.get("item") else None,
              "target": str(s["target"]).strip().upper() if s.get("target") else None,
              "condition": str(s["condition"]).strip() if s.get("condition") else None,
              "enables": as_int(s.get("enables")), "serves": as_int(s.get("serves"))}
        if t not in STEP_TYPES:
            notes.append({"step": i, "what": "removed", "why": f"unknown type '{t}'", "text": text})
            continue
        if t in STAGE3_ONLY:
            notes.append({"step": i, "what": "removed", "why": f"{t} is written in Stage 3 (as an answer), "
                                                               f"not in Stage 2", "text": text})
            continue
        if t == RECEIVE and st["target"] not in others:
            notes.append({"step": i, "what": "removed", "why": f"{t} names no existing other robot "
                                                               f"(target={st['target']})", "text": text})
            continue
        if t == ASK_HELP:
            if st["target"]:
                notes.append({"step": i, "what": "cleared target", "why": "ASK_HELP names no robot"})
            st["target"] = None
            st["condition"] = st["condition"] or text
        else:
            st["condition"] = None
        if not text:
            if t == RECEIVE and st["item"]:
                st["text"] = f"get the {st['item']} from {st['target']}"
            else:
                notes.append({"step": i, "what": "removed", "why": "empty step"})
                continue
        if st["serves"] is not None and not 0 <= st["serves"] < len(goals):
            notes.append({"step": i, "what": "cleared serves", "why": f"serves={st['serves']} is not a goal index"})
            st["serves"] = None
        if t not in REQUEST_TYPES and st["enables"] is not None:
            st["enables"] = None          # only requests enable a later step
        st["room"] = me.profile.room
        kept.append(st)
    # enables must point to a LATER step that survived
    alive = {s["_i"] for s in kept}
    for s in kept:
        en = s["enables"]
        if en is not None and not (en > s["_i"] and en in alive):
            notes.append({"step": s["_i"], "what": "cleared enables",
                          "why": f"enables={en} is not a later step of this plan"})
            s["enables"] = None
    # a RECEIVE must say which of my steps uses the object; without it the request has no purpose
    out = []
    for s in kept:
        if s["type"] == RECEIVE and s["enables"] is None:
            notes.append({"step": s["_i"], "what": "removed",
                          "why": "RECEIVE without a later step that uses the object (enables)", "text": s["text"]})
            continue
        out.append(s)
    alive = {s["_i"] for s in out}
    for s in out:                          # an enables pointing to a removed step is cleared too
        if s["enables"] is not None and s["enables"] not in alive:
            s["enables"] = None
    return out, notes


async def make_local_plan(cfg: TaskConfig, agent: str, offers: dict[str, Offer], llm: BaseLLM,
                          log: EventLog, *, share_offers: bool = True) -> tuple[Plan, dict]:
    me = cfg.agent(agent)
    own = offers[agent]
    if share_offers:
        others = OTHERS_BLOCK.format(offers=_j([o.public() for a, o in offers.items() if a != agent]))
    else:
        others = NO_OTHERS_BLOCK.format(robots=_j({a.id: {"room": a.profile.room, "mobile": a.profile.mobile}
                                                    for a in cfg.agents if a.id != agent}))
    system = PLAN_SYSTEM.format(agent=agent, room=me.profile.room)
    user = PLAN_USER.format(task=cfg.task, deadline=cfg.deadline_min, own_offer=_j(own.public()),
                            others_block=others)
    d = await llm.complete(system, user, key=f"plan:{agent}")
    goals = as_list(d.get("goals"))
    kept, notes = tidy(d.get("steps"), agent, goals, cfg)

    plan = Plan(agent=agent, goals=goals, nodes={}, order=[])
    raw_to_id: dict[int, str] = {}
    for s in kept:
        nid = plan.new_id()
        raw_to_id[s["_i"]] = nid
        plan.insert(Node(id=nid, agent=agent, type=s["type"], text=s["text"], room=s["room"], item=s["item"],
                         target=s["target"], condition=s["condition"], serves=s["serves"]))
    for s in kept:
        if s["enables"] is not None:
            plan.nodes[raw_to_id[s["_i"]]].enables = raw_to_id[s["enables"]]
    for n in notes:
        log.log("plan", agent, n["what"], step=n["step"], why=n["why"])
    log.log("plan", agent, "broadcast", goals=len(goals), steps=len(plan.order),
            requests=sum(x.type in REQUEST_TYPES for x in plan.steps()))
    return plan, {"reasoning": d.get("reasoning", ""), "my_part": d.get("my_part", ""),
                  "left_to_others": as_list(d.get("left_to_others")), "tidy_notes": notes,
                  "n_raw_steps": len(d.get("steps") or []) if isinstance(d.get("steps"), list) else 0}
