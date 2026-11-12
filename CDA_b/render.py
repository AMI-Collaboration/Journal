"""Rule-based (template) rendering of the Joint Plan, Provenance and Report, plus metrics. No LLM here."""
from __future__ import annotations

from .graph import PlanGraph
from .schemas import ASK_HELP, HELP, LOCAL, PASS, PHASE_MIN, RECEIVE, REQUEST_TYPES, action_str


def _item(x: str | None) -> str:
    """has_items entries look like "white mug (cabinet, image 1)": show only the name."""
    return (x or "").split("(")[0].strip() or (x or "")


def _line(g: PlanGraph, nid: str) -> str:
    n = g.nodes[nid]
    room = {a.id: a.profile.room for a in g.cfg.agents}
    prov = g.providers_of(nid)
    partner = g.nodes[prov[0].src].agent if prov else None
    served = [g.nodes[e.dst].agent for e in g.executing() if e.src == nid]
    if n.type == ASK_HELP:
        body = f"wait for {partner} to: {action_str(n.action)}"
    elif n.type == RECEIVE:
        body = f"receive {_item(n.item)} from {partner}"
        if partner and g.cfg.mover(partner, n.agent) == n.agent:
            body += f" (collects it from the {room[partner]})"
    elif n.type == HELP:
        body = f"{action_str(n.action)} (help {n.target} in the {n.location})"
    elif n.type == PASS:
        tgt = served[0] if served else n.target
        body = f"pass {_item(n.item)} to {tgt}" + (" (offered)" if n.origin == "offer" else "")
        body += (f" (brings it to the {room.get(tgt, '?')})" if g.cfg.mover(n.agent, tgt) == n.agent
                 else f" (hands it over; {tgt} collects it)")
    else:
        body = action_str(n.action)
    if served:
        body += f" (also serves {', '.join(served)}'s request)"
    waits = [e.src for e in g.order_edges if e.dst == nid and g.active(e.src)]
    if waits:
        body += f" [after {', '.join(waits)}]"
    return f"- {n.agent} [{n.type}] {body}  ({nid})"


def render(g: PlanGraph) -> str:
    rep = g.report
    act = sorted((i for i in g.nodes if g.active(i)
                  and not (i in g.merged and g.active(g.merged[i]))),
                 key=lambda i: (g.nodes[i].phase or 0, g.nodes[i].t_start or 0, g.nodes[i].agent, i))
    ms = g.makespan_min()
    ok = "OK" if ms <= g.cfg.deadline_min else "EXCEEDED"
    robots = ", ".join(f"{a.id}:{a.profile.embodiment.split('.')[0]}({a.profile.room})" for a in g.cfg.agents)
    lines = [f"### Joint Plan — {g.cfg.task_id}  (about {ms} min / deadline {g.cfg.deadline_min} min: {ok})",
             f"### Robots: {robots}"]
    last = None
    for i in act:
        ph = g.nodes[i].phase or 1
        if ph != last:
            last = ph
            lines += ["", f"[{(ph - 1) * PHASE_MIN}-{ph * PHASE_MIN} min]"]
        lines.append(_line(g, i))

    # ---------------- Provenance: how each collaboration was decided
    lines += ["", "### Provenance (collaboration edges)"]
    for e in sorted(g.executing(), key=lambda e: e.dst):
        p, r = g.nodes[e.src], g.nodes[e.dst]
        lines.append(f"- {r.id} ({r.agent} {r.type}) <- {p.id} ({p.agent} {p.type})  "
                     f"κ={e.kappa}, decided by {e.decided_by}")
    applied = [x for x in g.edit_log if x["applied"]]
    if applied:
        lines += ["", "### Graph LLM edits (applied)"]
        lines += [f"- {x['edit'].get('op')} {_ids(x['edit'])} — {x['rationale']}" for x in applied]

    # ---------------- Report
    lines += ["", "### Report: goal coverage"]
    for row in rep.get("goals", []):
        cause = f" — {', '.join(row['cause'])}" if row.get("cause") and row["status"] != "covered" else ""
        note = f" ({row['note']})" if row.get("note") else ""
        ev = f" [{', '.join(row['evidence'])}]" if row.get("evidence") else ""
        lines.append(f"- {row['robot']}.g{row['goal']} {row['text']}: {row['status']}{cause}{ev}{note}")
    if rep.get("unresolved_requests"):
        lines += ["", "### Unresolved requests"]
        for u in rep["unresolved_requests"]:
            replies = "; ".join(f"{x['agent']}: {x['answer']} {x['reason']}".strip() for x in u["replies"])
            lines.append(f"- {u['agent']} {u['request']} {u['text']} — {u['why']}" + (f" | {replies}" if replies else ""))
    if rep.get("rejected_edits"):
        lines += ["", "### Rejected edits"]
        lines += [f"- {x['edit'].get('op')} {_ids(x['edit'])} — {x['error']}" for x in rep["rejected_edits"]]
    if rep.get("dropped"):
        lines += ["", "### Dropped by the Graph LLM"]
        lines += [f"- {d['agent']} [{d['type']}] {d['text']} ({d['node']}) — {d['rationale']}" for d in rep["dropped"]]
    if rep.get("merged"):
        lines += ["", "### Merged by the Graph LLM"]
        lines += [f"- {d['agent']} [{d['type']}] {d['text']} ({d['node']}) -> folded into {d['into']} "
                  f"({d['into_agent']}) — {d['rationale']}" for d in rep["merged"]]
    if rep.get("removed_by_closure"):
        lines += ["", "### Removed by dependency closure"]
        lines += [f"- {d['agent']} [{d['type']}] {d['text']} ({d['node']}) — {d['reason']}"
                  for d in rep["removed_by_closure"]]
    if rep.get("invariant_violations"):
        lines += ["", "### Invariant violations (recorded)"]
        lines += [f"- {v}" for v in rep["invariant_violations"]]
    return "\n".join(lines)


def _ids(op: dict) -> str:
    return " ".join(f"{k}={op[k]}" for k in ("provider", "request", "into", "node", "before", "after") if k in op)


def metrics(g: PlanGraph, plan_meta: dict, llm_usage: dict) -> dict:
    nodes = list(g.nodes.values())
    final = g.executing()
    requests = [n for n in nodes if n.type in REQUEST_TYPES]
    goals = g.report.get("goals", [])
    return {
        "task_id": g.cfg.task_id,
        "n_steps_total": len(nodes),
        "n_steps_active": sum(g.active(n.id) for n in nodes),
        "n_requests": len(requests),
        "n_requests_served": sum(1 for r in requests if g.active(r.id) and g.providers_of(r.id)),
        "n_requests_unresolved": len(g.unresolved),
        "n_candidates_from_stage3": g.n_candidates,
        "n_collab_edges_final": len(final),
        "n_help_edges": sum(e.kind == "HELP" for e in final),
        "n_transfer_edges": sum(e.kind == "TRANSFER" for e in final),
        "decided_by_select": sum(e.decided_by == "SELECT" for e in final),
        "decided_by_merge": sum(e.decided_by == "MERGE" for e in final),
        "decided_by_default": sum(e.decided_by == "default" for e in final),
        "kappa_final": {k: sum(e.kappa == k for e in final) for k in ("mutual", "provider-only", "merged")},
        "graph_edits_applied": sum(x["applied"] for x in g.edit_log),
        "graph_edits_rejected": sum(not x["applied"] for x in g.edit_log),
        "n_dropped_by_graph": len(g.drops),
        "n_merged_by_graph": len(g.merges),
        "n_removed_by_closure": len(g.removals),
        "n_requests_moved_later": g.n_reordered,
        "n_invariant_violations": len(g.invariant_violations),
        "goals_total": len(goals),
        "goals_covered": sum(x["status"] == "covered" for x in goals),
        "goals_partial": sum(x["status"] == "partial" for x in goals),
        "goals_uncovered": sum(x["status"] == "uncovered" for x in goals),
        "goal_causes": {c: sum(c in (x.get("cause") or []) for x in goals if x["status"] != "covered")
                        for c in ("No volunteer", "Capability gap", "Left unresolved", "Infeasible",
                                  "Deadline exceeded")},
        "plan_fix_rounds": {a: m.get("fix_rounds", 0) for a, m in plan_meta.items()},
        "n_steps_excluded_stage2": sum(len(m.get("excluded") or []) for m in plan_meta.values()),
        "makespan_min": g.makespan_min(),
        "deadline": g.cfg.deadline_min,
        "deadline_ok": g.makespan_min() <= g.cfg.deadline_min,
        **llm_usage,
    }
