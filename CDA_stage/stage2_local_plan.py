"""Stage 2 - Local Plan. Each robot, in parallel, writes LOCAL / ASK_HELP / RECEIVE / PASS steps.

Code checks FORMAT only (numbers and lists, never meaning):
- the step type is allowed; target is another existing robot
- uses / enables / serves are existing indices (enables: an own LATER LOCAL step; required for ASK_HELP)
- a PASS item is in the robot's own has_items; a RECEIVE item is in the target's has_items
- two fixed robots do not exchange an object; a LOCAL step is in the robot's own room
On format errors the robot rewrites its plan ONCE. Steps that still have format errors are excluded
before broadcast and recorded. Meaning (duplicates, infeasible actions, ...) is judged in Stage 4.2.

Plan-shape rules (SOFT: they trigger the rewrite but never exclude a step, so a main action is not lost):
- an object action names the exact place of the object (not just the room)
- a mobile robot writes a move_to step before it acts at a different place; a room change names the room
- every pick_up is followed by a put_down / place / PASS of the same object. If the plan still ends with
  the object in hand after the rewrite, the code appends the put_down (back to the place it was picked from).
"""
from __future__ import annotations

import re

from .llm import BaseLLM
from .core import (ASK_HELP, CAPABILITY_TAGS, LOCAL, PASS, PLAN_TYPES, RECEIVE, REQUEST_TYPES,
                      EventLog, Node, Offer, TaskConfig, _j, action_str, agent_num, indexed, match_item, norm)


# ================================================================================================
# PROMPTS — Stage 2 Local Plan
# ================================================================================================

# ================================================================ Shared guidance (prompt only, no rule checks)
_WORDING = """WORDING:
- EXACT NAMES: use the exact has_items name everywhere.
- Avoid vague words: help with, assist, prepare, handle, ensure, take care of, tidy up, organize,
  arrange, coordinate, as needed, if necessary, etc., all, other, remaining, everything,
  "safe location", "appropriate place", "nearby", "somewhere".
- CONCRETE DESTINATIONS: every move/place/put_down names real furniture.
  CORRECT: "move mug from counter to cabinet shelf"   WRONG: "move mug to safe location"
- PHYSICAL ACTIONS ONLY: atomic actions that change the room (no look / check / search / monitor;
  robots cannot explore). CORRECT: "turn off ceiling lamp" + "turn on floor lamp"   WRONG: "dim the lights"
- ONE OBJECT, ONE STEP, ONCE. Every pick_up is followed by put_down, PASS, or use.
- NO MEANINGLESS MOVES: never pick up an object only to put it back where it started (or an
  equivalent spot) -- if an object does not need to move or change state, leave it alone entirely.
  Every pick_up must lead to a genuinely different location, a hand-off (PASS), or a real state
  change (slice/cook/toggle/open/...), never a round trip back to its own starting place.
- YOUR OWN HAND: you have no separate word for your gripper/hand -- when an object ends up in your
  own grasp, call that place by your own name "{agent}", not "gripper"/"arm"/"hand".
  CORRECT: "from":"counter","to":"{agent}" (picking it up), then "from":"{agent}","to":"shelf"
  (putting it down)   WRONG: "to":"gripper" / "from":"my hand" / "to":"the arm"."""

_ESSENTIAL = """TEAM GOAL: ESSENTIAL work first — what the task cannot succeed without.
Think beyond literal words: "watch a movie" -> TV on + sofa arranged + lighting adjusted + snacks.
"guest coming" -> seating ready + drinks + surfaces clear.
Use the deadline well: more robots = more parallel work.
FINISH WHAT YOU START: if an object must end up somewhere specific (another room, a named robot,
a container) to satisfy a goal, your plan must carry it all the way there -- not just pick it up,
prepare it (e.g. slice it), or move it partway and stop. If you will not have time to finish every
goal, drop a lower-priority goal entirely rather than leaving a started one half-done: an item you
picked up, prepared, or half-moved and then abandoned is worse than one you never touched."""

_SPACE_RULES = """SPACE RULES:
- Every robot works only in its OWN room unless doing HELP/PASS/RECEIVE.
- Two collaboration types only:
  CAPABILITY: your body cannot do it -> ASK_HELP (target = a robot whose body can).
  OBJECT: you need an object from another room -> RECEIVE (target = the robot that has it).
- Mobile giver brings the object. Fixed giver hands over; mobile receiver collects.
  Two fixed robots cannot exchange objects. Never ask a third robot to carry."""


# ================================================================ Stage 2: Local Plan
PLAN_SYSTEM = """You are robot {agent} in the {room}. Write YOUR part of the shared plan as a list of steps.

Current environment state (S0): {env_state}

THINK FIRST (write it in "reasoning"):
1. MY SUB-GOALS: your own "intends" (numbered in YOUR intends). Every step serves one of them.
2. OTHER ROBOTS: read ALL robots' intends in ALL OFFERS. Do not repeat work another robot intends.
3. MY STEPS: what my body does in my room, using my has_items and can_do.
4. COLLABORATION: what my body cannot do (ASK_HELP), what I need from another room (RECEIVE),
   what I can offer to another room (PASS).
   If a FIXED robot's own OFFER lists "see_items" (visible but out of its reach), and one of those
   objects is needed, that robot cannot fetch it itself: ASK_HELP a mobile robot to bring it over,
   or (if the object is already closer to you) RECEIVE it yourself once someone else picks it up.

STEP FORMAT (indices are positions in YOUR steps list, starting at 0):
- LOCAL:    {{"type":"LOCAL", "action":{{"verb":"...","object":"...","from":"...","to":"..."}}, "uses":<index in YOUR can_do>, "serves":<index in YOUR intends>}}
  Verbs: move_to, move, pick_up, put_down, push, slice, cook, turn_on, turn_off, open, close, fill, place, pour
  "move" relocates an OBJECT (it needs "object"); "move_to" is YOU travelling (it has no "object", see MOVING).
- ASK_HELP: {{"type":"ASK_HELP", "action":{{...what the other robot should do...}}, "condition":{{"mobile":true/false,"can_do_keyword":"..."}}, "enables":<index of YOUR later LOCAL step that needs it>, "serves":<intends index>}}
  Do NOT name a specific robot. Instead describe, in "condition", what capability the helper must
  have: "can_do_keyword" MUST be exactly one tag from this fixed list -- {capability_tags_list} --
  never a free-text phrase (a made-up word like "PourObject" matches nobody; only these tags do).
  Pick the tag whose name covers the action, e.g. MANIPULATE_HEAVY for furniture-class objects,
  MANIPULATE_LIGHT for small ones, LIQUID_HANDLING for pouring/filling. BEFORE writing the ASK_HELP,
  check the OFFERS above: if no robot's "capability_tags" contains the tag you are about to request
  (not even yourself), that help does not exist anywhere on this team -- do not request it; instead
  find a different action, using a tag someone (possibly you) actually has, that still serves the
  same intend (e.g. hand over an already-filled container instead of asking someone to pour).
  Every robot whose capability_tags contains the tag will be asked in Stage 3; the best one is
  chosen later -- you do not pick who.
  ONLY set "mobile" when the helper genuinely needs to TRAVEL to reach you (e.g. bring an object from
  elsewhere, or physically come help in your room). If the help happens right where you already are
  (you need a capability, not a visitor), omit "mobile" (or set it to null) -- naming a mobile
  requirement you don't actually need can rule out the one fixed robot who could otherwise help.
- RECEIVE:  {{"type":"RECEIVE", "item":"exact name from target's has_items", "target":"RN", "enables":<optional: index of YOUR later LOCAL step that uses it>, "serves":<intends index>}}
- PASS:     {{"type":"PASS", "item":"exact name from YOUR has_items", "target":"RN", "serves":<intends index>}}
  (an offer: the receiver decides later whether to take it)
- "target" (RECEIVE / PASS only) is a hint ("I hope this robot does it"); another robot may answer instead.

PLACES, MOVING AND PUTTING DOWN (these three rules are required):
1. WHERE THE OBJECT IS: every action on an object names the exact place of that object, as furniture or a
   surface together with its room, e.g. "bedroom_desk", "living_room_floor" -- never only the room name.
   pick_up / move / push / open / close / turn_on / turn_off / slice / cook / fill / pour: put it in "from".
   put_down / place: put the target place in "to".
2. MOVING: if you are MOBILE (see ROBOT PROFILES), travel with a step before you act at a different place:
   {{"type":"LOCAL","action":{{"verb":"move_to","from":"<where you are now>","to":"<place you go to>","room":"<room of that place>"}},"serves":<intends index>,"preconditions":[],"effects":[]}}
   When the place is in ANOTHER room (for example to bring an object to a robot there before a PASS), "room"
   must be that room's name: a room change is always written out. A FIXED robot never uses move_to; it acts only
   from where it is, in its own room.
3. PICK UP => PUT DOWN: every pick_up must be followed, later in YOUR steps, by a put_down / place of that same
   object, or by a PASS of it. Never end your plan still holding an object.
4. TIME BUDGET: every step takes about 1 minute (a PASS in which you travel to the receiver takes 2), and YOUR
   steps run one after another, move_to included. The sum of your minutes must fit inside the DEADLINE. Plan the
   essential goals first. If your steps (with the moves) do not fit, drop the lowest-priority goal completely
   instead of starting something you cannot finish.

PRECONDITIONS AND EFFECTS -- for EVERY step you write, you MUST also include:
- "preconditions": conditions that must already be true before this step can run.
  Each one: {{"object_id":"...","field":"location"|"toggle"|"clean","value":"..."}}
- "effects": state changes caused by this step once it completes.
  Each one: {{"object_id":"...","field":"location"|"toggle"|"clean","value":"..."}}
Every step's preconditions must already be satisfied -- either by S0 above, or by the effects of an
earlier step in YOUR OWN plan. If a precondition is not yet satisfied by anything you control (the
object is not yet in your hands / room), insert a RECEIVE or ASK_HELP step first to satisfy it.

""" + _WORDING + "\n" + _ESSENTIAL + "\n" + _SPACE_RULES + """

EXAMPLE (R4 = mobile light robot in the living room; intends = ["safe walkway for the grandmother", "tea served at the sofa"]):
{{"reasoning":"1) My goals: walkway (0), tea at the sofa (1). 2) R1 makes tea, R3 pushes furniture. 3) I clear small items from the floor. 4) The armchair is too heavy for me -> ASK_HELP (mobile/heavy-capable helper); I need the mug from R1 -> RECEIVE.",
 "steps":[
  {{"type":"LOCAL","action":{{"verb":"move_to","from":"living_room_door","to":"living_room_floor","room":"living_room"}},"serves":0,
   "preconditions":[],"effects":[]}},
  {{"type":"LOCAL","action":{{"verb":"move","object":"black bag","from":"floor","to":"shelf"}},"uses":0,"serves":0,
   "preconditions":[{{"object_id":"Bag_1","field":"location","value":"living_room_floor"}}],
   "effects":[{{"object_id":"Bag_1","field":"location","value":"living_room_shelf"}}]}},
  {{"type":"ASK_HELP","action":{{"verb":"push","object":"brown armchair","from":"walkway","to":"wall"}},
   "condition":{{"mobile":true,"can_do_keyword":"MANIPULATE_HEAVY"}},"enables":4,"serves":0,
   "preconditions":[{{"object_id":"Armchair_1","field":"location","value":"living_room_walkway"}}],
   "effects":[{{"object_id":"Armchair_1","field":"location","value":"living_room_wall"}}]}},
  {{"type":"LOCAL","action":{{"verb":"move_to","from":"living_room_floor","to":"living_room_shelf","room":"living_room"}},"serves":0,
   "preconditions":[],"effects":[]}},
  {{"type":"LOCAL","action":{{"verb":"place","object":"floor mat","from":"shelf","to":"walkway"}},"uses":0,"serves":0,
   "preconditions":[{{"object_id":"Armchair_1","field":"location","value":"living_room_wall"}}],
   "effects":[{{"object_id":"Mat_1","field":"location","value":"living_room_walkway"}}]}},
  {{"type":"RECEIVE","item":"white mug","target":"R1","enables":7,"serves":1,
   "preconditions":[{{"object_id":"Mug_1","field":"toggle","value":null}}],
   "effects":[{{"object_id":"Mug_1","field":"location","value":"robot_R4"}}]}},
  {{"type":"LOCAL","action":{{"verb":"move_to","from":"living_room_shelf","to":"living_room_coffee_table","room":"living_room"}},"serves":1,
   "preconditions":[],"effects":[]}},
  {{"type":"LOCAL","action":{{"verb":"put_down","object":"white mug","from":"R4","to":"coffee table"}},"uses":0,"serves":1,
   "preconditions":[{{"object_id":"Mug_1","field":"location","value":"robot_R4"}}],
   "effects":[{{"object_id":"Mug_1","field":"location","value":"living_room_coffee_table"}}]}}
 ]}}

Return JSON: {{"reasoning":"...", "steps":[...]}}"""

PLAN_USER = """## TASK:
{task}
DEADLINE: {deadline} minutes

YOUR OFFER: {own_offer}
YOUR can_do (use these indices for "uses"):
{can_do_indexed}
YOUR intends (use these indices for "serves"):
{intends_indexed}
ALL OFFERS: {public_offers}
ROBOT PROFILES: {profiles}"""

PLAN_FIX = """Your plan has FORMAT errors (wrong indices, unknown robots, items not in a has_items list, ...):
{errors}
Fix ONLY these problems and return the full corrected JSON {{"reasoning":"...", "steps":[...]}}."""


def plan_system(agent: str, room: str, env_state: str = "[]") -> str:
    from .core import CAPABILITY_TAGS
    return PLAN_SYSTEM.format(agent=agent, room=room, env_state=env_state,
                              capability_tags_list=", ".join(CAPABILITY_TAGS))


# ================================================================================================
# CODE — Stage 2 Local Plan
# ================================================================================================

_PRE_EFF_FIELDS = {"location", "toggle", "clean"}


def _as_ops(raw) -> list[dict]:
    """A preconditions/effects list: keep only well-formed {object_id, field, value} dicts."""
    out = []
    for x in raw or []:
        if not isinstance(x, dict):
            continue
        oid, fld = x.get("object_id"), x.get("field")
        if not oid or fld not in _PRE_EFF_FIELDS:
            continue
        out.append({"object_id": str(oid), "field": fld, "value": x.get("value")})
    return out


_ROOM_STOP = {"the", "a", "an", "of", "in", "on", "at", "room", "bedroom", "bathroom", "kitchen", "living", "dining"}
_OBJ_FROM = {"pick_up", "move", "push", "open", "close", "turn_on", "turn_off", "slice", "cook", "fill", "pour"}
_OBJ_TO = {"put_down", "place", "drop"}


def _words(x) -> set[str]:
    return {w for w in re.split(r"[^a-z0-9]+", str(x or "").lower()) if w}


def _specific(place) -> bool:
    """The place names furniture or a surface, not only the room."""
    return bool(_words(place) - _ROOM_STOP)


def _same_place(a, b) -> bool:
    wa, wb = _words(a), _words(b)
    return bool(wa) and bool(wb) and (wa <= wb or wb <= wa)


def _int(x):
    if isinstance(x, bool):
        return None
    if isinstance(x, int):
        return x
    if isinstance(x, str) and x.strip().lstrip("-").isdigit():
        return int(x.strip())
    return None


def validate(raw_steps: list, agent: str, offers: dict[str, Offer], cfg: TaskConfig
             ) -> tuple[list[dict], list[str]]:
    """Return step dicts (each with its own 'errors' list) and all error strings."""
    me = cfg.agent(agent)
    own = offers[agent]
    others = [x for x in cfg.ids if x != agent]
    raw_steps = raw_steps if isinstance(raw_steps, list) else []
    types = [str(s.get("type", "")).upper().strip() if isinstance(s, dict) else "" for s in raw_steps]
    steps, errors = [], []
    state: dict[str, dict] = {}
    for obj in own.env_state:
        state[obj.object_id] = {"location": obj.location, "toggle": obj.toggle, "clean": obj.clean}
    # objects this robot may legally name in a LOCAL action: its own has_items, plus anything it
    # expects to RECEIVE later in this same plan (a RECEIVE's declared "enables" LOCAL step uses an
    # item that is not yet in has_items but is still grounded, not hallucinated)
    grounded_items = list(own.has_items) + [str(s["item"]) for s in raw_steps
                                            if isinstance(s, dict) and str(s.get("type", "")).upper() == RECEIVE
                                            and s.get("item")]
    held: str | None = None     # object currently in this robot's own grasp (LOCAL steps only)
    held_step: int | None = None          # index of the pick_up that put it there
    cur_room = me.profile.room            # changes only through a move_to with a room
    cur_at: str | None = None             # place the robot is at (None: no place yet)
    rooms = {frozenset(_words(a.profile.room)) for a in cfg.agents}
    for i, s in enumerate(raw_steps):
        s = s if isinstance(s, dict) else {}
        t = types[i]
        e: list[str] = []
        soft: list[str] = []      # plan-shape feedback: triggers the rewrite, never excludes the step
        st = {"_i": i, "type": t, "action": s.get("action", ""),
              "item": str(s["item"]).strip() if s.get("item") else None,
              "target": str(s["target"]).strip().upper() if s.get("target") else None,
              "condition": s.get("condition") if isinstance(s.get("condition"), dict) else None,
              "uses": _int(s.get("uses")), "enables": _int(s.get("enables")),
              "serves": _int(s.get("serves")), "location": me.profile.room,
              "preconditions": _as_ops(s.get("preconditions")), "effects": _as_ops(s.get("effects"))}
        if t not in PLAN_TYPES:
            e.append(f"type '{t}' is not allowed (use LOCAL, ASK_HELP, RECEIVE, PASS)")
        if not (st["serves"] is not None and 0 <= st["serves"] < len(own.intends)):
            e.append(f"serves={s.get('serves')} is not an index of your intends (0..{len(own.intends) - 1})")
        for pre in st["preconditions"]:
            obj_id, field, expected = pre["object_id"], pre["field"], pre["value"]
            actual = state.get(obj_id, {}).get(field)
            if actual != expected:
                e.append(f"precondition not met for {obj_id}.{field}: expected '{expected}', current '{actual}'")
        if t == LOCAL:
            act = st["action"] if isinstance(st["action"], dict) else {}
            verb = str(act.get("verb", "")).strip().lower()
            if verb == "move_to":
                st["uses"] = None                       # travelling needs no can_do entry
            elif not (st["uses"] is not None and 0 <= st["uses"] < len(own.can_do)):
                e.append(f"uses={s.get('uses')} is not an index of your can_do (0..{len(own.can_do) - 1})")
            loc = s.get("location")
            if loc and norm(str(loc)) != norm(cur_room):
                e.append(f"LOCAL is in '{loc}', but you are in '{cur_room}' (a room change is written as move_to)")
            if not action_str(st["action"]):
                e.append("LOCAL needs an action")
            st["enables"] = None
            obj = act.get("object")
            if verb == "move_to":
                dest, room = str(act.get("to") or "").strip(), str(act.get("room") or "").strip()
                if not me.profile.mobile:
                    e.append("you are a FIXED robot: do not use move_to (you act only from where you are)")
                if not dest:
                    e.append("move_to needs 'to' (the place you go to)")
                if not room:
                    soft.append("move_to needs 'room': the room of the place (a room change must be written out)")
                elif frozenset(_words(room)) not in rooms:
                    soft.append(f"move_to room '{room}' is not one of {sorted(a.profile.room for a in cfg.agents)}")
                elif me.profile.mobile and dest:
                    cur_room, cur_at = room, dest
            else:
                if obj:
                    hit = match_item(obj, grounded_items)
                    if hit is None:
                        e.append(f"object '{obj}' is not in your has_items {own.has_items} "
                                 "(do not invent objects not on your own list)")
                    else:
                        obj = hit
                where = act.get("from") if verb in _OBJ_FROM else act.get("to") if verb in _OBJ_TO else None
                if verb in _OBJ_FROM and not _specific(act.get("from")):
                    soft.append(f"'{verb}': name the exact place of '{obj}' in 'from' (furniture or surface and its room, "
                                "not only the room)")
                if verb in _OBJ_TO and not _specific(act.get("to")):
                    soft.append(f"'{verb}': name the exact target place of '{obj}' in 'to' (furniture or surface and its "
                                "room, not only the room)")
                if me.profile.mobile and where and _specific(where):
                    if cur_at is None or not _same_place(cur_at, where):
                        soft.append(f"you are at '{cur_at or 'your start'}': add a move_to step to '{where}' before this step")
                    cur_at = str(where)
                if verb == "pick_up":
                    if held is not None and obj and norm(obj) != norm(held):
                        e.append(f"still holding '{held}' -- put it down (or PASS/use it) "
                                 f"before picking up '{obj}'")
                    elif not e:     # don't update held state off a step that's already broken
                        held, held_step = obj, i
                elif verb in ("put_down", "place", "drop"):
                    held, held_step = None, None
        st["location"] = cur_room    # the robot's current room, kept from the last move_to -- not just for
                                      # LOCAL: PASS/RECEIVE/ASK_HELP happen wherever the robot now stands
        if t in (RECEIVE, PASS):
            st["uses"] = None
            if st["target"] not in others:
                e.append(f"{t} needs a target among {others}, got {st['target']}")
        if t == ASK_HELP:
            st["target"] = None
            if not action_str(st["action"]):
                e.append("ASK_HELP needs an action")
            if not st["condition"]:
                e.append("ASK_HELP must have 'condition' dict, not 'target'")
            else:
                kw = st["condition"].get("can_do_keyword")
                if kw:
                    kw = str(kw).strip().upper()
                    if kw not in CAPABILITY_TAGS:
                        e.append(f"condition.can_do_keyword must be exactly one of {CAPABILITY_TAGS}, "
                                 f"not '{s['condition'].get('can_do_keyword')}'")
                    else:
                        st["condition"]["can_do_keyword"] = kw
            en = st["enables"]
            if not (en is not None and i < en < len(raw_steps) and types[en] == LOCAL):
                e.append(f"ASK_HELP needs 'enables' = index of one of YOUR later LOCAL steps (got {s.get('enables')})")
        if t == RECEIVE:
            en = st["enables"]
            if en is not None and not (i < en < len(raw_steps) and types[en] == LOCAL):
                e.append(f"RECEIVE 'enables'={en} is not one of YOUR later LOCAL steps (omit it or fix it)")
            if not st["item"]:
                e.append("RECEIVE needs an item")
            elif st["target"] in offers:
                hit = match_item(st["item"], offers[st["target"]].has_items)
                if hit is None:
                    e.append(f"RECEIVE item '{st['item']}' is not in {st['target']}'s has_items "
                             f"{offers[st['target']].has_items}")
                else:
                    st["item"] = hit
            if st["target"] in cfg.ids and cfg.mover(st["target"], agent) is None:
                e.append(f"{st['target']} and {agent} are both fixed: nobody can move an object between them")
            st["action"] = action_str(st["action"]) or f"receive {st['item']}"
        if t == PASS:
            st["enables"] = None
            held, held_step = None, None
            if not st["item"]:
                e.append("PASS needs an item from YOUR has_items")
            else:
                hit = match_item(st["item"], own.has_items)
                if hit is None:
                    e.append(f"PASS item '{st['item']}' is not in YOUR has_items {own.has_items}")
                else:
                    st["item"] = hit
            if st["target"] in cfg.ids and cfg.mover(agent, st["target"]) is None:
                e.append(f"{agent} and {st['target']} are both fixed: nobody can move an object between them")
            st["action"] = action_str(st["action"]) or f"pass {st['item']} to {st['target']}"
        st["errors"] = e
        st["soft"] = soft
        errors += [f"step {i}: {x}" for x in e + soft]
        if not e:
            for eff in st["effects"]:
                obj_id, field, value = eff["object_id"], eff["field"], eff["value"]
                state.setdefault(obj_id, {"location": None, "toggle": None, "clean": None})[field] = value
        steps.append(st)
    minutes = sum(1 if t in (LOCAL, RECEIVE) else
                  (2 if t == PASS and s_.get("target") in cfg.ids and cfg.mover(agent, str(s_["target"]).upper()) == agent else 1)
                  if t == PASS else 0
                  for t, s_ in zip(types, (x if isinstance(x, dict) else {} for x in raw_steps)))
    if minutes > cfg.deadline_min:        # SOFT: triggers the rewrite, never excludes a step
        errors.append(f"your own steps need about {minutes} minutes, but the deadline is {cfg.deadline_min}: "
                      "keep the essential goals and drop the lowest-priority goal completely")
    if held is not None and held_step is not None and held_step < len(steps):
        steps[held_step]["unreleased"] = True
        errors.append(f"step {held_step}: you pick up '{held}' but never put it down or PASS it: "
                      "add a put_down / place (or PASS) of it later in your steps")
    if not raw_steps:
        errors.append("plan has no steps")
    return steps, errors


async def make_local_plan(cfg: TaskConfig, agent: str, offers: dict[str, Offer], llm: BaseLLM,
                          log: EventLog, max_fix: int = 2) -> tuple[list[Node], dict]:
    me = cfg.agent(agent)
    own = offers[agent]
    system = plan_system(agent, me.profile.room, env_state=_j([
        {"object_id": o.object_id, "object_type": o.object_type, "location": o.location,
         "accessible": o.accessible, "toggle": o.toggle, "clean": o.clean} for o in own.env_state]))
    user = PLAN_USER.format(
        task=cfg.task, deadline=cfg.deadline_min, own_offer=_j(own.to_dict()),
        can_do_indexed=indexed(own.can_do), intends_indexed=indexed(own.intends),
        public_offers=_j([o.public() for o in offers.values()]),
        profiles=_j({a.id: {"room": a.profile.room, "mobile": a.profile.mobile,
                            **({"payload_kg": a.profile.payload_kg} if a.profile.payload_kg else {}),
                            "embodiment": a.profile.embodiment} for a in cfg.agents}),
    )
    d = await llm.complete(system, user, key=f"plan:{agent}")
    steps, errors = validate(d.get("steps"), agent, offers, cfg)
    first_errors = list(errors)
    n_fix = 0
    while errors and n_fix < max_fix:          # one self-fix, format errors only
        n_fix += 1
        log.log("plan", agent, "self_fix", errors=len(errors))
        fix_user = user + "\n\nYOUR PREVIOUS PLAN:\n" + _j(d) + "\n\n" + PLAN_FIX.format(
            errors="\n".join(f"- {x}" for x in errors))
        d = await llm.complete(system, fix_user, key=f"plan:{agent}:fix")
        steps, errors = validate(d.get("steps"), agent, offers, cfg)

    # steps with remaining format errors are excluded before broadcast
    kept = [s for s in steps if not s["errors"]]
    excluded = [{"step": s["_i"], "type": s["type"], "text": action_str(s["action"]) or (s["item"] or ""),
                 "errors": s["errors"]} for s in steps if s["errors"]]
    n = agent_num(agent)
    nodes: list[Node] = []
    raw_to_id: dict[int, str] = {}
    for k, s in enumerate(kept, start=1):
        nid = f"r{n}_s{k}"
        raw_to_id[s["_i"]] = nid
        nodes.append(Node(id=nid, agent=agent, type=s["type"], action=s["action"], item=s["item"],
                          target=s["target"], condition=s["condition"], uses=s["uses"], location=s["location"],
                          origin="offer" if s["type"] == PASS else "local",
                          serves=s["serves"], serves_text=own.intends[s["serves"]],
                          preconditions=s["preconditions"], effects=s["effects"]))
    for s, node in zip(kept, nodes):
        if s["enables"] is not None:
            node.enables = raw_to_id.get(s["enables"])     # None if the enabled step was excluded
    for s in kept:                       # still holding an object after the rewrites: put it back where it was
        if not s.get("unreleased"):
            continue
        pick = nodes[kept.index(s)]
        obj_id = next((p["object_id"] for p in pick.preconditions if p.get("field") == "location"), None)
        back = next((p["value"] for p in pick.preconditions if p.get("field") == "location"), None)
        act = pick.action if isinstance(pick.action, dict) else {}
        place = act.get("from") or back or me.profile.room
        nid = f"r{n}_s{len(nodes) + 1}"
        nodes.append(Node(id=nid, agent=agent, type=LOCAL,
                          action={"verb": "put_down", "object": act.get("object", ""), "from": agent, "to": place},
                          location=me.profile.room, origin="auto_release", uses=pick.uses, serves=pick.serves,
                          serves_text=pick.serves_text,
                          preconditions=([{"object_id": obj_id, "field": "location", "value": f"robot_{agent}"}] if obj_id else []),
                          effects=([{"object_id": obj_id, "field": "location", "value": back or place}] if obj_id else [])))
        log.log("plan", agent, "auto_release", item=str(act.get("object", "")), to=str(place))
    for x in excluded:
        log.log("plan", agent, "step_excluded", step=x["step"], errors=len(x["errors"]))
    log.log("plan", agent, "broadcast", steps=len(nodes),
            requests=sum(x.type in REQUEST_TYPES for x in nodes),
            offers=sum(x.type == PASS for x in nodes), excluded=len(excluded))
    return nodes, {"reasoning": d.get("reasoning", ""), "fix_rounds": n_fix,
                   "format_errors_first": first_errors, "remaining_errors": errors, "excluded": excluded}
