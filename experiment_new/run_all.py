"""
experiment_new 구조에서 5개 방법론을 모두 실행하는 통합 스크립트.

사용법:
    python run_all.py --task task1_abstract
    python run_all.py --task task1_abstract --skip lamma_p smart_llm
"""
import argparse
import subprocess
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))

parser = argparse.ArgumentParser()
parser.add_argument("--task", required=True, help="예: task1_abstract")
parser.add_argument("--gpt-version", default="gpt-4o")
parser.add_argument(
    "--skip", nargs="*", default=[],
    choices=["central", "independent", "ours", "lamma_p", "smart_llm"],
    help="건너뛸 방법론"
)
args = parser.parse_args()


def run(label, cmd):
    if label in args.skip:
        print(f"건너뜀: {label}")
        return
    print(f"\n{'='*50}")
    print(f"실행 중: {label}")
    print(f"{'='*50}")
    result = subprocess.run(cmd, cwd=HERE)
    if result.returncode != 0:
        print(f"실패: {label} (returncode={result.returncode})")
    else:
        print(f"완료: {label}")


run("central", [sys.executable, "run_central.py", "--task", args.task, "--gpt-version", args.gpt_version])
run("independent", [sys.executable, "run_independent.py", "--task", args.task, "--gpt-version", args.gpt_version])
run("ours", [sys.executable, "run_ours.py", "--task", args.task, "--gpt-version", args.gpt_version, "--quiet"])
run("lamma_p", [sys.executable, "run_lamma_p.py", "--task", args.task, "--gpt-version", args.gpt_version])
run("smart_llm", [sys.executable, "run_smart_llm.py", "--task", args.task, "--gpt-version", args.gpt_version])

print(f"\n{'='*50}")
print(f"전체 완료! task={args.task}")
print(f"{'='*50}")
