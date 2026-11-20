"""Stage 3 - Edge Proposal. Requests (ASK_HELP, RECEIVE) are shown to every other robot; a PASS offer
is shown to its target. Every robot, in parallel, answers each one with YES or NO (+ reason).

YES to a request    -> a new HELP / PASS step in the answering robot's own plan, born with
                       answers=<request id> (pairing by id, never by text); or, with existing_step,
                       an edge from a step the robot already has (no new step).
YES to a PASS offer -> a RECEIVE step (+ a LOCAL use step only if the robot wrote one).
NO / no answer      -> no edge; the reason is kept on the request / offer node.

Consent label κ, set by code:
    mutual         the request named me (or the offer was made to me) and I said YES
    provider-only  I volunteered for a request that named another robot
    (a PASS offer nobody took stays an "open offer" node: provider-only, no edge yet)
Several robots may answer YES to one request, and one robot may promise its item to several
requests: all of them stay candidates. Stage 4.2 decides.

Code checks FORMAT only: can_do index, item in own has_items, a fixed robot does not leave its room,
two fixed robots do not exchange objects. Nothing is dropped or blocked here.
"""
from __future__ import annotations

import asyncio

from .llm import BaseLLM
from .core import (ASK_HELP, HELP, HELP_EDGE, LOCAL, MUTUAL, PASS, PROVIDER_FOR, PROVIDER_ONLY,
                      RECEIVE, REQUEST_TYPES, TRANSFER, Edge, EventLog, Node, Offer, ObjectState, TaskConfig,
                      _j, action_str, agent_num, indexed, match_item, norm)


# ================================================================================================
# PROMPTS — Stage 3 Edge Proposal
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


def propose_system(agent: str) -> str:
    return PROPOSE_SYSTEM.format(agent=agent)


# ================================================================================================
# CODE — Stage 3 Edge Proposal
# ================================================================================================


def _plan_view(nodes: list[Node]) -> list[dict]:
    return [{"id": n.id, "type": n.type, "text": n.text(), "target": n.target} for n in nodes]


def _int(x):
    return x if isinstance(x, int) and not isinstance(x, bool) else (
        int(x) if isinstance(x, str) and x.strip().isdigit() else None)


def meets_condition(agent_id: str, cfg: TaskConfig, offers: dict[str, Offer], condition: dict) -> bool:
    """ASK_HELP no longer names a robot; this checks whether `agent_id` has the capability the
    requester's 'condition' describes (mobile / a can_do_keyword). No numeric weight check: no
    object in this project has a real kg value, so a payload_kg comparison would just be two
    made-up numbers compared against each other -- MANIPULATE_HEAVY vs MANIPULATE_LIGHT is the only
    grounded signal we actually have for lift capacity. can_do_keyword is exact membership in
    CAPABILITY_TAGS (a shared, fixed vocabulary), checked against that robot's own Offer.capability_tags
    -- not a free-text can_do substring search, which only matched when two robots happened to phrase
    the same ability identically. mobile comes from the static profile."""
    profile = cfg.agent(agent_id).profile
    if condition.get("mobile") is not None and profile.mobile != condition["mobile"]:
        return False
    if condition.get("can_do_keyword"):
        keyword = str(condition["can_do_keyword"]).strip().upper()
        tags = offers[agent_id].capability_tags if agent_id in offers else []
        if keyword not in tags:
            return False
    return True


def propagate_effects(env_state: list[ObjectState], effects: list[dict]) -> None:
    """A request's declared effects, once a provider is confirmed, update the requester's own
    env_state snapshot in place so later reads (Stage 4) see the resulting state, not stale S0."""
    for eff in effects or []:
        obj_id, field, value = eff.get("object_id"), eff.get("field"), eff.get("value")
        if not obj_id or field not in ("location", "toggle", "clean"):
            continue
        for obj in env_state:
            if obj.object_id == obj_id:
                setattr(obj, field, value)


async def _answer(cfg: TaskConfig, agent: str, plans: dict[str, list[Node]], offers: dict[str, Offer],
                  requests: list[Node], passes: list[Node], llm: BaseLLM, log: EventLog) -> list[dict]:
    visible = [r for r in requests if r.agent != agent]
    to_me = [p for p in passes if p.target == agent]
    if not visible and not to_me:
        log.log("propose", agent, "skip_nothing_to_answer")
        return []
    user = PROPOSE_USER.format(
        task=cfg.task, own_offer=_j(offers[agent].to_dict()), can_do_indexed=indexed(offers[agent].can_do),
        own_plan=_j(_plan_view(plans[agent])),
        requests=_j([r.brief() | {"location": r.location} for r in visible]) if visible else "(none)",
        offers=_j([p.brief() | {"for": p.serves_text} for p in to_me]) if to_me else "(none)")
    d = await llm.complete(propose_system(agent), user, key=f"propose:{agent}")
    ans = d.get("answers", []) or []
    log.log("propose", agent, "answered", n=len(ans),
            yes=sum(str(a.get("answer", "")).upper() == "YES" for a in ans if isinstance(a, dict)))
    return [a for a in ans if isinstance(a, dict)]


def _insert(order: list[Node], node: Node, after) -> None:
    if not after or str(after).upper() == "START":
        order.insert(0, node)
        return
    for i, n in enumerate(order):
        if n.id == after:
            order.insert(i + 1, node)
            return
    order.append(node)       # unknown anchor -> end of own plan


async def edge_proposal(cfg: TaskConfig, plans: dict[str, list[Node]], offers: dict[str, Offer],
                        llm: BaseLLM, log: EventLog) -> tuple[list[Edge], list[dict]]:
    """Mutates `plans` (inserts provider / RECEIVE steps). Returns candidate edges and an answer record."""
    requests = [n for a in cfg.ids for n in plans[a] if n.type in REQUEST_TYPES]
    passes = [n for a in cfg.ids for n in plans[a] if n.type == PASS and n.origin == "offer"]
    by_id = {n.id: n for n in requests + passes}
    raw = await asyncio.gather(*[_answer(cfg, a, plans, offers, requests, passes, llm, log) for a in cfg.ids])

    edges: list[Edge] = []
    record: list[dict] = []
    counters = {a: max([int(n.id.split("_s")[1]) for n in plans[a]] or [0]) for a in cfg.ids}

    def new_id(a: str) -> str:
        counters[a] += 1
        return f"r{agent_num(a)}_s{counters[a]}"

    answered: set[tuple[str, str]] = set()
    for agent, answers in zip(cfg.ids, raw):
        me = cfg.agent(agent)
        own = offers[agent]
        for a in answers:
            xid = str(a.get("id") or a.get("request") or a.get("offer") or "")
            x = by_id.get(xid)
            yes = str(a.get("answer", a.get("decision", ""))).upper().strip() in ("YES", "ACCEPT", "VOLUNTEER", "RECEIVE")
            rec = {"agent": agent, "id": xid, "answer": "YES" if yes else "NO", "reason": str(a.get("reason", ""))}
            if x is None or x.agent == agent or (agent, xid) in answered or \
                    (x.type == PASS and x.target != agent):
                rec["result"] = "invalid id (not something you were asked)"
                record.append(rec)
                continue
            answered.add((agent, xid))
            if not yes:
                x.replies.append({"agent": agent, "answer": "NO", "reason": rec["reason"]})
                rec["result"] = "no edge"
                record.append(rec)
                continue

            problem = None
            # ---------------- YES to a PASS offer made to me: RECEIVE (+ optional use step)
            if x.type == PASS:
                if cfg.mover(x.agent, agent) is None:
                    problem = f"{x.agent} and {agent} are both fixed"
                if problem:
                    rec["result"] = f"rejected_by_format_check: {problem}"
                    x.replies.append({"agent": agent, "answer": "YES (format error)", "reason": problem})
                    record.append(rec)
                    continue
                rcv = Node(id=new_id(agent), agent=agent, type=RECEIVE, item=x.item,
                           action=f"receive {x.item}", target=x.agent, location=me.profile.room,
                           origin="receive", serves_text=f"offered {x.item}")
                _insert(plans[agent], rcv, a.get("insert_after"))
                use_action = action_str(a.get("use_action") or "")
                uses = _int(a.get("uses"))
                use = None
                if use_action and not norm(use_action).startswith("receive") and \
                        uses is not None and 0 <= uses < len(own.can_do):
                    use = Node(id=new_id(agent), agent=agent, type=LOCAL, action=use_action, uses=uses,
                               location=me.profile.room, origin="receive", serves_text=f"offered {x.item}")
                    plans[agent].insert(plans[agent].index(rcv) + 1, use)
                    rcv.enables = use.id
                edges.append(Edge(x.id, rcv.id, TRANSFER, MUTUAL))
                rec.update(result="CANDIDATE", kappa=MUTUAL, receive=rcv.id, use=use.id if use else None)
                record.append(rec)
                log.log("propose", agent, "offer_taken", offer=x.id, receive=rcv.id)
                continue

            # ---------------- YES to a request
            if x.type == ASK_HELP:
                kappa = MUTUAL if meets_condition(agent, cfg, offers, x.condition or {}) else PROVIDER_ONLY
            else:
                kappa = MUTUAL if x.target == agent else PROVIDER_ONLY
            kind = HELP_EDGE if x.type == ASK_HELP else TRANSFER
            ex = str(a.get("existing_step") or a.get("covered_by") or "")
            if ex:
                own_ids = {n.id: n for n in plans[agent]}
                want = (LOCAL, HELP) if x.type == ASK_HELP else (PASS,)
                if ex not in own_ids or own_ids[ex].type not in want:
                    problem = f"existing_step '{ex}' is not one of your {'/'.join(want)} steps"
                elif any(e.key == (ex, x.id) for e in edges):
                    problem = "already linked"
                if not problem:
                    edges.append(Edge(ex, x.id, kind, kappa, existing=True))
                    propagate_effects(offers[x.agent].env_state, x.effects)
                    rec.update(result="CANDIDATE", kappa=kappa, provider=ex, existing=True)
                    record.append(rec)
                    log.log("propose", agent, "yes_existing", request=x.id, provider=ex, kappa=kappa)
                    continue
            elif x.type == ASK_HELP:
                uses = _int(a.get("uses"))
                if not (uses is not None and 0 <= uses < len(own.can_do)):
                    problem = f"uses={a.get('uses')} is not a valid can_do index"
                elif not me.profile.mobile and norm(x.location) != norm(me.profile.room):
                    problem = f"a fixed robot cannot leave the {me.profile.room} to help in the {x.location}"
                if not problem:
                    node = Node(id=new_id(agent), agent=agent, type=HELP,
                                action=action_str(a.get("action")) or action_str(x.action), target=x.agent,
                                uses=uses, location=x.location,
                                origin="accept" if kappa == MUTUAL else "volunteer", answers=x.id)
            else:   # RECEIVE
                item = match_item(a.get("item") or x.item, own.has_items)
                if item is None:
                    problem = f"item '{a.get('item') or x.item}' is not in your has_items"
                elif cfg.mover(agent, x.agent) is None:
                    problem = f"{agent} and {x.agent} are both fixed: nobody can move the object"
                if not problem:
                    node = Node(id=new_id(agent), agent=agent, type=PASS, item=item,
                                action=action_str(a.get("action")) or f"pass {item} to {x.agent}",
                                target=x.agent, location=me.profile.room,
                                origin="accept" if kappa == MUTUAL else "volunteer", answers=x.id)
            if problem:
                rec["result"] = f"rejected_by_format_check: {problem}"
                x.replies.append({"agent": agent, "answer": "YES (format error)", "reason": problem})
                record.append(rec)
                log.log("propose", agent, "yes_rejected_by_format_check", request=x.id)
                continue
            _insert(plans[agent], node, a.get("insert_after"))
            edges.append(Edge(node.id, x.id, kind, kappa))
            propagate_effects(offers[x.agent].env_state, x.effects)
            rec.update(result="CANDIDATE", kappa=kappa, provider=node.id)
            record.append(rec)
            log.log("propose", agent, "yes", request=x.id, provider=node.id, kappa=kappa)

    # a named robot that did not answer at all: keep that visible on the node
    for x in requests + passes:
        tgt = x.target
        if tgt in cfg.ids and (tgt, x.id) not in answered:
            x.replies.append({"agent": tgt, "answer": "NO ANSWER", "reason": ""})
    return edges, record
