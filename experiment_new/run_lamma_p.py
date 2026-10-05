"""
experiment_new 구조를 사용해 LaMMA-P를 실행하는 스크립트.

사용법:
    python run_lamma_p.py --task task1_abstract
"""
import sys
import types

# Windows에서 ai2thor(Unix 전용 모듈 의존)를 import하기 위한 더미 모듈 등록
for _mod in ("tty", "termios", "fcntl"):
    if _mod not in sys.modules:
        sys.modules[_mod] = types.ModuleType(_mod)

import argparse
import json
import os
import shutil
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from loader import load_all, build_lamma_p_input  # noqa: E402

LAMMA_P_DIR = os.path.join(HERE, "..", "LaMMA-P")

parser = argparse.ArgumentParser()
parser.add_argument("--task", required=True, help="예: task1_abstract")
parser.add_argument("--gpt-version", default="gpt-4o")
args = parser.parse_args()

data = load_all()
if args.task not in data["tasks"]:
    raise SystemExit(f"알 수 없는 task_n: {args.task}")

lamma_input = build_lamma_p_input(args.task, data)
main_fp = lamma_input.pop("_main_room_fp")
main_room_num = main_fp.replace("FP", "")

print(f"📋 Task: {args.task}")
print(f"  main_room = FloorPlan{main_room_num}")
print(f"  robot list = {lamma_input['robot list']}")

dst = os.path.join(LAMMA_P_DIR, "data", "final_test", f"FloorPlan{main_room_num}.json")
with open(dst, "w", encoding="utf-8") as f:
    f.write(json.dumps(lamma_input) + "\n")
print(f"✅ 저장: {dst}")

cmd = [
    "python", "scripts/pddlrun_llmseparate.py",
    "--floor-plan", str(main_room_num),
    "--gpt-version", args.gpt_version,
]
print(f"🚀 실행: {' '.join(cmd)} (cwd={LAMMA_P_DIR})")
result = subprocess.run(cmd, cwd=LAMMA_P_DIR)

if result.returncode != 0:
    print(f"⚠️ LaMMA-P 실행이 비정상 종료됨 (code={result.returncode})")
else:
    print("✅ LaMMA-P 실행 완료")

    import glob
    logs_dir = os.path.join(LAMMA_P_DIR, "logs")
    log_folders = sorted(glob.glob(os.path.join(logs_dir, "*")), key=os.path.getmtime)

    result_record = {
        "task_n": args.task,
        "method": "lamma_p",
    }

    if log_folders:
        latest = log_folders[-1]
        result_record["log_folder"] = latest

        for fname in ["log.txt", "decomposed_plan.py", "allocated_plan.py", "code_plan.py", "code_planpddl.py", "combined_plan.py", "validated_plan.py"]:
            fpath = os.path.join(latest, fname)
            if os.path.exists(fpath):
                with open(fpath, encoding="utf-8") as f:
                    result_record[fname.replace(".", "_")] = f.read()
    else:
        print("⚠️ 로그 폴더를 찾지 못함")

    results_dir = os.path.join(HERE, "results")
    os.makedirs(results_dir, exist_ok=True)
    out_path = os.path.join(results_dir, f"{args.task}_lamma_p_result.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result_record, f, ensure_ascii=False, indent=2)
    print(f"📁 저장: {out_path}")
