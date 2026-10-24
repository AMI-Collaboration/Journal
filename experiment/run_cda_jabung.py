"""
experiment: C-DA 파이프라인 실행 스크립트
"""
import argparse
import asyncio
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CDA_DIR = os.path.join(HERE, "..", "C-DA_jabung")
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
parser.add_argument("--n-robots", type=int, default=4, choices=[2,3,4,6,8])
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

# task.json에서 deadline 읽기 (없으면 args.deadline 사용)
task_deadline = data["tasks"].get(args.task, {}).get("deadline", args.deadline)
cfg_dict = build_cda_task_config(args.task, data, mode=args.mode, deadline_min=task_deadline, n_robots=args.n_robots)
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
# JSON action을 자연어로 변환
from openai import OpenAI as _OpenAI
_sync_client = _OpenAI(api_key=open(os.path.join(HERE, "..", "LaMMA-P", "api_key.txt")).read().strip())

def _naturalize(plan_text: str) -> str:
    prompt = f"""Convert the following robot plan into natural language.
Each action line may contain a JSON dict like {{'verb': 'pick_up', 'object': 'apple', 'from': 'counter', 'to': 'table'}}.
Convert ONLY the JSON dict parts into fluent English phrases. Keep everything else exactly as is.

Rules:
- Convert verb+object+from+to into a natural sentence, e.g.:
  pick up the apple from the counter
  move the laptop from the sofa to the coffee table
  slice the bread
  turn on the stove
  push the couch against the wall
- Do NOT change robot labels, step ids, time blocks, or any non-dict text.
- Keep the same line structure.

Plan:
{plan_text}

Return ONLY the converted plan starting with "### Joint Plan", no preamble or explanation."""
    r = _sync_client.chat.completions.create(
        model=args.model, temperature=0.0,
        messages=[{"role": "user", "content": prompt}],
    )
    return r.choices[0].message.content.strip()

raw_plan = result["joint_plan_text"]
naturalized = _naturalize(raw_plan)
print(naturalized)

results_dir = os.path.join(HERE, "results", "jabung")
os.makedirs(results_dir, exist_ok=True)

result_record = {
    "task_n": args.task,
    "mode": args.mode,
    "model": args.model,
    "task_text": cfg_dict["task"],
    "joint_plan_text": naturalized.split("### Unresolved")[0].split("### Blocked")[0].split("### Dropped")[0].split("### Skipped")[0].split("### Warnings")[0].strip(),
    "joint_plan_full": result["joint_plan_text"],
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

# io_log 저장
io_log_path = os.path.join(results_dir, f"{args.task}_{args.mode}_cda{suffix}_io_log.json")
with open(io_log_path, "w", encoding="utf-8") as f:
    json.dump(llm.io_log, f, ensure_ascii=False, indent=2)
print(f"📋 IO 로그: {io_log_path}")

log_usage_from_metrics("cda", args.task, result.get("metrics", {}))
print(f"\n📁 저장: {out_path}")
