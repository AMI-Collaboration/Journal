"""Stage 1 - OFFER.

Each robot independently describes ONLY task-relevant information:
- what it can do for the global task
- what it cannot do when that limitation affects its contribution
- what it can provide
- what it genuinely needs

IMPORTANT:
- The Offer is NOT a general capability inventory.
- "Cannot do X" does NOT imply "Needs X".
- A NEED must be a genuine dependency of this robot's own contribution.

No robot is assigned a task at this stage.

The Offer is later used by Local Planning to construct:
    LOCAL
    ASK_HELP
    HELP
    RECEIVE
    PASS
"""

from __future__ import annotations

import re

from runtime import Agent
from schemas import (
    AgentInput,
    CanProvide,
    Offer,
    OfferNeed,
    RawOffer,
)


# ===========================================================================
# Physical passability check
# ===========================================================================

NON_PASSABLE_KW = {
    "sink",
    "counter",
    "shelf",
    "surface",
    "floor",
    "wall",
    "room",
    "space",
    "area",
    "cleaned",
    "wiped",
    "organized",
    "tidied",
    "cleared",
    "arranged",
    "set",
    "setup",
    "confirmation",
    "confirm",
    "status",
    "done",
    "ready",
    "complete",
    "completed",
}


def _keywords(text: str) -> set[str]:
    return set(
        re.findall(
            r"[a-z0-9]+",
            text.lower(),
        )
    )


def _is_passable(item: CanProvide) -> bool:
    """Check whether a can_provide item is physically transferable."""

    if item.type != "item":
        return True

    if not item.object:
        return False

    return not bool(
        _keywords(item.object) & NON_PASSABLE_KW
    )


# ===========================================================================
# Example
# ===========================================================================

_OFFER_EXAMPLE = """
EXAMPLE

Global task:
"Prepare the living room for exercise."

Robot capability:
"Mobile robot with a light-duty arm. Can move between rooms but
cannot move heavy furniture."

Observed room:
- bathtub
- sink
- toilet
- bath mat
- trash bin

VALID OFFER:

{
  "capability": "Mobile robot with a light-duty arm. Can move between rooms but cannot move heavy furniture.",

  "obs_scope": [
    {
      "object": "bath mat",
      "location": "bathroom"
    },
    {
      "object": "trash bin",
      "location": "bathroom"
    }
  ],

  "can_do": [
    {
      "action": "pick up",
      "object": "bath mat",
      "location": "bathroom",
      "target": "move to living room"
    }
  ],

  "cannot_do": [],

  "can_provide": [
    {
      "type": "item",
      "object": "bath mat",
      "location": "bathroom",
      "action": "move to living room"
    }
  ],

  "needs": []
}

IMPORTANT:
Although this robot cannot move heavy furniture, that does NOT
create a NEED.

The robot's own contribution is handling the bath mat.
Its contribution does not depend on another robot moving furniture.

Therefore:

"cannot do X" != "need X"

A NEED is valid ONLY when:
1. the robot is actually trying to accomplish Y, AND
2. Y is blocked or impossible without another robot performing X.

BAD:

{
  "kind": "task",
  "object": "heavy furniture",
  "location": "living room",
  "action": "move"
}

Reason:
Moving heavy furniture is not part of this robot's own contribution.

---

CONTRASTING GOOD EXAMPLE (when a NEED IS valid):

Global task:
"Clear and prepare the living room for a home workout."

Robot capability:
"Mobile robot in the living room. Can move light objects but
cannot move heavy furniture."

Observed room:
- coffee table (heavy)
- floor lamp
- pillows

This robot's own contribution IS clearing/preparing the living room
(the task explicitly targets this robot's own room).
The heavy coffee table blocks that contribution, and this robot
cannot move it.

VALID NEED:

{
  "kind": "task",
  "object": "coffee table",
  "location": "living_room",
  "action": "move"
}

Reason:
Unlike the earlier BAD example, here the robot's own room IS the
target of the task, and the robot's own required contribution
(clearing the room) is directly blocked by something it cannot do
itself. This is a genuine dependency, not an unrelated request.

KEY DISTINCTION:
- BAD example: robot in bathroom, task in living room -> unrelated, no NEED.
- GOOD example: robot in living room, task in living room -> directly
  blocked, NEED is valid.

Always check: is the blocking object in MY OWN observed room, and is
clearing/using it part of MY OWN required contribution? Only then is
a NEED valid.
"""


# ===========================================================================
# System prompt
# ===========================================================================

OFFER_SYSTEM = f"""
You are one robot in a team of heterogeneous robots.

Each robot works in a different room and has access only to:
- its own images
- its own capability
- its own hidden information

There is NO central task allocator at this stage.

Your job is to independently construct an OFFER containing ONLY
information that is relevant to THIS ROBOT'S contribution to the
GLOBAL TASK.

The OFFER is NOT:
- a complete list of everything the robot can do
- a complete list of everything the robot cannot do
- a list of all objects in the room
- a list of tasks that other robots should perform

When uncertain whether something is relevant, OMIT it.

{_OFFER_EXAMPLE}

Return exactly ONE JSON object. Include a short "reasoning" field
(1-3 sentences) explaining WHY you included what you included -- e.g.
why a NEED is genuine, why a CANNOT_DO is listed, why a CAN_PROVIDE
was or wasn't added. This is for debugging/transparency only; it does
not affect scoring.

JSON format:

{{
  "capability": "...",

  "reasoning": "...",

  "obs_scope": [
    {{
      "object": "...",
      "location": "...",
      "state": "..."
    }}
  ],

  "can_do": [
    {{
      "action": "...",
      "object": "...",
      "location": "...",
      "target": "..."
    }}
  ],

  "cannot_do": [
    {{
      "action": "...",
      "object": "...",
      "location": "...",
      "reason": "..."
    }}
  ],

  "can_provide": [
    {{
      "type": "item" | "task",
      "object": "...",
      "location": "...",
      "action": "..."
    }}
  ],

  "needs": [
    {{
      "kind": "item" | "task",
      "object": "...",
      "location": "...",
      "action": "..."
    }}
  ]
}}

RULES

1. CAPABILITY
- Copy the provided capability faithfully.
- Never claim abilities that contradict the capability.
- Respect mobility, payload, manipulation, and room-access constraints.

2. OBS_SCOPE
- Include only objects or areas visible in your images or explicitly
  stated in HIDDEN INFO.
- Never invent unseen objects.
- OBS_SCOPE is an observation list, not a task list.

3. DO NOT FIXATE ON A SINGLE SUB-GOAL

A shared TASK sentence may describe more than one thing that needs
to happen, not just one. Before writing your OFFER, re-read the
TASK sentence carefully and identify EVERY distinct sub-goal it
describes, not just the first or most obvious one.

For each sub-goal you identify, separately ask whether your own
room contains anything relevant to it (an object you could provide,
or a capability you could use). Do not let one sub-goal (e.g.
clearing/tidying something) crowd out the others just because it is
the easiest or most literal reading of the sentence.

3b. GLOBAL TASK RELEVANCE — CRITICAL

Before adding ANY CAN_DO, CANNOT_DO, CAN_PROVIDE, or NEED, ask:

"Does this information directly affect THIS ROBOT'S meaningful
contribution to the GLOBAL TASK?"

If NO:
- Do NOT include it.

Do NOT include information merely because:
- the object exists
- the robot can physically manipulate it
- the robot cannot physically manipulate it
- another robot might need it
- the action appears somewhere in the global task
- the action happens in another room

Only include information that could actually contribute to solving
the global task or affect this robot's own coordination.

4. CAN_DO

List concrete actions that YOU can physically execute.

Requirements:
- The action must be directly relevant to the GLOBAL TASK.
- Ground the action in OBS_SCOPE.
- The action must be allowed by your capability.
- Do not include actions that require another robot.
- Do not list generic capabilities.
- Do not list unrelated actions just because they are possible.

BAD:
"move objects"

GOOD:
"pick up the bath mat"

5. GROUNDING RULE (applies to CANNOT_DO and NEEDS about OBJECTS)

This rule applies ONLY to limitations about a SPECIFIC OBJECT. It
does NOT apply to your embodiment's fixed physical capabilities
(see 5b below, which is mandatory regardless of what you observe).

Every object-specific CANNOT_DO entry and every NEED must reference
a specific object that YOU actually observed in YOUR OWN room
(present in your OBS_SCOPE or HIDDEN INFO).

Do NOT invent a CANNOT_DO about an object that does not exist in
your own room.

BAD (invents a nonexistent object):
{{"action": "move", "object": "piano", "reason": "too heavy"}}
-> invalid if no piano was observed in this robot's own room.

GOOD (grounded in an observed object):
{{"action": "move", "object": "coffee table", "reason": "too heavy, observed in own room"}}

5b. MANDATORY EMBODIMENT LIMITS (always include, independent of 5)

Your CAPABILITY text states fixed physical limits of your own body
(e.g. "CANNOT: PushFurniture" or "CANNOT: can_navigate"). These are
NOT grounded in any single observed object -- they describe what your
embodiment can NEVER do, anywhere, regardless of your own room's
contents.

You MUST always include these embodiment-level limits in CANNOT_DO,
even if:
- your own room has no object that triggers them right now
- the limitation seems irrelevant to your own room's contribution

This is because OTHER robots read your broadcast OFFER and need to
know your hard physical limits before assigning you any HELP/PASS
role during Local Planning and Auction -- if you omit them here,
another robot may (incorrectly) expect you to volunteer for a task
you can never actually perform.

Example: your CAPABILITY says "CANNOT: PushFurniture, can_navigate".
Even if your own room (e.g. kitchen) has no furniture to push, you
MUST still include:
{{"action": "push furniture", "reason": "embodiment cannot push furniture (fixed physical limit)"}}
{{"action": "navigate between rooms", "reason": "embodiment is fixed in place"}}

Do NOT omit these just because your own room does not need them.

6. CANNOT_DO

List ONLY task-relevant actions that would otherwise matter to
THIS ROBOT'S contribution but that YOU cannot perform.

IMPORTANT:

A physical limitation alone does NOT belong here.

BAD:
"cannot move heavy furniture"

if the robot has no responsibility involving heavy furniture.

GOOD:
"cannot move the heavy table blocking the object this robot must retrieve"

because that limitation directly affects the robot's own contribution.

Therefore:
- Do not enumerate all physical limitations.
- Do not list unrelated tasks.
- Do not list actions that belong entirely to another robot.
- CANNOT_DO describes relevant limitations, not the robot's full
  capability profile.

6. CAN_PROVIDE

IMPORTANT: CAN_PROVIDE is what YOU can offer to the WHOLE TEAM, not
just what your own room currently needs. List a task-relevant
capability here even if nothing in your own room requires it --
another robot's request may depend on it.

MULTIPLE EXAMPLES (different rooms, same principle):

Example A:
  Robot: Mobile_Heavy in the bathroom.
  Own room needs no furniture moved.
  -> STILL list: {{"type": "task", "action": "move", "object": "heavy furniture"}}
     because this robot's embodiment can do it, and some other room's
     request may need exactly this.

Example B:
  Robot: Gripper in the kitchen.
  Own room needs no items passed to the living room.
  -> STILL list: {{"type": "item", "object": "mug", "location": "kitchen", "action": "hand over"}}
     if the mug is relevant to the GLOBAL TASK, even though this
     robot has no reason yet to think anyone needs it.

Example C (do NOT do this):
  Robot: Mobile_Heavy in the bathroom, reasoning:
  "My own room has no heavy furniture, so I have nothing to
   CAN_PROVIDE about moving heavy furniture."
  -> WRONG. This suppresses a real team-wide capability just because
     it is not needed in this robot's own room. CAN_PROVIDE describes
     capability, not local relevance.

RULE OF THUMB:
- CANNOT_DO / NEEDS -> must be grounded in YOUR OWN room / own contribution.
- CAN_PROVIDE -> must be grounded in YOUR OWN capability, but its
  USE may be in ANY room. Do not filter it by "does my room need this."

There are two forms.

ITEM:
- A physical object/resource that another robot could receive.
- It must exist in OBS_SCOPE or HIDDEN INFO.
- It must be physically transferable.
- It should have a plausible role in the GLOBAL TASK.

TASK:
- A concrete task YOU are physically capable of performing.
- The task must be relevant to the GLOBAL TASK.
- This does NOT mean you are already assigned to perform it.
- It describes a capability that may later become a HELP relation.

Do NOT provide:
- abstract states
- room conditions
- generic capabilities
- unrelated tasks
- objects that have no plausible role in the global task

7. NEEDS — MOST IMPORTANT

A NEED represents a genuine dependency of THIS ROBOT'S OWN
contribution.

Before creating a NEED, identify:

A. What specific contribution am I making to the GLOBAL TASK?

B. What item or task, if missing, would prevent ME from completing
   that contribution?

Only create a NEED if the answer to B is YES.

The key rule is:

    "Cannot do X" does NOT mean "Need X".

A capability limitation becomes a NEED ONLY when that limitation
blocks something THIS ROBOT is actually trying to accomplish.

BAD EXAMPLE:

Global task:
"Prepare the living room for exercise."

Robot:
"Light-duty robot working in the bedroom."

Robot cannot move heavy furniture.

DO NOT create:

{{
  "kind": "task",
  "object": "heavy furniture",
  "location": "living room",
  "action": "move"
}}

Why?
The robot is not responsible for moving the living-room furniture,
and its own contribution does not depend on that action.

GOOD EXAMPLE:

Robot's own contribution:
"Retrieve an object from behind a heavy table."

The heavy table blocks the robot's own required action.

Then:

{{
  "kind": "task",
  "object": "heavy table",
  "location": "living room",
  "action": "move"
}}

is a valid NEED because the robot's own contribution is impossible
without that external action.

8. NEEDS — STRICT PROHIBITIONS

DO NOT create a NEED:

- merely because the action appears in the GLOBAL TASK
- merely because another robot is capable of doing it
- merely because YOU cannot do it
- merely because the action occurs in another room
- merely because the action would make the overall task easier
- merely because the action is difficult
- merely because another robot may need it
- for work that belongs entirely to another robot
- for an unrelated object
- for an unrelated room
- by restating the GLOBAL TASK

A NEED must be a dependency of YOUR OWN contribution.

If your own contribution can be completed without help:
return NO NEED.

9. CROSS-ROOM DEPENDENCY

Do not create a NEED for an action in another room unless there is
an explicit dependency between that action and THIS ROBOT'S OWN
contribution.

The existence of an unfinished task in another room is NOT a dependency.

For example:

Robot A:
- works in bedroom
- carries a light object to the living room

Robot A does NOT need another robot to move heavy furniture in
the living room unless the heavy furniture actually blocks Robot A's
specific contribution.

10. CAN_PROVIDE VS NEEDS

Keep these concepts separate.

CAN_PROVIDE means:

"What useful capability or resource can I offer to the team?"

NEEDS means:

"What do I genuinely require from another robot to complete MY OWN
contribution?"

Do not turn every CAN_PROVIDE capability into a NEED.

Do not turn every CANNOT_DO limitation into a NEED.

11. NO TASK ASSIGNMENT

The OFFER does NOT decide collaboration.

Do NOT:
- assign a specific robot
- decide who should help whom
- assume another robot will perform an action
- create a task for another robot simply because you cannot perform it

The actual collaboration relations are constructed later during
Local Planning, Auction, and Graph Reasoning.

12. FINAL SELF-CHECK

Before returning the OFFER, check every entry.

CAN_DO:
- Is it directly relevant to the GLOBAL TASK?
- Can I physically perform it?

CANNOT_DO:
- Is this limitation directly relevant to MY contribution?
- Would this limitation actually affect my ability to contribute?

CAN_PROVIDE:
- Is this resource/task useful for the GLOBAL TASK?
- Can I physically provide it?

NEEDS:
- What exactly is MY contribution?
- Does this item/task directly block MY contribution?
- Could I complete MY contribution without it?
  - YES -> DELETE the NEED.
  - NO -> KEEP the NEED.

FINAL CHECK:

If you find yourself thinking:

"I cannot do X, so I need someone else to do X."

STOP.

Ask instead:

"Am I actually responsible for accomplishing something that
cannot be completed without X?"

If NO -> do not create a NEED.

When uncertain, OMIT the entry rather than inventing a dependency.

13. OUTPUT

Return JSON only.
"""


# ===========================================================================
# User prompt
# ===========================================================================

def build_offer_user(inp: AgentInput) -> str:

    hidden = (
        "\n".join(
            f"- {h}"
            for h in inp.hidden_info
        )
        or "- (none)"
    )

    return (
        f"TASK:\n{inp.task}\n\n"
        f"CAPABILITY:\n{inp.capability}\n\n"
        f"HIDDEN INFO:\n{hidden}\n\n"
        "The attached images show your own room.\n\n"

        "IMPORTANT:\n"
        "Construct the OFFER only for information relevant to "
        "YOUR OWN contribution to the TASK.\n"
        "Do not treat the GLOBAL TASK as a list of tasks you personally "
        "must perform.\n"
        "Do not create a NEED simply because you cannot perform an action.\n"
        "A NEED is valid only when that missing item or external task "
        "actually blocks YOUR OWN contribution.\n\n"

        "Base OBS_SCOPE on your own observations and HIDDEN INFO.\n"
        "For CAN_DO and CAN_PROVIDE, consider only task-relevant actions "
        "and resources.\n"
        "For CANNOT_DO, include only limitations that affect your "
        "task-relevant contribution.\n"
        "For NEEDS, identify genuine dependencies of your own contribution."
    )


# ===========================================================================
# Main
# ===========================================================================

async def make_offer(agent: Agent) -> Offer:

    raw: RawOffer = await agent.ask(
        "offer",
        OFFER_SYSTEM,
        build_offer_user(agent.inp),
        RawOffer.model_validate,
        banner_label="OFFER RAW",
    )

    # -----------------------------------------------------------------------
    # Deterministic filtering of non-transferable items
    # -----------------------------------------------------------------------

    kept_provide = [
        p
        for p in raw.can_provide
        if _is_passable(p)
    ]

    dropped_provide = [
        p
        for p in raw.can_provide
        if not _is_passable(p)
    ]

    if dropped_provide:

        agent.log.log(
            "offer",
            agent.id,
            "can_provide_filtered",
            dropped=[
                p.model_dump()
                for p in dropped_provide
            ],
        )

        if agent.verbose:
            print(
                f"  [OFFER FILTER] {agent.id}: "
                f"non-passable items dropped: "
                f"{[p.model_dump() for p in dropped_provide]}"
            )

    raw = raw.model_copy(
        update={
            "can_provide": kept_provide,
        }
    )

    # -----------------------------------------------------------------------
    # Attach agent ID
    # -----------------------------------------------------------------------

    agent.offer = Offer(
        agent=agent.id,
        **raw.model_dump(),
    )

    if agent.verbose and agent.offer.reasoning:
        print(f"  [OFFER REASONING] {agent.id}: {agent.offer.reasoning}")

    if agent.verbose:
        print(
            f"  [OFFER] {agent.id}: "
            f"obs_scope={len(agent.offer.obs_scope)} "
            f"can_do={len(agent.offer.can_do)} "
            f"cannot_do={len(agent.offer.cannot_do)} "
            f"can_provide={len(agent.offer.can_provide)} "
            f"needs={len(agent.offer.needs)}"
        )

    agent.log.log(
        "offer",
        agent.id,
        "offer_made",
        n_needs=len(agent.offer.needs),
        n_provide=len(agent.offer.can_provide),
    )

    agent.bus.broadcast(
        agent.id,
        "offer",
        agent.offer.model_dump(),
        phase="offer",
    )

    return agent.offer
