"""Stage 4 - Graph-based Plan Alignment (design v4).

4.1 build the plan graph + labels                 (code)
4.2 edits Δ (SELECT/MERGE/DROP/ORDER) + coverage  (Graph LLM, ONE call, no CoT / few-shot)
4.3 admissibility check (in output order, no retry) + edge finalization (default policy)   (code)
4.4 dependency closure (incl. cycles left)        (code)
4.5 scheduling: wait-late, default sizes by type, 5-minute slots   (code)
4.6 report finalization: evidence check, deadline (code)

Without an LLM (ablation "rules only"): no edits, no coverage judgment; only the default policy.
"""
from __future__ import annotations

from .graph import PlanGraph
from .llm import BaseLLM
from .log import EventLog
from .prompts import GRAPH_USER, _j, graph_system
from .schemas import Edge, Node, Offer, TaskConfig

_RANK = {"SELECT": 0, "MERGE": 0, "DROP": 1, "ORDER": 2}


async def graph_alignment(cfg: TaskConfig, plans: dict[str, list[Node]], collab: list[Edge],
                          offers: dict[str, Offer], record: list[dict], llm: BaseLLM | None,
                          log: EventLog) -> PlanGraph:
    g = PlanGraph(cfg, plans, collab, offers, record)                                   # 4.1
    log.log("graph", "-", "built", nodes=len(g.nodes), candidates=len(g.collab),
            open_offers=len(g.open_offers()), in_cycle=len(g.cycle_nodes()))

    if llm is not None:                                                                  # 4.2
        view = g.graph_view()
        d = await llm.complete(graph_system(), GRAPH_USER.format(
            task=cfg.task, deadline=cfg.deadline_min, offers=_j(view["offers"]),
            plans=_j(view["plans"]), edges=_j({"collaboration": view["edges"],
                                               "open_offers": view["open_offers"]})), key="graph")
        edits = [e for e in (d.get("edits") or []) if isinstance(e, dict)]
        # apply in the requested order SELECT/MERGE -> DROP -> ORDER (stable within a group)
        edits.sort(key=lambda e: _RANK.get(str(e.get("op", "")).upper(), 3))
        for k, op in enumerate(edits):                                                   # 4.3 (1)
            err = g.apply_edit(op)
            g.edit_log.append({"k": k, "edit": op, "applied": err is None, "error": err,
                               "rationale": op.get("rationale", "")})
            log.log("graph", "llm", f"edit_{str(op.get('op', '?')).upper()}", ok=err is None,
                    **({"error": err} if err else {}))
        g.coverage_raw = d.get("coverage") or []

    g.finalize_edges()                                                                   # 4.3 (2)(3)
    log.log("graph", "-", "edges_confirmed", n=len(g.executing()), unresolved=len(g.unresolved),
            violations=len(g.invariant_violations))
    g.closure()                                                                          # 4.4
    log.log("graph", "-", "closure", removed=len(g.removals))
    g.schedule()                                                                         # 4.5
    g.finalize_report()                                                                  # 4.6
    log.log("graph", "-", "scheduled", makespan_min=g.makespan_min(), deadline=cfg.deadline_min,
            goals_covered=sum(x["status"] == "covered" for x in g.report["goals"]),
            goals=len(g.report["goals"]))
    return g


graph_reasoning = graph_alignment     # old name kept for notebooks that import it
