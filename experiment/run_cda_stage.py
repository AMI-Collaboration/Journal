"""
experiment: CDA_stage (현재 메인 방법론) 실행 스크립트. run_cda_gc.py와 같은 흐름이지만
CDA_stage는 유효한 패키지 이름(언더스코어)이라 importlib 해킹 없이 바로 import한다.
CDA_stage.render.render()는 이미 자연어 문장을 그대로 렌더링하므로(별도 GPT 자연어 변환 불필요),
run_cda_gc.py에 있던 _naturalize() 후처리 단계가 없다.
"""
import argparse
import asyncio
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
AAMAS_DIR = os.path.join(HERE, "..")
sys.path.insert(0, AAMAS_DIR)
sys.path.insert(0, HERE)

from loader import load_all, build_cda_task_config, log_usage_from_metrics, save_method_raw_result, final_task_dir

parser = argparse.ArgumentParser()
parser.add_argument("--task", required=True)
parser.add_argument("--mode", default="multi_room", choices=["multi_room", "single_room"])
parser.add_argument("--model", default="gpt-4o")
parser.add_argument("--deadline", type=int, default=20)
parser.add_argument("--n-robots", type=int, default=4, choices=[2, 3, 4, 6, 8])
parser.add_argument("--no-offer", action="store_true", help="ablation: Stage 2 does not see other offers")
parser.add_argument("--no-proposal", action="store_true", help="ablation: no Stage 3, code drafts every answer")
parser.add_argument("--no-graph-llm", action="store_true", help="ablation: Stage 4 rules only, no Graph LLM")
parser.add_argument("--run", type=int, default=1)
parser.add_argument("--dry-run", action="store_true", help="API 호출 없이 loader만 테스트")
parser.add_argument("--quiet", action="store_true")
args = parser.parse_args()

data = load_all()
if args.task not in data["tasks"]:
    raise SystemExit(f"알 수 없는 task: {args.task}")

task_deadline = data["tasks"].get(args.task, {}).get("deadline", args.deadline)
cfg_dict = build_cda_task_config(args.task, data, mode=args.mode, deadline_min=task_deadline, n_robots=args.n_robots)
if args.dry_run:
    print("✅ dry-run: loader 성공, API 호출 없음")
    sys.exit(0)
print(f"📋 Task: {args.task}  (robots: {len(cfg_dict['agents'])}, mode: {args.mode}, model: {args.model})")

from CDA_stage.core import TaskConfig
from CDA_stage.llm import OpenAILLM, MockLLM
from CDA_stage.pipeline import run_pipeline

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
llm = OpenAILLM(model=args.model)

print("\n🚀 CDA_stage 파이프라인 실행 중...")
_t0 = time.time()
result = asyncio.run(
    run_pipeline(
        config, llm,
        share_offers=not args.no_offer,
        use_edge_proposal=not args.no_proposal,
        use_graph_llm=not args.no_graph_llm,
        verbose=not args.quiet,
    )
)
_elapsed = round(time.time() - _t0, 1)
result["metrics"]["wall_time_sec"] = _elapsed
print("\n✅ 완료")

full_text = result["joint_plan_text"]
print(full_text.split("### Provenance")[0].strip())

result_record = {
    "task_n": args.task,
    "mode": args.mode,
    "model": args.model,
    "task_text": cfg_dict["task"],
    "joint_plan_text": full_text.split("### Provenance")[0].strip(),
    "joint_plan_full": full_text,
    "offers": result.get("offers", {}),
    "local_plans": result.get("local_plans", {}),
    "plan_meta": result.get("plan_meta", {}),
    "proposal": result.get("proposal", {}),
    "graph": result.get("graph", {}),
    "report": result.get("report", {}),
    "metrics": result.get("metrics", {}),
    "config": {
        "share_offers": not args.no_offer,
        "use_edge_proposal": not args.no_proposal,
        "use_graph_llm": not args.no_graph_llm,
        "deadline_min": cfg_dict["deadline_min"],
    },
}

suffix = ""
if args.no_offer:
    suffix += "_no_offer"
if args.no_proposal:
    suffix += "_no_proposal"
if args.no_graph_llm:
    suffix += "_no_graph_llm"

if suffix:
    task_dir = final_task_dir(args.task, n_robots=args.n_robots, run=args.run)
    out_path = os.path.join(task_dir, f"ours_cda{suffix}.json")
    io_log_path = os.path.join(task_dir, f"ours_cda{suffix}_io_log.json")
else:
    out_path = save_method_raw_result(args.task, "cda", result_record, n_robots=args.n_robots, run=args.run)
    io_log_path = os.path.join(os.path.dirname(out_path), "ours_cda_io_log.json")

if suffix:
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result_record, f, ensure_ascii=False, indent=2)
with open(io_log_path, "w", encoding="utf-8") as f:
    json.dump(llm.io_log, f, ensure_ascii=False, indent=2)
print(f"📋 IO 로그: {io_log_path}")

log_usage_from_metrics("cda", args.task, result.get("metrics", {}))
print(f"\n📁 저장: {out_path}")
