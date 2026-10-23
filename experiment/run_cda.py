"""
experiment: C-DA 파이프라인 실행 스크립트
"""
import argparse
import asyncio
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CDA_DIR = os.path.join(HERE, "..", "C-DA")
AAMAS_DIR = os.path.join(HERE, "..")
sys.path.insert(0, AAMAS_DIR)
sys.path.insert(0, HERE)

# C-DA를 'C-DA' 이름 그대로 import (importlib 사용)
import importlib.util

def _load_cda_module(name, relpath):
    path = os.path.join(CDA_DIR, relpath)
    spec = importlib.util.spec_from_file_location(name, path,
        submodule_search_locations=[CDA_DIR])
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

# C-DA 패키지를 'cda'로 등록
import types
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
_load_cda_module("cda.pipeline", "pipeline.py")

from loader import load_all, build_cda_task_config, log_usage_from_metrics

parser = argparse.ArgumentParser()
parser.add_argument("--task", required=True)
parser.add_argument("--mode", default="multi_room", choices=["multi_room", "single_room"])
parser.add_argument("--model", default="gpt-4o")
parser.add_argument("--deadline", type=int, default=20)
parser.add_argument("--no-proposal", action="store_true")
parser.add_argument("--no-graph-llm", action="store_true")
parser.add_argument("--rounds", type=int, default=2)
parser.add_argument("--run", type=int, default=1)
parser.add_argument("--dry-run", action="store_true", help="API 호출 없이 loader만 테스트")
parser.add_argument("--quiet", action="store_true")
args = parser.parse_args()

data = load_all()
if args.task not in data["tasks"]:
    raise SystemExit(f"알 수 없는 task: {args.task}")

cfg_dict = build_cda_task_config(args.task, data, mode=args.mode, deadline_min=args.deadline)
if args.dry_run:
    print("✅ dry-run: loader 성공, API 호출 없음")
    sys.exit(0)
print(f"📋 Task: {args.task}  (robots: {len(cfg_dict['agents'])}, mode: {args.mode}, model: {args.model})")

from cda.schemas import TaskConfig
from cda.llm import OpenAILLM, MockLLM
from cda.pipeline import run_pipeline

api_key_path = os.path.join(HERE, "..", "LaMMA-P", "api_key.txt")
if not os.environ.get("OPENAI_API_KEY"):
    if os.path.exists(api_key_path):
        os.environ["OPENAI_API_KEY"] = open(api_key_path).read().strip()
    else:
        raise SystemExit("OPENAI_API_KEY 환경변수가 없고 api_key.txt도 없습니다.")

config = TaskConfig.from_notebook(
    task=cfg_dict["task"],
    agents=cfg_dict["agents"],
    deadline_min=cfg_dict["deadline_min"],
    task_id=cfg_dict["task_id"],
)
llm = MockLLM() if args.model == "mock" else OpenAILLM(model=args.model)

print("\n🚀 C-DA 파이프라인 실행 중...")
result = asyncio.run(
    run_pipeline(
        config, llm,
        use_edge_proposal=not args.no_proposal,
        use_graph_llm=not args.no_graph_llm,
        max_graph_rounds=args.rounds,
        verbose=not args.quiet,
    )
)

print("\n✅ 완료")
print(result["joint_plan_text"])

results_dir = os.path.join(HERE, "results", f"run{args.run}")
os.makedirs(results_dir, exist_ok=True)

result_record = {
    "task_n": args.task,
    "mode": args.mode,
    "model": args.model,
    "task_text": cfg_dict["task"],
    "joint_plan_text": result["joint_plan_text"],
    "offers": result.get("offers", {}),
    "local_plans": result.get("local_plans", {}),
    "judgments": result.get("judgments", []),
    "graph": result.get("graph", {}),
    "metrics": result.get("metrics", {}),
    "config": {
        "use_edge_proposal": not args.no_proposal,
        "use_graph_llm": not args.no_graph_llm,
        "max_graph_rounds": args.rounds,
        "deadline_min": args.deadline,
    },
}

suffix = ""
if args.no_proposal:
    suffix += "_no_proposal"
if args.no_graph_llm:
    suffix += "_no_graph_llm"

out_path = os.path.join(results_dir, f"{args.task}_{args.mode}_cda{suffix}_result.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(result_record, f, ensure_ascii=False, indent=2)

log_usage_from_metrics("cda", args.task, result.get("metrics", {}))
print(f"\n📁 저장: {out_path}")
