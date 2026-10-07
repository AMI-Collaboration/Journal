"""
한 task의 모든 방법론 결과를 한 화면에 모아서 보여준다:
자연어 계획 + LLM Judge 점수 + Object Grounding + 토큰/비용

사용법:
    python show_report.py --task task6_abstract
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

METHODS = ["ours", "central", "independent", "lamma_p", "smart_llm"]
METHOD_NAMES = {
    "ours": "Ours (P2P)", "central": "Centralized", "independent": "Independent",
    "lamma_p": "LaMMA-P", "smart_llm": "SMART-LLM",
}

parser = argparse.ArgumentParser()
parser.add_argument("--task", required=True)
args = parser.parse_args()

results_dir = os.path.join(HERE, "results")


def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_result(method):
    if method == "ours":
        path = os.path.join(results_dir, f"{args.task}_result.json")
    else:
        path = os.path.join(results_dir, f"{args.task}_{method}_result.json")
    return load_json(path)


summary = load_json(os.path.join(results_dir, f"{args.task}_summary.json")) or {}
usage_log = load_json(os.path.join(HERE, "usage_log.json")) or []

usage_by_method = {}
for e in usage_log:
    if e.get("task_n") != args.task:
        continue
    m = e["method"]
    usage_by_method.setdefault(m, {"calls": 0, "prompt": 0, "completion": 0})
    usage_by_method[m]["calls"] += e.get("calls", 1)
    usage_by_method[m]["prompt"] += e.get("prompt_tokens", 0)
    usage_by_method[m]["completion"] += e.get("completion_tokens", 0)

USD_PER_1M_INPUT = 2.5
USD_PER_1M_OUTPUT = 10.0
KRW_PER_USD = 1400


def to_krw(p, c):
    usd = (p / 1_000_000) * USD_PER_1M_INPUT + (c / 1_000_000) * USD_PER_1M_OUTPUT
    return usd * KRW_PER_USD


print(f"\n{'='*70}")
print(f"  {args.task}  전체 방법론 리포트")
print(f"{'='*70}")

for m in METHODS:
    r = load_result(m)
    print(f"\n{'─'*70}")
    print(f" [{METHOD_NAMES[m]}]")
    print(f"{'─'*70}")

    if not r:
        print("  (결과 없음 - 실행되지 않음)")
        continue

    plan_text = r.get("joint_plan_text")
    if plan_text:
        print("\n  ▶ 자연어 계획:")
        for line in plan_text.strip().splitlines():
            print(f"    {line}")
    else:
        print("\n  ▶ 자연어 계획: (joint_plan_text 없음)")

    judge = summary.get(m, {}).get("track_a_llm_judge")
    gc = summary.get(m, {}).get("track_b_gc")
    grounding = summary.get(m, {}).get("object_grounding")

    print("\n  ▶ 평가 점수:")
    if isinstance(judge, dict):
        print(f"    TF={judge.get('TF')}  PF={judge.get('PF')}  OC={judge.get('OC')}  SC={judge.get('SC')}  Final={judge.get('final_score')}")
    else:
        print(f"    LLM Judge: {judge}")
    print(f"    GC (goal_states 매칭): {gc}")

    print("\n  ▶ Object Grounding (실제 물건 사용 여부):")
    if isinstance(grounding, dict):
        hall = grounding.get("hallucinated_objects") or []
        print(f"    Rate={grounding.get('grounding_rate')}  Hallucinated={hall if hall else '없음'}")
    else:
        print(f"    {grounding}")

    u = usage_by_method.get(m)
    print("\n  ▶ 토큰/비용:")
    if u:
        total = u["prompt"] + u["completion"]
        cost = to_krw(u["prompt"], u["completion"])
        print(f"    호출 {u['calls']}회, {total} tokens (prompt={u['prompt']}, completion={u['completion']}) 약 {cost:.1f}원")
    else:
        print("    (기록 없음)")

print(f"\n{'='*70}\n")
