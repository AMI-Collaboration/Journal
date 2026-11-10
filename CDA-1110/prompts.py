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
- ONE OBJECT, ONE STEP, ONCE. Every pick_up is followed by put_down, PASS, or use."""

_ESSENTIAL = """TEAM GOAL: ESSENTIAL work first — what the task cannot succeed without.
Think beyond literal words: "watch a movie" -> TV on + sofa arranged + lighting adjusted + snacks.
"guest coming" -> seating ready + drinks + surfaces clear.
Use the deadline well: more robots = more parallel work."""

_SPACE_RULES = """SPACE RULES:
- Every robot works only in its OWN room unless doing HELP/PASS/RECEIVE.
- Two collaboration types only:
  CAPABILITY: your body cannot do it -> ASK_HELP (target = a robot whose body can).
  OBJECT: you need an object from another room -> RECEIVE (target = the robot that has it).
- Mobile giver brings the object. Fixed giver hands over; mobile receiver collects.
  Two fixed robots cannot exchange objects. Never ask a third robot to carry."""


# ================================================================ Stage 1: Offer
OFFER_SYSTEM = """You are robot {agent}, a household robot that sees only its own room.

STEP 1 — LIST has_items: every clearly visible movable object (and furniture you act on) in your images.
Format: "<color> <noun> (<location>, image <k>)". Never infer unlisted objects. Only what you directly see.

STEP 2 — THINK (write it in "reasoning"):
a) GOAL STATE: what must be true when the task is done? Think beyond literal words.
b) EACH ROOM'S ROLE: what does each room contribute toward that end state?
c) MY CONTRIBUTION: which parts of that end state can MY room and MY body serve?
d) PRIORITY: which of my contributions matter most given the deadline?

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
 "reasoning":"a) Grandmother needs warm tea and a snack. b) Kitchen: drinks and food; living room: seating. c) I can heat water and fill a mug, and bring fruit. d) Tea first, the kettle takes time.",
 "capability":"I am mobile and can carry light objects up to 5 kg with one arm.",
 "can_do":["PickupLightObject: lift mugs, fruit, small items","PourObject: pour from a kettle into a cup","ToggleObject: turn on/off kettle, lights, appliances"],
 "cannot_do":["PickupHeavyObject: cannot lift furniture","SliceObject: no cutting tool"],
 "need_from_others":["someone who can slice fruit"],
 "intends":["warm tea ready for the grandmother","fresh fruit available as a snack"],
 "obs_scope":"I can observe the kitchen only."}}

Return JSON:
{{"has_items": [...], "reasoning": "a)... b)... c)... d)...", "capability": "...",
 "can_do": [...], "cannot_do": [...], "need_from_others": [...], "intends": [...], "obs_scope": "..."}}"""

OFFER_USER = """## TASK (serve this only):
{task}
DEADLINE: {deadline} minutes

YOUR BODY: room={room}, mobile={mobile}, payload={payload}, embodiment={embodiment}

ABOUT AREAS YOU CANNOT SEE:
{instruction}

Images attached ({n_img} image(s)), image 1 to {n_img}."""


# ================================================================ Stage 2: Local Plan
PLAN_SYSTEM = """You are robot {agent} in the {room}. Write YOUR part of the shared plan as a list of steps.

THINK FIRST (write it in "reasoning"):
1. MY SUB-GOALS: your own "intends" (numbered in YOUR intends). Every step serves one of them.
2. OTHER ROBOTS: read ALL robots' intends in ALL OFFERS. Do not repeat work another robot intends.
3. MY STEPS: what my body does in my room, using my has_items and can_do.
4. COLLABORATION: what my body cannot do (ASK_HELP), what I need from another room (RECEIVE),
   what I can offer to another room (PASS).

STEP FORMAT (indices are positions in YOUR steps list, starting at 0):
- LOCAL:    {{"type":"LOCAL", "action":{{"verb":"...","object":"...","from":"...","to":"..."}}, "uses":<index in YOUR can_do>, "serves":<index in YOUR intends>}}
  Verbs: move, pick_up, put_down, push, slice, cook, turn_on, turn_off, open, close, fill, place, pour
- ASK_HELP: {{"type":"ASK_HELP", "action":{{...what the other robot should do...}}, "target":"RN", "enables":<index of YOUR later LOCAL step that needs it>, "serves":<intends index>}}
- RECEIVE:  {{"type":"RECEIVE", "item":"exact name from target's has_items", "target":"RN", "enables":<optional: index of YOUR later LOCAL step that uses it>, "serves":<intends index>}}
- PASS:     {{"type":"PASS", "item":"exact name from YOUR has_items", "target":"RN", "serves":<intends index>}}
  (an offer: the receiver decides later whether to take it)
- "target" is a hint ("I hope this robot does it"); another robot may answer instead.

""" + _WORDING + "\n" + _ESSENTIAL + "\n" + _SPACE_RULES + """

EXAMPLE (R4 = mobile light robot in the living room; intends = ["safe walkway for the grandmother", "tea served at the sofa"]):
{{"reasoning":"1) My goals: walkway (0), tea at the sofa (1). 2) R1 makes tea, R3 pushes furniture. 3) I clear small items from the floor. 4) The armchair is too heavy for me -> ASK_HELP R3; I need the mug from R1 -> RECEIVE.",
 "steps":[
  {{"type":"LOCAL","action":{{"verb":"move","object":"black bag","from":"floor","to":"shelf"}},"uses":0,"serves":0}},
  {{"type":"ASK_HELP","action":{{"verb":"push","object":"brown armchair","from":"walkway","to":"wall"}},"target":"R3","enables":2,"serves":0}},
  {{"type":"LOCAL","action":{{"verb":"place","object":"floor mat","from":"shelf","to":"walkway"}},"uses":0,"serves":0}},
  {{"type":"RECEIVE","item":"white mug","target":"R1","enables":4,"serves":1}},
  {{"type":"LOCAL","action":{{"verb":"put_down","object":"white mug","from":"gripper","to":"coffee table"}},"uses":0,"serves":1}}
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

LOOK AT
- requests with several candidates, or one provider-only candidate: who should serve them?
- one object wanted by several requests: who gets it?
- requests nobody serves that another existing step already satisfies
- duplicate work (two robots doing the same thing to the same object)
- steps that contradict their robot's offer (cannot_do, items it does not have) or do nothing useful
- cross-robot order that is needed (same object / same space), and cycles

OPERATIONS (existing ids only)
- {{"op":"SELECT","provider":PROVIDER_ID,"request":REQUEST_ID,"rationale":"..."}}
    choose (or replace) the provider for a request among its candidates. For an open offer, "request"
    may be an existing step of the offer's target that needs the object.
- {{"op":"MERGE","request":REQUEST_ID,"into":STEP_ID,"rationale":"..."}}
    the request is already satisfied by another robot's existing step; the provider step is NOT changed.
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
EDGES: {edges}"""


def plan_system(agent: str, room: str) -> str:
    return PLAN_SYSTEM.format(agent=agent, room=room)


def propose_system(agent: str) -> str:
    return PROPOSE_SYSTEM.format(agent=agent)


def graph_system() -> str:
    return GRAPH_SYSTEM.format()


def indexed(xs: list[str]) -> str:
    return "\n".join(f"[{i}] {x}" for i, x in enumerate(xs)) or "(none)"


__all__ = ["_j", "OFFER_SYSTEM", "OFFER_USER", "PLAN_USER", "PLAN_FIX", "PROPOSE_USER",
           "GRAPH_USER", "plan_system", "propose_system", "graph_system", "indexed"]
