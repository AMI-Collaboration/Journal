"""
experiment_new 구조를 사용해 ours_new 파이프라인을 실행 (reasoning 포함 전체 저장)

사용법:
    python run_ours_reasoning.py --task task1_abstract
"""
import argparse
import asyncio
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OURS_NEW_DIR = os.path.join(HERE, "..", "ours_new")
sys.path.insert(0, OURS_NEW_DIR)
sys.path.insert(0, HERE)

from loader import load_all, build_agent_inputs  # noqa: E402

parser = argparse.ArgumentParser()
parser.add_argument("--task", required=True, help="예: task1_abstract")
parser.add_argument("--mode", default="multi_room", choices=["multi_room", "single_room"])
parser.add_argument("--gpt-version", default="gpt-4o")
parser.add_argument("--mock", action="store_true")
parser.add_argument("--quiet", action="store_true")
args = parser.parse_args()

data = load_all()
if args.task not in data["tasks"]:
    raise SystemExit(f"알 수 없는 task_n: {args.task}")

task_info = data["tasks"][args.task]
task_text = task_info["task"]
agents_raw = build_agent_inputs(args.task, data, mode=args.mode)

print(f"📋 Task: {args.task}  (robots: {len(agents_raw)}, mode: {args.mode})")
for label, info in agents_raw.items():
    print(f"  {label}: {info['room_type']} ({info['fp']})  images={[os.path.basename(p) for p in info['images']]}")

agent_list = [
    {"capability": info["capability"], "images": info["images"], "hidden_info": info["hidden_info"]}
    for info in agents_raw.values()
]
task_config_json = {"task": task_text, "agents": agent_list}

from schemas import TaskConfig  # noqa: E402
from embedding import get_embedder  # noqa: E402
from pipeline import run_pipeline  # noqa: E402

if args.mock:
    from demo_script import DEMO_SCRIPT  # noqa: E402
    from llm import ScriptedClient  # noqa: E402
    llm = ScriptedClient(DEMO_SCRIPT)
else:
    from llm import OpenAIClient  # noqa: E402
    api_key_path = os.path.join(HERE, "..", "LaMMA-P", "api_key.txt")
    os.environ["OPENAI_API_KEY"] = open(api_key_path).read().strip()
    llm = OpenAIClient(model=args.gpt_version)

config_obj = TaskConfig.model_validate(task_config_json)
embedder = get_embedder("hash")

print("\n🚀 ours_new 파이프라인 실행 중 (reasoning 포함)...")
result = asyncio.run(run_pipeline(config_obj, llm, embedder, verbose=not args.quiet))

print("\n✅ 완료")
print(result["joint_plan_text"])

results_dir = os.path.join(HERE, "results")
os.makedirs(results_dir, exist_ok=True)

result_record = {
    "task_n": args.task,
    "mode": args.mode,
    "task_text": task_text,
    "joint_plan_text": result["joint_plan_text"],
    "offers": result["offers"],
    "local_plans": result["local_plans"],
    "graph_ops": result["graph_ops"],
    "metrics": result["metrics"],
}

out_path = os.path.join(results_dir, f"{args.task}_result_reasoning.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(result_record, f, ensure_ascii=False, indent=2)

print(f"\n📁 저장: {out_path}")
