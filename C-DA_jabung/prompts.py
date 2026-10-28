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

STEP 2 — CHAIN-OF-THOUGHT REASONING (think step by step):
a) GOAL STATE: what must be true when task is done? Think beyond literal words.
   e.g. "watch movie" → TV on + dim lighting + snacks + comfortable seating
b) EACH ROOM'S ROLE: what does each room need to contribute toward that end state?
   Think about ALL rooms, not just yours.
c) MY CONTRIBUTION: given the end state, what can MY room contribute?
   Even if my room is not the main focus, find supporting actions.
   Ask: "what items in my room serve the task's end goal, directly or indirectly?"
d) PRIORITY: which of my contributions matter most given the deadline?
e) FOR OTHERS: which of my has_items should go to another room? Be generous.

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

━━━ FEW-SHOT EXAMPLE (grandmother visit, R1=Mobile_Light in kitchen) ━━━
{{"has_items":["silver kettle (counter, image 1)","white mug (cabinet, image 1)","green apple (counter, image 2)","orange (counter, image 2)"],
 "reasoning":"a) Grandmother needs warm tea + healthy snacks — elderly visitor comfort. b) Tea prep is top priority; kettle takes time. c) I toggle kettle, pick mug, pour tea. d) Mug with tea goes to living room via R4 PASS; fruit also to R4.",
 "capability":"I am mobile and can carry light objects up to 5 kg.",
 "can_do":["PickupLightObject: lift mugs, fruit, small items","PassReceiveObject: transfer items to/from other robots","ToggleObject: turn on/off kettle, lights, appliances"],
 "cannot_do":["PickupHeavyObject: cannot lift heavy furniture","PushFurniture: cannot push sofa","SliceObject: cannot slice food","PourObject: cannot pour precisely"],
 "suggests":["silver kettle","white mug"],
 "intends":["toggle silver kettle from off to on","pick up white mug from cabinet","pour hot water into mug","pass mug to R4"],
 "need_from_others":["R4 to receive mug and deliver tea to grandmother in living room"],
 "obs_scope":"I can observe and interact with items in the kitchen only."}}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

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

CHAIN-OF-THOUGHT before writing steps:
1. TASK END STATE: what must be true when done? (same as offer stage)
2. OTHER ROBOTS: scan ALL robots intends in PUBLIC OFFERS. Who is doing what?
3. GAPS: what essential actions are NOT covered by others?
4. MY STEPS: fill the gaps using MY has_items and capabilities. Never duplicate others.
5. COLLABORATION: what do I need from others (ASK_HELP)? What can I send (PASS)?

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

━━━ FEW-SHOT EXAMPLE (task: "grandmother visiting in 15 min") ━━━
R1 (mobile_light, kitchen): goals=[prepare warm tea, pass to R4]
reasoning: "R2 handles fruit — I do NOT duplicate. Kettle on first (takes time). Pour after kettle ready. PASS mug to R4 — I cannot navigate to living room."
steps:
  {{"type":"LOCAL","action":{{"verb":"toggle","object":"silver kettle","from":"off","to":"on"}},"uses":0,"serves":1,"reason":"boil water immediately — heating takes time"}},
  {{"type":"LOCAL","action":{{"verb":"pick_up","object":"white mug","from":"cabinet","to":"gripper"}},"uses":0,"serves":1,"reason":"vessel for tea while kettle heats"}},
  {{"type":"LOCAL","action":{{"verb":"pour","object":"silver kettle","from":"kettle","to":"white mug"}},"uses":0,"serves":1,"reason":"fill mug with hot water for grandmother"}},
  {{"type":"PASS","item":"white mug","target":"R4","reason":"cannot navigate to living room; R4 delivers tea to grandmother"}}

R2 (gripper, kitchen): goals=[prepare sliced fruit, pass to R4]
reasoning: "R1 handles kettle/tea — do NOT touch kettle. Only I can SliceObject. Slice apple, pick orange, PASS both to R4."
steps:
  {{"type":"LOCAL","action":{{"verb":"slice","object":"green apple","from":"counter","to":"cutting board"}},"uses":0,"serves":1,"reason":"sliced fruit easier for elderly; only Gripper can slice"}},
  {{"type":"LOCAL","action":{{"verb":"pick_up","object":"orange","from":"counter","to":"gripper"}},"uses":0,"serves":1,"reason":"healthy vitamin snack for grandmother"}},
  {{"type":"PASS","item":"green apple","target":"R4","reason":"Gripper fixed in kitchen; R4 places fruit on coffee table"}},
  {{"type":"PASS","item":"orange","target":"R4","reason":"same — R4 delivers all food to grandmother"}}

R3 (mobile_heavy, living_room): goals=[clear walkway, arrange seating]
reasoning: "Only I can push furniture. Grandmother is elderly — floor obstacles are dangerous. Push sofa first to open walkway, then move box, then armchair."
steps:
  {{"type":"LOCAL","action":{{"verb":"push","object":"gray sofa","from":"center of room","to":"against the wall"}},"uses":0,"serves":1,"reason":"open central walkway — critical fall prevention for elderly"}},
  {{"type":"LOCAL","action":{{"verb":"move","object":"cardboard box","from":"floor","to":"cabinet"}},"uses":0,"serves":1,"reason":"eliminate trip hazard from walking path"}},
  {{"type":"LOCAL","action":{{"verb":"push","object":"brown armchair","from":"corner","to":"near gray sofa"}},"uses":0,"serves":1,"reason":"additional comfortable seating for elderly visitor"}}

R4 (mobile_light, living_room): goals=[clear floor, lights on, receive all items, place on table]
reasoning: "I am receiver hub. Clear floor FIRST (trip hazards). Then lights on. Then receive tea/fruit/cushion. Place all on coffee table/sofa."
steps:
  {{"type":"LOCAL","action":{{"verb":"pick_up","object":"black bag","from":"floor","to":"shelf"}},"uses":0,"serves":1,"reason":"trip hazard removal — elderly safety priority"}},
  {{"type":"LOCAL","action":{{"verb":"pick_up","object":"brown shoes","from":"floor","to":"cabinet"}},"uses":0,"serves":1,"reason":"remove additional trip hazard"}},
  {{"type":"LOCAL","action":{{"verb":"toggle","object":"floor lamp","from":"off","to":"on"}},"uses":0,"serves":1,"reason":"bright lighting critical for elderly visibility"}},
  {{"type":"ASK_HELP","action":{{"verb":"prepare","object":"warm tea","from":"kitchen","to":"white mug filled with hot water"}},"enables":"r4_receive_mug","reason":"R1 has kettle; I need tea delivered to serve grandmother"}},
  {{"type":"RECEIVE","item":"white mug","from":"R1","reason":"accepting warm tea prepared by R1"}},
  {{"type":"RECEIVE","item":"green apple","from":"R2","reason":"accepting healthy sliced snack"}},
  {{"type":"LOCAL","action":{{"verb":"put_down","object":"white mug","from":"gripper","to":"coffee table"}},"uses":0,"serves":1,"reason":"tea accessible for seated grandmother"}},
  {{"type":"RECEIVE","item":"blue cushion","from":"R5","reason":"accepting comfort cushion from bedroom"}},
  {{"type":"LOCAL","action":{{"verb":"put_down","object":"blue cushion","from":"gripper","to":"gray sofa"}},"uses":0,"serves":1,"reason":"back support for elderly grandmother"}}

R5 (mobile_light, bedroom): goals=[pass cushion to R4, tidy bedroom]
reasoning: "Blue cushion for grandmother's comfort. R4 is receiver in living room — PASS to R4. Tidy bedroom after."
steps:
  {{"type":"LOCAL","action":{{"verb":"pick_up","object":"blue cushion","from":"bed","to":"gripper"}},"uses":0,"serves":1,"reason":"soft cushion for grandmother's back support"}},
  {{"type":"PASS","item":"blue cushion","target":"R4","reason":"R4 places on sofa for grandmother's comfort"}},
  {{"type":"LOCAL","action":{{"verb":"arrange","object":"gray blanket","from":"bed","to":"neatly on bed"}},"uses":0,"serves":1,"reason":"presentable bedroom in case grandmother rests"}}

R6 (mobile_light, bathroom): goals=[hang towel, turn on light, tidy sink]
reasoning: "Grandmother will need bathroom. Fresh towel + bright light = elderly safety. Tidy sink. All self-contained — no cross-room help needed."
steps:
  {{"type":"LOCAL","action":{{"verb":"hang","object":"white towel","from":"counter","to":"towel rack"}},"uses":0,"serves":1,"reason":"fresh towel for grandmother — cleanliness for elderly guest"}},
  {{"type":"LOCAL","action":{{"verb":"toggle","object":"bathroom light","from":"off","to":"on"}},"uses":0,"serves":1,"reason":"well-lit bathroom critical for elderly safety"}},
  {{"type":"LOCAL","action":{{"verb":"move","object":"pink soap","from":"sink","to":"cabinet"}},"uses":0,"serves":1,"reason":"tidy sink area for grandmother's comfort"}}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

""" + _WORDING + "\n" + _ESSENTIAL + "\n" + _SPACE_RULES + """

BEFORE RETURNING, verify silently:
✓ Every object is in a has_items list
✓ No banned words
✓ Every pick_up has a follow-up step (put_down to DIFFERENT location, PASS, or use)
✓ No from==to moves
✓ No pick_up → put_down to the SAME location (that is a no-op — remove both steps)
✓ Every destination is real furniture
✓ ≥2 active steps per robot
✓ No self-pass (PASS to yourself)
✓ pick_up bread → must carry somewhere useful, not just hold it

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

[CRITICAL] AVOID DUPLICATE WORK:
Before writing ANY step, scan ALL robots' "intends" in PUBLIC OFFERS above.
- If ANY other robot already intends to do the same action on the same object → DO NOT repeat it.
- If ANY other robot intends to turn on/off the same light/appliance → skip it, they handle it.
- If ANY other robot intends to move the same object → skip it.
- "Same work" means same verb + same object, even if worded differently.
  ("turn off ceiling lamp" = "turn off the light" if it's the same fixture)
- This applies to ALL robots, not just your roommates.

[SAME-ROOM] Divide objects explicitly: if 3 robots share a room with 6 objects,
each robot handles 2 different objects. Never two robots touching the same object.

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

CHAIN-OF-THOUGHT before deciding:
1. TASK NEED: does this offer/request actually serve the task end goal?
2. MY PLAN: do I already cover this? (already_doing) Or conflict with it?
3. CAPABILITY: can I physically do what is asked?
4. EFFICIENCY: is accepting this the most efficient path, or is there a better way?
5. DECIDE: accept/reject/already_doing/volunteer based on above reasoning.

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

━━━ FEW-SHOT EXAMPLE (grandmother visit, R4 in living_room) ━━━
Offers to R4: [r1_pass_mug, r2_pass_apple, r2_pass_orange, r5_pass_cushion]
Requests to judge: [r4_ask_help_tea (target=R1)]
R4 response:
{{"offers":[
  {{"offer":"r1_pass_mug","decision":"receive","action":"receive white mug (with hot tea) from R1","uses":1,"insert_after":"r4_toggle_ceiling_light","reason":"I am mobile receiver; R1 cannot navigate. Accepting tea to place on coffee table for grandmother."}},
  {{"offer":"r2_pass_apple","decision":"receive","action":"receive sliced green apple from R2","uses":1,"insert_after":"r4_receive_mug","reason":"Healthy snack for grandmother; Gripper R2 cannot navigate. I place on coffee table."}},
  {{"offer":"r2_pass_orange","decision":"receive","action":"receive orange from R2","uses":1,"insert_after":"r4_receive_apple","reason":"Additional snack; same rationale as apple."}},
  {{"offer":"r5_pass_cushion","decision":"receive","action":"receive blue cushion from R5","uses":1,"insert_after":"r4_place_orange","reason":"Comfort cushion for grandmother; R5 in bedroom cannot place in living room."}}
],
"judgments":[
  {{"request":"r4_ask_help_tea","decision":"accept","reason":"R4 correctly identifies I have kettle. I will toggle kettle, pour water, PASS mug. Legitimate cross-room collaboration.","action":"pour silver kettle into white mug then PASS to R4","uses":1,"insert_after":"r1_pick_up_mug"}}
]}}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

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

CHAIN-OF-THOUGHT before deciding each op:
1. ISSUE TYPE: what kind of conflict is this? (duplicate, ordering, cycle, mismatch)
2. ROOT CAUSE: why did this issue arise? (same object, same action, wrong order)
3. CONSEQUENCE: what happens if left unresolved? (blocked steps, wasted work)
4. BEST FIX: which op resolves it with minimum disruption? (drop/connect/order/disconnect)
5. VERIFY: after applying op, does the plan make sense?

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

Answer EVERY issue with exactly one operation. Return JSON: {"ops":[...]}

━━━ FEW-SHOT EXAMPLE (grandmother visit) ━━━
Issues:
  I1: DUPLICATE_WORK — r2_s0 (R2: pick up silver kettle) vs r1_s1 (R1: toggle silver kettle). R1 already owns kettle.
  I2: ORDER_CANDIDATE — r4_ask_help (R4 ASK_HELP tea) must precede r1_pour (R1 pour kettle).
ops:
  {{"op":"drop","node":"r2_s0","why":"DUPLICATE_WORK with R1 who handles kettle for tea. R2 must focus on fruit only."}}
  {{"op":"order","before":"r4_ask_help","after":"r1_pour","why":"ASK_HELP must be established before R1 pours — ensures correct dependency chain."}}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

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
