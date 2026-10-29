"""
LaMMA-P / SMART-LLM 결과를 Joint Plan 텍스트로 변환.

사용법:
    python convert_to_joint_plan.py --task task1_abstract --method lamma_p
    python convert_to_joint_plan.py --task task1_abstract --method smart_llm
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from loader import load_all  # noqa: E402

from openai import OpenAI  # noqa: E402

parser = argparse.ArgumentParser()
parser.add_argument("--task", required=True)
parser.add_argument("--method", required=True, choices=["lamma_p", "smart_llm"])
parser.add_argument("--gpt-version", default="gpt-4o")
parser.add_argument("--run", type=int, default=1)
args = parser.parse_args()

data = load_all()
task_text = data["tasks"][args.task]["task"]

if args.task.startswith("mat_"):
    result_path = os.path.join(HERE, "results", "matthor", f"{args.task}_{args.method}_result.json")
elif "simple" in args.task:
    result_path = os.path.join(HERE, "results", "simple", f"{args.task}_{args.method}_result.json")
elif "abstract" in args.task:
    result_path = os.path.join(HERE, "results", "abstract", f"run{args.run}", f"{args.task}_{args.method}_result.json")
else:
    result_path = os.path.join(HERE, "results", f"run{args.run}", f"{args.task}_{args.method}_result.json")
if not os.path.exists(result_path):
    raise SystemExit(f"결과 파일이 없습니다: {result_path}")

with open(result_path, encoding="utf-8") as f:
    method_result = json.load(f)

decomposed = method_result.get("decomposed_plan_py", "")
allocated = method_result.get("allocated_plan_py", "")

if not decomposed and not allocated:
    raise SystemExit(f"{result_path}에 decomposed_plan_py / allocated_plan_py 필드가 없습니다.")

api_key_path = os.path.join(HERE, "..", "LaMMA-P", "api_key.txt")
client = OpenAI(api_key=open(api_key_path).read().strip())

PROMPT = f"""
You are converting a multi-robot task plan into a clean, human-readable Joint Plan format.

## Task
{task_text}

## Original Decomposed Plan (pseudo-code style)
{decomposed}

## Original Allocation (robot assignment)
{allocated}

## Output Format
Use time blocks. All robots' actions are interleaved in chronological order within each block.

[0-5 min]
- R<n> [TAG] <action description>  (r<n>_s<step>)

[5-10 min]
- R<n> [TAG] <action description>  (r<n>_s<step>)

Tags:
- [LOCAL]: robot acts on its own
- [PASS]: robot hands object to another robot
- [RECEIVE]: robot receives object from another robot
- [HELP]: robot helps another robot
- [ASK_HELP]: robot requests help from another robot

Rules:
- Actions are sorted by time across ALL robots (not grouped by robot)
- Use robot labels R1, R2, R3... matching the allocation (robot1 -> R1, etc.)
- Step number is per robot, starting at 1 (r1_s1, r2_s1, ...)
- Keep descriptions short, plain English (not code/PDDL)
- Output ONLY the plan, starting with "### Joint Plan"
"""

print(f"Task: {args.task} (method={args.method})")
print("Joint Plan 변환 중...")

response = client.chat.completions.create(
    model=args.gpt_version, temperature=0.0,
    messages=[{"role": "user", "content": PROMPT}],
)
joint_plan_text = response.choices[0].message.content.strip()

print("\n" + joint_plan_text)

method_result["joint_plan_text"] = joint_plan_text
with open(result_path, "w", encoding="utf-8") as f:
    json.dump(method_result, f, ensure_ascii=False, indent=2)
print(f"\n저장: {result_path}")
