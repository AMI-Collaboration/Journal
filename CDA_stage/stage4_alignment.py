"""Stage 4 - Graph-based Plan Alignment (graph reasoning).

    4.1 build the plan graph                                    code
        nodes = steps, edges = each robot's order (SEQ) + candidate links from Stage 3
    4.2 walk the graph                                          code
        per request: candidates, flags (fixed robot would move, cycle), the chain of steps that is
        lost if it stays unserved; graph summary (end times, longest chain, objects in several steps)
    4.3 ONE Graph LLM call on the graph written as text         LLM
        graph-level judgments:
          (1) choose links together (several answers to one request, the same object wanted twice)
          (2) weigh the chains: which requests matter most for the task
          (3) find overlapping work: a request already done by another robot's step -> drop it as
              a duplicate (its later steps then survive)
          (4) add cross-robot ORDER edges that no link expresses
    4.4 verify (rules only check, never rewrite)                code
        not a candidate / creates a cycle / provider step used twice / a fixed robot would have to move
        -> rejected and recorded. A request the LLM did not decide stays unresolved.
    4.5 clean up                                                code
        unchosen answer steps are removed; an unserved request is removed together with the step it
        enables (repeated until nothing changes). All recorded.
    4.6 schedule in minutes (5-minute blocks only for output)   code

Ablation use_graph_llm=False ("no graph reasoning"): rules only. For each request, in robot order,
the first answer that passes the rules is taken; no drops, no orders.
"""
from __future__ import annotations

import re

import networkx as nx

from .core import (ASK_HELP, DURATION_MIN, FROM_STAGE3, HELP, HELP_EDGE, LOCAL, ORDER, PASS, PROVIDER_TYPES, RECEIVE,
                   REQUEST_TYPES, SEQ, Edge, EventLog, Node, Offer, Plan, TaskConfig, _j, norm)
from .llm import BaseLLM

# ================================================================================================
# PROMPT
# ================================================================================================
GRAPH_SYSTEM = """You align a multi-robot plan by reasoning over its plan graph.
Every step was written by the robot that will do it. You never create work; you choose links,
remove duplicate steps and add waiting orders.

THE GRAPH (given as text)
- Each robot's steps run top to bottom.
- Under each request (RECEIVE / ASK_HELP) its candidate answers are listed ("answer <id> by R<n>"):
  PASS / HELP steps that other robots offered for it. They appear only there. "needed by" names the step that waits for the request; "if unserved, removed" lists
  every step that disappears if the request gets no link.
- (!) marks a problem the rules found; such a choice will be rejected.
- GRAPH SUMMARY: end time per robot, the longest chain, objects that appear in several steps.

REASON OVER THE WHOLE GRAPH. First write "think" (a few sentences), then decide in this order.
Whatever you put in "keep" is carried out: the other steps of that group are dropped.
0. SAME WORK FIRST: robots wrote their plans at the same time, so the same work often appears
   several times in DIFFERENT robots' plans: two robots doing the same thing (two LOCAL steps),
   several robots requesting the same delivery, a robot doing itself what another robot requests,
   or a request for work another robot already does. List every such group in "same_work"
   (step ids). Then keep ONE step per group and drop the others as duplicates (question 3).
   Several requests for the same delivery are same work too: keep one request.
   A request and the answers to it are NOT same work: they are candidates, decided in question 1.
1. LINKS: for EVERY request choose one candidate or null. Choose links together: one answer step
   serves one request only, one object can be given only once. Check that the answer really gives
   what the request needs. Each candidate shows when its robot and the whole plan would end if it
   were chosen ("R2 ends 8 min, plan 8 min"): spread answers over robots when that ends the plan
   earlier, instead of giving every answer to the same robot.
2. CHAINS: when a request has no good candidate, look at what is lost ("if unserved, removed") and
   at question 3 before giving up.
3. OVERLAP: if a request, or any step, is already done by ANOTHER robot's step, drop it as a
   duplicate (give duplicate_of). A request dropped as a duplicate does not remove the step it
   enabled, so that step stays in the plan; then ALSO add an ORDER from duplicate_of to that step
   (e.g. "arrange the food" must wait until the other robot "places the food").
   - A request that its robot does not really need (the step after it can be done without it)
     can be dropped as "unneeded": the request goes, the step after it stays.
   - If a needed request has no good answer, choose null for it (then the step after it goes too).
   - Never drop a request as a "constraint".
   - "constraint" is only for a robot's own step that breaks its own physical limit.
   - Do NOT drop answer steps that you simply did not choose: they are removed automatically.
4. ORDER: add {"before": id, "after": id} when a step of one robot must wait for a step of ANOTHER
   robot and no link expresses it (e.g. "arrange the table" after another robot "places the food").
5. DEADLINE: if the summary says the plan is over the deadline, remove duplicate work first.

Every decision needs a short reason that refers to the graph (which steps, which chain).

Return JSON:
{"think":"<2-4 sentences: which work appears twice, which requests matter most, which robot is idle>",
 "same_work":[{"steps":["<id>","<id>"],"keep":"<id>","what":"..."}],
 "choices":[{"request":"<id>","edge":"<answer id>-><request id>" or null,"reason":"..."}],
 "drops":[{"step":"<id>","reason":"duplicate"|"unneeded"|"constraint","duplicate_of":"<id or null>","why":"..."}],
 "orders":[{"before":"<id>","after":"<id>","reason":"..."}]}"""

GRAPH_USER = """TASK: {task}
DEADLINE: {deadline} minutes

{graph}"""


# ================================================================================================
# GRAPH
# ================================================================================================
class PlanGraph:
    def __init__(self, cfg: TaskConfig, plans: dict[str, Plan], cand: dict[tuple[str, str], Edge]):
        self.cfg = cfg
        self.plans = plans
        self.nodes: dict[str, Node] = {nid: n for p in plans.values() for nid, n in p.nodes.items()}
        self.cand = cand
        self.chosen: dict[str, Edge] = {}          # request id -> chosen collaboration edge
        self.orders: list[Edge] = []
        self.rejected: list[dict] = []             # LLM outputs rejected by the rules
        self.decisions: list[dict] = []            # per request: what happened and why
        self.drops: list[dict] = []
        self.removed: list[dict] = []              # removed in cleanup
        self.unresolved: dict[str, str] = {}       # request id -> cause
        self.violations: list[str] = []
        self.choice_rejected: dict[str, str] = {}  # request id -> why the Graph LLM's choice was rejected
        self.ignored: list[dict] = []              # LLM outputs about steps it dropped itself (not errors)
        self.analysis: dict = {}
        self.coverage: list[dict] = []
        self.report: dict = {}
        self.vocab: set[str] = set()               # object names from the offers (for the overlap hint)

    # ------------------------------------------------------------ basics
    def active(self, nid: str) -> bool:
        return nid in self.nodes and self.nodes[nid].status == "active"

    # Timing model -------------------------------------------------------------------------------
    # Every step takes 1 minute (ASK_HELP 0: it only marks "I need help here").
    # A robot does one step at a time. Only these dependencies make a step wait:
    #   - a robot's LOCAL steps keep the order it wrote them in
    #   - an ASK_HELP comes after the robot's LOCAL step before it ("help me now")
    #   - the step a request enables waits for the request (no enables: the next LOCAL step waits)
    #   - PASS -> RECEIVE, and ASK_HELP -> HELP -> the step the request enables
    #   - a PASS waits for the giver's own step named in "after" (e.g. "make the salad")
    #   - ORDER edges from the Graph LLM
    # While a robot waits for a RECEIVE / ASK_HELP it keeps doing other ready steps, and it answers
    # other robots (PASS / HELP) as soon as they are ready, before its own LOCAL work.

    def need_of(self, rid: str) -> str | None:
        """The step that waits for request `rid`: its enables, else the robot's next LOCAL step."""
        r = self.nodes[rid]
        if r.enables and self.active(r.enables):
            return r.enables
        order = self.plans[r.agent].order
        return next((i for i in order[order.index(rid) + 1:]
                     if self.active(i) and self.nodes[i].type == LOCAL), None)

    def seq_edges(self) -> list[Edge]:
        """Dependencies inside one robot (see the timing model above)."""
        out = []
        for p in self.plans.values():
            ids = [i for i in p.order if self.active(i)]
            last_local = None
            for i in ids:
                n = self.nodes[i]
                if n.type == LOCAL:
                    if last_local:
                        out.append(Edge(last_local, i, SEQ))
                    last_local = i
                elif n.type in REQUEST_TYPES:
                    if n.type == ASK_HELP and last_local:
                        out.append(Edge(last_local, i, SEQ))
                    need = self.need_of(i)
                    if need:
                        out.append(Edge(i, need, SEQ))
                elif n.type in PROVIDER_TYPES and n.after and self.active(n.after):
                    out.append(Edge(n.after, i, SEQ))
        return out

    def links(self) -> list[Edge]:
        return [e for e in self.chosen.values() if self.active(e.src) and self.active(e.dst)]

    def edges(self) -> list[Edge]:
        return self.seq_edges() + self.links() + [e for e in self.orders if self.active(e.src) and self.active(e.dst)]

    def expand(self, e: Edge) -> list[tuple[str, str]]:
        """Graph edges of one plan edge. A HELP link: ASK_HELP -> HELP -> the step the request enables.
        Every other edge is just src -> dst."""
        if e.kind == HELP_EDGE and self.nodes[e.src].type == HELP:
            out = [(e.dst, e.src)]
            need = self.need_of(e.dst)
            if need:
                out.append((e.src, need))
            return out
        return [(e.src, e.dst)]

    def dag(self, extra: list[Edge] | tuple = ()) -> nx.DiGraph:
        g = nx.DiGraph()
        g.add_nodes_from(i for i in self.nodes if self.active(i))
        for e in self.edges() + list(extra):
            for u, v in self.expand(e):
                if self.active(u) and self.active(v) and u != v:
                    g.add_edge(u, v)
        return g

    def times(self, extra: list[Edge] | tuple = ()) -> dict[str, tuple[float, float]] | None:
        """(start, end) of every active step, or None if the dependencies contain a cycle.
        List scheduling: every minute, each free robot starts its best ready step
        (answers to other robots first, then the order it wrote)."""
        g = self.dag(extra)
        if not nx.is_directed_acyclic_graph(g):
            return None
        rank = {nid: (0 if self.nodes[nid].type in PROVIDER_TYPES else 1,
                      self.plans[self.nodes[nid].agent].order.index(nid)) for nid in g.nodes}
        done: dict[str, tuple[float, float]] = {}
        busy_until = {a: 0.0 for a in self.plans}
        t = 0.0
        left = set(g.nodes)
        while left:
            progressed = True
            while progressed:                       # zero-length steps and robots free at time t
                progressed = False
                ready = [n for n in left if all(p in done and done[p][1] <= t for p in g.predecessors(n))]
                for n in sorted(ready, key=lambda x: rank[x]):
                    d = DURATION_MIN[self.nodes[n].type]
                    a = self.nodes[n].agent
                    if d == 0:
                        done[n] = (t, t)
                        left.discard(n)
                        progressed = True
                    elif busy_until[a] <= t:
                        done[n] = (t, t + d)
                        busy_until[a] = t + d
                        left.discard(n)
                        progressed = True
            if left:
                t += 1.0
        return done

    def body_ok(self, e: Edge) -> tuple[bool, str]:
        s, d = self.nodes[e.src], self.nodes[e.dst]
        if s.type == PASS and self.cfg.mover(s.agent, d.agent) is None:
            return False, f"{s.agent} and {d.agent} are both fixed: neither can carry the object"
        if s.type == HELP and not self.cfg.can_help(s.agent):
            return False, f"{s.agent} is fixed: it cannot go to {d.agent}'s room"
        return True, ""

    def candidates_of(self, rid: str) -> list[Edge]:
        return [e for e in self.cand.values() if e.dst == rid and self.active(e.src)]

    # ------------------------------------------------------------ 4.2 analysis
    def analyse(self) -> dict:
        base = self.times() or {}
        if not base:
            self.violations.append("the plans without links already contain a cycle")
        reqs = [n for n in self.nodes.values() if self.active(n.id) and n.type in REQUEST_TYPES]
        provider_wanted: dict[str, list[str]] = {}
        for e in self.cand.values():
            provider_wanted.setdefault(e.src, []).append(e.dst)
        requests = []
        for r in reqs:
            cands = []
            for e in self.candidates_of(r.id):
                ok, why = self.body_ok(e)
                cyc = self.times([e]) is None
                pe = base.get(e.src, (0, 0))[1]
                rs = max(base.get(r.id, (0, 0))[0], pe)
                tt = (self.times([e]) or {}) if ok and not cyc else {}
                pa = self.nodes[e.src].agent
                p_end = max((tt[i][1] for i in self.plans[pa].order if i in tt), default=0)
                plan_end = max((v[1] for v in tt.values()), default=0)
                cands.append({"edge": e.id, "provider": self.nodes[e.src].brief(), "proposed_by": e.proposed_by,
                              "provider_robot_ends": p_end, "plan_ends": plan_end,
                              "reasons": e.reasons, "body_ok": ok, **({"body_problem": why} if not ok else {}),
                              "creates_cycle": cyc, "provider_ends_at": pe, "request_starts_at": rs,
                              "also_candidate_for": [x for x in provider_wanted.get(e.src, []) if x != r.id]})
            lost = self.lost_if_unserved(r.id)
            tg = self.dag(self.tentative_links())
            answers = {e.src for e in self.cand.values() if e.dst == r.id}
            affected = sorted(x for x in (nx.descendants(tg, r.id) if r.id in tg else set())
                              if x not in lost and x not in answers)
            requests.append({"request": r.brief(), "candidates": cands, "if_unserved": lost, "affected": affected})
        unlinked = [self.nodes[n].brief() for n in self.nodes
                    if self.active(n) and self.nodes[n].type in PROVIDER_TYPES and n not in provider_wanted]
        # conflicts: one provider step wanted by several requests; the same object in several PASS / RECEIVE
        conflicts = [{"provider_step": p, "wanted_by": rs} for p, rs in provider_wanted.items() if len(rs) > 1]
        by_item: dict[tuple[str, str], list[str]] = {}
        for n in self.nodes.values():
            if self.active(n.id) and n.type in (PASS, RECEIVE) and n.item:
                by_item.setdefault((n.type, norm(n.item)), []).append(n.id)
        conflicts += [{"same_object": item, "type": t, "steps": ids} for (t, item), ids in by_item.items()
                      if len(ids) > 1]
        load = {}
        for a, p in self.plans.items():
            ids = [i for i in p.order if self.active(i)]
            load[a] = {"steps": len(ids),
                       "candidate_links_as_provider": sum(self.nodes[e.src].agent == a for e in self.cand.values()),
                       "ends_at_without_links": max((base[i][1] for i in ids if i in base), default=0)}
        self.analysis = {"requests": requests, "unlinked_offers": unlinked, "conflicts": conflicts, "load": load}
        return self.analysis

    def lost_if_unserved(self, rid: str) -> list[str]:
        """Steps that would be removed if this request stays unserved (its enables chain, one level of
        broken links included). Used only for the analysis; cleanup recomputes it on the real graph."""
        out, todo = [], [rid]
        while todo:
            x = todo.pop()
            if x in out or not self.active(x):
                continue
            out.append(x)
            n = self.nodes[x]
            if n.enables:
                todo.append(n.enables)
        return out

    def tentative_links(self) -> list[Edge]:
        """For the summary only: every candidate that passes the rules, added one by one."""
        out: list[Edge] = []
        for e in self.cand.values():
            if self.active(e.src) and self.active(e.dst) and self.body_ok(e)[0] and self.times(out + [e]) is not None:
                out.append(e)
        return out

    def longest_chain(self, extra: list[Edge]) -> tuple[list[str], float]:
        t = self.times(extra) or {}
        if not t:
            return [], 0.0
        g = self.dag(extra)
        cur = max(t, key=lambda i: t[i][1])
        chain = [cur]
        while True:
            prev = [p for p in g.predecessors(cur) if abs(t[p][1] - t[cur][0]) < 1e-9]
            if not prev:
                break
            cur = max(prev, key=lambda p: t[p][1])
            chain.append(cur)
        return chain[::-1], max(v[1] for v in t.values())

    def graph_text(self) -> str:
        """The plan graph written as text for the Graph LLM (4.2 results inline)."""
        a = self.analysis or self.analyse()
        req_info = {r["request"]["id"]: r for r in a["requests"]}
        answers_for: dict[str, list[str]] = {}
        for e in self.cand.values():
            answers_for.setdefault(e.src, []).append(e.dst)
        lines = ["ROBOTS AND STEPS"]
        for aid, p in self.plans.items():
            x = self.cfg.agent(aid)
            own = sum(self.active(i) and self.nodes[i].origin == "plan" for i in p.order)
            ans = sum(self.active(i) and self.nodes[i].origin != "plan" for i in p.order)
            lines.append(f"{aid} ({x.profile.room}, {'mobile' if x.profile.mobile else 'FIXED'}) "
                         f"— {own} own steps, answered {ans} requests | {x.profile.embodiment}")
            lines.append("  goals: " + "  ".join(f"[{i}] {g}" for i, g in enumerate(p.goals)))
            for n in p.steps():
                if not self.active(n.id) or n.origin != "plan":
                    continue                   # answer steps are shown only under their request
                head = f"  {n.id} {n.type:<8} "
                if n.type == RECEIVE:
                    head += f"{n.item} <- {n.target} | "
                elif n.type == PASS:
                    head += f"{n.item} -> {n.target} | "
                elif n.type == HELP:
                    head += f"for {n.target} in the {self.cfg.room_of(n.target)} | "
                body = head + n.text
                if n.type == ASK_HELP and n.condition:
                    body += f"  (helper must: {n.condition})"
                if n.origin != "plan":
                    body += f"  [answer added in Stage 3 for {', '.join(answers_for.get(n.id, []))}]"
                lines.append(body)
                if n.id in req_info:
                    r = req_info[n.id]
                    cs = []
                    for c in r["candidates"]:
                        src = c["edge"].split("->")[0]
                        if not c["body_ok"] or c["creates_cycle"]:
                            cs.append(f"{src} (!) " + (c.get("body_problem") or "creates a cycle"))
                        else:
                            cs.append(f"{src} ({self.nodes[src].agent} ends {c['provider_robot_ends']:g} min, "
                                      f"plan {c['plan_ends']:g} min)")
                    if not cs:
                        lines.append("      answers: none")
                    for c, txt in zip(r["candidates"], cs):
                        an = self.nodes[c["edge"].split("->")[0]]
                        what = f"{an.item} -> {an.target}: " if an.type == PASS else ""
                        lines.append(f"      answer {txt.split(' ', 1)[0]} by {an.agent} [{an.type}] {what}{an.text}"
                                     f"  {txt.split(' ', 1)[1] if ' ' in txt else ''}")
                    lines.append(f"      if unserved, removed: {', '.join(r['if_unserved'])}"
                                 + (f" | later steps that wait for it: {', '.join(r['affected'])}" if r["affected"] else ""))
        tl = self.tentative_links()
        t = self.times(tl) or {}
        chain, ms = self.longest_chain(tl)
        ends = {aid: max((t[i][1] for i in p.order if i in t), default=0) for aid, p in self.plans.items()}
        same_obj = [c for c in a["conflicts"] if "same_object" in c]
        over = (f"  (!) over the deadline by {ms - self.cfg.deadline_min:g} min: remove duplicate work first"
                if ms > self.cfg.deadline_min else None)
        lines += ["", "GRAPH SUMMARY (if every valid candidate were used)",
                  f"  ends at: " + ", ".join(f"{k} {v:g} min" for k, v in ends.items())
                  + f" | makespan {ms:g} / deadline {self.cfg.deadline_min} min"] + ([over] if over else []) + [
                  f"  longest chain: {' -> '.join(chain) if chain else '-'}",
                  "  objects in several steps: " + ("; ".join(f"{c['same_object']} ({', '.join(c['steps'])})"
                                                          for c in same_obj) if same_obj else "none")]
        shared = self.shared_objects()
        lines.append("  POSSIBLY THE SAME WORK (the same object in steps of different robots; check them for "
                     "question 0): " + ("; ".join(f"{o}: {', '.join(ids)}" for o, ids in shared) if shared else "none"))
        return "\n".join(lines)

    def shared_objects(self) -> list[tuple[str, list[str]]]:
        """Code-made hint for the overlap check: object names (from the offers and the steps) that
        appear in the own steps (not answers) of two or more robots. The LLM decides if it is the
        same work; this only points at candidates."""
        vocab = {norm(v) for v in self.vocab if v} | {norm(n.item) for n in self.nodes.values() if n.item}
        vocab = {v for v in vocab if len(v) >= 3}
        out = []
        for obj in sorted(vocab):
            # skip uses as part of furniture / appliance names ("coffee table", "coffee machine")
            pat = re.compile(r"\b" + re.escape(obj) + r"s?\b(?!\s+(table|machine|maker|counter|shelf|cabinet|box)\b)")
            ids = [n.id for n in self.nodes.values()
                   if self.active(n.id) and n.origin == "plan" and (pat.search(norm(n.text)) or norm(n.item) == obj)]
            if len({self.nodes[i].agent for i in ids}) >= 2:
                out.append((obj, ids))
        return out

    # ------------------------------------------------------------ 4.4 verification
    def try_link(self, e: Edge, decided_by: str, reason: str = "") -> str:
        """Accept a link or return why it is rejected."""
        if e.dst in self.chosen:
            return f"request {e.dst} already has a link"
        if any(x.src == e.src for x in self.chosen.values()):
            return f"provider step {e.src} already serves another request"
        ok, why = self.body_ok(e)
        if not ok:
            return why
        if self.times([e]) is None:
            return "creates a cycle"
        e.decided_by = decided_by
        self.chosen[e.dst] = e
        self.decisions.append({"request": e.dst, "edge": e.id, "decided_by": decided_by,
                               "proposed_by": e.proposed_by, "reason": reason})
        return ""

    def apply_llm(self, d: dict, log: EventLog) -> set[str]:
        """Apply the Graph LLM output in the order drops -> choices -> orders. Returns the requests
        the LLM decided (link or null)."""
        decided: set[str] = set()

        def reject(kind: str, item, why: str):
            self.rejected.append({"kind": kind, "output": item, "why": why})
            log.log("graph", "rule", "rejected", kind=kind, why=why)

        for x in d.get("drops") or []:
            x = x if isinstance(x, dict) else {}
            sid, why_kind = str(x.get("step") or ""), str(x.get("reason") or "").lower()
            if not self.active(sid):
                reject("drop", x, f"{sid} is not an active step")
                continue
            if why_kind == "duplicate":
                dup = str(x.get("duplicate_of") or "")
                if dup == sid or not self.active(dup):
                    reject("drop", x, "duplicate_of must be another active step")
                    continue
                if (dup, sid) in self.cand or (sid, dup) in self.cand:
                    reject("drop", x, f"{sid} and {dup} are a request and its own answer, not duplicates; "
                                      f"choose the answer for the request instead")
                    continue
                text = f"duplicate of {dup}" + (f": {x['why']}" if x.get("why") else "")
            elif why_kind == "unneeded":
                if self.nodes[sid].type not in REQUEST_TYPES:
                    reject("drop", x, "only a request (RECEIVE / ASK_HELP) can be dropped as unneeded")
                    continue
                if not str(x.get("why") or "").strip():
                    reject("drop", x, "an unneeded drop must say why the next step does not need it")
                    continue
                text = f"unneeded: {x['why']}"
            elif why_kind == "constraint":
                if self.nodes[sid].type in REQUEST_TYPES:
                    reject("drop", x, "a request can be dropped only as a duplicate; "
                                      "if nobody can serve it, its choice must be null")
                    continue
                if not str(x.get("why") or "").strip():
                    reject("drop", x, "a constraint drop must say which limit is broken")
                    continue
                text = f"constraint: {x['why']}"
            else:
                reject("drop", x, "reason must be 'duplicate', 'unneeded' or 'constraint'")
                continue
            n = self.nodes[sid]
            n.status, n.status_reason = "dropped", text
            self.drops.append({"step": sid, "robot": n.agent, "type": n.type, "text": n.text, "why": text})
            log.log("graph", "llm", "drop", step=sid)

        # same_work: carry out the LLM's own "keep" decision. Every other step of a group is dropped
        # as a duplicate of the kept one, except a request and its own answer (they are a pair,
        # decided by the choices) and answer steps (decided by the choices too).
        for grp in d.get("same_work") or []:
            if not isinstance(grp, dict):
                continue
            keep = str(grp.get("keep") or "")
            ids = [str(i) for i in grp.get("steps") or []]
            if keep not in ids or not self.active(keep):
                if ids:
                    reject("same_work", grp, f"keep={keep or None} is not an active step of the group")
                continue
            for sid in ids:
                if sid == keep or not self.active(sid) or self.nodes[sid].origin != "plan":
                    continue
                if (keep, sid) in self.cand or (sid, keep) in self.cand:
                    continue
                n = self.nodes[sid]
                why = f"duplicate of {keep} (same work, kept by the Graph LLM): {grp.get('what', '')}".strip()
                n.status, n.status_reason = "dropped", why
                self.drops.append({"step": sid, "robot": n.agent, "type": n.type, "text": n.text, "why": why})
                log.log("graph", "llm", "drop", step=sid, by="same_work")

        for x in d.get("choices") or []:
            x = x if isinstance(x, dict) else {}
            rid, edge, reason = str(x.get("request") or ""), x.get("edge"), str(x.get("reason") or "")
            if rid in self.nodes and self.nodes[rid].status == "dropped":
                self.ignored.append({"output": x, "why": f"{rid} was dropped in the same answer"})
                continue
            if not (self.active(rid) and self.nodes[rid].type in REQUEST_TYPES):
                reject("choice", x, f"{rid} is not an active request")
                continue
            if rid in decided:
                reject("choice", x, f"{rid} was already decided")
                continue
            if edge in (None, "", "null", "none"):
                decided.add(rid)
                self.unresolved[rid] = f"Graph LLM chose no link: {reason}".strip()
                self.decisions.append({"request": rid, "edge": None, "decided_by": "graph_llm", "reason": reason})
                continue
            edge = str(edge)
            src = edge.split("->")[0].strip()
            e = self.cand.get((src, rid))
            if e is None:
                reject("choice", x, f"{edge} is not a candidate link of {rid}")
                continue
            if not self.active(src):
                reject("choice", x, f"provider step {src} is not active")
                continue
            why = self.try_link(e, "graph_llm", reason)
            if why:
                reject("choice", x, why)
                self.choice_rejected[rid] = f"{e.id}: {why}"
                continue
            decided.add(rid)
            log.log("graph", "llm", "link", edge=e.id)

        for x in d.get("orders") or []:
            x = x if isinstance(x, dict) else {}
            b, a = str(x.get("before") or ""), str(x.get("after") or "")
            if not (self.active(b) and self.active(a)):
                reject("order", x, "both steps must be active")
                continue
            if self.nodes[b].agent == self.nodes[a].agent:
                reject("order", x, "an ORDER links steps of two different robots")
                continue
            e = Edge(b, a, ORDER, reasons=[str(x.get("reason") or "")], decided_by="graph_llm")
            if self.times([e]) is None:
                reject("order", x, "creates a cycle")
                continue
            self.orders.append(e)
            log.log("graph", "llm", "order", edge=e.id)
        return decided

    def apply_default(self, decided: set[str], log: EventLog, llm_used: bool = True) -> None:
        """Requests the Graph LLM did not decide.
        - with the Graph LLM: they stay unresolved (the LLM must decide every request)
        - rules only (ablation): the first answer, in robot order, that passes the rules is taken"""
        for r in [n for n in self.nodes.values() if self.active(n.id) and n.type in REQUEST_TYPES]:
            if r.id in decided or r.id in self.chosen:
                continue
            cands = self.candidates_of(r.id)
            if llm_used:
                if r.id in self.choice_rejected:
                    cause = f"the Graph LLM's choice was rejected ({self.choice_rejected[r.id]})"
                elif not cands:
                    cause = "no robot answered this request, and the Graph LLM did not resolve it"
                else:
                    cause = "the Graph LLM did not decide this request"
            else:
                why_not = []
                for e in sorted(cands, key=lambda e: e.src):
                    why = self.try_link(e, "rule", "first valid answer (rules only)")
                    if not why:
                        log.log("graph", "rule", "link", edge=e.id, by="rule")
                        break
                    why_not.append(f"{e.id}: {why}")
                else:
                    cause = ("no robot answered this request" if not cands
                             else "every answer broke a rule (" + "; ".join(why_not) + ")")
                    self.unresolved[r.id] = cause
                    self.decisions.append({"request": r.id, "edge": None, "decided_by": "rule", "reason": cause})
                continue
            self.unresolved[r.id] = cause
            self.decisions.append({"request": r.id, "edge": None, "decided_by": "rule", "reason": cause})

    # ------------------------------------------------------------ 4.5 cleanup
    def _remove(self, nid: str, why: str, log: EventLog) -> bool:
        if not self.active(nid):
            return False
        n = self.nodes[nid]
        n.status, n.status_reason = "removed", why
        self.removed.append({"step": nid, "robot": n.agent, "type": n.type, "text": n.text, "why": why})
        log.log("cleanup", n.agent, "removed", step=nid, why=why)
        return True

    def cleanup(self, log: EventLog) -> None:
        changed = True
        while changed:
            changed = False
            # links whose ends are gone
            for rid, e in list(self.chosen.items()):
                if not (self.active(e.src) and self.active(e.dst)):
                    del self.chosen[rid]
                    if self.active(rid):
                        self.unresolved[rid] = f"its provider step {e.src} was removed"
                    changed = True
            used = {e.src for e in self.chosen.values()} | set(self.chosen)
            for n in list(self.nodes.values()):
                if not self.active(n.id):
                    continue
                if n.type in PROVIDER_TYPES and n.id not in used:
                    why = ("answer added in Stage 3, not chosen" if n.origin == FROM_STAGE3
                           else "central draft answer, not chosen" if n.origin == "center"
                           else "not linked to any request")
                    changed |= self._remove(n.id, why, log)
                elif n.type in REQUEST_TYPES and n.id not in self.chosen:
                    if n.origin == FROM_STAGE3:
                        why = "added in Stage 3 for a link that was not chosen"
                    else:
                        why = "request not served: " + self.unresolved.setdefault(n.id, "no link")
                    if self._remove(n.id, why, log):
                        changed = True
                        if n.enables and self.active(n.enables):
                            self._remove(n.enables, f"needs {n.id} ({n.type}), which was not served", log)

    # ------------------------------------------------------------ 4.6 schedule
    def schedule(self) -> None:
        t = self.times()
        if t is None:                                  # should not happen: every link was cycle-checked
            self.violations.append("cycle at scheduling time: links and orders ignored for timing")
            keep_c, keep_o = self.chosen, self.orders
            self.chosen, self.orders = {}, []
            t = self.times() or {}
            self.chosen, self.orders = keep_c, keep_o
        for nid, (s, e) in t.items():
            self.nodes[nid].t_start, self.nodes[nid].t_end = s, e

    def makespan_min(self) -> float:
        return max((n.t_end or 0 for n in self.nodes.values() if self.active(n.id)), default=0)

    # ------------------------------------------------------------ coverage
    def finish_coverage(self, llm_rows: list | None) -> None:
        rows: dict[tuple[str, int], dict] = {}
        for x in llm_rows or []:
            if not isinstance(x, dict):
                continue
            a, gi = str(x.get("robot") or "").upper(), x.get("goal")
            if a in self.plans and isinstance(gi, int) and 0 <= gi < len(self.plans[a].goals):
                rows[(a, gi)] = {"robot": a, "goal": gi, "text": self.plans[a].goals[gi],
                                 "status": str(x.get("status") or "uncovered"),
                                 "evidence": [str(i) for i in x.get("evidence") or []],
                                 "cause": str(x.get("cause") or ""), "by": "graph_llm"}
        for a, p in self.plans.items():
            for gi, goal in enumerate(p.goals):
                serving = [n.id for n in p.steps() if self.active(n.id) and n.serves == gi]
                if (a, gi) not in rows:
                    rows[(a, gi)] = {"robot": a, "goal": gi, "text": goal,
                                     "status": "covered" if serving else "uncovered", "evidence": serving,
                                     "cause": "" if serving else "no active step serves this goal", "by": "rule"}
                    continue
                r = rows[(a, gi)]
                gone = [i for i in r["evidence"] if not self.active(i)]
                if gone and r["status"] != "uncovered":
                    alive = [i for i in r["evidence"] if self.active(i)]
                    r["evidence"] = alive
                    r["status"] = "partial" if alive else "uncovered"
                    r["cause"] = (r["cause"] + "; " if r["cause"] else "") + f"evidence removed in cleanup: {gone}"
        self.coverage = [rows[k] for k in sorted(rows)]

    # ------------------------------------------------------------ output
    def to_dict(self) -> dict:
        from dataclasses import asdict
        return {"nodes": {k: asdict(v) for k, v in self.nodes.items()},
                "order": {a: p.order for a, p in self.plans.items()},
                "candidates": [{"edge": e.id, "kind": e.kind, "proposed_by": e.proposed_by, "reasons": e.reasons}
                               for e in self.cand.values()],
                "links": [{"edge": e.id, "kind": e.kind, "proposed_by": e.proposed_by, "decided_by": e.decided_by}
                          for e in self.links()],
                "orders": [{"edge": e.id, "reason": e.reasons} for e in self.orders]}


# ================================================================================================
# Stage 4 entry
# ================================================================================================
async def graph_alignment(cfg: TaskConfig, plans: dict[str, Plan], cand: dict[tuple[str, str], Edge],
                          offers: dict[str, Offer], llm: BaseLLM | None, log: EventLog) -> PlanGraph:
    g = PlanGraph(cfg, plans, cand)
    g.vocab = {x for o in offers.values() for x in o.has_items}
    a = g.analyse()                                                    # 4.1 + 4.2
    log.log("graph", "rule", "analysed", requests=len(a["requests"]), candidates=len(cand),
            no_candidate=sum(not r["candidates"] for r in a["requests"]))
    decided: set[str] = set()
    llm_out: dict = {}
    graph_text = g.graph_text()
    if llm is not None:                                                # 4.3
        user = GRAPH_USER.format(task=cfg.task, deadline=cfg.deadline_min, graph=graph_text)
        llm_out = await llm.complete(GRAPH_SYSTEM, user, key="graph")
        decided = g.apply_llm(llm_out, log)                            # 4.4 (LLM part)
    g.apply_default(decided, log, llm is not None)                     # 4.4 (undecided requests)
    g.cleanup(log)                                                     # 4.5
    g.schedule()                                                       # 4.6
    g.finish_coverage(None)                                            # goal coverage by rule (report only)
    dup_no_order = []
    gdag = g.dag()
    for x in g.drops:
        n = g.nodes[x["step"]]
        dup = x["why"].split(":")[0].replace("duplicate of ", "").split(" (")[0].strip() if x["why"].startswith("duplicate of") else None
        if n.type in REQUEST_TYPES and dup and n.enables and g.active(n.enables) and g.active(dup):
            if not nx.has_path(gdag, dup, n.enables):
                dup_no_order.append({"request": n.id, "duplicate_of": dup, "waiting_step": n.enables,
                                     "note": f"{n.enables} does not wait for {dup}"})
    open_overlaps = []
    for grp in (llm_out.get("same_work") or []) if isinstance(llm_out, dict) else []:
        ids = [str(i) for i in (grp.get("steps") or [])] if isinstance(grp, dict) else []
        alive = [i for i in ids if g.active(i)]
        linked = {e.src for e in g.links() if e.dst in alive} | {e.dst for e in g.links() if e.src in alive}
        alive = [i for i in alive if i not in linked or not any(
            (e.src == i and e.dst in alive) or (e.dst == i and e.src in alive) for e in g.links())]
        if len(alive) > 1:
            open_overlaps.append({"steps": ids, "still_active": alive, "what": grp.get("what", "")})
    g.report = {
        "decisions": g.decisions,
        "unresolved_requests": [{"request": r, "robot": g.nodes[r].agent, "type": g.nodes[r].type,
                                 "text": g.nodes[r].text, "why": why} for r, why in g.unresolved.items()],
        "rejected_llm_outputs": g.rejected,
        "dropped": g.drops,
        "orders": [{"before": e.src, "after": e.dst, "reason": " ".join(e.reasons)} for e in g.orders],
        "removed": g.removed,
        "coverage": g.coverage,
        "violations": g.violations,
        "makespan_min": g.makespan_min(),
        "deadline_min": cfg.deadline_min,
        "graph_input": graph_text,
        "same_work": llm_out.get("same_work", []) if isinstance(llm_out, dict) else [],
        "same_work_still_active": open_overlaps,
        "duplicate_without_order": dup_no_order,
        "ignored_llm_outputs": g.ignored,
        "graph_llm_output": llm_out,
        "analysis": a,
    }
    log.log("graph", "rule", "done", links=len(g.links()), unresolved=len(g.unresolved),
            dropped=len(g.drops), removed=len(g.removed), makespan=g.makespan_min())
    return g
