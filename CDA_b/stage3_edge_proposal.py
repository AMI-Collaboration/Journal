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
from .log import EventLog
from .prompts import PROPOSE_USER, _j, indexed, propose_system
from .schemas import (ASK_HELP, HELP, HELP_EDGE, LOCAL, MUTUAL, PASS, PROVIDER_FOR, PROVIDER_ONLY,
                      RECEIVE, REQUEST_TYPES, TRANSFER, Edge, Node, Offer, TaskConfig, action_str,
                      agent_num, match_item, norm)


def _plan_view(nodes: list[Node]) -> list[dict]:
    return [{"id": n.id, "type": n.type, "text": n.text(), "target": n.target} for n in nodes]


def _int(x):
    return x if isinstance(x, int) and not isinstance(x, bool) else (
        int(x) if isinstance(x, str) and x.strip().isdigit() else None)


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
            rec.update(result="CANDIDATE", kappa=kappa, provider=node.id)
            record.append(rec)
            log.log("propose", agent, "yes", request=x.id, provider=node.id, kappa=kappa)

    # a named robot that did not answer at all: keep that visible on the node
    for x in requests + passes:
        tgt = x.target
        if tgt in cfg.ids and (tgt, x.id) not in answered:
            x.replies.append({"agent": tgt, "answer": "NO ANSWER", "reason": ""})
    return edges, record
