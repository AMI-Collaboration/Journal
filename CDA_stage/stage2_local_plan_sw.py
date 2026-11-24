"""Stage 2 - Local Plan. Each robot, in parallel, writes its goals, its own work and what it needs.

Stage 2 keeps the existing collaboration tags:
    LOCAL     an atomic piece of work performed by this robot
    RECEIVE   "I need movable object o from robot i" (the hand-off is completed in Stage 3)
    ASK_HELP  "I need this exact work done in my room" (no helper robot is named)
PASS and HELP are NOT written here: another robot adds them in Stage 3 to answer a request.

For object relocation, LOCAL text uses a small canonical action vocabulary:
    pick_up  ->  move (only when relocation is needed)  ->  put_down
These are still LOCAL nodes; no new collaboration tag or low-level motion/path details are added.

Stage 2 keeps the existing output schema and collaboration tags. In addition to format checks, it
uses conservative deterministic guards to suppress duplicated can_do responsibilities, duplicate
production/transfer requests, orphan pickups, and duplicate local transport plans. Fixed-producer
product transfers use one ASK_HELP -> Stage 3 HELP path, including final placement in the destination
room. Stage 4 remains responsible for graph-level alignment and final scheduling.
"""
from __future__ import annotations

import re

from .core import (ASK_HELP, HELP, PASS, RECEIVE, REQUEST_TYPES, STEP_TYPES, EventLog, Node, Offer, Plan,
                   TaskConfig, _j, as_int, as_list)

STAGE3_ONLY = (PASS, HELP)
from .llm import BaseLLM

# ================================================================================================
# PROMPTS
# ================================================================================================
PLAN_SYSTEM = """You are robot {agent} in the {room}. Create YOUR part of a cooperative multi-robot plan.

ROLE AND SCOPE
You are a high-level task planner, not a motion controller. Plan meaningful task operations only.
Do not output routes, coordinates, trajectories, joint angles, gripper poses, motor commands,
waypoints, or invented movement times. Stage 2 runs in parallel: you see robot offers, but you do
not see the other robots' Stage 2 plans yet. Stage 3 will answer explicit requests.

1. UNDERSTAND THIS TASK BEFORE ASSIGNING WORK
- Read the task and identify the required final states, objects, operations, source/destination
  locations, and prerequisite relationships.
- Split the task into distinct work units only when they represent genuinely different operations
  or responsibilities. A single goal may require preparation, transport, and final placement; do not
  assign the whole goal independently to multiple robots.
- Adapt the plan to THIS task. Do not assume that every task is object transport, food preparation,
  cleaning, or any other fixed pattern. Do not add actions merely because they appeared in examples.
- Distinguish different instances of the same object type when the task or available facts identify
  them (for example by room, source, label, or role). Do not merge two distinct objects just because
  they share a type name.

2. ASSIGN EACH RESPONSIBILITY ONCE
Use the offers as a team-wide assignment guide:
- Your own offer is authoritative for your room, mobility, capability, can_do, can_help, and has_items.
- When shared, other robots' offers are authoritative for those robots' corresponding facts. Do not
  invent facts when offers are not shared.
- Compare can_do entries by their meaning and resulting world-state effect, not only by wording.
  If two robots offer the same indivisible operation for the same object instance and target state,
  assign that operation to ONE robot only. For a single physical object, two different final placement
  surfaces (for example, sofa versus coffee table) are competing outcomes, not two separate jobs;
  assign one owner and do not plan both destinations unless the task explicitly requires a sequence.
- Choose the owner in this order: (a) the robot whose explicit capabilities make the operation
  executable; (b) the robot that has the required object(s) or is already in the required room; (c)
  the robot requiring fewer hand-offs or unnecessary transfers; (d) lowest robot ID only as the final
  deterministic tie-break. Do not choose the lowest ID automatically when it is less capable or does
  not have access to the required object/location.
- Only the selected owner writes that indivisible operation as LOCAL. Every other robot omits it and
  records it in left_to_others with the owner's ID. A different wording does not make the same work
  new work.
- Assign distinct complementary sub-operations to different robots when that improves feasibility.
  For example, preparation and transport can have different owners; do not confuse this with two
  robots both preparing the same object.
- A can_help entry describes what you are able to help with; it is NOT automatically an assigned LOCAL
  step. If a FIXED robot produces a tangible object that must go to another room and a mobile helper
  explicitly offers compatible carrying help, use ONE collaboration path: the producer requests the
  complete transfer-and-placement with ASK_HELP; the helper leaves that transfer out of its LOCAL plan
  and answers in Stage 3. Do NOT also create RECEIVE for that same product. Do NOT plan duplicate
  pick_up/move/put_down steps for that product.
- If another robot already owns the same production operation, do not ASK_HELP for that production
  again. Ask only for a distinct operation that remains unassigned.
- If no work is assigned to you in Stage 2, return empty goals and steps. Do not invent work just to
  appear useful; Stage 3 can still ask you to answer another robot's request.

3. RESPECT ROBOT AND OBJECT CONSTRAINTS
- A FIXED robot can act only at its own spot in its own room. It cannot navigate to another spot or
  room. A mobile robot can navigate between rooms, but mobility alone does NOT prove it has a gripper.
- The capability description is a hard constraint. A stated CANNOT capability always overrides a
  broad can_do or can_help claim. Do not infer a gripper, arm, grasping, lifting, slicing, pouring, or
  furniture-moving ability unless the facts support it.
- Check object weight against the stated pickup capability when weight is known. Do not assume an
  object is light or heavy when the input does not establish it.
- Treat has_items as movable objects available in that robot's stated room. It does not mean the
  object is already held, and it does not reveal an exact counter/table/shelf unless stated elsewhere.
- An object produced by one of your earlier LOCAL steps becomes available only after that step.
  Respect this dependency. Never claim an object is already grasped, delivered, prepared, clean, open,
  or in another state unless the task, an offer, or an earlier step establishes that state.
- Do not invent an object's source, owner, state, or destination. Use a source surface only when known.

4. CHOOSE THE RIGHT ACTION GRANULARITY FOR THE TASK
A. Physical relocation or explicit placement of a movable object:
- Use separate LOCAL steps with these meanings when the task truly requires handling and relocating
  or placing a named object:
  1) "pick_up <object> [from <known source>]" = grasp/lift the object. It does not include travel
     or final release.
  2) "move <object> to <destination>" = navigate while holding the already picked-up object. Include
     this only when the object must change location. A fixed robot cannot do this.
  3) "put_down <object> at/on <destination>" = release/place the object at the required destination.
- The order is pick_up -> move (only if needed) -> put_down. If the object is already in the correct
  room/spot, omit move. Do not combine grasp, travel, and release into one vague action.
- Do not repeat a pick_up if the object has just been handed to you through RECEIVE; the Stage 3 PASS
  already includes the hand-off. After RECEIVE, add move only if you must transport it farther, and
  put_down only if the task requires a final placement.
B. State-changing or service operations:
- Operations such as preparing, slicing, pouring, wiping, opening, closing, switching, or cleaning
  should normally remain one meaningful LOCAL step when that is the actual task operation.
- Do not split them into approach/reach/grasp/rotate/wait/motor-level actions. Do not force the
  pick_up/move/put_down pattern onto a task that does not require relocating or placing an object.
C. Mixed tasks:
- Plan each required operation according to its actual purpose. A task can contain both atomic
  state-changing work and a separate object transfer; decompose only the transfer part.

5. REQUEST THE RIGHT KIND OF COLLABORATION
- RECEIVE: use when a later LOCAL step that YOU will perform requires a movable object held or
  produced by another robot. Set item to that exact object, target to its owner/producer, and enables
  to the first later LOCAL step that actually uses it. Do not request an object speculatively.
- ASK_HELP: use when another robot must perform a distinct operation for you, such as a transfer
  your body cannot perform. Describe the complete required result, including final placement when the
  task asks that an object be put in a destination. Do not name a helper robot.
- SPECIAL CROSS-ROOM PRODUCT CASE: when a FIXED robot creates a tangible product and a mobile robot
  explicitly offers to transport it to the task's destination, the FIXED producer's ASK_HELP is the
  single request. The mobile helper must NOT add a RECEIVE or duplicate LOCAL transfer chain; it
  answers that ASK_HELP in Stage 3.
- If YOU need another robot to perform a preparation/state-changing operation and then YOU will use
  the resulting tangible object, request the resulting object with RECEIVE (target the known producer)
  and make its first use a later LOCAL step. Do not use ASK_HELP merely to ask a FIXED robot to travel
  or perform work in another room.
- RECEIVE is for obtaining an object for your own later LOCAL work; ASK_HELP is for delegating an
  operation. Do not create both for the same product/transfer.
- Do not create both ASK_HELP and a LOCAL step that performs the same operation. If the HELP itself
  completes that operation, enables is null. Otherwise enables points to the first later LOCAL step
  that depends on the help.
- Stage 2 never writes PASS or HELP. Those are created by the responding robot in Stage 3.
- Do not ask for work already assigned to another robot's can_do, even when the request uses
  synonyms or a slightly different description of the same object and destination. In particular, if
  another robot already offers to move/carry an object to the required room, do not ASK_HELP for
  that same transfer. Do not ask for an object that you do not use in a later step.

6. ORDER AND AUDIT YOUR PLAN
Before returning, check all of the following:
- Every required part of the task is either assigned to you, assigned to another robot, or explicitly
  requested from another robot. Do not silently omit a required part.
- No indivisible operation or final-state effect is duplicated across robots.
- Different operations on the same object are not mistakenly removed as duplicates; only overlapping
  work with the same object instance, operation/effect, and destination is duplicate work.
- Every LOCAL step is physically executable by your robot and advances one of your goals.
- Objects are available before use; requests precede the first step that depends on them; production
  precedes handling; pick_up precedes move; move precedes put_down. A pick_up with no later use,
  transfer, placement, or explicit pickup goal is an incomplete orphan action and must be omitted.
- No request and LOCAL step duplicate the same operation. No unsupported source, object, capability,
  state, or destination has been invented.
- Respect the deadline by avoiding unnecessary work, but do not omit required work to make the plan
  appear shorter. Do not estimate durations; Stage 4 applies its own fixed duration model.

OUTPUT FIELDS
- reasoning: brief decision summary only (not hidden chain-of-thought); state what you own, what is
  delegated, and any important feasibility constraint.
- my_part: one sentence describing only the work assigned to YOU in Stage 2.
- left_to_others: list work assigned to other robots, each with its robot ID. Do not list speculative
  help that has not been requested as already assigned work.
- goals: 0-3 concrete outcomes of YOUR assigned part only. Use [] when no work is assigned to you.
- steps: your steps in execution order. Every step must advance one of your goals. Use [] when none.
- serves is a zero-based index into your own goals. enables is a zero-based index into your own later
  steps and must point forward.

STEP TYPES (ONLY THESE THREE)
- LOCAL: a meaningful operation performed by you.
  Example: {{"type":"LOCAL","text":"pick_up the book from the shelf","serves":0}}
- RECEIVE: an object needed by a later LOCAL step.
  Example: {{"type":"RECEIVE","text":"receive the book from R1","item":"book","target":"R1","enables":1,"serves":0}}
- ASK_HELP: exact work another robot must perform, with no robot named.
  Example: {{"type":"ASK_HELP","text":"move the box from the kitchen to the study","condition":"mobile robot able to grasp and carry the box","enables":null,"serves":0}}

Return valid JSON only, with exactly these top-level fields:
{{"reasoning":"...","my_part":"...","left_to_others":[...],"goals":[...],"steps":[...]}}"""

PLAN_USER = """TASK: {task}
DEADLINE: {deadline} minutes

YOUR OFFER: {own_offer}

{others_block}"""

OTHERS_BLOCK = "OTHER ROBOTS' OFFERS: {offers}"
NO_OTHERS_BLOCK = ("OTHER ROBOTS (their offers are not shared; you know only who they are): {robots}")


# ================================================================================================
# CODE
# ================================================================================================
_ARTICLES_AND_FILLERS = {
    "a", "an", "the", "and", "or", "with", "using", "from", "to", "at", "on", "in", "into",
    "onto", "for", "of", "by", "my", "your", "their", "our", "some", "any", "thing", "things",
    "item", "items", "object", "objects", "please", "then", "there", "here", "it", "them",
    "up", "down",
}
_ACTION_ALIASES = {
    "prepare": "make", "assemble": "make", "create": "make", "produce": "make",
    "put_down": "put", "putdown": "put", "place": "put", "set": "put",
    "pick_up": "pick", "pickup": "pick", "grab": "pick", "take": "pick", "get": "pick",
    "carry": "move", "transport": "move", "bring": "move", "deliver": "move",
}
_TRANSFER_WORDS = {"pick", "move", "put", "carry", "transport", "bring", "deliver", "place", "set"}


def _words(text: str | None) -> list[str]:
    """Lowercase tokens, treating underscore action names as ordinary words."""
    return re.findall(r"[a-z0-9]+", (text or "").lower().replace("_", " "))


def _meaningful_tokens(text: str | None) -> set[str]:
    tokens = _words(text)
    out = set()
    for token in tokens:
        token = _ACTION_ALIASES.get(token, token)
        if token not in _ARTICLES_AND_FILLERS and len(token) > 1:
            out.add(token)
    return out


def _action_family(text: str | None) -> str:
    tokens = _words(text)
    if not tokens:
        return ""
    first = tokens[0]
    return _ACTION_ALIASES.get(first, first)


def _same_responsibility(left: str | None, right: str | None) -> bool:
    """Match near-identical work descriptions after normalizing action particles/synonyms."""
    lv, rv = _action_family(left), _action_family(right)
    if not lv or lv != rv:
        return False
    lt, rt = _meaningful_tokens(left), _meaningful_tokens(right)
    if not lt or not rt:
        return False
    overlap = len(lt & rt)
    union = len(lt | rt)
    return (overlap / union >= 0.78) or (lt == rt)


def _robot_order(robot_id: str) -> tuple[int, str]:
    match = re.search(r"(\d+)$", str(robot_id))
    return (int(match.group(1)) if match else 10**9, str(robot_id))


def _offer_views(offers: dict[str, Offer]) -> list[dict]:
    """Return public offer dictionaries while ensuring each has its robot id."""
    views = []
    for robot_id, offer in offers.items():
        public = offer.public()
        if not isinstance(public, dict):
            continue
        view = dict(public)
        view.setdefault("agent", str(robot_id))
        view["agent"] = str(view["agent"])
        view["can_do"] = as_list(view.get("can_do"))
        view["can_help"] = as_list(view.get("can_help"))
        view["has_items"] = as_list(view.get("has_items"))
        views.append(view)
    return views


def _operation_feasible(text: str, offer: dict) -> bool:
    """Reject only explicit capability conflicts; never infer missing capabilities."""
    capability = str(offer.get("capability") or "").lower()
    mobile = bool(offer.get("mobile", False))
    tokens = _meaningful_tokens(text)
    needs = set()
    if tokens & {"slice", "chop", "cut"}:
        needs.add("sliceobject")
    if tokens & {"pour", "fill"}:
        needs.add("pourobject")
    if tokens & {"push", "move"}:
        if "push" in tokens:
            needs.add("pushfurniture")
    if needs and any(f"cannot: {need}" in capability or f"cannot: ... {need}" in capability
                     for need in needs):
        return False
    if "cannot:" in capability:
        cannot_part = capability.split("cannot:", 1)[1]
        can_part = capability.split("cannot:", 1)[0]
        if any(need in cannot_part for need in needs):
            return False
        if "move" in tokens and not mobile:
            return False
        # If a specific required ability is listed in neither CAN nor CANNOT, leave it unknown;
        # the LLM must resolve that uncertainty rather than code inventing a capability.
        if any(need not in can_part and need not in cannot_part for need in needs):
            return False
    return True


def _candidate_score(text: str, offer: dict, task: str = "") -> tuple:
    """Deterministic suitability score for duplicate can_do ownership."""
    feasible = _operation_feasible(text, offer)
    action_tokens = _meaningful_tokens(text)
    item_tokens = set()
    for item in offer.get("has_items") or []:
        item_tokens.update(_meaningful_tokens(str(item)))
    inventory_match = len(action_tokens & item_tokens)
    room = str(offer.get("room") or "").lower().replace("_", " ")
    room_match = int(any(word in room.split() for word in action_tokens))
    task_tokens = _meaningful_tokens(task)
    task_match = len(action_tokens & task_tokens)
    target_match = len(_target_tokens(text) & task_tokens)
    # Capability remains the hard first criterion; possession/location follow, then task wording
    # resolves conflicting target surfaces (e.g. coffee table versus sofa).
    return (int(feasible), inventory_match, room_match, task_match + 2 * target_match)


def _duplicate_ownership(views: list[dict], task: str = "") -> dict[str, list[tuple[str, str]]]:
    """Map losing robots to (duplicate responsibility, selected owner) pairs."""
    entries = []
    for view in views:
        robot = str(view.get("agent") or "")
        for phrase in view.get("can_do") or []:
            phrase = str(phrase).strip()
            if phrase:
                entries.append((robot, phrase, view))
    parent = list(range(len(entries)))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for i, (robot_i, phrase_i, _) in enumerate(entries):
        for j in range(i + 1, len(entries)):
            robot_j, phrase_j, _ = entries[j]
            if robot_i != robot_j and _same_assigned_work(phrase_i, phrase_j):
                union(i, j)

    groups: dict[int, list[int]] = {}
    for i in range(len(entries)):
        groups.setdefault(find(i), []).append(i)

    blocked: dict[str, list[tuple[str, str]]] = {}
    for indexes in groups.values():
        robots = {entries[i][0] for i in indexes}
        if len(robots) < 2:
            continue
        # Use one representative phrase for the duplicate work unit. All phrases in this group
        # have already passed the conservative same-operation/same-content test.
        representative = entries[indexes[0]][1]
        candidate_views: dict[str, tuple[str, dict]] = {}
        for i in indexes:
            robot, phrase, view = entries[i]
            current = candidate_views.get(robot)
            if current is None or _candidate_score(phrase, view, task) > _candidate_score(current[0], current[1], task):
                candidate_views[robot] = (phrase, view)
        # Explicit and stable tie-break, independent of dictionary or task iteration order.
        best_score = max(_candidate_score(candidate_views[r][0], candidate_views[r][1], task)
                         for r in candidate_views)
        tied = [r for r in candidate_views
                if _candidate_score(candidate_views[r][0], candidate_views[r][1], task) == best_score]
        owner = min(tied, key=_robot_order)
        for loser in sorted(robots - {owner}, key=_robot_order):
            blocked.setdefault(loser, []).append((representative, owner))
    return blocked


def _product_name(phrase: str) -> str | None:
    """Extract a likely tangible product from a production offer, conservatively."""
    text = (phrase or "").strip().lower().replace("_", " ")
    match = re.match(
        r"^(?:make|prepare|assemble|cook|bake|create|produce)\s+(?:a|an|the)?\s*([^,]+?)"
        r"(?:\s+(?:with|using|from|for|at|in|on|to)\b|$)", text
    )
    if not match:
        return None
    generic = {"food", "meal", "breakfast", "lunch", "dinner", "dish", "item", "things",
               "quick", "simple", "fresh", "hot", "cold", "small", "large", "basic"}
    product = next((w for w in _words(match.group(1)) if w not in generic and w not in _ARTICLES_AND_FILLERS), None)
    return product


def _has_product_token(text: str, product: str) -> bool:
    tokens = set(_words(text))
    return product in tokens or f"{product}s" in tokens or f"{product}es" in tokens


_PRODUCTION_VERBS = {"make", "prepare", "assemble", "cook", "bake", "create", "produce"}
_DESTINATION_PREPOSITIONS = {
    "from", "to", "onto", "into", "on", "at", "in", "off", "against", "beside", "near",
    "under", "with", "using", "through", "toward", "towards",
}
_PICKUP_GOAL_VERBS = {"pick", "pickup", "collect", "gather", "take", "get", "retrieve", "acquire"}


def _object_tokens(text: str | None) -> set[str]:
    """Extract the primary manipulated object, not its source, ingredients, or destination."""
    tokens = _words(text)
    if not tokens:
        return set()
    family = _action_family(text)
    if family in {"pick", "put"} and len(tokens) > 1 and tokens[1] in {"up", "down"}:
        tokens = tokens[2:]
    else:
        tokens = tokens[1:]
    for i, token in enumerate(tokens):
        if token in _DESTINATION_PREPOSITIONS:
            tokens = tokens[:i]
            break
    return {t for t in tokens if t not in _ARTICLES_AND_FILLERS and len(t) > 1}


def _target_tokens(text: str | None) -> set[str]:
    """Extract a final destination phrase for placement/transfer comparison."""
    tokens = _words(text)
    if not tokens:
        return set()
    family = _action_family(text)
    if family == "move":
        starts = [i for i, token in enumerate(tokens) if token in {"to", "into", "onto", "toward", "towards"}]
        start = starts[-1] + 1 if starts else len(tokens)
    elif family == "put":
        starts = [i for i, token in enumerate(tokens) if token in {"on", "onto", "in", "into", "at", "to"}]
        start = starts[0] + 1 if starts else len(tokens)
    else:
        return set()
    return {t for t in tokens[start:] if t not in _ARTICLES_AND_FILLERS and len(t) > 1}


def _same_object_reference(left: str | None, right: str | None) -> bool:
    a, b = _object_tokens(left), _object_tokens(right)
    if not a or not b:
        return False
    overlap = len(a & b)
    return bool(overlap) and (a <= b or b <= a or overlap / len(a | b) >= 0.5)


def _same_object_operation(left: str | None, right: str | None) -> bool:
    """Match the same operation on the same object, including conflicting placement targets."""
    lf, rf = _action_family(left), _action_family(right)
    if not lf or lf != rf or not _same_object_reference(left, right):
        return False
    if lf == "move":
        # A move to different named destinations can be a legitimate sequence. Treat it as the
        # same work only when the final destination matches or one description omits it.
        lt, rt = _target_tokens(left), _target_tokens(right)
        return not lt or not rt or lt == rt or bool(lt & rt)
    # A single object cannot finish on two different surfaces. For put/place, deliberately match
    # even when the destination phrases differ so the conflict is resolved by one owner.
    return True


def _same_assigned_work(left: str | None, right: str | None) -> bool:
    return _same_responsibility(left, right) or _same_object_operation(left, right)


def _request_duplicates_assigned_work(text: str, agent: str, views: list[dict], task: str = "") -> str | None:
    """Return the already-assigned owner when ASK_HELP repeats another robot's can_do work."""
    request_tokens = set(_words(text))
    request_family = _action_family(text)
    request_product = _product_name(text)
    request_has_production = bool(request_tokens & _PRODUCTION_VERBS) or request_family in _PRODUCTION_VERBS
    has_transfer_intent = bool(request_tokens & {"carry", "transport", "move", "bring", "deliver"})
    for view in views:
        owner = str(view.get("agent") or "")
        if not owner or owner == agent:
            continue
        for phrase in view.get("can_do") or []:
            phrase = str(phrase)
            if _same_assigned_work(text, phrase):
                return owner
            offered_product = _product_name(phrase)
            # A differently worded request to make the same tangible product is still duplicate
            # production work (including wording such as "help me prepare a sandwich"). Do not
            # collapse a separate carry/place operation into production.
            if (offered_product and _has_product_token(text, offered_product)
                    and request_has_production and not has_transfer_intent):
                return owner
            if (request_product and offered_product == request_product
                    and request_has_production and not has_transfer_intent):
                return owner
    return None


def _pickup_has_followup(step: dict, all_steps: list[dict], goals: list[str]) -> bool:
    """A standalone pickup is kept only when a later step uses that object or a goal asks for pickup."""
    obj = _object_tokens(step.get("text"))
    if not obj:
        return True  # unknown wording: be conservative and do not delete it
    raw_index = step.get("_i", -1)
    for later in all_steps:
        if later.get("_i", -1) <= raw_index or later.get("type") != "LOCAL":
            continue
        if _same_object_reference(step.get("text"), later.get("text")):
            return True
    for goal in goals:
        goal_tokens = set(_words(goal))
        if (obj & goal_tokens) and (goal_tokens & _PICKUP_GOAL_VERBS):
            return True
    return False


_FOOD_INTENT_WORDS = {
    "eat", "food", "meal", "snack", "breakfast", "lunch", "dinner", "brunch",
    "drink", "beverage", "refreshment", "hungry", "appetite", "edible", "pack",
}
_FOOD_PRODUCTS = {
    "sandwich", "salad", "soup", "pizza", "burger", "hamburger", "toast", "bread",
    "pasta", "noodle", "noodles", "rice", "cake", "cookie", "cookies", "muffin",
    "pancake", "waffle", "omelet", "omelette", "egg", "fruit", "fruitplate", "snack",
    "meal", "breakfast", "lunch", "dinner", "tea", "coffee", "juice", "smoothie",
    "drink", "wrap", "burrito", "taco", "sushi", "dumpling", "dumplings", "stew",
    "porridge", "cereal", "yogurt", "cheese", "cracker", "crackers",
}


def _room_name(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "").lower().replace("_", " ").replace("-", " ")).strip()


def _task_has_food_intent(task: str) -> bool:
    tokens = set(_words(task))
    return bool(tokens & _FOOD_INTENT_WORDS)


def _product_is_task_relevant(product: str, task_tokens: set[str], task: str) -> bool:
    explicitly_named = product in task_tokens or f"{product}s" in task_tokens or f"{product}es" in task_tokens
    # The task may request food generically ("something quick to eat") without naming
    # the concrete product that a robot's can_do offer says it can prepare.
    implied_food = _task_has_food_intent(task) and product in _FOOD_PRODUCTS
    return explicitly_named or implied_food


def _cross_room_product_transfers(views: list[dict], task: str) -> tuple[
    dict[str, list[tuple[str, str]]], dict[str, list[tuple[str, str, str]]]
]:
    """Identify fixed-robot products that need a mobile cross-room transfer.

    Returns:
      helper_map[mobile_robot] = [(product, fixed_producer), ...]
      producer_map[fixed_robot] = [(product, destination_room, helper_condition), ...]

    This is conservative: the product must be a tangible product named by a can_do production
    action, the task must ask for that product (explicitly or as food), a destination room must be
    named by the task, and a mobile robot must explicitly offer compatible carrying help.
    """
    task_tokens = set(_words(task))
    helper_map: dict[str, list[tuple[str, str]]] = {}
    producer_map: dict[str, list[tuple[str, str, str]]] = {}
    normalized_rooms = {_room_name(v.get("room")) for v in views if _room_name(v.get("room"))}

    for producer in views:
        producer_id = str(producer.get("agent") or "")
        producer_room = _room_name(producer.get("room"))
        if not producer_id or not producer_room or bool(producer.get("mobile", False)):
            continue

        products = {
            product
            for phrase in producer.get("can_do") or []
            if (product := _product_name(str(phrase)))
            and _product_is_task_relevant(product, task_tokens, task)
        }
        if not products:
            continue

        destinations = sorted(
            room for room in normalized_rooms
            if room != producer_room and all(part in task_tokens for part in room.split())
        )
        if not destinations:
            continue

        for destination in destinations:
            eligible_helpers: list[str] = []
            transferable_products: set[str] = set()
            for helper in views:
                helper_id = str(helper.get("agent") or "")
                if not helper_id or helper_id == producer_id or not bool(helper.get("mobile", False)):
                    continue
                help_text = " ".join(str(x).lower() for x in helper.get("can_help") or []).replace("_", " ")
                if not re.search(r"\b(carry|transport|move|bring|deliver)\b", help_text):
                    continue
                help_tokens = set(_words(help_text))
                # A can_help offer need not repeat the destination named in the task. Accept a
                # generic "carry food/items" offer, but reject it when it explicitly names a
                # different known destination (for example, "carry food to the kitchen").
                explicit_other_destination = False
                for known_room in normalized_rooms:
                    if known_room == destination:
                        continue
                    room_pattern = r"\b(?:to|into|toward|towards)\s+" + r"\s+".join(
                        re.escape(part) for part in known_room.split()
                    ) + r"\b"
                    if re.search(room_pattern, help_text):
                        explicit_other_destination = True
                        break
                if explicit_other_destination:
                    continue
                # Mobility alone is not evidence of grasping. Require an explicit light-object
                # pickup/gripper capability; a food item's exact weight is otherwise unknown.
                capability = str(helper.get("capability") or "").lower().replace("_", "")
                if "cannot: pickuplightobject" in capability or "cannot: pickup light object" in capability:
                    continue
                if not ("pickuplightobject" in capability or "pickup light object" in capability
                        or "can grasp and carry" in capability):
                    continue

                # Generic "items" help is acceptable only because this producer's output is a
                # task-relevant tangible product and the destination is explicitly stated.
                eligible_products = [
                    product for product in products
                    if help_tokens & {"food", "item", "items", "object", "objects", product}
                ]
                if not eligible_products:
                    continue

                eligible_helpers.append(helper_id)
                for product in eligible_products:
                    transferable_products.add(product)
                    helper_map.setdefault(helper_id, []).append((product, producer_id))

            if eligible_helpers:
                for product in transferable_products:
                    condition = (
                        f"mobile robot with an explicit light-object grasping capability, able to "
                        f"carry the prepared {product} from {producer_room} to {destination}"
                    )
                    producer_map.setdefault(producer_id, []).append((product, destination, condition))

    # Preserve order while removing repeated offer phrases that refer to the same product/producer.
    for mapping in (helper_map, producer_map):
        for robot, entries in list(mapping.items()):
            mapping[robot] = list(dict.fromkeys(entries))
    return helper_map, producer_map


def _delegated_transfer_products(views: list[dict], task: str) -> dict[str, list[tuple[str, str]]]:
    """Products whose transfer is delegated to a Stage 3 HELP answer, keyed by helper."""
    return _cross_room_product_transfers(views, task)[0]


def _producer_transfer_requests(views: list[dict], task: str) -> dict[str, list[tuple[str, str, str]]]:
    """Required ASK_HELP requests for fixed producers, keyed by the producing robot."""
    return _cross_room_product_transfers(views, task)[1]


def _is_product_transfer_step(text: str, product: str, task: str = "") -> bool:
    """Recognize product transfers, including task-grounded generic phrases like 'packed food'."""
    normalized = (text or "").lower().replace("_", " ")
    has_transfer_action = bool(re.search(
        r"\b(?:pick(?:\s+up)?|move|carry|transport|bring|deliver|place|put\s+down|set\s+down)\b",
        normalized,
    ))
    if not has_transfer_action:
        return False
    if _has_product_token(text, product):
        return True
    if _task_has_food_intent(task) and product in _FOOD_PRODUCTS:
        # The task may refer to the prepared item generically ("packed food", "something to eat")
        # while the producing offer names the concrete product (e.g. sandwich).
        generic_food_reference = bool(set(_words(text)) & {
            "food", "meal", "snack", "breakfast", "lunch", "dinner", "eat", "edible", "packed"
        })
        return generic_food_reference
    return False


def _is_product_reference(text: str | None, product: str, task: str = "") -> bool:
    """Match an explicitly named product or a task-grounded generic food reference."""
    if _has_product_token(text or "", product):
        return True
    if _task_has_food_intent(task) and product in _FOOD_PRODUCTS:
        return bool(set(_words(text)) & {
            "food", "meal", "snack", "breakfast", "lunch", "dinner", "eat", "edible", "packed"
        })
    return False


def _prune_unserved_goals(goals: list[str], raw_steps, kept: list[dict]) -> tuple[list[str], list[dict], list[dict]]:
    """Remove goals whose only supporting steps were suppressed during Stage 2 validation."""
    raw_list = raw_steps if isinstance(raw_steps, list) else []
    raw_serves = {
        as_int(step.get("serves")) for step in raw_list if isinstance(step, dict)
    } - {None}
    kept_serves = {step.get("serves") for step in kept if step.get("serves") is not None}
    goal_notes: list[dict] = []

    if not kept:
        if goals:
            goal_notes.append({"step": -1, "what": "removed unassigned goals",
                               "why": "no Stage 2 steps remain after responsibility/transfer validation"})
        return [], kept, goal_notes

    # Prune only when the model supplied valid serves references. If it omitted all serves values,
    # preserve its goals rather than guessing which remaining step was intended to support them.
    if raw_serves and kept_serves:
        keep_indexes = [i for i in range(len(goals)) if i in kept_serves]
        removed_indexes = [i for i in range(len(goals)) if i not in kept_serves and i in raw_serves]
        if removed_indexes:
            for i in removed_indexes:
                goal_notes.append({"step": -1, "what": "removed unassigned goal",
                                   "why": f"goal {i} was supported only by suppressed steps"})
        remap = {old: new for new, old in enumerate(keep_indexes)}
        new_goals = [goals[i] for i in keep_indexes]
        for step in kept:
            old = step.get("serves")
            if old is not None:
                step["serves"] = remap.get(old)
        return new_goals, kept, goal_notes

    return goals, kept, goal_notes


def tidy(raw_steps, agent: str, goals: list[str], cfg: TaskConfig,
         blocked_local_actions: list[tuple[str, str]] | None = None,
         delegated_products: list[tuple[str, str]] | None = None,
         team_views: list[dict] | None = None) -> tuple[list[dict], list[dict]]:
    """Validate and tidy Stage 2 steps; preserve raw indices for enables remapping."""
    me = cfg.agent(agent)
    others = [x for x in cfg.ids if x != agent]
    raw_steps = raw_steps if isinstance(raw_steps, list) else []
    notes: list[dict] = []
    kept: list[dict] = []
    # The fixed producer's ASK_HELP is the sole request for a delegated cross-room product,
    # regardless of which mobile robot independently tries to request/receive that same item.
    # LOCAL transfer pruning remains restricted to robots explicitly listed as eligible helpers.
    team_delegated_products = list(delegated_products or [])
    if team_views:
        _, team_producer_map = _cross_room_product_transfers(team_views, cfg.task)
        for producer, products in team_producer_map.items():
            for product, _destination, _condition in products:
                entry = (product, producer)
                if entry not in team_delegated_products:
                    team_delegated_products.append(entry)
    for i, s in enumerate(raw_steps):
        s = s if isinstance(s, dict) else {}
        t = str(s.get("type", "")).upper().strip()
        text = str(s.get("text") or s.get("action") or "").strip()
        if t == "LOCAL" and text:
            duplicate = next((owner for phrase, owner in (blocked_local_actions or [])
                              if _same_assigned_work(text, phrase)), None)
            if duplicate:
                notes.append({"step": i, "what": "removed duplicate LOCAL",
                              "why": f"same can_do responsibility is assigned to {duplicate}",
                              "text": text, "owner": duplicate})
                continue
            delegated = next(((product, producer) for product, producer in (delegated_products or [])
                              if _is_product_transfer_step(text, product, cfg.task)), None)
            if delegated:
                product, producer = delegated
                notes.append({"step": i, "what": "removed duplicate transfer LOCAL",
                              "why": f"{product} is produced by fixed robot {producer}; matching mobile help is handled through Stage 3",
                              "text": text, "owner": producer, "item": product})
                continue
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
        if t == RECEIVE:
            duplicate_product = next(((product, producer) for product, producer in team_delegated_products
                                      if agent != producer and (
                                          _is_product_reference(text, product, cfg.task)
                                          or _is_product_reference(st.get("item"), product, cfg.task)
                                      )), None)
            if duplicate_product:
                product, producer = duplicate_product
                notes.append({"step": i, "what": "removed duplicate RECEIVE",
                              "why": f"{product} transfer is already delegated through the producer's ASK_HELP/Stage 3 HELP path",
                              "text": text, "owner": producer})
                continue
        if t == ASK_HELP:
            if st["target"]:
                notes.append({"step": i, "what": "cleared target", "why": "ASK_HELP names no robot"})
            st["target"] = None
            st["condition"] = st["condition"] or text
            duplicate_request = next((producer for product, producer in team_delegated_products
                                      if agent != producer and _is_product_transfer_step(text, product, cfg.task)), None)
            if duplicate_request:
                notes.append({"step": i, "what": "removed duplicate ASK_HELP",
                              "why": f"fixed producer {duplicate_request} owns the product-transfer request",
                              "text": text, "owner": duplicate_request})
                continue
            assigned_owner = _request_duplicates_assigned_work(text, agent, team_views or [], task=cfg.task)
            if assigned_owner:
                notes.append({"step": i, "what": "removed duplicate ASK_HELP",
                              "why": f"requested operation is already assigned in {assigned_owner}'s can_do",
                              "text": text, "owner": assigned_owner})
                continue
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

    # A request must not ask another robot to perform an operation already present in this
    # robot's own LOCAL plan. This also catches requests that appear before the matching LOCAL
    # step in the model's JSON order.
    own_locals = [st for st in kept if st["type"] == "LOCAL"]
    deduped: list[dict] = []
    for st in kept:
        if st["type"] == ASK_HELP:
            duplicate_local = next((local for local in own_locals
                                    if _same_assigned_work(st["text"], local["text"])), None)
            if duplicate_local:
                notes.append({"step": st["_i"], "what": "removed duplicate ASK_HELP",
                              "why": "the same operation is already included in this robot's LOCAL plan",
                              "text": st["text"]})
                continue
        deduped.append(st)
    kept = deduped

    # A pickup with no later use is not a completed object-transfer plan. Remove it unless
    # the task goal explicitly asks to pick/collect that exact object. This prevents plans such
    # as "pick_up Apple" from surviving after the move/place/request that should consume it vanished.
    filtered: list[dict] = []
    for st in kept:
        if st["type"] == "LOCAL" and _action_family(st["text"]) == "pick":
            if not _pickup_has_followup(st, kept, goals):
                notes.append({"step": st["_i"], "what": "removed orphan pickup LOCAL",
                              "why": "picked object has no later LOCAL use/transfer and no goal explicitly requires pickup",
                              "text": st["text"]})
                continue
        filtered.append(st)
    kept = filtered

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
    blocked_local_actions: list[tuple[str, str]] = []
    delegated_products: list[tuple[str, str]] = []
    views: list[dict] = []
    required_transfer_requests: list[tuple[str, str, str]] = []
    if share_offers:
        views = _offer_views(offers)
        others = OTHERS_BLOCK.format(offers=_j([v for v in views if v.get("agent") != agent]))
        blocked_local_actions = _duplicate_ownership(views, task=cfg.task).get(agent, [])
        helper_map, producer_map = _cross_room_product_transfers(views, cfg.task)
        delegated_products = helper_map.get(agent, [])
        required_transfer_requests = producer_map.get(agent, [])
    else:
        others = NO_OTHERS_BLOCK.format(robots=_j({a.id: {"room": a.profile.room, "mobile": a.profile.mobile}
                                                    for a in cfg.agents if a.id != agent}))
    system = PLAN_SYSTEM.format(agent=agent, room=me.profile.room)
    user = PLAN_USER.format(task=cfg.task, deadline=cfg.deadline_min, own_offer=_j(own.public()),
                            others_block=others)
    d = await llm.complete(system, user, key=f"plan:{agent}")
    goals = as_list(d.get("goals"))
    raw_steps = d.get("steps")
    kept, notes = tidy(raw_steps, agent, goals, cfg,
                       blocked_local_actions=blocked_local_actions,
                       delegated_products=delegated_products,
                       team_views=views)

    # If this robot is the fixed producer of a task-relevant tangible product, and a mobile robot
    # explicitly offers to carry it to a task-mentioned destination, make the dependency explicit.
    # Do this in Stage 2 (the only file changed): producer LOCAL -> ASK_HELP -> Stage 3 HELP.
    for product, destination, condition in required_transfer_requests:
        has_production_step = any(
            step.get("type") == "LOCAL" and _product_name(step.get("text", "")) == product
            for step in kept
        )
        if not has_production_step:
            continue
        already_requested = any(
            step.get("type") == ASK_HELP and _is_product_transfer_step(step.get("text", ""), product, cfg.task)
            for step in kept
        )
        if already_requested:
            continue
        source_room = _room_name(me.profile.room)
        request_text = (f"carry the prepared {product} from {source_room} to {destination} "
                        f"and put it down in {destination}, completing the requested placement")
        next_index = max((step.get("_i", -1) for step in kept), default=-1) + 1
        kept.append({
            "_i": next_index,
            "type": ASK_HELP,
            "text": request_text,
            "item": None,
            "target": None,
            "condition": condition,
            "enables": None,
            "serves": next((step.get("serves") for step in kept
                            if step.get("type") == "LOCAL" and _product_name(step.get("text", "")) == product
                            and step.get("serves") is not None), 0 if len(goals) == 1 else None),
            "room": me.profile.room,
        })
        notes.append({"step": next_index, "what": "added required ASK_HELP",
                      "why": f"fixed producer {agent} creates {product}; mobile cross-room transfer is required and offered"})

    goals, kept, goal_notes = _prune_unserved_goals(goals, raw_steps, kept)
    notes.extend(goal_notes)

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
    left_to_others = as_list(d.get("left_to_others"))
    for note in notes:
        owner = note.get("owner")
        if owner and note.get("what") == "removed duplicate LOCAL":
            assigned = f"{note.get('text', 'duplicate work')} ({owner})"
            if assigned not in left_to_others:
                left_to_others.append(assigned)
    my_part = d.get("my_part", "")
    reasoning = d.get("reasoning", "")
    added_requests = [note for note in notes if note.get("what") == "added required ASK_HELP"]
    if added_requests:
        request_summary = "; ".join(note.get("why", "") for note in added_requests)
        my_part = (str(my_part).strip() + " Request a mobile helper to transfer the prepared product.").strip()
        reasoning = (str(reasoning).strip() + " Stage 2 added the required cross-room ASK_HELP request: "
                     + request_summary + ".").strip()
    if not kept and not goals and any(note.get("what", "").startswith("removed duplicate") for note in notes):
        my_part = "No independent Stage 2 work remains; I can answer another robot's request in Stage 3."
        reasoning = (str(reasoning).strip() + " The overlapping work was assigned to another robot, "
                     "so no duplicate local steps remain.").strip()
    return plan, {"reasoning": reasoning, "my_part": my_part,
                  "left_to_others": left_to_others, "tidy_notes": notes,
                  "n_raw_steps": len(raw_steps) if isinstance(raw_steps, list) else 0}
