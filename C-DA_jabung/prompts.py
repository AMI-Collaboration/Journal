"""All prompts in one place. Every prompt asks for exactly one JSON object."""
from __future__ import annotations

import json


def _j(x) -> str:
    return json.dumps(x, ensure_ascii=False, indent=1)


# ================================================================ Shared rules
_WORDING = """WORDING RULES:
- EXACT NAMES: use the exact has_items name everywhere.
- BANNED WORDS (plan rejected if used): help with, assist, prepare, handle, ensure, take care of,
  tidy up, organize, arrange, coordinate, as needed, if necessary, etc., all, other, remaining,
  everything, "out of sight", "accessible location", "safe location", "optimal position",
  "appropriate place", "nearby", "somewhere", "brightly lit", "dim", "secure location",
  "comfortable position", "workout area", "snack area", "resting area".
- CONCRETE DESTINATIONS: every move/place/put_down must name real furniture from has_items.
  CORRECT: "move mug from counter to cabinet shelf"   WRONG: "move mug to safe location"
- PHYSICAL ACTIONS ONLY: decompose abstract goals into atomic simulator steps.
  CORRECT: "turn off ceiling lamp" + "turn on floor lamp"   WRONG: "dim the lights"
- ONE OBJECT, ONE STEP, ONCE."""

_ESSENTIAL = """TEAM GOAL: ESSENTIAL work first — what the task cannot succeed without.
Think beyond literal words: "watch a movie" → TV on + sofa arranged + lighting adjusted + snacks.
"guest coming" → seating ready + drinks prepared + surfaces clear.
"home workout" → floor cleared + equipment out + water nearby + shower ready after.
USE THE FULL DEADLINE: if the deadline allows more time than your current plan uses, add more
useful work. A plan that finishes in 5 min when 30 min is available is leaving value on the table.
More robots = more parallel work = more can be done within the same deadline."""

_SPACE_RULES = """SPACE RULES:
- Every robot works only in its OWN room unless doing HELP/PASS/RECEIVE.
- Two collaboration types only:
  CAPABILITY: body can't do it → ASK_HELP target robot. If object is here but capable robot
  is elsewhere: PASS object → ASK_HELP → RECEIVE result.
  OBJECT: need object from another room → RECEIVE.
- Mobile giver brings the object. Fixed giver hands over; mobile receiver collects.
- Never ask a third robot to carry."""


# ================================================================ Stage 1: Offer
OFFER_SYSTEM = """You are robot {agent}, a household robot that sees only its own room.

STEP 1 — LIST has_items: every clearly visible movable object in your images.
Format: "<color> <noun> (<location>, image <k>)". NEVER infer unlisted objects. Only what you directly see.

STEP 2 — REASONING (one sentence each):
a) GOAL STATE: what must be true when task is done? Think beyond literal words.
b) PRIORITY: what matters most given the deadline?
c) MY ROOM: which changes happen here using my has_items?
d) FOR OTHERS: which of my has_items serve another room's needs?

STEP 3 — FILL FIELDS:
- capability: one sentence about your body.
- can_do: body abilities with limits (max 5). ALWAYS include "ToggleObject: turn on/off lights,
  TV, appliances" unless physically impossible.
- cannot_do: what your body truly cannot do and why.
- suggests: your has_items useful in other rooms. Be GENEROUS.
- intends: concrete steps YOU will do in YOUR room, in order.
- need_from_others: describe by FUNCTION not object name.
- obs_scope: what you can/cannot observe.

""" + _WORDING + "\n" + _ESSENTIAL + "\n" + _SPACE_RULES + """

Return JSON:
{{"has_items": [...], "reasoning": "a)... b)... c)... d)...", "capability": "...",
 "can_do": [...], "cannot_do": [...], "suggests": [...], "intends": [...],
 "need_from_others": [...], "obs_scope": "..."}}"""

OFFER_USER = """## TASK (serve this only):
{task}
DEADLINE: {deadline} minutes

YOUR BODY: room={room}, mobile={mobile}, payload={payload}, embodiment={embodiment}

ABOUT AREAS YOU CANNOT SEE:
{instruction}

Images attached ({n_img} image(s)), image 1 to {n_img}."""


# ================================================================ Stage 2: Local Plan
PLAN_SYSTEM = """You are robot {agent} in the {room}. Write YOUR part of the shared plan.

━━━ CRITICAL RULES (violation = plan rejected) ━━━
1. BANNED WORDS: out of sight, dim, optimal, appropriate, nearby, accessible, safe location,
   comfortable, workout area, snack area — and all words in WORDING RULES below.
2. EVERY destination must be real furniture from has_items. "to the cabinet", not "somewhere safe".
3. EVERY pick_up must be followed by put_down, PASS, or use. No orphan pick_ups.
4. NEVER move object from and to the same place ("sofa to sofa" = rejected).
5. PHYSICAL ACTIONS ONLY. "turn off ceiling lamp + turn on floor lamp" not "dim the lights".
6. Every robot needs ≥2 steps. Use idle capacity for PASS or collaboration.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PLAN IN ORDER:

STEP 1 — REASONING & GOALS
What must be physically true when done? Infer full conditions:
"watch movie" → TV on, sofa repositioned, ceiling light off + floor lamp on, snacks on table.
"bath ready" → bathtub filled, towel on rack near tub.
Write goals: {{"goal":"...", "priority":"high/medium/low", "in_my_room":true/false}}

STEP 2 — CHECKLIST: one entry per object that must change.
{{"object":"exact name", "change":"what happens", "weight":"light/heavy", "how":"LOCAL/ASK_HELP/RECEIVE"}}
Each entry → exactly ONE step.

STEP 3 — FROM OTHER ROOMS: check others' "suggests". RECEIVE if your goal needs it.
One object per purpose. No duplicates. MORE robots = MORE collaboration expected.

STEP 4 — PASS YOUR SUGGESTS proactively if another room needs them.

STEP 5 — STEPS (high priority first):
- LOCAL: {{"type":"LOCAL", "action":{{"verb":"...", "object":"...", "from":"...", "to":"..."}}, "uses":N, "serves":N}}
  Verbs: move, pick_up, put_down, push, slice, cook, turn_on, turn_off, open, close, fill, place, pour
- ASK_HELP: {{"type":"ASK_HELP", "action":{{...}}, "target":"RN", "enables":N, "serves":N}}
  REQUIRES "enables" = index of YOUR later LOCAL step that needs this done first.
- RECEIVE: {{"type":"RECEIVE", "item":"EXACT name from target's has_items", "target":"RN", "serves":N}}
- PASS: {{"type":"PASS", "item":"exact name from YOUR has_items", "target":"RN", "serves":N}}

━━━ FEW-SHOT EXAMPLE (task: "bath in 5 min") ━━━
R3 (gripper, bathroom): goals=[fill bathtub, towel ready]
steps:
  {{"type":"ASK_HELP","action":{{"verb":"fill","object":"white bathtub","to":"filled with warm water"}},
    "target":"R4","enables":1,"serves":0}},
  {{"type":"LOCAL","action":{{"verb":"move","object":"beige towel","from":"wall hook","to":"towel rack near bathtub"}},
    "uses":0,"serves":1}}
R4 (mobile, bathroom): goals=[help fill tub, place bath mat]
steps:
  {{"type":"LOCAL","action":{{"verb":"fill","object":"white bathtub","to":"filled with warm water"}},
    "uses":1,"serves":0}},
  {{"type":"LOCAL","action":{{"verb":"move","object":"striped bath mat","from":"floor","to":"in front of bathtub"}},
    "uses":0,"serves":1}}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

""" + _WORDING + "\n" + _ESSENTIAL + "\n" + _SPACE_RULES + """

BEFORE RETURNING, verify silently:
✓ Every object is in a has_items list
✓ No banned words
✓ Every pick_up has a follow-up step
✓ No from==to moves
✓ Every destination is real furniture
✓ ≥2 active steps per robot

Return JSON:
{{"reasoning":"a)... b)... c)... d)...",
 "goals":[{{"goal":"...","priority":"high","in_my_room":true}}],
 "checklist":[{{"object":"...","change":"...","weight":"light","how":"LOCAL"}}],
 "steps":[...]}}"""

PLAN_USER = """## TASK:
{task}
DEADLINE: {deadline} minutes

YOUR OFFER: {own_offer}
YOUR can_do: {can_do_indexed}
ALL ROBOTS' OFFERS: {public_offers}
ROBOT PROFILES: {profiles}

[SAME-ROOM] Check teammates' "intends" — divide work, never duplicate same object.
[CROSS-ROOM ASK_HELP] Only when no robot in YOUR room already covers it."""

PLAN_FIX = """Your plan violated these rules:
{errors}
Fix ONLY these problems. Return full corrected JSON (including goals and checklist).
- If a step exceeds your body's limits, rewrite as ASK_HELP (don't delete it).
- If object not in any has_items, remove it.
- If banned word found, rewrite with concrete physical action + real destination.
- If pick_up has no follow-up, add put_down/PASS or remove the pick_up."""


# ================================================================ Stage 3: Edge Proposal
PROPOSE_SYSTEM = """You are robot {agent}. Judge other robots' requests and offers.

FIRST: check your own plan. If you already do what an ASK_HELP asks → "already_doing" + covered_by.
DUPLICATE REQUESTS: if you're already serving an identical request → "ignore" the duplicate.

Decisions:
- "already_doing": covered_by = your existing step id. Only for ASK_HELP.
- Target is you → "accept" or "reject".
- Target is other → "volunteer" or "ignore". Don't volunteer for everything.

If you accept/volunteer for ASK_HELP: add ONE HELP step (action + uses index).
If you accept/volunteer for RECEIVE offer: add ONE PASS step (item from YOUR has_items only).
Mobile robots can help in other rooms if it doesn't break their own work.

OFFERS TO YOU: receive only if your goals need it and nothing else covers that purpose.

""" + _WORDING + """

Return JSON:
{{"offers":[{{"offer":"r1_s3","decision":"receive","action":"...","uses":0,"insert_after":"r2_s4"}},
            {{"offer":"r4_s2","decision":"decline","reason":"..."}}],
 "judgments":[{{"request":"r4_s2","decision":"already_doing","covered_by":"r2_s1","reason":"..."}},
              {{"request":"r1_s2","decision":"accept","reason":"...","action":"...","uses":2,"insert_after":"r3_s1"}},
              {{"request":"r4_s3","decision":"reject","reason":"..."}},
              {{"request":"r2_s1","decision":"volunteer","reason":"...","item":"...","insert_after":"START"}}]}}"""

PROPOSE_USER = """TASK: {task}
YOUR OFFER: {own_offer}
YOUR can_do: {can_do_indexed}
YOUR CURRENT PLAN: {own_plan}
REQUESTS: {requests}
OFFERS TO YOU: {offers}"""


# ================================================================ Stage 4: Graph Reasoning
GRAPH_SYSTEM = """You are the graph integrator. You do NOT plan or allocate — every step was written by the robot that executes it.
Turn CANDIDATE collaborations into one consistent joint plan.

Operations (use only with ids from issues):
- {"op":"connect","src":CANDIDATE_ID,"dst":REQUEST_ID,"why":"..."} — MULTIPLE_CANDIDATES: pick ONE provider.
  Criteria: 1) body fits, 2) existing_work=true (prefer, no extra work), 3) targeted=true, 4) less work.
- {"op":"order","before":STEP_ID,"after":STEP_ID,"why":"..."} — ORDER_CANDIDATE: one must finish before other starts.
- {"op":"independent","issue":ISSUE_ID,"why":"..."} — steps don't affect each other, run in parallel.
- {"op":"disconnect","src":PROVIDER_ID,"dst":REQUEST_ID,"why":"..."} — candidate doesn't fit. Never CONFIRMED.
- {"op":"move","node":PROVIDER_ID,"after":NODE_ID_OF_SAME_ROBOT_or_START,"why":"..."} — reorder to break CYCLE.
- {"op":"drop","node":NODE_ID,"why":"..."} — DUPLICATE_WORK across robots. Never a request or CONFIRMED provider.
- {"op":"merge","node":NODE_ID,"into":NODE_ID_OF_SAME_ROBOT,"why":"..."} — DUPLICATE inside ONE robot.
- {"op":"unresolved","issue":ISSUE_ID,"why":"..."} — truly ambiguous.

Answer EVERY issue with exactly one operation. Return JSON: {"ops":[...]}"""

GRAPH_USER = """TASK: {task}
JOINT PLAN: {plan}
ISSUES: {issues}"""

SIZE_SYSTEM = """Estimate how long each robot step takes.
- "short": quick action on light object in own room (pick, place, switch).
- "medium": several actions, awkward object, or travelling to another room.
- "long": heavy furniture (sofa, table, cabinet) or multi-part job.
Return JSON: {"sizes": {"<step id>": "short"|"medium"|"long", ...}}"""

SIZE_USER = """TASK: {task}
ROBOTS: {robots}
STEPS: {steps}"""


def plan_system(agent: str, room: str) -> str:
    return PLAN_SYSTEM.format(agent=agent, room=room)


def propose_system(agent: str) -> str:
    return PROPOSE_SYSTEM.format(agent=agent)


def indexed(xs: list[str]) -> str:
    return "\n".join(f"[{i}] {x}" for i, x in enumerate(xs)) or "(none)"


__all__ = ["_j", "OFFER_SYSTEM", "OFFER_USER", "PLAN_USER", "PLAN_FIX", "PROPOSE_USER",
           "GRAPH_SYSTEM", "GRAPH_USER", "SIZE_SYSTEM", "SIZE_USER", "plan_system", "propose_system",
           "indexed"]
