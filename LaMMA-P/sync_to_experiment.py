"""
최신 LaMMA-P 실행 결과에서 평가에 필요한 것만 추출해 task6/results/lamma_p/에 저장
- NL 플랜 텍스트 (combined_plan.py 내용)
- PDDL 텍스트 (validated_subtask의 각 로봇 problem 파일 내용)
"""
import os, glob

LOGS_DIR = "logs"
DEST_DIR = "../experiment/task6/results/lamma_p"

log_dirs = sorted(glob.glob(f"{LOGS_DIR}/*"), key=os.path.getmtime, reverse=True)
if not log_dirs:
    print("❌ 로그가 없습니다. 먼저 pddlrun_llmseparate.py를 실행하세요.")
    exit(1)

latest = log_dirs[0]
os.makedirs(DEST_DIR, exist_ok=True)

# NL 결과 텍스트만 저장
nl_path = os.path.join(latest, "combined_plan.py")
nl_text = open(nl_path).read() if os.path.exists(nl_path) else ""
with open(os.path.join(DEST_DIR, "lamma_p_nl.txt"), "w") as f:
    f.write(nl_text)

# PDDL 결과 텍스트만 저장 (로봇별 problem 파일 내용 이어붙임)
pddl_files = sorted(glob.glob(os.path.join(latest, "validated_subtask", "*_problem.pddl")))
pddl_text = "\n\n".join(open(p).read() for p in pddl_files)
with open(os.path.join(DEST_DIR, "lamma_p_pddl.txt"), "w") as f:
    f.write(pddl_text)

print(f"✅ 결과 저장 완료 (출처 로그: {os.path.basename(latest)})")
print(f"  - lamma_p_nl.txt   ({len(nl_text)} chars)")
print(f"  - lamma_p_pddl.txt ({len(pddl_text)} chars, {len(pddl_files)}개 로봇)")
