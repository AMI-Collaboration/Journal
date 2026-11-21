"""CDA pipeline: Offer -> Local Plan -> Edge Proposal -> Graph-based Plan Alignment -> Joint Plan.

Stages 1-3 run on every robot concurrently (asyncio.gather) with a barrier between stages.
Stage 4 is central: graph analysis by code, one Graph LLM call, verification by rules.

Ablations (paper)
    share_offers=False       "no offer"            Stage 2 does not see the other robots' offers
    use_edge_proposal=False  "no edge proposal"    robots do not answer; code drafts every possible answer
                                                   and the Graph LLM chooses centrally
    use_graph_llm=False      "no graph reasoning"  rules only: first valid answer per request

CLI:
    python -m CDA_stage.pipeline --task task.json --model gpt-4o
Notebook (event loop already running):
    res = await run_pipeline(cfg, llm)
"""
from __future__ import annotations

import argparse
import asyncio
import json
from dataclasses import asdict
from pathlib import Path

from .core import EventLog, TaskConfig
from .llm import BaseLLM, MockLLM, OpenAILLM
from .render import metrics, render
from .stage1_offer import make_offer
from .stage2_local_plan import make_local_plan
from .stage3_edge_proposal import center_candidates, edge_proposal
from .stage4_alignment import graph_alignment


async def run_pipeline(cfg: TaskConfig, llm: BaseLLM, *, share_offers: bool = True,
                       use_edge_proposal: bool = True, use_graph_llm: bool = True,
                       out_dir: str | Path | None = None, verbose: bool = True) -> dict:
    llm.reset_usage()
    log = EventLog(verbose)
    ids = cfg.ids

    # 1. Offer
    offers = dict(zip(ids, await asyncio.gather(*[make_offer(cfg, cfg.agent(a), llm, log) for a in ids])))

    # 2. Local Plan
    res = await asyncio.gather(*[make_local_plan(cfg, a, offers, llm, log, share_offers=share_offers) for a in ids])
    plans = {a: r[0] for a, r in zip(ids, res)}
    plan_meta = {a: r[1] for a, r in zip(ids, res)}
    local_snapshot = {a: {"goals": p.goals, "steps": [asdict(n) for n in p.steps()]} for a, p in plans.items()}

    # 3. Edge Proposal
    if use_edge_proposal:
        cand, proposal = await edge_proposal(cfg, plans, offers, llm, log)
    else:
        cand, proposal = center_candidates(cfg, plans)

    # 4. Graph-based Plan Alignment
    g = await graph_alignment(cfg, plans, cand, offers, llm if use_graph_llm else None, log)

    text = render(g)
    m = metrics(g, plan_meta, proposal, llm.usage())
    m["config"] = {"share_offers": share_offers, "use_edge_proposal": use_edge_proposal,
                   "use_graph_llm": use_graph_llm}
    out = {"offers": {a: o.to_dict() for a, o in offers.items()}, "local_plans": local_snapshot,
           "plan_meta": plan_meta, "proposal": proposal, "graph": g.to_dict(), "report": g.report,
           "joint_plan_text": text, "metrics": m, "events": log.events, "_graph_obj": g}

    if out_dir:
        od = Path(out_dir)
        od.mkdir(parents=True, exist_ok=True)
        for k in ("offers", "local_plans", "plan_meta", "proposal", "graph", "report", "metrics", "events"):
            (od / f"{k}.json").write_text(json.dumps(out[k], ensure_ascii=False, indent=1), encoding="utf-8")
        (od / "joint_plan.md").write_text(text, encoding="utf-8")
        (od / "io_log.json").write_text(json.dumps(llm.io_log, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True)
    ap.add_argument("--mock", help="scripted MockLLM json (no API key needed)")
    ap.add_argument("--model", default="gpt-4o")
    ap.add_argument("--no-offer", action="store_true", help="ablation: offers are not shared")
    ap.add_argument("--no-proposal", action="store_true", help="ablation: no Stage 3 (central linking)")
    ap.add_argument("--no-graph-llm", action="store_true", help="ablation: rules-only Stage 4")
    ap.add_argument("--out", default=None)
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    cfg = TaskConfig.load(a.task)
    llm = MockLLM(a.mock) if a.mock else OpenAILLM(a.model)
    out_dir = a.out or f"runs/{cfg.task_id}{'_mock' if a.mock else ''}"
    res = asyncio.run(run_pipeline(cfg, llm, share_offers=not a.no_offer, use_edge_proposal=not a.no_proposal,
                                   use_graph_llm=not a.no_graph_llm, out_dir=out_dir, verbose=not a.quiet))
    print("\n" + res["joint_plan_text"])
    print(f"\nsaved to {out_dir}/")


if __name__ == "__main__":
    main()
