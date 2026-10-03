# run_all.py
import argparse, subprocess, sys
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--task", required=True, help="예: task6")
parser.add_argument("--gpt-version", default="gpt-4o")
parser.add_argument("--skip", nargs="*", default=[], 
                    choices=["central", "independent", "ours", "lamma_p", "smart_llm"],
                    help="건너뛸 모듈")
args = parser.parse_args()

EXPERIMENT_DIR = Path(__file__).parent
LAMMA_P_DIR = EXPERIMENT_DIR / "../LaMMA-P"
SMART_LLM_DIR = EXPERIMENT_DIR / "../SMART-LLM"

def run(label, cmd, cwd=None):
    if label in args.skip:
        print(f"⏭️  {label} 건너뜀")
        return
    print(f"\n{'='*50}")
    print(f"🚀 {label} 실행 중...")
    print(f"{'='*50}")
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        print(f"❌ {label} 실패 (returncode={result.returncode})")
    else:
        print(f"✅ {label} 완료")

# 1. Centralized baseline
run("central", [
    sys.executable, "baseline_central.py",
    "--task", args.task,
    "--gpt-version", args.gpt_version
], cwd=EXPERIMENT_DIR)

# 2. Independent baseline
run("independent", [
    sys.executable, "baseline_independent.py",
    "--task", args.task,
    "--gpt-version", args.gpt_version
], cwd=EXPERIMENT_DIR)

# 3. Ours
run("ours", [
    sys.executable, "run_ours.py",
    "--task", args.task,
    "--gpt-version", args.gpt_version,
    "--quiet"
], cwd=EXPERIMENT_DIR)

# 4. LaMMA-P 실행 + sync
run("lamma_p", [
    sys.executable, "run_lamma_p.py",
    "--task", args.task,
    "--gpt-version", args.gpt_version
], cwd=EXPERIMENT_DIR)

run("lamma_p", [
    sys.executable, "sync_to_experiment.py",
    "--task", args.task
], cwd=LAMMA_P_DIR)

# 5. SMART-LLM 실행 + sync
run("smart_llm", [
    sys.executable, "run_smart_llm.py",
    "--task", args.task,
    "--gpt-version", args.gpt_version
], cwd=EXPERIMENT_DIR)

run("smart_llm", [
    sys.executable, "sync_to_experiment.py",
    "--task", args.task
], cwd=SMART_LLM_DIR)

print(f"\n{'='*50}")
print(f"전체 완료! task={args.task}")
print(f"{'='*50}")