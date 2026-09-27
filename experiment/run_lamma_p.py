"""
task.json의 main_room 값을 읽어, 해당 FloorPlan에 lamma_p_input.json을 배치하고
LaMMA-P 파이프라인을 자동 실행하는 래퍼.
사용법: python run_lamma_p.py --task task6
"""
import json, shutil, subprocess, argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--task", required=True, help="예: task6")
parser.add_argument("--gpt-version", default="gpt-4o")
args = parser.parse_args()

TASK_DIR = Path(args.task)
LAMMA_P_DIR = Path("../LaMMA-P")

# 1) task.json에서 main_room 읽기
with open(TASK_DIR / "task_scene" / "task.json") as f:
    task_info = json.load(f)

main_room = task_info["main_room"]
print(f"📍 main_room = {main_room} ({task_info.get('main_room_name', '')})")

# 2) lamma_p_input.json → LaMMA-P/data/final_test/FloorPlan{main_room}.json 로 복사
src = TASK_DIR / "lamma_p_input.json"
dst = LAMMA_P_DIR / "data" / "final_test" / f"FloorPlan{main_room}.json"
shutil.copy(src, dst)
print(f"✅ {src} → {dst} 복사 완료")

# 3) LaMMA-P 파이프라인 실행
cmd = [
    "python", "scripts/pddlrun_llmseparate.py",
    "--floor-plan", str(main_room),
    "--gpt-version", args.gpt_version
]
print(f"🚀 실행: {' '.join(cmd)} (cwd={LAMMA_P_DIR})")
subprocess.run(cmd, cwd=LAMMA_P_DIR)
