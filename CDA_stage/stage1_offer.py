"""Stage 1 - Offer. Each robot, in parallel, declares O_i = <capability, can_do, cannot_do, has_items,
need_from_others, intends>. intends are sub-goals (G_i), the reference for coverage in Stage 4.
Everything except obs_scope / reasoning is broadcast. No rule checks here."""
from __future__ import annotations

from .llm import BaseLLM
from .core import AgentInput, CAPABILITY_TAGS, EventLog, Offer, ObjectState, TaskConfig


# ================================================================================================
# PROMPTS — Stage 1 Offer
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
- capability_tags: from this FIXED list only -- {capability_tags_list} -- every tag that genuinely
  applies to your body (based on what you just wrote in can_do), and nothing else. This is the exact
  vocabulary other robots' ASK_HELP requests will match against, so use it precisely: if you can pour
  or fill liquids, include LIQUID_HANDLING; if you cannot, leave it out (and do not substitute a
  different tag just to appear more capable).
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
 "capability_tags":["MANIPULATE_LIGHT","LIQUID_HANDLING","TOGGLE"],
 "need_from_others":["someone who can slice fruit"],
 "intends":["warm tea ready for the grandmother","fresh fruit available as a snack"],
 "obs_scope":"I can observe the kitchen only."}}

Return JSON (add "see_items" too, only if you were asked for one above):
{{"has_items": [...], "other_robots_in_room": [...], "env_state": [...],
 "reasoning": "a)... b)... c)... d)...", "capability": "...",
 "can_do": [...], "cannot_do": [...], "capability_tags": [...],
 "need_from_others": [...], "intends": [...], "obs_scope": "..."}}"""

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


# ================================================================================================
# CODE — Stage 1 Offer
# ================================================================================================


def _as_list(x) -> list[str]:
    if isinstance(x, str):
        return [x] if x.strip() else []
    out = []
    for v in x or []:
        if isinstance(v, dict):          # e.g. {"goal": "..."} -> "..."
            v = next((v[k] for k in ("goal", "intent", "name", "text") if v.get(k)), "")
        if str(v).strip():
            out.append(str(v).strip())
    return out


def _as_tags(raw) -> list[str]:
    """Keep only entries that are actually in CAPABILITY_TAGS -- a robot naming anything else
    (a typo, a free-text phrase) is silently dropped rather than polluting the shared vocabulary."""
    if not raw:
        return []
    raw = [raw] if isinstance(raw, str) else raw
    return [t for t in (str(x).strip().upper() for x in raw) if t in CAPABILITY_TAGS]


def _as_robots(raw) -> list[dict]:
    if not raw or not isinstance(raw, list):
        return []
    out = []
    for r in raw:
        if isinstance(r, dict) and r.get("id"):
            out.append({"id": str(r["id"]), "distance": str(r.get("distance", "") or "")})
    return out


def _parse_env_state(raw) -> list[ObjectState]:
    if not raw or not isinstance(raw, list):
        return []
    result = []
    for obj in raw:
        if not isinstance(obj, dict):
            continue
        result.append(ObjectState(
            object_id=str(obj.get("object_id", "")),
            object_type=str(obj.get("object_type", "")),
            location=str(obj.get("location", "")),
            accessible=bool(obj.get("accessible", False)),
            toggle=obj.get("toggle"),
            clean=obj.get("clean"),
        ))
    return result


async def make_offer(cfg: TaskConfig, a: AgentInput, llm: BaseLLM, log: EventLog) -> Offer:
    fixed = not a.profile.mobile
    catalog = ", ".join(a.object_catalog) if a.object_catalog else \
        "(no catalog provided -- use your best judgement, but do not invent exotic items)"
    user = OFFER_USER.format(task=cfg.task, deadline=cfg.deadline_min, room=a.profile.room,
                             mobile=a.profile.mobile,
                             payload=(f"{a.profile.payload_kg:g} kg" if a.profile.payload_kg
                                      else "not specified (judge from your embodiment)"),
                             embodiment=a.profile.embodiment,
                             see_items_block=(SEE_ITEMS_BLOCK if fixed else ""),
                             instruction=a.instruction or "(none)", n_img=len(a.images))
    d = await llm.complete(OFFER_SYSTEM.format(agent=a.id, object_catalog=catalog,
                                               capability_tags_list=", ".join(CAPABILITY_TAGS)),
                           user, key=f"offer:{a.id}", images=a.images)
    offer = Offer(
        agent=a.id,
        capability=str(d.get("capability", a.profile.embodiment)),
        can_do=_as_list(d.get("can_do")),
        cannot_do=_as_list(d.get("cannot_do")),
        has_items=_as_list(d.get("has_items")),
        need_from_others=_as_list(d.get("need_from_others")),
        intends=_as_list(d.get("intends")),
        see_items=_as_list(d.get("see_items")) if fixed else [],   # mobile robots: always empty
        other_robots_in_room=_as_robots(d.get("other_robots_in_room")),
        env_state=_parse_env_state(d.get("env_state")),
        capability_tags=_as_tags(d.get("capability_tags")),
        obs_scope=str(d.get("obs_scope", "")),
        reasoning=str(d.get("reasoning", "")),
    )
    log.log("offer", a.id, "broadcast", can_do=len(offer.can_do), items=len(offer.has_items),
            needs=len(offer.need_from_others), intends=len(offer.intends))
    return offer
