# experiment/run_smart_llm.py
import json, shutil, subprocess, argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--task", required=True, help="예: task6")
parser.add_argument("--gpt-version", default="gpt-4o")
args = parser.parse_args()

TASK_DIR = Path(args.task)
SMART_LLM_DIR = Path("../SMART-LLM")

with open(TASK_DIR / "input/scene/task.json") as f:
    task_info = json.load(f)

main_room = task_info["main_room"]
print(f"📍 main_room = {main_room} ({task_info.get('main_room_name', '')})")

src = TASK_DIR / "lamma_p_input.json"
dst = SMART_LLM_DIR / "data" / "final_test" / f"FloorPlan{main_room}.json"
shutil.copy(src, dst)
print(f"✅ {src} → {dst} 복사 완료")

cmd = [
    "python", "scripts/run_llm.py",
    "--floor-plan", str(main_room),
    "--gpt-version", args.gpt_version
]
print(f"🚀 실행: {' '.join(cmd)} (cwd={SMART_LLM_DIR})")
result = subprocess.run(cmd, cwd=SMART_LLM_DIR)

if result.returncode == 0:
    # sync 결과 자동 복사
    subprocess.run(
        ["python", "sync_to_experiment.py", "--task", args.task],
        cwd=SMART_LLM_DIR
    )