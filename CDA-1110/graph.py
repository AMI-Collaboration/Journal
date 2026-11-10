"""Plan graph for Stage 4 (Graph-based Plan Alignment, design v4).

Nodes = steps. Edges = "src must finish before dst can finish".
    SEQ       consecutive active steps of the same robot (from each robot's own order)
    TRANSFER  PASS -> RECEIVE (or -> an existing step that needs the object, via SELECT of an open offer)
    HELP      HELP / existing step -> ASK_HELP
    ORDER     added by the Graph LLM: a step of one robot before a step of ANOTHER robot

Who does what
    4.1 build + labels                      code   (this file)
    4.2 edits + coverage judgment           Graph LLM (one call, stage4_graph_reasoning.py)
    4.3 admissibility check, edge finalize  code   apply_edit / finalize_edges
    4.4 dependency closure                  code   closure
    4.5 scheduling                          code   schedule
    4.6 report finalization                 code   finalize_report
Rules check structure only (ids, consent label, robot boundary, cycles). They never judge meaning.
"""
from __future__ import annotations

import math

import networkx as nx

from .schemas import (ASK_HELP, CONFIRMED, HELP, HELP_EDGE, LOCAL, MERGED, MUTUAL, ORDER, PASS,
                      PHASE_MIN, PROPOSED, PROVIDER_ONLY, RECEIVE, REQUEST_TYPES, SEQ, SIZE_MIN,
                      TRANSFER, Edge, Node, Offer, TaskConfig)

OPS = ("SELECT", "MERGE", "DROP", "ORDER")
ANSWER_ORIGINS = ("accept", "volunteer", "offer")   # provider steps that exist only for a collaboration


class PlanGraph:
    def __init__(self, cfg: TaskConfig, plans: dict[str, list[Node]], collab: list[Edge],
                 offers: dict[str, Offer] | None = None, record: list[dict] | None = None):
        self.cfg = cfg
        self.offers = offers or {}
        self.record = record or []
        self.nodes: dict[str, Node] = {n.id: n for a in cfg.ids for n in plans[a]}
        self.order: dict[str, list[str]] = {a: [n.id for n in plans[a]] for a in cfg.ids}
        self.collab: dict[tuple[str, str], Edge] = {e.key: e for e in collab}
        self.order_edges: list[Edge] = []
        self._initial_nodes = set(self.nodes)
        self.n_candidates = len(collab)
        # 4.2 / 4.3
        self.selected: dict[str, str] = {}       # request (or offer target step) id -> provider id
        self.merged: dict[str, str] = {}         # request id -> existing step id
        self.edit_log: list[dict] = []
        self.coverage_raw: list = []
        # 4.3 - 4.6
        self.unresolved: dict[str, str] = {}     # request id -> why no edge was confirmed
        self.removals: list[dict] = []           # 4.4 closure
        self.drops: list[dict] = []              # 4.2 DROP
        self.invariant_violations: list[str] = []
        self.n_reordered = 0
        self.report: dict = {}

    # ============================================================ basic views
    def active(self, nid: str | None) -> bool:
        return nid in self.nodes and self.nodes[nid].status == "active"

    def seq_edges(self) -> list[Edge]:
        out = []
        for ids in self.order.values():
            act = [i for i in ids if self.active(i)]
            out += [Edge(a, b, SEQ, status=CONFIRMED, source="local") for a, b in zip(act, act[1:])]
        return out

    def candidates(self, rid: str) -> list[Edge]:
        """YES-edges from Stage 3 into a request whose provider is still active."""
        return [e for e in self.collab.values() if e.dst == rid and e.source == "stage3" and self.active(e.src)]

    def executing(self) -> list[Edge]:
        """Collaboration edges confirmed in 4.3 whose both ends are still active."""
        return [e for e in self.collab.values()
                if e.status == CONFIRMED and self.active(e.src) and self.active(e.dst)]

    def providers_of(self, rid: str) -> list[Edge]:
        return [e for e in self.executing() if e.dst == rid]

    def open_offers(self) -> list[Node]:
        return [n for n in self.nodes.values() if self.active(n.id) and n.type == PASS and n.origin == "offer"
                and not any(e.src == n.id for e in self.collab.values())]

    def _digraph(self, collab: list[Edge]) -> nx.DiGraph:
        g = nx.DiGraph()
        g.add_nodes_from(i for i in self.nodes if self.active(i))
        for e in self.seq_edges() + collab + [o for o in self.order_edges
                                              if self.active(o.src) and self.active(o.dst)]:
            if self.active(e.src) and self.active(e.dst):
                g.add_edge(e.src, e.dst, kind=e.kind)
        return g

    def nx(self) -> nx.DiGraph:
        return self._digraph(self.executing())

    # ============================================================ 4.1 labels + view for the Graph LLM
    def cycle_nodes(self) -> set[str]:
        """Steps on a cycle if every YES-candidate were executed (an informative label only)."""
        g = self._digraph([e for e in self.collab.values()])
        return {n for comp in nx.strongly_connected_components(g) if len(comp) > 1 for n in comp}

    def graph_view(self) -> dict:
        in_cycle = self.cycle_nodes()
        plans = {}
        for a, ids in self.order.items():
            steps = []
            for i in ids:
                if not self.active(i):
                    continue
                n = self.nodes[i]
                d = n.brief()
                if n.serves is not None:
                    d["serves"] = n.serves
                elif n.serves_text:
                    d["serves"] = n.serves_text
                if n.type in REQUEST_TYPES:
                    c = self.candidates(i)
                    d["candidates"] = [{"provider": e.src, "robot": self.nodes[e.src].agent, "kappa": e.kappa,
                                        **({"existing_step": True} if e.existing else {})} for e in c]
                    if not c:
                        d["no_candidate"] = True
                    if n.enables:
                        d["enables"] = n.enables
                if n.answers:
                    d["answers"] = n.answers
                if n.replies:
                    d["replies"] = n.replies
                if i in in_cycle:
                    d["in_cycle"] = True
                steps.append(d)
            plans[a] = steps
        edges = [{"provider": e.src, "request": e.dst, "kind": e.kind, "kappa": e.kappa}
                 for e in self.collab.values() if self.active(e.src) and self.active(e.dst)]
        open_offers = [{"offer": n.id, "robot": n.agent, "item": n.item, "target": n.target,
                        "kappa": PROVIDER_ONLY, "replies": n.replies} for n in self.open_offers()]
        offers = {a: {k: v for k, v in o.to_dict().items() if k not in ("obs_scope", "reasoning")}
                  for a, o in self.offers.items()}
        return {"offers": offers, "plans": plans, "edges": edges, "open_offers": open_offers}

    # ============================================================ 4.3 (1) admissibility of one edit
    def projected(self) -> list[Edge]:
        """The collaboration edges that would run if we finalized now (selections + default policy)."""
        out = []
        for rid, r in self.nodes.items():
            if not self.active(rid):
                continue
            if rid in self.merged and self.active(self.merged[rid]):
                out.append(self.collab[(self.merged[rid], rid)])
            elif rid in self.selected and self.active(self.selected[rid]) and (self.selected[rid], rid) in self.collab:
                out.append(self.collab[(self.selected[rid], rid)])
            elif r.type in REQUEST_TYPES:
                c = self.candidates(rid)
                if len(c) == 1 and c[0].kappa == MUTUAL:
                    out.append(c[0])
        return out

    def _cyclic(self) -> bool:
        return not nx.is_directed_acyclic_graph(self._digraph(self.projected()))

    def apply_edit(self, op: dict) -> str | None:
        """Apply one Graph LLM edit, or return why it is rejected (structure only, no retry)."""
        if not isinstance(op, dict):
            return "edit is not an object"
        kind = str(op.get("op") or op.get("operation") or op.get("type") or "").upper().strip()
        if kind not in OPS:
            return f"unknown op '{kind}' (allowed: {', '.join(OPS)})"

        def need(*keys) -> tuple[list[str], str | None]:
            ids = [str(op.get(k) or "") for k in keys]
            for k, i in zip(keys, ids):
                if i not in self.nodes:
                    return ids, f"{k} '{i}' does not exist"
                if not self.active(i):
                    return ids, f"{k} '{i}' was already removed (by an earlier edit)"
            return ids, None

        if kind == "SELECT":
            (p, r), err = need("provider", "request")
            if err:
                return err
            e = self.collab.get((p, r))
            created = False
            if e is None:
                pn, rn = self.nodes[p], self.nodes[r]
                if pn in self.open_offers() and pn.target == rn.agent and rn.type != PASS:
                    e = Edge(p, r, TRANSFER, PROVIDER_ONLY, source="graph")   # open offer -> existing step
                    self.collab[e.key] = e
                    created = True
                else:
                    return f"'{p}' -> '{r}' is not a YES candidate (SELECT only among agreed edges)"
            elif e.kappa not in (MUTUAL, PROVIDER_ONLY):
                return f"edge '{p}' -> '{r}' has no provider consent"
            prev = self.selected.get(r)
            self.selected[r] = p
            if self._cyclic():
                self.selected.pop(r) if prev is None else self.selected.__setitem__(r, prev)
                if created:
                    self.collab.pop(e.key)
                return "this selection creates a dependency cycle"
            return None

        if kind == "MERGE":
            (r, into), err = need("request", "into")
            if err:
                return err
            rn, xn = self.nodes[r], self.nodes[into]
            if rn.type not in REQUEST_TYPES:
                return f"'{r}' is not a request (ASK_HELP / RECEIVE)"
            if xn.agent == rn.agent:
                return "MERGE needs a step of another robot"
            if xn.type not in (LOCAL, HELP, PASS):
                return f"'{into}' must be a LOCAL / HELP / PASS step"
            key = (into, r)
            existed = key in self.collab
            if not existed:
                self.collab[key] = Edge(into, r, HELP_EDGE if rn.type == ASK_HELP else TRANSFER, MERGED,
                                        source="graph")
            prev = self.merged.get(r)
            self.merged[r] = into
            if self._cyclic():
                self.merged.pop(r) if prev is None else self.merged.__setitem__(r, prev)
                if not existed:
                    self.collab.pop(key)
                return "this merge creates a dependency cycle"
            return None

        if kind == "DROP":
            (nid,), err = need("node")
            if err:
                return err
            n = self.nodes[nid]
            n.status, n.status_reason = "dropped", "4.2 DROP: " + str(op.get("rationale", ""))
            self.drops.append({"node": nid, "agent": n.agent, "type": n.type, "text": n.text(),
                               "rationale": str(op.get("rationale", ""))})
            return None

        # ORDER
        (a, b), err = need("before", "after")
        if err:
            return err
        if self.nodes[a].agent == self.nodes[b].agent:
            return "ORDER is only between different robots (a robot's own order is fixed)"
        e = Edge(a, b, ORDER, status=CONFIRMED, source="graph")
        self.order_edges.append(e)
        if self._cyclic():
            self.order_edges.remove(e)
            return "this order creates a dependency cycle"
        return None

    # ============================================================ 4.3 (2)+(3) edge finalization
    def finalize_edges(self) -> None:
        for e in self.projected():
            e.status = CONFIRMED
            e.decided_by = ("MERGE" if self.merged.get(e.dst) == e.src else
                            "SELECT" if self.selected.get(e.dst) == e.src else "default")
        for rid, r in self.nodes.items():
            if not self.active(rid) or r.type not in REQUEST_TYPES or self.providers_of(rid):
                continue
            c = self.candidates(rid)
            if not c:
                why = "no candidate (nobody said YES)"
            elif len(c) > 1:
                why = f"{len(c)} candidates, none selected"
            else:
                why = "single provider-only candidate, not selected"
            self.unresolved[rid] = why
        self.check_invariants()

    def check_invariants(self) -> None:
        """Recorded, never raised: the pipeline does not stop."""
        if not set(self.nodes) <= self._initial_nodes:
            self.invariant_violations.append("I1: a step was created in Stage 4")
        for e in self.executing():
            if e.kappa not in (MUTUAL, PROVIDER_ONLY, MERGED):
                self.invariant_violations.append(f"I1: edge {e.src}->{e.dst} has no consent label")
        if not nx.is_directed_acyclic_graph(self.nx()):
            self.invariant_violations.append("I3: the graph has a cycle after 4.3 (cleaned up in 4.4)")

    # ============================================================ 4.4 dependency closure
    def _remove(self, nid: str, why: str, queue: list) -> None:
        n = self.nodes.get(nid)
        if n is None or n.status != "active":
            return
        n.status, n.status_reason = "removed", why
        self.removals.append({"node": nid, "agent": n.agent, "type": n.type, "text": n.text(), "reason": why})
        queue.append(nid)

    def _propagate(self, queue: list) -> None:
        while queue:
            nid = queue.pop()
            n = self.nodes[nid]
            # a request that will not be served: the own step it enables cannot run (RECEIVE included)
            if n.type in REQUEST_TYPES and n.enables:
                self._remove(n.enables, f"needs {nid}, which will not happen", queue)
            # a step that served other robots: their requests lose this provider
            for e in [e for e in self.collab.values() if e.src == nid and e.status == CONFIRMED]:
                if self.active(e.dst) and not self.providers_of(e.dst):
                    self._remove(e.dst, f"its provider {nid} was removed", queue)
            # requests that existed only to enable this step are moot, and so are their answer-only providers
            for r in [r for r in self.nodes.values() if r.enables == nid and self.active(r.id)]:
                self._remove(r.id, f"moot: {nid} will not happen", queue)
            # providers that existed only to serve this step (answers / offers) are no longer needed
            for e in [e for e in self.collab.values() if e.dst == nid and e.status == CONFIRMED]:
                p = self.nodes[e.src]
                if self.active(p.id) and p.origin in ANSWER_ORIGINS and not any(
                        x.src == p.id and self.active(x.dst) for x in self.executing()):
                    self._remove(p.id, f"not needed: {nid} will not happen", queue)

    def closure(self) -> None:
        queue: list[str] = []
        for rid, why in self.unresolved.items():                     # unserved requests
            self._remove(rid, "unresolved: " + why, queue)
        for n in list(self.nodes.values()):                          # answers / offers not selected
            if self.active(n.id) and n.origin in ANSWER_ORIGINS and n.type in (HELP, PASS) and \
                    not any(e.src == n.id for e in self.executing()):
                self._remove(n.id, "offer not taken" if n.origin == "offer" else "answer not selected", queue)
        queue += [d["node"] for d in self.drops]                     # dependents of 4.2 DROPs
        self._propagate(queue)
        while True:                                                  # cycles still left
            g = self.nx()
            try:
                cyc = nx.find_cycle(g)
            except nx.NetworkXNoCycle:
                break
            for u, _ in cyc:
                self._remove(u, "on a dependency cycle", queue)
            self._propagate(queue)

    # ============================================================ 4.5 scheduling
    def _wait_late(self) -> None:
        """Move each request to just before the step it enables (WHEN only; content unchanged)."""
        for r in [n for n in self.nodes.values() if n.type in REQUEST_TYPES and self.active(n.id)]:
            if not self.active(r.enables):
                continue
            ids = self.order[r.agent]
            i, j = ids.index(r.id), ids.index(r.enables)
            if j <= i + 1 or not [x for x in ids[i + 1:j] if self.active(x)]:
                continue
            old = list(ids)
            ids.remove(r.id)
            ids.insert(ids.index(r.enables), r.id)
            if not nx.is_directed_acyclic_graph(self.nx()):
                self.order[r.agent] = old
            else:
                self.n_reordered += 1

    def _size(self, n: Node) -> str | None:
        if n.type == ASK_HELP:
            return None
        if n.type == HELP:
            return "medium"
        if n.type == PASS and self.cfg.mover(n.agent, n.target) == n.agent:
            return "medium"
        if n.type == RECEIVE:
            giver = self.providers_of(n.id)
            if giver and self.cfg.mover(self.nodes[giver[0].src].agent, n.agent) == n.agent:
                return "medium"
        return "short"

    def schedule(self) -> None:
        self._wait_late()
        g = self.nx()
        for nid in nx.topological_sort(g):
            n = self.nodes[nid]
            own = [p for p in g.predecessors(nid) if g.edges[p, nid]["kind"] in (SEQ, ORDER)]
            given = [p for p in g.predecessors(nid) if g.edges[p, nid]["kind"] not in (SEQ, ORDER)]
            ready = max([self.nodes[p].t_end for p in own] or [0])
            got = max([self.nodes[p].t_end for p in given] or [0])
            n.size = self._size(n)
            dur = SIZE_MIN.get(n.size, 0)
            if n.type == ASK_HELP:                       # waiting only
                n.t_start, n.t_end = ready, max(ready, got)
            else:
                n.t_start = max(ready, got)
                n.t_end = n.t_start + dur
            n.phase = max(1, math.ceil(n.t_end / PHASE_MIN)) if n.t_end else 1

    def makespan_min(self) -> int:
        ends = [n.t_end for n in self.nodes.values() if self.active(n.id) and n.t_end is not None]
        return int(math.ceil(max(ends or [0]) / PHASE_MIN) * PHASE_MIN)

    # ============================================================ 4.6 report
    def finalize_report(self) -> None:
        judged = {}
        for c in self.coverage_raw if isinstance(self.coverage_raw, list) else []:
            if not isinstance(c, dict):
                continue
            try:
                judged[(str(c.get("robot", "")).upper(), int(c.get("goal")))] = c
            except (TypeError, ValueError):
                continue
        deadline = self.cfg.deadline_min
        goals = []
        for a in self.cfg.ids:
            for gi, text in enumerate(self.offers[a].intends if a in self.offers else []):
                c = judged.get((a, gi))
                row = {"robot": a, "goal": gi, "text": text}
                if c is None:
                    row.update(status="uncovered", cause=["Left unresolved"], evidence=[],
                               note="not judged by the Graph LLM")
                    goals.append(row)
                    continue
                status = str(c.get("status", "")).lower().strip()
                ev = [str(x) for x in (c.get("evidence") or []) if x]
                cause = [str(c["cause"])] if c.get("cause") else []
                note = ""
                if status in ("covered", "partial"):
                    if not ev:
                        status, cause, note = "uncovered", ["Left unresolved"], "judged covered without evidence"
                    else:
                        lost = [x for x in ev if not self.active(x)]
                        if lost:
                            status = "uncovered" if len(lost) == len(ev) else "partial"
                            cause, note = ["Infeasible"], f"evidence gone: {', '.join(lost)}"
                        late = [x for x in ev if self.active(x) and (self.nodes[x].t_end or 0) > deadline]
                        if late:
                            cause.append("Deadline exceeded")
                            note = (note + "; " if note else "") + f"after the deadline: {', '.join(late)}"
                elif status != "uncovered":
                    status, cause, note = "uncovered", cause or ["Left unresolved"], f"unknown status '{status}'"
                if status != "covered" and not cause:
                    cause = ["Left unresolved"]
                row.update(status=status, cause=cause, evidence=ev, note=note,
                           llm_status=c.get("status"), llm_cause=c.get("cause"))
                goals.append(row)
        ms = self.makespan_min()
        self.report = {
            "goals": goals,
            "unresolved_requests": [{"request": rid, "agent": self.nodes[rid].agent, "text": self.nodes[rid].text(),
                                     "why": why, "replies": self.nodes[rid].replies}
                                    for rid, why in self.unresolved.items()],
            "rejected_edits": [x for x in self.edit_log if not x["applied"]],
            "dropped": self.drops,
            "removed_by_closure": self.removals,
            "invariant_violations": self.invariant_violations,
            "deadline": {"makespan_min": ms, "deadline_min": deadline, "exceeded": ms > deadline},
        }

    # ============================================================ export
    def to_dict(self) -> dict:
        from dataclasses import asdict
        return {"nodes": [asdict(n) for n in self.nodes.values()], "order": self.order,
                "edges": [asdict(e) for e in self.seq_edges() + list(self.collab.values()) + self.order_edges],
                "edit_log": self.edit_log, "report": self.report}


__all__ = ["PlanGraph"]
