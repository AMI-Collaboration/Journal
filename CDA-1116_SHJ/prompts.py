"""All prompts in one place. Every prompt asks for exactly one JSON object (design v4)."""
from __future__ import annotations

import json


def _j(x) -> str:
    return json.dumps(x, ensure_ascii=False, indent=1)


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


# ================================================================ Stage 1: Offer
OFFER_SYSTEM = """You are robot {agent}, a household robot that sees only its own room.

KNOWN OBJECTS IN THIS ROOM (ground truth -- the only objects that actually exist here):
{object_catalog}
Every object you name in has_items / see_items / env_state must be one of these types (you may still
describe it naturally, e.g. "green apple" for a catalog entry "Apple" -- the catalog gives the type,
not the exact words you must use). If you see more than one of the same type, number them when you
write env_state ("Apple_1", "Apple_2", ...). Never name a type that is not on this list, and never
skip an item just because its exact name isn't here -- match it to the closest real type instead.

STEP 1 — LIST has_items: every clearly visible movable object (and furniture you act on) in your images.
Format: "<color> <noun> (<location>, image <k>)". Never infer unlisted objects. Only what you directly see.
Before moving on, cross-check your list against the KNOWN OBJECTS catalog above: look back through your
images for any catalog item you have not listed yet, especially one whose function matches something the
task text literally asks for (e.g. a Faucet for water/filling, a Lamp for lighting, a Stove for cooking).
A fixture you'd normally overlook (a faucet, a switch) is still an item you must list if it is visible and
the task needs it.

STEP 1b — LIST other_robots_in_room: other robots visible in YOUR OWN images only (never a robot you
only infer is in another room). Format: [{{"id":"R2 (or unknown_1 if you cannot read its id)","distance":"close"|"far"}}].

STEP 1c — LIST env_state: for every object in has_items (and see_items, if you were asked for one), give its current state:
[{{"object_id":"Kettle_1","object_type":"Kettle","location":"<room>_<furniture>","accessible":true/false,
"toggle":"on"|"off"|null,"clean":"dirty"|"clean"|null}}]
- "toggle" only for objects that can be switched on/off (Kettle, Microwave, Lamp, TV, ...); otherwise null.
- "clean" only for objects that can be dirty/clean (Plate, Mug, Fork, dishware, ...); otherwise null.
- "accessible" is true only for has_items objects, false for see_items objects.
- "location" follows AI2-THOR style: room name + the furniture/surface it is on.
- Only your own room's objects -- never guess at objects in another room.

STEP 2 — THINK (write it in "reasoning"):
a) GOAL STATE: what must be true when the task is done? Think beyond literal words.
b) EACH ROOM'S ROLE: what does each room contribute toward that end state?
c) MY CONTRIBUTION: which parts of that end state can MY room and MY body serve?
d) PRIORITY: which of my contributions matter most given the deadline?
e) COMPLETENESS CHECK: re-read the task text literally. For every action it explicitly names
   (fill, pour, slice, turn on/off, ...), does it match a capability on YOUR can_do list? If so,
   claim it as one of your intends, even if you assume another robot will also do it, and even if
   you cannot act on it alone from your own room (that is what ASK_HELP/RECEIVE in Stage 2 are for).
   You do not yet see other robots' offers, so you cannot know who else might claim it -- a goal no
   one claims never gets attempted at all, while a goal claimed twice is simply resolved later.
   Claiming too much is always safer than leaving a literal, capability-matched requirement unclaimed.

STEP 3 — FILL FIELDS:
- capability: one sentence about your body.
- can_do: body abilities with limits (max 5). Include "ToggleObject: turn on/off lights, TV,
  appliances" unless physically impossible.
- cannot_do: what your body truly cannot do and why. Do not plan these yourself later.
- need_from_others: describe by FUNCTION, not object name.
- intends: the SUB-GOALS you take on (outcomes, not steps), most important first, max 4.
  CORRECT: "warm tea ready for the grandmother"   WRONG: "toggle silver kettle"
- obs_scope: what you can/cannot observe (kept private).

""" + _WORDING + "\n" + _ESSENTIAL + "\n" + _SPACE_RULES + """

EXAMPLE (grandmother visit, R1 = mobile light robot in the kitchen):
{{"has_items":["silver kettle (counter, image 1)","white mug (cabinet, image 1)","green apple (counter, image 2)"],
 "other_robots_in_room":[],
 "env_state":[
   {{"object_id":"Kettle_1","object_type":"Kettle","location":"kitchen_counter","accessible":true,"toggle":"off","clean":null}},
   {{"object_id":"Mug_1","object_type":"Mug","location":"kitchen_cabinet","accessible":true,"toggle":null,"clean":"dirty"}},
   {{"object_id":"Apple_1","object_type":"Apple","location":"kitchen_counter","accessible":true,"toggle":null,"clean":null}}
 ],
 "reasoning":"a) Grandmother needs warm tea and a snack. b) Kitchen: drinks and food; living room: seating. c) I can heat water and fill a mug, and bring fruit. d) Tea first, the kettle takes time.",
 "capability":"I am mobile and can carry light objects up to 5 kg with one arm.",
 "can_do":["PickupLightObject: lift mugs, fruit, small items","PourObject: pour from a kettle into a cup","ToggleObject: turn on/off kettle, lights, appliances"],
 "cannot_do":["PickupHeavyObject: cannot lift furniture","SliceObject: no cutting tool"],
 "need_from_others":["someone who can slice fruit"],
 "intends":["warm tea ready for the grandmother","fresh fruit available as a snack"],
 "obs_scope":"I can observe the kitchen only."}}

Return JSON (add "see_items" too, only if you were asked for one above):
{{"has_items": [...], "other_robots_in_room": [...], "env_state": [...],
 "reasoning": "a)... b)... c)... d)...", "capability": "...",
 "can_do": [...], "cannot_do": [...], "need_from_others": [...], "intends": [...], "obs_scope": "..."}}"""

SEE_ITEMS_BLOCK = """
ADDITIONAL FIELD -- you are a FIXED robot, so some visible objects may be out of your reach:
see_items: objects you can see in the images but CANNOT reach or interact with
(e.g. objects on high shelves, behind barriers, too far from your fixed base).
Format: exact same as has_items. Only for fixed robots -- you are one, so include this field.
If every visible object is reachable, return an empty list, but still include the field.
"""

OFFER_USER = """## TASK (serve this only):
{task}
DEADLINE: {deadline} minutes

YOUR BODY: room={room}, mobile={mobile}, payload={payload}, embodiment={embodiment}
{see_items_block}
ABOUT AREAS YOU CANNOT SEE:
{instruction}

Images attached ({n_img} image(s)), image 1 to {n_img}."""


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
  have (mobile, and/or a keyword that must appear in their can_do, e.g. "PickupHeavyObject" for
  furniture-class objects vs "PickupLightObject" for small ones -- there is no numeric weight to give,
  only light/heavy). Every robot that meets the condition will be asked in Stage 3; the best one is
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
   "condition":{{"mobile":true,"can_do_keyword":"PushFurniture"}},"enables":4,"serves":0,
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


# ================================================================ Stage 3: Edge Proposal
PROPOSE_SYSTEM = """You are robot {agent}. Other robots published requests (ASK_HELP, RECEIVE) and offers (PASS to you).
Answer each one with YES or NO, using your own body, items and plan.

- REQUESTS: answer the ones you can serve. "target" is only a hint: YES is allowed even if another robot
  was named, NO is allowed even if you were named. You may skip requests that have nothing to do with you.
  YES to an ASK_HELP: give "action" (what you will do) and "uses" (index in YOUR can_do).
    Mobile robots may go to the requester's room; a fixed robot can only help in its own room.
  YES to a RECEIVE: give "item" (exact name from YOUR has_items).
  If your plan ALREADY has a step that does this, give "existing_step" (its id) instead of a new action.
  "insert_after": the id of your own step after which the new step goes (or "START").
- OFFERS TO YOU: YES if your sub-goals need the object. You may add "use_action" (what you do with it,
  e.g. "put down the white mug on the coffee table") with "uses" (index in YOUR can_do).
- Always give a short "reason"; for NO say why (e.g. "my body cannot lift it", "busy with my own goals").

""" + _WORDING + """

Return JSON:
{{"answers":[
  {{"id":"r4_s2","answer":"YES","action":"push the brown armchair from the walkway to the wall","uses":0,"insert_after":"r3_s1","reason":"..."}},
  {{"id":"r4_s4","answer":"YES","item":"white mug (cabinet, image 1)","insert_after":"START","reason":"..."}},
  {{"id":"r2_s1","answer":"YES","existing_step":"r3_s2","reason":"I already move that box"}},
  {{"id":"r1_s3","answer":"YES","use_action":"put down the green apple on the coffee table","uses":0,"insert_after":"r4_s5","reason":"..."}},
  {{"id":"r5_s2","answer":"NO","reason":"..."}}
]}}"""

PROPOSE_USER = """TASK: {task}
YOUR OFFER: {own_offer}
YOUR can_do:
{can_do_indexed}
YOUR CURRENT PLAN: {own_plan}
REQUESTS: {requests}
OFFERS TO YOU: {offers}"""


# ================================================================ Stage 4: Graph-based Plan Alignment
GRAPH_SYSTEM = """You align a multi-robot plan. You are NOT an allocator: every step was written by the robot that
executes it, and every collaboration candidate exists only because the providing robot said YES.
Never create work and never give work to a robot that did not agree.

INPUT
- OFFERS: each robot's capability, can_do, cannot_do, has_items, need_from_others, intends (its sub-goals).
- PLANS: each robot's steps in its own order (id, type, text, item, target, serves = sub-goal index).
  Request steps (ASK_HELP / RECEIVE) list their candidates (provider step, robot, kappa) and the NO replies.
  kappa "mutual": the robot that was asked said YES; "provider-only": it volunteered / offered unasked.
  "open_offers": PASS offers nobody took.  "in_cycle": the step is on a dependency cycle.
- EDGES: collaboration candidates (provider -> request).
- AUTO_ORDER: {{"before":ID,"after":ID}} ORDER edges already added by code from declared
  preconditions/effects (B's effect satisfies A's precondition -> B before A).
- DUPLICATE_CANDIDATES: {{"duplicate id":"original id"}} pairs whose declared effects are identical.

LOOK AT
- requests with several candidates, or one provider-only candidate: who should serve them?
  A request is NEVER auto-confirmed just because it has one mutual candidate -- you must SELECT it,
  or it stays unresolved.
- one object wanted by several requests: who gets it?
- requests nobody serves that another existing step already satisfies
- duplicate work (two robots doing the same thing to the same object). DUPLICATE_CANDIDATES lists
  step pairs {{"duplicate id": "original id"}} whose declared effects are equivalent (same object_id
  and field, an equivalent value) -- for every pair, you MUST decide:
    - if the duplicate id is a LOCAL or HELP step (true for almost all DUPLICATE_CANDIDATES pairs):
      DROP the duplicate id. NEVER use MERGE here -- MERGE only takes a "request" (ASK_HELP/RECEIVE)
      and will be rejected on a LOCAL/HELP id.
    - only if the duplicate id is itself an ASK_HELP or RECEIVE request: MERGE it into the original id.
  Do not leave a listed pair untouched.
- steps that contradict their robot's offer (cannot_do, items it does not have) or do nothing useful
- cross-robot order that is needed (same object / same space), and cycles. AUTO_ORDER already lists
  {{"before":ID,"after":ID}} pairs added from declared preconditions/effects; add more ORDER edits only
  where still needed, do not duplicate what AUTO_ORDER already has.

OPERATIONS (existing ids only)
- {{"op":"SELECT","provider":PROVIDER_ID,"request":REQUEST_ID,"rationale":"..."}}
    choose (or replace) the provider for a request among its candidates. For an open offer, "request"
    may be an existing step of the offer's target that needs the object.
- {{"op":"MERGE","request":REQUEST_ID,"into":STEP_ID,"rationale":"..."}}
    REQUEST_ID must be an ASK_HELP or RECEIVE step (rejected otherwise): it is already satisfied by
    another robot's existing step; the provider step is NOT changed. Two LOCAL/HELP steps duplicating
    each other are DROP, never MERGE.
- {{"op":"DROP","node":STEP_ID,"rationale":"..."}}
    remove an unnecessary, duplicate or infeasible step (also to break a cycle).
- {{"op":"ORDER","before":STEP_ID,"after":STEP_ID,"rationale":"..."}}
    a step of one robot must finish before a step of ANOTHER robot starts (never inside one robot).
Write edits in this order: SELECT / MERGE first, then DROP, then ORDER.
If something is ambiguous, do NOT edit it: leave it unresolved.
Default after your edits: an untouched request keeps its candidate only if it is a single "mutual" one;
otherwise it stays unresolved.

COVERAGE: for EVERY sub-goal of EVERY robot, judge the plan as it will be after your edits:
- "status": "covered" | "partial" | "uncovered"
- "evidence": ids of the steps that achieve it (required for covered / partial)
- "cause" (partial / uncovered only): "No volunteer" | "Capability gap" | "Left unresolved"
  (use the NO replies: nobody agreed -> No volunteer; no robot's body can do it -> Capability gap)

Return ONLY this JSON:
{{"edits":[{{"op":"SELECT|MERGE|DROP|ORDER", ...ids..., "rationale":"..."}}],
 "coverage":[{{"robot":"R1","goal":0,"status":"covered","evidence":["r1_s1","r1_s2"],"cause":null}}]}}"""

GRAPH_USER = """TASK: {task}
DEADLINE: {deadline} minutes
OFFERS: {offers}
PLANS: {plans}
EDGES: {edges}
AUTO_ORDER: {auto_order}
DUPLICATE_CANDIDATES: {duplicate_candidates}"""


def plan_system(agent: str, room: str, env_state: str = "[]") -> str:
    return PLAN_SYSTEM.format(agent=agent, room=room, env_state=env_state)


def propose_system(agent: str) -> str:
    return PROPOSE_SYSTEM.format(agent=agent)


def graph_system() -> str:
    return GRAPH_SYSTEM.format()


def indexed(xs: list[str]) -> str:
    return "\n".join(f"[{i}] {x}" for i, x in enumerate(xs)) or "(none)"


__all__ = ["_j", "OFFER_SYSTEM", "OFFER_USER", "SEE_ITEMS_BLOCK", "PLAN_USER", "PLAN_FIX", "PROPOSE_USER",
           "GRAPH_USER", "plan_system", "propose_system", "graph_system", "indexed"]
