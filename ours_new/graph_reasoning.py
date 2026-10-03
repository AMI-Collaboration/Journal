"""
Stage 3 (was 4) - GRAPH REASONING

Centralized global coordination over independently generated local plans.
Auction has been removed: candidate HELP/PASS <-> ASK_HELP/RECEIVE edges are
now built directly here (Layer 0) from the robots' own self-proposed
HELP/PASS steps, which they already write during Local Planning after
reading other robots' broadcast OFFER `needs`.

Pipeline is now:
    Offer -> Local Plan (incl. self-proposed HELP/PASS) -> Graph Reasoning -> Render

Step-type semantics:
    LOCAL      Execute an action locally.
    ASK_HELP   Request another robot to perform a task.
    HELP       Volunteer to perform a task requested by another robot.
    RECEIVE    Request / receive a physical item from another robot.
    PASS       Provide / pass a physical item to another robot.

Matching channels:
    ASK_HELP <-> HELP
    RECEIVE  <-> PASS

Allowed LLM operations:
    reassign    Replace the current provider of a request with another candidate.
    unmatch     Remove an incorrect collaboration relation.
    add_order   Add a cross-robot ordering dependency.

The LLM cannot:
    - create new steps
    - delete steps
    - rewrite actions
    - create collaboration with a robot that was never a candidate
    - access private observations/images
"""

from __future__ import annotations

import copy
import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator

from llm import BaseLLM
from runtime import EventLog, call_validated
from schemas import LocalPlan, Step, agent_of


# ============================================================================
# Candidate generation (replaces the old Auction stage)
# ============================================================================

REQUEST_TYPES = {"ASK_HELP", "RECEIVE"}
PROVIDER_TYPES = {"HELP", "PASS"}

# request type -> expected provider type
CHANNEL = {
    "ASK_HELP": "HELP",
    "RECEIVE": "PASS",
}


def _tokens(text: str | None) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", (text or "").lower()))


def _overlap(a: str | None, b: str | None) -> float:
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / max(1, min(len(ta), len(tb)))


def build_candidates(plans: dict[str, LocalPlan]) -> dict[str, list[dict]]:
    """Build candidate provider edges for every request, directly from the
    robots' own self-proposed HELP/PASS steps (written during Local
    Planning). No embedding model is used; matching is by step-type
    channel compatibility, item-name overlap (for RECEIVE/PASS), action-text
    overlap (for ASK_HELP/HELP), and `target` hints as a bonus.

    Returns: request_id -> [{"pass": provider_id, "score": float}, ...]
             sorted by score descending.
    """

    requests = [
        s for plan in plans.values() for s in plan.steps if s.type in REQUEST_TYPES
    ]
    providers = [
        s for plan in plans.values() for s in plan.steps if s.type in PROVIDER_TYPES
    ]

    candidates: dict[str, list[dict]] = {r.id: [] for r in requests}

    for req in requests:
        req_agent = agent_of(req.id)
        expected_type = CHANNEL[req.type]

        for prov in providers:
            prov_agent = agent_of(prov.id)

            if prov_agent == req_agent:
                continue  # a robot cannot collaborate with itself

            if prov.type != expected_type:
                continue

            if req.type == "RECEIVE":
                if not req.item or not prov.item:
                    continue
                score = _overlap(req.item, prov.item)
                if score < 0.3:
                    continue
            else:  # ASK_HELP <-> HELP
                score = max(_overlap(req.action, prov.action), 0.3)

            # target hint bonus: either side explicitly named the other
            if req.target == prov_agent or prov.target == req_agent:
                score += 0.3

            candidates[req.id].append(
                {"pass": prov.id, "score": round(min(score, 1.0), 4)}
            )

    for rid in candidates:
        candidates[rid].sort(key=lambda c: (-c["score"], c["pass"]))

    return candidates


def initial_edge_selection(
    candidates: dict[str, list[dict]],
) -> tuple[dict[str, str], dict[str, float]]:
    """Greedy 1:1 initial selection over the candidates: one provider per
    request, one request per provider."""

    ranked = sorted(
        (
            (c["score"], rid, c["pass"])
            for rid, clist in candidates.items()
            for c in clist
        ),
        key=lambda x: (-x[0], x[1], x[2]),
    )

    used_requests: set[str] = set()
    used_providers: set[str] = set()

    handoff: dict[str, str] = {}
    handoff_score: dict[str, float] = {}

    for score, request_id, provider_id in ranked:
        if request_id in used_requests or provider_id in used_providers:
            continue
        used_requests.add(request_id)
        used_providers.add(provider_id)
        handoff[request_id] = provider_id
        handoff_score[request_id] = float(score)

    return handoff, handoff_score


# ============================================================================
# Graph
# ============================================================================

@dataclass
class Node:
    id: str
    agent: str
    order: int
    type: str
    kind: Optional[str]
    action: str
    item: Optional[str]
    active: bool = True


@dataclass(frozen=True)
class Edge:
    src: str
    dst: str
    kind: str
    status: str = "confirmed"
    # kind: sequence | collaboration
    # status: confirmed | candidate


class PlanGraph:

    def __init__(
        self,
        task: str,
        plans: dict[str, LocalPlan],
        candidates: dict[str, list[dict]],
    ) -> None:

        self.task = task

        # ------------------------------------------------------------
        # Nodes
        # ------------------------------------------------------------

        self.nodes: dict[str, Node] = {}

        for aid, plan in plans.items():
            for step in plan.steps:
                self.nodes[step.id] = Node(
                    id=step.id,
                    agent=aid,
                    order=step.order,
                    type=step.type,
                    kind=step.kind,
                    action=step.action,
                    item=step.item,
                    active=True,
                )

        # ------------------------------------------------------------
        # Layer 0 - initial 1:1 selection over self-proposed candidates
        # ------------------------------------------------------------

        self.candidates: dict[str, list[dict]] = candidates

        self.handoff, self.handoff_score = initial_edge_selection(candidates)

        self.extra_collaboration: list[tuple[str, str]] = []

        # ------------------------------------------------------------
        # Provider activation: an unmatched HELP/PASS stays inactive but
        # can be reactivated later by Graph Reasoning via `reassign`.
        # ------------------------------------------------------------

        matched_providers = set(self.handoff.values())

        for node in self.nodes.values():
            if node.type in {"HELP", "PASS"}:
                node.active = node.id in matched_providers

    # ----------------------------------------------------------------
    # Views
    # ----------------------------------------------------------------

    def active_ids(self) -> list[str]:
        return [nid for nid, n in self.nodes.items() if n.active]

    def sort_key(self, node_id: str):
        node = self.nodes[node_id]
        try:
            agent_num = int(node.agent.split("_")[-1])
        except ValueError:
            agent_num = 0
        return (agent_num, node.order)

    def agent_sequence(self, agent: str) -> list[Node]:
        return sorted(
            (n for n in self.nodes.values() if n.agent == agent and n.active),
            key=lambda n: n.order,
        )

    # ----------------------------------------------------------------
    # Edges
    # ----------------------------------------------------------------

    def edges(self, include_candidates: bool = False) -> list[Edge]:

        out: list[Edge] = []

        agents = sorted({n.agent for n in self.nodes.values()})
        for agent in agents:
            sequence = self.agent_sequence(agent)
            for a, b in zip(sequence, sequence[1:]):
                out.append(Edge(src=a.id, dst=b.id, kind="sequence", status="confirmed"))

        for request_id, provider_id in sorted(self.handoff.items()):
            if request_id not in self.nodes or provider_id not in self.nodes:
                continue
            request_node = self.nodes[request_id]
            provider_node = self.nodes[provider_id]
            if not request_node.active or not provider_node.active:
                continue
            out.append(Edge(src=provider_id, dst=request_id, kind="collaboration", status="confirmed"))

        for src, dst in self.extra_collaboration:
            if src not in self.nodes or dst not in self.nodes:
                continue
            if not self.nodes[src].active or not self.nodes[dst].active:
                continue
            out.append(Edge(src=src, dst=dst, kind="collaboration", status="confirmed"))

        if include_candidates:
            confirmed_pairs = {(p, r) for r, p in self.handoff.items()}
            for request_id, candidate_list in self.candidates.items():
                if request_id not in self.nodes or not self.nodes[request_id].active:
                    continue
                for candidate in candidate_list:
                    provider_id = candidate["pass"]
                    if provider_id not in self.nodes:
                        continue
                    if (provider_id, request_id) in confirmed_pairs:
                        continue
                    out.append(Edge(src=provider_id, dst=request_id, kind="collaboration", status="candidate"))

        if not include_candidates:
            out = [e for e in out if e.status == "confirmed"]

        return out

    # ----------------------------------------------------------------
    # Snapshot / restore
    # ----------------------------------------------------------------

    def snapshot(self):
        return copy.deepcopy((
            {nid: n.active for nid, n in self.nodes.items()},
            self.handoff,
            self.handoff_score,
            self.extra_collaboration,
        ))

    def restore(self, snapshot) -> None:
        active, self.handoff, self.handoff_score, self.extra_collaboration = copy.deepcopy(snapshot)
        for nid, is_active in active.items():
            self.nodes[nid].active = is_active

    # ----------------------------------------------------------------
    # Serialization
    # ----------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "nodes": [n.__dict__ for n in sorted(self.nodes.values(), key=lambda n: self.sort_key(n.id))],
            "handoffs": [
                {"need": rid, "pass": pid, "score": self.handoff_score.get(rid)}
                for rid, pid in sorted(self.handoff.items())
            ],
            "extra_collaboration": [list(p) for p in self.extra_collaboration],
            "edges": [e.__dict__ for e in self.edges(include_candidates=True)],
        }


# ============================================================================
# Graph algorithms (unchanged)
# ============================================================================

def find_cycle(graph: PlanGraph) -> list[Edge] | None:
    adjacency: dict[str, list[Edge]] = defaultdict(list)
    for edge in graph.edges(include_candidates=False):
        adjacency[edge.src].append(edge)

    color = {nid: 0 for nid in graph.active_ids()}
    parent: dict[str, Edge] = {}

    def dfs(node_id: str):
        color[node_id] = 1
        for edge in adjacency[node_id]:
            next_id = edge.dst
            if color[next_id] == 0:
                parent[next_id] = edge
                result = dfs(next_id)
                if result:
                    return result
            elif color[next_id] == 1:
                cycle = [edge]
                current = node_id
                while current != next_id:
                    parent_edge = parent[current]
                    cycle.append(parent_edge)
                    current = parent_edge.src
                return cycle
        color[node_id] = 2
        return None

    for node_id in sorted(color, key=graph.sort_key):
        if color[node_id] == 0:
            result = dfs(node_id)
            if result:
                return result
    return None


def topological_levels(graph: PlanGraph):
    node_ids = graph.active_ids()
    indegree = {nid: 0 for nid in node_ids}
    successors: dict[str, list[str]] = defaultdict(list)

    for edge in graph.edges(include_candidates=False):
        successors[edge.src].append(edge.dst)
        indegree[edge.dst] += 1

    level = {nid: 0 for nid in node_ids}
    ready = sorted([nid for nid in node_ids if indegree[nid] == 0], key=graph.sort_key)
    order: list[str] = []

    while ready:
        current = ready.pop(0)
        order.append(current)
        for next_id in successors[current]:
            level[next_id] = max(level[next_id], level[current] + 1)
            indegree[next_id] -= 1
            if indegree[next_id] == 0:
                ready.append(next_id)
                ready.sort(key=graph.sort_key)

    if len(order) != len(node_ids):
        return None
    return order, level


def reachable(graph: PlanGraph, source: str, target: str) -> bool:
    adjacency: dict[str, list[str]] = defaultdict(list)
    for edge in graph.edges(include_candidates=False):
        adjacency[edge.src].append(edge.dst)

    visited = {source}
    stack = [source]
    while stack:
        current = stack.pop()
        if current == target:
            return True
        for next_id in adjacency[current]:
            if next_id not in visited:
                visited.add(next_id)
                stack.append(next_id)
    return False


# ============================================================================
# Layer 1 - Rule verification (unchanged)
# ============================================================================

@dataclass
class RuleReport:
    fixes: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    unresolved_needs: list[str] = field(default_factory=list)
    order: list[str] = field(default_factory=list)
    levels: dict[str, int] = field(default_factory=dict)
    ok: bool = True

    def to_dict(self) -> dict:
        return self.__dict__.copy()


def rule_verify(graph: PlanGraph) -> RuleReport:
    report = RuleReport()

    matched_providers = {
        pid for rid, pid in graph.handoff.items()
        if rid in graph.nodes and graph.nodes[rid].active
    }

    for node in graph.nodes.values():
        if node.type not in {"HELP", "PASS"}:
            continue
        if node.id in matched_providers:
            node.active = True
            continue
        if node.active:
            node.active = False
            report.fixes.append({"rule": "orphan_provider_withdrawn", "step": node.id, "type": node.type})

    while True:
        cycle = find_cycle(graph)
        if cycle is None:
            break

        collaboration_edges = [e for e in cycle if e.kind == "collaboration" and e.status == "confirmed"]

        handoff_edges = [
            e for e in collaboration_edges
            if e.dst in graph.handoff and graph.handoff.get(e.dst) == e.src
        ]

        if handoff_edges:
            weakest = min(handoff_edges, key=lambda e: graph.handoff_score.get(e.dst, 0.0))
            request_id, provider_id = weakest.dst, weakest.src
            del graph.handoff[request_id]
            graph.handoff_score.pop(request_id, None)
            if provider_id in graph.nodes:
                graph.nodes[provider_id].active = False
            report.fixes.append({"rule": "cycle_broken", "removed_handoff": [provider_id, request_id]})
            continue

        extra_edges = [e for e in collaboration_edges if (e.src, e.dst) in graph.extra_collaboration]
        if extra_edges:
            edge = extra_edges[-1]
            graph.extra_collaboration.remove((edge.src, edge.dst))
            report.fixes.append({"rule": "cycle_broken", "removed_order": [edge.src, edge.dst]})
            continue

        report.ok = False
        report.warnings.append("unbreakable cycle inside a single robot's own sequence")
        return report

    report.unresolved_needs = [
        n.id for n in graph.nodes.values()
        if n.active and n.type in {"ASK_HELP", "RECEIVE"} and n.id not in graph.handoff
    ]

    for request in graph.nodes.values():
        if not (request.active and request.type == "RECEIVE" and request.kind == "item" and request.item):
            continue
        for node in graph.agent_sequence(request.agent):
            if node.type == "LOCAL" and node.order < request.order and request.item.lower() in node.action.lower():
                report.warnings.append(f"{node.id} seems to use '{request.item}' before it is received at {request.id}")

    result = topological_levels(graph)
    if result is None:
        report.ok = False
    else:
        report.order, report.levels = result

    return report


# ============================================================================
# Layer 2 - LLM Graph Reasoner (unchanged except prompt wording)
# ============================================================================

class GraphOp(BaseModel):
    op: Literal["reassign", "unmatch", "add_order"]
    need: Optional[str] = None
    to_pass: Optional[str] = None
    before: Optional[str] = None
    after: Optional[str] = None
    reason: str = ""

    @model_validator(mode="after")
    def validate_fields(self):
        required_fields = {
            "reassign": ("need", "to_pass"),
            "unmatch": ("need",),
            "add_order": ("before", "after"),
        }[self.op]
        for field_name in required_fields:
            if not getattr(self, field_name):
                raise ValueError(f"op '{self.op}' needs field '{field_name}'")
        return self


class RawGraphOps(BaseModel):
    ops: list[GraphOp] = Field(default_factory=list)


GRAPH_SYSTEM = """
You are the centralized graph reasoner of a heterogeneous robot team.

You are NOT a planner.

Each robot independently generated its own local plan, including any
HELP/PASS steps it volunteered after reading other robots' broadcast
OFFER needs. A rule-based layer already made an initial 1:1 selection
among these self-proposed candidates.

Your job is to determine whether those relations form a globally
consistent dependency graph.

------------------------------------------------------------
STEP TYPES
------------------------------------------------------------
LOCAL      A robot performs an action locally.
ASK_HELP   A robot requests another robot to perform a task.
HELP       A robot volunteers to perform a task for another robot.
RECEIVE    A robot requests / receives a physical item.
PASS       A robot provides / passes a physical item.

Valid collaboration relations are ONLY:
    ASK_HELP <-> HELP
    RECEIVE <-> PASS

------------------------------------------------------------
CURRENT GRAPH
------------------------------------------------------------
A confirmed handoff is represented as: provider -> requester
Each request lists its candidate providers (self-proposed by robots
during Local Planning). Candidate providers are the ONLY providers
that may be selected.

------------------------------------------------------------
AVAILABLE OPERATIONS
------------------------------------------------------------
1. reassign
{"op": "reassign", "need": "<request step id>", "to_pass": "<candidate provider step id>", "reason": "..."}
The `to_pass` MUST already appear in the request's candidate list.

2. unmatch
{"op": "unmatch", "need": "<request step id>", "reason": "..."}

3. add_order
{"op": "add_order", "before": "<step id>", "after": "<step id>", "reason": "..."}
The two steps must belong to different robots. Do not add an ordering
relation if it is already implied by the existing dependency graph.

------------------------------------------------------------
IMPORTANT CONSTRAINTS
------------------------------------------------------------
You may NOT:
- create a new step
- delete a step
- rewrite an action
- invent a provider
- create a collaboration that is not in the candidates
- access private observations or images
- perform task planning from scratch

You may ONLY modify: collaboration relations, provider assignment,
cross-robot ordering relations.

------------------------------------------------------------
WHAT TO CHECK
------------------------------------------------------------
For every ASK_HELP: does the selected HELP provider actually perform
the requested task?
For every RECEIVE: does the selected PASS provider actually provide
the requested item?
Also check: candidate alternatives, collaboration consistency,
dependency ordering, cycles, use-before-receive problems, unnecessary
cross-robot dependencies.

Prefer minimal intervention. If the graph is already consistent:
{"ops": []}

Return exactly ONE JSON object: {"ops": [...]}
"""


def serialize_for_llm(graph: PlanGraph, report: RuleReport, scope: str = "full") -> str:

    def brief(node: Node) -> dict:
        data = {"id": node.id, "type": node.type, "action": node.action}
        if node.kind:
            data["kind"] = node.kind
        if node.item:
            data["item"] = node.item
        return data

    robots: dict[str, list[dict]] = {}
    for agent in sorted({n.agent for n in graph.nodes.values()}):
        sequence = graph.agent_sequence(agent)
        robots[agent] = [brief(n) for n in sequence if (scope == "full" or n.type != "LOCAL")]

    candidates = {}
    for request_id, candidate_list in graph.candidates.items():
        if request_id not in graph.nodes or not graph.nodes[request_id].active:
            continue
        formatted = []
        for candidate in candidate_list:
            provider_id = candidate["pass"]
            if provider_id not in graph.nodes:
                continue
            provider = graph.nodes[provider_id]
            used_by_other = (
                provider_id in graph.handoff.values()
                and graph.handoff.get(request_id) != provider_id
            )
            formatted.append({
                "pass": provider_id, "score": candidate["score"], "type": provider.type,
                "action": provider.action, "item": provider.item, "used_by_other_need": used_by_other,
            })
        candidates[request_id] = formatted

    handoffs = []
    for request_id, provider_id in sorted(graph.handoff.items()):
        if request_id not in graph.nodes or provider_id not in graph.nodes:
            continue
        if not graph.nodes[request_id].active or not graph.nodes[provider_id].active:
            continue
        handoffs.append({
            "need": request_id, "pass": provider_id,
            "need_type": graph.nodes[request_id].type, "pass_type": graph.nodes[provider_id].type,
            "score": graph.handoff_score.get(request_id),
        })

    collaboration_edges = [
        {"src": e.src, "dst": e.dst, "status": e.status}
        for e in graph.edges(include_candidates=True) if e.kind == "collaboration"
    ]

    payload = {
        "task": graph.task,
        "robots": robots,
        "handoffs": handoffs,
        "collaboration_edges": collaboration_edges,
        "candidates": candidates,
        "unresolved_requests": report.unresolved_needs,
        "rule_warnings": report.warnings,
    }

    return json.dumps(payload, ensure_ascii=False, indent=2)


def apply_op(graph: PlanGraph, op: GraphOp) -> tuple[bool, str]:
    nodes = graph.nodes
    snapshot = graph.snapshot()

    if op.op == "reassign":
        request_id, provider_id = op.need, op.to_pass
        if request_id not in nodes:
            return False, "unknown request step"
        request = nodes[request_id]
        if request.type not in {"ASK_HELP", "RECEIVE"}:
            return False, "step is not a collaboration request"
        if not request.active:
            return False, "request step is inactive"
        if provider_id not in nodes:
            return False, "unknown provider step"
        provider = nodes[provider_id]
        expected = {"ASK_HELP": "HELP", "RECEIVE": "PASS"}[request.type]
        if provider.type != expected:
            return False, f"invalid provider type: {request.type} requires {expected}"

        candidate_scores = {c["pass"]: c["score"] for c in graph.candidates.get(request_id, [])}
        if provider_id not in candidate_scores:
            return False, "provider is not a self-proposed candidate for this request"
        if provider.agent == request.agent:
            return False, "request and provider belong to the same robot"

        current_request = next((rid for rid, pid in graph.handoff.items() if pid == provider_id and rid != request_id), None)
        if current_request is not None:
            return False, f"provider is already assigned to request {current_request}"

        old_provider = graph.handoff.get(request_id)
        if old_provider is not None and old_provider in nodes:
            nodes[old_provider].active = False

        provider.active = True
        graph.handoff[request_id] = provider_id
        graph.handoff_score[request_id] = candidate_scores[provider_id]

    elif op.op == "unmatch":
        request_id = op.need
        if request_id not in graph.handoff:
            return False, "request has no confirmed handoff"
        provider_id = graph.handoff[request_id]
        del graph.handoff[request_id]
        graph.handoff_score.pop(request_id, None)
        if provider_id in nodes:
            nodes[provider_id].active = False

    else:  # add_order
        before, after = op.before, op.after
        if before not in nodes or after not in nodes:
            return False, "unknown step"
        if not nodes[before].active or not nodes[after].active:
            return False, "step is inactive"
        if nodes[before].agent == nodes[after].agent:
            return False, "same robot: local sequence already defines the order"
        if reachable(graph, before, after):
            return False, "ordering is already implied"
        graph.extra_collaboration.append((before, after))

    if find_cycle(graph) is not None:
        graph.restore(snapshot)
        return False, "operation would create a cycle; reverted"

    return True, "ok"


async def llm_reason(
    graph: PlanGraph, report: RuleReport, llm: BaseLLM, log: EventLog,
    *, scope: str = "full", max_ops: int = 8, max_retries: int = 2,
) -> list[dict]:

    raw: RawGraphOps = await call_validated(
        llm, log, phase="graph", who="reasoner", system=GRAPH_SYSTEM,
        user=serialize_for_llm(graph, report, scope),
        parse=RawGraphOps.model_validate, images=None, max_retries=max_retries,
    )

    records = []
    for op in raw.ops[:max_ops]:
        ok, reason = apply_op(graph, op)
        record = {**op.model_dump(exclude_none=True), "status": "applied" if ok else "rejected", "why": reason}
        records.append(record)
        log.log("graph", "reasoner", "op_applied" if ok else "op_rejected",
                 **{k: v for k, v in record.items() if k != "status"})

    for op in raw.ops[max_ops:]:
        records.append({**op.model_dump(exclude_none=True), "status": "rejected", "why": f"more than max_ops={max_ops}"})

    return records


@dataclass
class GraphResult:
    graph: PlanGraph
    report: RuleReport
    first_report: RuleReport
    ops: list[dict]
    stats: dict


async def graph_reasoning(
    task: str,
    plans: dict[str, LocalPlan],
    llm: BaseLLM,
    log: EventLog,
    *,
    use_llm: bool = True,
    scope: str = "full",
    max_ops: int = 8,
) -> GraphResult:

    candidates = build_candidates(plans)
    graph = PlanGraph(task, plans, candidates)

    initial_handoffs = len(graph.handoff)

    first_report = rule_verify(graph)
    log.log("graph", "rules", "verified", fixes=len(first_report.fixes),
            warnings=len(first_report.warnings), unresolved=len(first_report.unresolved_needs))

    ops: list[dict] = []
    final_report = first_report

    if use_llm:
        ops = await llm_reason(graph, first_report, llm, log, scope=scope, max_ops=max_ops)
        final_report = rule_verify(graph)
        log.log("graph", "rules", "verified_after_llm", fixes=len(final_report.fixes),
                warnings=len(final_report.warnings), unresolved=len(final_report.unresolved_needs))

    applied = [o for o in ops if o["status"] == "applied"]
    changed_matches = sum(1 for o in applied if o["op"] in {"reassign", "unmatch"})

    stats = {
        "ops_proposed": len(ops),
        "ops_applied": len(applied),
        "ops_rejected": len(ops) - len(applied),
        "reassigned": sum(1 for o in applied if o["op"] == "reassign"),
        "unmatched": sum(1 for o in applied if o["op"] == "unmatch"),
        "orders_added": sum(1 for o in applied if o["op"] == "add_order"),
        "rule_fixes": len(first_report.fixes) + (len(final_report.fixes) if use_llm else 0),
        "initial_handoffs": initial_handoffs,
        "final_handoffs": len(graph.handoff),
        "modification_ratio": round(changed_matches / max(1, initial_handoffs), 4),
        "unresolved_needs": len(final_report.unresolved_needs),
    }

    return GraphResult(graph=graph, report=final_report, first_report=first_report, ops=ops, stats=stats)
