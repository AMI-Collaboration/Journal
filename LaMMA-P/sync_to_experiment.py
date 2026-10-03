import os, glob, argparse

parser = argparse.ArgumentParser()
parser.add_argument("--task", required=True, help="예: task6")
args = parser.parse_args()

LOGS_DIR = "logs"
DEST_DIR = f"../experiment/{args.task}/results/lamma_p"

log_dirs = sorted(glob.glob(f"{LOGS_DIR}/*"), key=os.path.getmtime, reverse=True)
if not log_dirs:
    print("❌ 로그가 없습니다. 먼저 pddlrun_llmseparate.py를 실행하세요.")
    exit(1)

latest = log_dirs[0]
os.makedirs(DEST_DIR, exist_ok=True)

nl_path = os.path.join(latest, "combined_plan.py")
nl_text = open(nl_path).read() if os.path.exists(nl_path) else ""
with open(os.path.join(DEST_DIR, "lamma_p_nl.txt"), "w") as f:
    f.write(nl_text)

pddl_files = sorted(glob.glob(os.path.join(latest, "validated_subtask", "*.pddl")))
pddl_files = [f for f in pddl_files if not f.endswith("_plan.txt")]
pddl_text = "\n\n".join(open(p).read() for p in pddl_files)
with open(os.path.join(DEST_DIR, "lamma_p_pddl.txt"), "w") as f:
    f.write(pddl_text)

print(f"✅ 결과 저장 완료 (출처 로그: {os.path.basename(latest)})")
print(f"  - lamma_p_nl.txt   ({len(nl_text)} chars)")
print(f"  - lamma_p_pddl.txt ({len(pddl_text)} chars, {len(pddl_files)}개 로봇)")