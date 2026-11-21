"""Template rendering of the Joint Plan (no LLM rewrite), the provenance/report sections, and metrics.

The part before "### Provenance" is what the judge sees. It has no step ids, only robots, times and
short sentences, so it reads like the baselines' plans.
"""
from __future__ import annotations

from .core import ASK_HELP, HELP, PASS, PHASE_MIN, RECEIVE, REQUEST_TYPES, SEQ
from .stage4_alignment import PlanGraph


def _room(g: PlanGraph, a: str) -> str:
    return g.cfg.room_of(a).replace("_", " ")


def _line(g: PlanGraph, nid: str) -> str:
    n = g.nodes[nid]
    link_in = next((e for e in g.links() if e.dst == nid), None)
    link_out = next((e for e in g.links() if e.src == nid), None)
    if n.type == PASS and link_out:
        to = g.nodes[link_out.dst].agent
        mover = g.cfg.mover(n.agent, to)
        if g.cfg.room_of(n.agent) == g.cfg.room_of(to):
            how = f"hands it over to {to} in the {_room(g, to)}"
        elif mover == n.agent:
            how = f"{n.agent} brings it to {to} in the {_room(g, to)}"
        else:
            how = f"{to} comes to the {_room(g, n.agent)} to collect it"
        body = f"{n.text} ({how})"
    elif n.type == RECEIVE and link_in:
        giver = g.nodes[link_in.src].agent
        body = n.text if giver in n.text else f"{n.text} (from {giver})"
    elif n.type == HELP and link_out:
        req = g.nodes[link_out.dst].agent
        where = (f"in the {_room(g, req)}" if g.cfg.room_of(n.agent) == g.cfg.room_of(req)
                 else f"goes to the {_room(g, req)}")
        body = f"{where}, for {req}: {n.text}"
    elif n.type == ASK_HELP and link_in:
        body = f"asks {g.nodes[link_in.src].agent} for help: {n.text} (waits until it is done)"
    else:
        body = n.text
    waits = [g.nodes[e.src] for e in g.orders if e.dst == nid and g.active(e.src)]
    if waits:
        body += " (after " + "; ".join(f"{w.agent}: {w.text}" for w in waits) + ")"
    return f"- {n.agent}: {body}"


def render(g: PlanGraph) -> str:
    act = sorted((i for i in g.nodes if g.active(i)),
                 key=lambda i: (g.nodes[i].t_start or 0, g.nodes[i].agent, g.plans[g.nodes[i].agent].order.index(i)))
    ms = g.makespan_min()
    ok = "OK" if ms <= g.cfg.deadline_min else "EXCEEDED"
    robots = ", ".join(f"{a.id}:{a.profile.room}({'mobile' if a.profile.mobile else 'fixed'})" for a in g.cfg.agents)
    lines = [f"### Joint Plan — {g.cfg.task_id}  (about {ms:g} min / deadline {g.cfg.deadline_min} min: {ok})",
             f"### Robots: {robots}"]
    last = None
    for i in act:
        ph = g.nodes[i].phase or 1
        if ph != last:
            last = ph
            lines += ["", f"[{(ph - 1) * PHASE_MIN}-{ph * PHASE_MIN} min]"]
        lines.append(_line(g, i))

    rep = g.report
    lines += ["", "### Provenance", "", "Steps (id, start-end min):"]
    for i in act:
        n = g.nodes[i]
        lines.append(f"- {i} {n.agent} [{n.type}] {n.t_start:g}-{n.t_end:g}: {n.text}")
    lines += ["", "Links:"]
    for e in sorted(g.links(), key=lambda e: e.dst):
        lines.append(f"- {e.src} -> {e.dst} ({e.kind}; proposed by {e.proposed_by}; decided by {e.decided_by})")
    for e in g.orders:
        lines.append(f"- {e.src} -> {e.dst} (ORDER; {' '.join(e.reasons)})")

    lines += ["", "### Report: goal coverage (rule: an active step serves the goal)"]
    for r in rep.get("coverage", []):
        cause = f" — {r['cause']}" if r.get("cause") and r["status"] != "covered" else ""
        ev = f" [{', '.join(r['evidence'])}]" if r.get("evidence") else ""
        lines.append(f"- {r['robot']}.g{r['goal']} {r['text']}: {r['status']}{cause}{ev}")
    for title, key, fmt in (
            ("Unresolved requests", "unresolved_requests", lambda x: f"- {x['robot']} {x['request']} [{x['type']}] {x['text']} — {x['why']}"),
            ("Dropped by the Graph LLM", "dropped", lambda x: f"- {x['robot']} {x['step']} [{x['type']}] {x['text']} — {x['why']}"),
            ("Removed in cleanup", "removed", lambda x: f"- {x['robot']} {x['step']} [{x['type']}] {x['text']} — {x['why']}"),
            ("Rejected Graph LLM outputs", "rejected_llm_outputs", lambda x: f"- {x['kind']} {x['output']} — {x['why']}"),
            ("Same work found by the Graph LLM but still done twice", "same_work_still_active",
             lambda x: f"- {', '.join(x['still_active'])} — {x['what']}"),
            ("Duplicate requests whose next step does not wait (missing ORDER)", "duplicate_without_order",
             lambda x: f"- {x['request']} dropped as duplicate of {x['duplicate_of']}, but {x['note']}"),
            ("Violations", "violations", lambda x: f"- {x}")):
        if rep.get(key):
            lines += ["", f"### {title}"] + [fmt(x) for x in rep[key]]
    return "\n".join(lines)


def metrics(g: PlanGraph, plan_meta: dict, proposal: dict, llm_usage: dict) -> dict:
    nodes = list(g.nodes.values())
    links = g.links()
    requests = [n for n in nodes if n.type in REQUEST_TYPES and n.origin == "plan"]
    cov = g.coverage
    return {
        "task_id": g.cfg.task_id,
        "n_steps_stage2": sum(n.origin == "plan" for n in nodes),
        "n_answer_steps": sum(n.origin != "plan" for n in nodes),
        "n_requests_with_several_answers": sum(
            sum(e.dst == r.id for e in g.cand.values()) > 1 for r in nodes if r.type in REQUEST_TYPES),
        "n_steps_final": sum(g.active(n.id) for n in nodes),
        "n_tidy_notes_stage2": sum(len(m.get("tidy_notes") or []) for m in plan_meta.values()),
        "n_requests_stage2": len(requests),
        "n_candidates": len(g.cand),
        "n_proposals_rejected": len(proposal.get("rejected") or []),
        "n_requests_no_proposal": len(proposal.get("no_proposal") or []),
        "n_links_final": len(links),
        "n_transfer_links": sum(e.kind == "TRANSFER" for e in links),
        "n_help_links": sum(e.kind == "HELP" for e in links),
        "links_by_graph_llm": sum(e.decided_by == "graph_llm" for e in links),
        "links_by_rule": sum(e.decided_by == "rule" for e in links),
        "n_orders": len(g.orders),
        "n_unresolved_requests": len(g.unresolved),
        "n_dropped_by_graph": len(g.drops),
        "n_removed_cleanup": len(g.removed),
        "n_rejected_llm_outputs": len(g.rejected),
        "n_violations": len(g.violations),
        "goals_total": len(cov),
        "goals_covered": sum(r["status"] == "covered" for r in cov),
        "goals_partial": sum(r["status"] == "partial" for r in cov),
        "goals_uncovered": sum(r["status"] == "uncovered" for r in cov),
        "makespan_min": g.makespan_min(),
        "deadline": g.cfg.deadline_min,
        "deadline_ok": g.makespan_min() <= g.cfg.deadline_min,
        **llm_usage,
    }


COLORS = {"LOCAL": "#9aa5b1", "ASK_HELP": "#e8a33d", "HELP": "#3d9be8", "RECEIVE": "#e8603d", "PASS": "#46b37a"}
EDGE_COLORS = {"TRANSFER": "#46b37a", "HELP": "#3d9be8", "ORDER": "#b04fd6"}


def draw(g: PlanGraph, path: str | None = None, show: bool = True):
    """Gantt chart of the schedule with link arrows. matplotlib is imported only here."""
    import matplotlib.pyplot as plt
    ids = g.cfg.ids
    row = {a: len(ids) - 1 - i for i, a in enumerate(ids)}
    fig, ax = plt.subplots(figsize=(max(8, g.makespan_min() * 0.6 + 3), 1.3 * len(ids) + 1))
    pos = {}
    for nid, n in g.nodes.items():
        if not g.active(nid):
            continue
        y, x0, w = row[n.agent], n.t_start, n.t_end - n.t_start
        if w > 0:
            ax.barh(y, w, left=x0, height=0.5, color=COLORS[n.type], edgecolor="black", linewidth=0.4)
            ax.text(x0 + 0.05, y, f"{n.type}\n{nid}", va="center", fontsize=6)
        else:
            ax.plot([x0, x0], [y - 0.25, y + 0.25], color=COLORS[n.type], lw=2)
        pos[nid] = (n.t_end, y)
    for e in g.edges():
        if e.kind == SEQ or e.src not in pos or e.dst not in pos:
            continue
        ax.annotate("", xy=(g.nodes[e.dst].t_start, pos[e.dst][1]), xytext=pos[e.src],
                    arrowprops=dict(arrowstyle="->", color=EDGE_COLORS.get(e.kind, "black"), lw=1.4))
    ax.axvline(g.cfg.deadline_min, color="red", lw=1, ls=":")
    ax.set_yticks([row[a] for a in ids], ids)
    ax.set_xlabel("time (min)")
    ax.set_title(f"{g.cfg.task_id} — makespan {g.makespan_min():g} min / deadline {g.cfg.deadline_min}")
    fig.tight_layout()
    if path:
        fig.savefig(path, dpi=150)
    if show:
        plt.show()
    return fig
