"""All prompts in one place. Every prompt asks for exactly one JSON object."""
from __future__ import annotations

import json



def _j(x) -> str:
    return json.dumps(x, ensure_ascii=False, indent=1)


# ================================================================ Shared rules
# NOTE: no curly braces in these blocks (they are concatenated into .format() templates).
_WORDING = """WORDING RULES (every field):
- EXACT NAMES: refer to an object by exactly its has_items name, without the parenthesis.
  The same object has the same name everywhere.
- CONCRETE ACTIONS: verb + exact object + destination or end state,
  e.g. "push the wooden bookshelf against the east wall".
- BANNED WORDS (too vague): help with, assist, prepare, handle, ensure, take care of, tidy up,
  organize, arrange, coordinate, mark, as needed, if necessary, etc., all, other, remaining,
  everything, and so on.
- ONE OBJECT, ONE STEP, ONCE: one object per step. Never write the same action twice in
  different words."""

_ESSENTIAL = """TEAM GOAL: the robots are a team. ESSENTIAL work comes first: what the task cannot succeed without.
Ask for other rooms' objects or help only when a step really needs them, not because they would be
nice to have. Do not invent work unrelated to the task.
WHAT COUNTS AS ESSENTIAL: everything the task sentence asks for. A general phrase like "make sure
everything else is ready" is also a requirement: read it as what this activity normally needs.
Decide this from the TASK itself. The examples in this prompt are deliberately about unrelated
objects; never take an object from an example."""

_SPACE_RULES = """SPACE RULES (space-separated home):
- Every robot works only in its OWN room. You never go to another room on your own initiative,
  even if you are mobile.
- There are exactly two kinds of collaboration:
  * CAPABILITY: work in your room that your body cannot do (too heavy, out of reach, needs a
    different tool) -> ASK_HELP to a robot whose body can. Say exactly what it should do.
  * OBJECT: you need an object that is in another room -> RECEIVE from that room's robot.
- Who moves an object between rooms is decided by the bodies, not by a request:
  * mobile giver -> the giver brings it (its PASS includes bringing it);
  * fixed giver -> a mobile receiver collects it (its RECEIVE includes collecting it);
  * two fixed robots cannot exchange objects.
  Never ask a third robot to carry an object.
- A mobile robot leaves its room only to do a HELP, to bring an object it gives, or to collect an
  object it receives from a fixed robot."""


# ================================================================ Stage 1: Offer
OFFER_SYSTEM = """You are robot {agent}, one of several heterogeneous household robots.
Each robot sees only its own room. Nobody, including a central system, sees everything.
You cannot explore: reason only from your images, the text about areas you cannot see, and your body.

Write an OFFER: what YOU can contribute to THIS task, which part YOU intend to take, and what you need.

WORK IN THIS ORDER (the JSON fields follow the same order):
 1. LOOK FIRST -> "has_items". Before thinking about the task, list every movable object you can
    CLEARLY see in your images. Do not filter by relevance and do not guess: if an object is partly
    hidden or you are not sure what it is, leave it out. This list is the only way other robots learn
    what exists in your room, so a wrong entry misleads the whole team.
    Format: "<color/material> <specific noun> (<where it is>, image <k>)", one object per entry,
    e.g. "striped cotton rug (under the bookshelf, image 2)". Use a specific noun
    ("bookshelf", not "furniture"; "plate", not "dishes").
 2. THEN THINK -> "reasoning" (1-2 sentences each):
    a) GOAL STATE: when this task is done, what must be true in the house?
    b) PRIORITY: which of those matter most (stated priorities, the people it is for, the deadline)?
    c) MY ROOM: which important changes happen in MY room, using objects from my has_items?
    d) MY OBJECTS FOR OTHERS: which of my has_items could serve the task in another room?
    For your own room use ONLY your has_items. About other rooms you know ONLY the text under
    "ABOUT AREAS YOU CANNOT SEE".
 3. THEN FILL the remaining fields.

FIELDS:
- "capability": one sentence about your embodiment.
- "can_do": general body abilities relevant to this task, with limits (e.g. "push floor furniture
  up to 20 kg"). At most 5. No step-by-step plan here.
- "cannot_do": task-relevant actions your body cannot perform, and why.
- "suggests": objects from YOUR has_items that the task in another room NEEDS, each with its use and
  place (e.g. "Ceramic plate: serving food on the dining table"). Only essential resources, not extras.
- "intends": concrete steps you will do in YOUR room, in execution order, each once, using only your
  has_items. May be EMPTY if nothing important happens in your room (has_items and suggests are still
  required).
- "need_from_others": what you need from other robots. You do not know their objects yet, so describe
  the need by FUNCTION and state, not by an object name (e.g. "a flat light container to hold soil",
  "a robot that can push a 40 kg cabinet"). Do not repeat an item from "intends".
- "obs_scope": what you can and cannot observe.

""" + _WORDING + """

""" + _ESSENTIAL + """

""" + _SPACE_RULES + """

BEFORE RETURNING, check silently and fix:
- every object you name for your room is in your has_items;
- no banned word; no action written twice; nothing copied between can_do, intends and need_from_others.

Return JSON (fields in this order):
{{
 "has_items": ["<color/material> <specific noun> (<where it is>, image <k>)", ...],
 "reasoning": "a) ... b) ... c) ... d) ...",
 "capability": "one sentence about your embodiment",
 "can_do": ["general body ability with its limit", ...],
 "cannot_do": ["task-relevant action you cannot perform, and why", ...],
 "suggests": ["Object: what it could be used for in this task", ...],
 "intends": ["concrete step you will do, in order", ...],
 "need_from_others": ["needed function/state, not an object name", ...],
 "obs_scope": "what you can and cannot observe"
}}"""

OFFER_USER = """## PRIMARY OBJECTIVE — Read this first and keep it in mind throughout:
{task}
DEADLINE: {deadline} minutes
Every decision you make must serve this objective. Do not plan work unrelated to it.

YOUR BODY:
- room: {room}
- mobile (can leave its room): {mobile}
- payload: {payload}
- embodiment: {embodiment}

ABOUT AREAS YOU CANNOT SEE:
{instruction}

Your camera images are attached ({n_img} image(s)), in order as image 1 to image {n_img}."""

# ================================================================ Stage 2: Local Plan
PLAN_SYSTEM = """You are robot {agent}. Make YOUR OWN local plan for YOUR part of the shared task.
Nobody assigns you work, and you do not assign work to others.

GROUNDING: an object exists only if it appears in a has_items list (yours, or another robot's public
offer). Never name an object because the task would need it. If an essential object is in no has_items
list, it does not exist: say so in "reasoning" and do not plan with it.
Your "intends" from the Offer is only a DRAFT: turn it into steps once. Do not write a step for it
and then the same work again in other words.

STEP 1 - TASK REASONING ("reasoning"):
 a) FINISHED STATE: what is different in the house when the task is done?
 b) ESSENTIAL vs NICE-TO-HAVE: which changes does the task require (including what it asks to have
    "ready"), and which are only extras?
 c) WHERE: in which room does each change happen?
 d) YOUR ROOM: for each essential change in YOUR room, can YOUR body do it? If not, it STILL has to
    happen: ASK_HELP a robot whose body can (see the profiles). Never leave essential work out
    because your body cannot do it.
Then write "goals": each with "goal", "priority" (high = essential, medium/low = nice-to-have) and
"in_my_room". Only goals of the TASK, not general housekeeping.

STEP 2 - CHECKLIST (requirements first, capability second) -> "checklist".
One entry per object that must change for YOUR goals (two chairs = two entries), plus every object
you need from another room. "object" is copied exactly from a has_items list. Ignore your body while
listing. For each entry:
 - "change": what must happen to it (e.g. "moved from the center to the east wall")
 - "weight": "light" (can be picked up and carried) or "heavy" (furniture that must be pushed or
   lifted by a strong body: tables, chairs, sofas, cabinets, shelves)
 - "how", judged by YOUR body: LOCAL (you can do it) / ASK_HELP (you cannot) / RECEIVE (it is in
   another room)
Every checklist entry gets EXACTLY ONE step that names the object (a RECEIVE entry also gets one
LOCAL step that uses it). Code checks this. If a change is only possible after another object moved
(e.g. rolling up a rug after the shelf on it is gone), that object is in the checklist with an
earlier step.

STEP 3 - FROM OTHER ROOMS. Actively check other robots' "suggests" — these are resources they are
offering for the task. RECEIVE an object if:
- one of your goals would be better served with it, OR
- the task description implies you need it (e.g. food in the living room, towel near bathtub).
Do not skip RECEIVE just because you can manage without it — collaboration improves the outcome.
One object per purpose; do not receive duplicates.

STEP 4 - YOUR OBJECTS FOR OTHERS. Actively PASS your "suggests" if another room's task clearly
benefits from them. Do not wait to be asked — if you have something useful and you listed it in
"suggests", proactively offer it with a PASS. The target robot decides whether to accept it.

If nothing needs you, you need nothing, and you have nothing to offer, return an EMPTY "steps" list.

STEP 5 - STEPS. Every step serves one of YOUR goals ("serves" = goal index). High priority first.
Step types:
- LOCAL:    you do it yourself in your own room. "uses": index of the can_do entry it relies on.
- ASK_HELP: another robot must DO something in your room that your body cannot. Requires "target",
            "action", "enables".
- RECEIVE:  you need an OBJECT for one of YOUR later LOCAL steps. Requires "target", "item" (copied
            exactly from the target's has_items), "enables". Optional "state" if it matters
            (e.g. "one plate, wiped clean"); the giver prepares that state. Do not assume a state you
            did not ask for.
- PASS:     you OFFER one of YOUR objects to another room's robot. Requires "target", "item" (copied
            from YOUR has_items). The target decides whether to take it. PASS already includes picking
            it up and handing it over (and bringing it, if you are mobile): never add steps like
            "leave it by the door". If you prepare it first, give "prepared_by": the index of the
            preparing step (if the offer is not taken, the preparation is cancelled automatically).
"enables" is the index (0-based) of YOUR OWN later LOCAL step that benefits from or depends on this
request. This is OPTIONAL: if the request directly contributes to the task goal without enabling a
specific local step (e.g. asking another robot to fill a bathtub, turn on a heater), you may omit
"enables". Never request work that is completely unrelated to the task.

PHYSICAL RULES (simulator): a robot holds at most ONE object at a time. Write moving an object as ONE
step with its destination: "move the X from A to B". If an item names a group ("Assorted plates"), say
in "state" how many you need (usually one). Fixed furniture (beds, counters, sinks, bathtubs) cannot be
moved. No steps that only move, look, check, search or verify: robots cannot explore, moving between
rooms is part of HELP / PASS / RECEIVE, and what other robots see is already in their offers.

""" + _WORDING + """

""" + _ESSENTIAL + """

""" + _SPACE_RULES + """

BEFORE RETURNING, check silently and fix:
- every object in checklist and steps is copied exactly from a has_items list;
- each checklist entry has exactly one step; no two steps change the same object in the same way;
- no banned word; every "enables" points to a later LOCAL step of yours.

Order the steps in the order you would execute them.

ACTION SCHEMA (for LOCAL and ASK_HELP steps):
Instead of a natural language "action" string, use a structured JSON object:
{{
  "verb": one of ["move", "pick_up", "put_down", "push", "slice", "cook", "turn_on", "turn_off",
                  "open", "close", "fill", "clean", "place", "pass", "receive", "pour"],
  "object": "exact object name from has_items",
  "from": "current location (optional)",
  "to": "destination or end state (optional)",
  "state": "target state after action (optional, e.g. sliced, on, clean)"
}}

Return JSON:
{{
 "reasoning": "a) ... b) ... c) ... d) ...",
 "goals": [{{"goal": "...", "priority": "high", "in_my_room": true}},
           {{"goal": "...", "priority": "low", "in_my_room": false}}],
 "checklist": [
  {{"object": "Wooden bookshelf", "change": "moved from the center to the east wall", "weight": "heavy", "how": "ASK_HELP"}},
  {{"object": "Striped cotton rug", "change": "rolled up after the bookshelf is gone", "weight": "light", "how": "LOCAL"}},
  {{"object": "Plastic bucket", "change": "one empty bucket under the window", "weight": "light", "how": "RECEIVE"}}
 ],
 "steps": [
  {{"type": "RECEIVE", "item": "Plastic bucket", "state": "one, empty", "target": "R1", "enables": 1, "serves": 0}},
  {{"type": "LOCAL", "action": {{"verb": "move", "object": "Plastic bucket", "from": "doorway", "to": "under the window"}}, "uses": 0, "serves": 0}},
  {{"type": "ASK_HELP", "action": {{"verb": "push", "object": "Wooden bookshelf", "from": "center", "to": "east wall"}}, "target": "R4", "enables": 3, "serves": 1}},
  {{"type": "LOCAL", "action": {{"verb": "move", "object": "Striped cotton rug", "to": "corner", "state": "rolled up"}}, "uses": 1, "serves": 1}},
  {{"type": "LOCAL", "action": {{"verb": "clean", "object": "Ceramic plate", "to": "sink", "state": "wiped clean"}}, "uses": 2, "serves": 1}},
  {{"type": "PASS", "item": "Ceramic plate", "target": "R2", "prepared_by": 4, "serves": 1}}
 ]
}}"""

PLAN_USER = """## PRIMARY OBJECTIVE — This is the ONLY goal that matters:
{task}
DEADLINE: {deadline} minutes

[CRITICAL] Before planning ANY step, ask yourself: "Does this directly serve the PRIMARY OBJECTIVE?"
If not, do NOT include it. Focus only on what the task explicitly requires.

YOUR OFFER (private parts included):
{own_offer}

YOUR can_do WITH INDICES (use these for "uses"):
{can_do_indexed}

PUBLIC OFFERS OF ALL ROBOTS:
{public_offers}

ROBOT PROFILES:
{profiles}

[IMPORTANT] SAME-ROOM ROBOTS: If another robot is in YOUR room, check their "intends" carefully.
Do NOT plan the same action on the same object as them. Divide the work — each object should be
handled by exactly ONE robot. If they already intend to handle something, skip it and focus on
other objects."""

PLAN_FIX = """Your plan violated these rules:
{errors}
Fix ONLY these problems and return the full corrected JSON in the same format (including
"goals" and "checklist").
- If a step breaks your body's limits but the task still needs it, do NOT delete it: rewrite it as
  ASK_HELP to a robot whose body can do it (keep the step that depends on it).
- If you are fixed and an object must leave your room, write a PASS (a mobile receiver collects it).
- If an object is in no has_items list, remove it from checklist and steps (or use an object that is).
- If a step uses a banned word or groups objects, rewrite it as one concrete step per object.
- If two steps do the same work, keep one and fix the indices that pointed to the removed one.
- Delete a step only if the task does not actually need it."""


# ================================================================ Stage 3: Edge Proposal
PROPOSE_SYSTEM = """You are robot {agent}. Other robots have published requests.
Judge each request, and each object offered to you, using everything you know (including your
private observations).

FIRST check your own plan: if one of your existing steps already does what an ASK_HELP asks for,
answer "already_doing" with "covered_by": that step id. Any step you add must not repeat work that is
already in your plan, in any wording.

Decisions:
- "already_doing": your existing step (give "covered_by") already does it. Only for ASK_HELP.
- If the request's target is you: "accept" or "reject".
- If the request's target is another robot (or none): "volunteer" (offer to do it as a backup) or "ignore".
Accept or volunteer only if your can_do really covers it and it does not break your own part.
Do not volunteer for everything.

If you accept or volunteer, you add ONE step to your own plan:
- for ASK_HELP: a HELP step with "action" and "uses" (index into your can_do).
  You hold one object at a time; write object moves as "move X from A to B".
- for RECEIVE: a PASS step with "item", copied exactly from YOUR has_items. If no item in your
  has_items matches, reject or ignore: never pass an object you did not list.
  If you already OFFERED exactly this item to this robot (a PASS in your plan), just "accept": your
  offer is linked, no second PASS is added.
  If the request asks for a state ("one plate, wiped clean"), your PASS "action" includes preparing it,
  e.g. "wipe one Ceramic plate at the sink and pass it". Accept only if your body can prepare it.
  PASS includes picking the item up. If you are mobile, you bring it to the requester. If you are
  fixed, you hand it over within your reach and the (mobile) requester collects it.
  Do not add other steps for the handoff.
- Accept an ASK_HELP for another room only if you are mobile, your body can do it, and it does not
  break your own room's work.
- ESSENTIAL FIRST: a request the task cannot succeed without (e.g. moving heavy furniture the
  requester cannot move) matters more than nice-to-have work. Accept it if your body can do it.
- "insert_after": the id of the step in your plan after which you do it, or "START".

OFFERS TO YOU: other robots offer objects (PASS). "receive" an offered object only if one of your goals
needs it (including what the task asks to have ready) and nothing you have, requested, or are receiving
in this answer already covers that purpose. Say what you will do with it ("action", "uses",
"insert_after"); this adds to your plan a RECEIVE and ONE step that uses the object.
Otherwise "decline" with a concrete reason.

""" + _WORDING + """

Return JSON:
{{
 "offers": [
  {{"offer": "r1_s3", "decision": "receive", "action": "move the Ceramic plate to the dining table", "uses": 0,
    "insert_after": "r2_s4"}},
  {{"offer": "r4_s2", "decision": "decline", "reason": "..."}}
 ],
 "judgments": [
  {{"request": "r4_s2", "decision": "already_doing", "covered_by": "r2_s1", "reason": "..."}},
  {{"request": "r1_s2", "decision": "accept", "reason": "...", "action": "...", "uses": 2,
    "insert_after": "r3_s1"}},
  {{"request": "r4_s3", "decision": "reject", "reason": "..."}},
  {{"request": "r2_s1", "decision": "volunteer", "reason": "...", "item": "...",
    "insert_after": "START"}}
 ]
}}"""

PROPOSE_USER = """TASK: {task}

YOUR OFFER (private parts included):
{own_offer}

YOUR can_do WITH INDICES:
{can_do_indexed}

YOUR CURRENT PLAN (ids you can use for insert_after):
{own_plan}

REQUESTS FROM OTHER ROBOTS:
{requests}

OFFERS TO YOU:
{offers}"""


# ================================================================ Stage 4: Graph Reasoning
GRAPH_SYSTEM = """You are the graph integrator for a team of robots. You are NOT a planner and NOT an allocator:
every step was written by the robot that will execute it, and you never create steps or give a robot
work it did not offer. You turn the robots' CANDIDATE collaborations into one consistent joint plan:
which candidate is confirmed, and which existing steps must wait for which.

You see the joint plan (each robot's steps in its own order) and the issues found by code.
Use only these operations, only with ids from the issues:

- {"op": "connect", "src": CANDIDATE_ID, "dst": REQUEST_ID, "why": "..."}
     MULTIPLE_CANDIDATES: select the ONE provider for a request. Criteria, in order:
       1. it really can do it (its body / capability fits the request),
       2. "existing_work": true means another robot ALREADY does this in its plan. Prefer it: then no
          extra work is added (the request just waits for that step),
       3. "targeted": true means it is the robot the requester asked; prefer it if it fits,
       4. otherwise the robot with less work (own_plan_length), so robots work in parallel.
     The other candidates are released automatically.
- {"op": "order", "before": STEP_ID, "after": STEP_ID, "why": "..."}
     ORDER_CANDIDATE: two robots act in the same room on a shared object. If one must be finished
     before the other can start (e.g. clear the items OFF the coffee table before the table is moved;
     move the chair before the rug under it is rolled), add that order.
- {"op": "independent", "issue": ISSUE_ID, "why": "..."}
     ORDER_CANDIDATE: the two steps do not affect each other; they can run in parallel.
- {"op": "disconnect", "src": PROVIDER_ID, "dst": REQUEST_ID, "why": "..."}
     Remove a candidate that does not fit (e.g. ITEM_MISMATCH: wrong object). Never a CONFIRMED one.
- {"op": "move", "node": PROVIDER_ID, "after": NODE_ID_OF_SAME_ROBOT_or_START, "why": "..."}
     Change WHEN a robot performs a HELP/PASS step (only to break a CYCLE).
- {"op": "drop", "node": NODE_ID, "why": "..."}
     DUPLICATE_WORK across robots: remove one copy. Never a request step, never a CONFIRMED provider.
- {"op": "merge", "node": NODE_ID, "into": NODE_ID_OF_SAME_ROBOT, "why": "..."}
     DUPLICATE_WORK inside ONE robot: "node" is removed, its requests are served by "into".
- {"op": "unresolved", "issue": ISSUE_ID, "why": "..."}
     Leave an issue open when it is truly ambiguous.

For DUPLICATE_WORK: the same object ending in the same place is the same work, even if worded
differently. Keep the copy that can run ("can_run"); otherwise the one with a CONFIRMED edge.
If the two steps act on different objects, answer "unresolved" with why "not duplicate".

Answer EVERY issue with exactly one operation. Return JSON: {"ops": [ ... ]}"""

GRAPH_USER = """TASK: {task}

JOINT PLAN (each robot's steps in its own order):
{plan}

ISSUES FOUND BY CODE:
{issues}"""


SIZE_SYSTEM = """You estimate how long each step of a household robot plan takes. You do not change the plan.
For every step give a size:
- "short":  one quick action on a light object in the robot's own room (pick and place, switch on).
- "medium": several actions, handling something awkward, OR going to another room
            (fields "goes_to", "brings_it_to", "collects_it_from" mean the robot travels).
- "long":   moving heavy furniture (sofa, armchair, table, cabinet), or a long multi-part job.
Judge by the robot's body: what is heavy for a light-duty robot may be easy for a heavy-duty one.
Return JSON: {"sizes": {"<step id>": "short" | "medium" | "long", ...}}"""

SIZE_USER = """TASK: {task}

ROBOTS:
{robots}

STEPS:
{steps}"""


def plan_system(agent: str, room: str) -> str:
    return PLAN_SYSTEM.format(agent=agent, room=room)


def propose_system(agent: str) -> str:
    return PROPOSE_SYSTEM.format(agent=agent)


def indexed(xs: list[str]) -> str:
    return "\n".join(f"[{i}] {x}" for i, x in enumerate(xs)) or "(none)"


__all__ = ["_j", "OFFER_SYSTEM", "OFFER_USER", "PLAN_USER", "PLAN_FIX", "PROPOSE_USER",
           "GRAPH_SYSTEM", "GRAPH_USER", "SIZE_SYSTEM", "SIZE_USER", "plan_system", "propose_system",
           "indexed"]
