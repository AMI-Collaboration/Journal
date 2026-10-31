"""
CDA Ablation Study Runner
Variants: full, no_offer, no_edge, no_graph
"""
import asyncio, json, os, sys, argparse, types, importlib.util
from dataclasses import asdict

HERE = os.path.dirname(os.path.abspath(__file__))
CDA_DIR = os.path.join(HERE, '..', 'C-DA_jabung')
sys.path.insert(0, os.path.join(HERE, '..'))
sys.path.insert(0, HERE)

from loader import load_all, build_cda_task_config

def _load_cda_module(name, relpath):
    path = os.path.join(CDA_DIR, relpath)
    spec = importlib.util.spec_from_file_location(name, path,
        submodule_search_locations=[CDA_DIR])
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

cda_pkg = types.ModuleType("cda")
cda_pkg.__path__ = [CDA_DIR]
cda_pkg.__package__ = "cda"
sys.modules["cda"] = cda_pkg

_load_cda_module("cda.log", "log.py")
_load_cda_module("cda.schemas", "schemas.py")
_load_cda_module("cda.llm", "llm.py")
_load_cda_module("cda.prompts", "prompts.py")
_load_cda_module("cda.graph", "graph.py")
_load_cda_module("cda.render", "render.py")
_load_cda_module("cda.stage1_offer", "stage1_offer.py")
_load_cda_module("cda.stage2_local_plan", "stage2_local_plan.py")
_load_cda_module("cda.stage3_edge_proposal", "stage3_edge_proposal.py")
_load_cda_module("cda.stage4_graph_reasoning", "stage4_graph_reasoning.py")

from cda.llm import OpenAILLM
from cda.log import EventLog
from cda.render import metrics, render
from cda.stage1_offer import make_offer
from cda.stage2_local_plan import make_local_plan
from cda.stage3_edge_proposal import edge_proposal
from cda.stage4_graph_reasoning import graph_reasoning
from cda.schemas import TaskConfig

VARIANTS = ['full', 'no_offer', 'no_edge', 'no_graph']


async def run_variant(cfg, llm, variant):
    log = EventLog(verbose=False)
    ids = cfg.ids
    llm.reset_usage()  # variant 시작 전 리셋

    # Stage 1: Offer
    if variant == 'no_offer':
        # 이미지 없이 offer — 이미지만 제거한 cfg 생성
        from cda.schemas import AgentInput, TaskConfig as TC
        no_img_agents = [AgentInput(ag.id, ag.profile, [], ag.instruction) for ag in cfg.agents]
        no_img_cfg = TC(cfg.task_id, cfg.task, cfg.deadline_min, no_img_agents)
        offers_l = await asyncio.gather(*[make_offer(no_img_cfg, no_img_cfg.agent(a), llm, log) for a in ids])
        offers = dict(zip(ids, offers_l))
    else:
        offers_l = await asyncio.gather(*[make_offer(cfg, cfg.agent(a), llm, log) for a in ids])
        offers = dict(zip(ids, offers_l))

    # Stage 2: Local Plan
    res = await asyncio.gather(*[make_local_plan(cfg, a, offers, llm, log) for a in ids])
    plans = {a: r[0] for a, r in zip(ids, res)}
    plan_meta = {a: r[1] for a, r in zip(ids, res)}

    # Stage 3: Edge Proposal
    collab, judgments = [], []
    if variant != 'no_edge':
        collab, judgments = await edge_proposal(cfg, plans, offers, llm, log)

    # Stage 4: Graph Reasoning
    use_graph_llm = (variant != 'no_graph')
    g = await graph_reasoning(cfg, plans, collab, offers, judgments,
                              llm if use_graph_llm else None, log, max_rounds=2)

    text = render(g)
    m = metrics(g, plan_meta, llm.usage())
    m["variant"] = variant
    return {"variant": variant, "joint_plan_text": text, "metrics": m}


async def run_all(task_n, n_robots, run_n, data, mode):
    cfg_dict = build_cda_task_config(task_n, data, mode=mode, n_robots=n_robots)
    cfg = TaskConfig.from_notebook(
        task=cfg_dict["task"],
        agents=cfg_dict["agents"],
        deadline_min=cfg_dict["deadline_min"],
        task_id=cfg_dict["task_id"],
    )
    llm = OpenAILLM()
    results = {}
    for variant in VARIANTS:
        print(f"  [{variant}] running...", flush=True)
        try:
            _t0 = __import__("time").time()
            r = await run_variant(cfg, llm, variant)
            r["metrics"]["wall_time_sec"] = __import__("time").time() - _t0
            results[variant] = r
            print(f"  [{variant}] ✅")
        except Exception as e:
            import traceback
            print(f"  [{variant}] ❌ {e}")
            traceback.print_exc()
            results[variant] = {"variant": variant, "error": str(e)}

    out_dir = os.path.join(HERE, 'results', 'ablation')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f'{task_n}_ablation_run{run_n}.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"💾 saved: {out_path}")
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--task', required=True)
    ap.add_argument('--n-robots', type=int, default=4)
    ap.add_argument('--run', type=int, default=1)
    ap.add_argument('--mode', default='multi_room')
    a = ap.parse_args()
    data = load_all()
    print(f"=== Ablation: {a.task} (n={a.n_robots}, run{a.run}) ===")
    asyncio.run(run_all(a.task, a.n_robots, a.run, data, a.mode))

if __name__ == '__main__':
    main()
