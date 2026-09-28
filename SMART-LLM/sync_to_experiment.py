"""
최신 SMART-LLM 실행 결과에서 NL 플랜만 추출해 task6/results/smart_llm/에 저장
(SMART-LLM은 PDDL을 생성하지 않으므로 NL만 처리)
"""
import os, glob

LOGS_DIR = "logs"
DEST_DIR = "../experiment/task6/results/smart_llm"

log_dirs = sorted(glob.glob(f"{LOGS_DIR}/*"), key=os.path.getmtime, reverse=True)
if not log_dirs:
    print("❌ 로그가 없습니다.")
    exit(1)

latest = log_dirs[0]
os.makedirs(DEST_DIR, exist_ok=True)

nl_path = os.path.join(latest, "code_plan.py")
nl_text = open(nl_path).read() if os.path.exists(nl_path) else ""
with open(os.path.join(DEST_DIR, "smart_llm_nl.txt"), "w") as f:
    f.write(nl_text)

print(f"✅ 결과 저장 완료 (출처: {os.path.basename(latest)})")
print(f"  - smart_llm_nl.txt ({len(nl_text)} chars)")
