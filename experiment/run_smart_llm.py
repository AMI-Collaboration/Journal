"""
SMART-LLM 베이스라인 실행 스크립트.

사용법:
    python run_smart_llm.py --task task1_abstract
"""
import argparse
import glob
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from loader import load_all, build_lamma_p_input  # noqa: E402

SMART_LLM_DIR = os.path.join(HERE, "..", "SMART-LLM")

parser = argparse.ArgumentParser()
parser.add_argument("--task", required=True)
parser.add_argument("--gpt-version", default="gpt-4o")
parser.add_argument("--run", type=int, default=1)
parser.add_argument("--n-robots", type=int, default=4)
args = parser.parse_args()

data = load_all()
if args.task not in data["tasks"]:
    raise SystemExit(f"알 수 없는 task: {args.task}")

smart_input = build_lamma_p_input(args.task, data)
main_fp = smart_input.pop("_main_room_fp")
main_room_num = main_fp.replace("FP", "")

print(f"📋 Task: {args.task}")
print(f"  main_room = FloorPlan{main_room_num}")
print(f"  robot list = {smart_input['robot list']}")

dst = os.path.join(SMART_LLM_DIR, "data", "final_test", f"FloorPlan{main_room_num}.json")
with open(dst, "w", encoding="utf-8") as f:
    f.write(json.dumps(smart_input) + "\n")
print(f"✅ 저장: {dst}")

cmd = [
    "python", "scripts/run_llm.py",
    "--floor-plan", str(main_room_num),
    "--gpt-version", args.gpt_version,
]
print(f"🚀 실행: {' '.join(cmd)} (cwd={SMART_LLM_DIR})")
_t0 = __import__("time").time()
result = subprocess.run(cmd, cwd=SMART_LLM_DIR, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
print(result.stdout)
_smart_output = result.stdout or ""

if result.returncode != 0:
    print(f"⚠️ SMART-LLM 실행이 비정상 종료됨 (code={result.returncode})")
else:
    print("✅ SMART-LLM 실행 완료")

    logs_dir = os.path.join(SMART_LLM_DIR, "logs")
    log_folders = sorted(glob.glob(os.path.join(logs_dir, "*")), key=os.path.getmtime)

    _t1 = __import__("time").time()
    import re as _re3
    _pt2, _ct2 = 0, 0
    _m2 = _re3.search(r'\[TOKEN_USAGE\] prompt=(\d+) completion=(\d+)', _smart_output if "_smart_output" in dir() else "")
    if _m2: _pt2, _ct2 = int(_m2.group(1)), int(_m2.group(2))
    result_record = {"task_n": args.task, "method": "smart_llm", "metrics": {"wall_time_sec": _t1 - _t0 if "_t0" in dir() else 0, "prompt_tokens": _pt2, "completion_tokens": _ct2}}

    if log_folders:
        latest = log_folders[-1]
        result_record["log_folder"] = latest
        for fname in ["log.txt", "decomposed_plan.py", "allocated_plan.py", "code_plan.py"]:
            fpath = os.path.join(latest, fname)
            if os.path.exists(fpath):
                with open(fpath, encoding="utf-8") as f:
                    result_record[fname.replace(".", "_")] = f.read()
    else:
        print("⚠️ 로그 폴더를 찾지 못함")

    if "simple" in args.task:
        results_dir = os.path.join(HERE, "results", "simple")
    elif args.task.startswith("mat_"):
        results_dir = os.path.join(HERE, "results", "matthor")
    elif "abstract" in args.task:
        results_dir = os.path.join(HERE, "results", "abstract", f"run{args.run}")
    else:
        results_dir = os.path.join(HERE, "results", f"run{args.run}")
    os.makedirs(results_dir, exist_ok=True)
    out_path = os.path.join(results_dir, f"{args.task}_smart_llm_result.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result_record, f, ensure_ascii=False, indent=2)
    print(f"📁 저장: {out_path}")
