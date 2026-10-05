"""
experiment_new 구조를 사용해 Central(중앙집중형) 베이스라인을 실행.

사용법:
    python run_central.py --task task1_abstract
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from loader import load_all, build_agent_inputs  # noqa: E402

from openai import OpenAI  # noqa: E402

parser = argparse.ArgumentParser()
parser.add_argument("--task", required=True, help="예: task1_abstract")
parser.add_argument("--mode", default="multi_room", choices=["multi_room", "single_room"])
parser.add_argument("--gpt-version", default="gpt-4o")
args = parser.parse_args()

data = load_all()
if args.task not in data["tasks"]:
    raise SystemExit(f"알 수 없는 task_n: {args.task}")

task_text = data["tasks"][args.task]["task"]
agents = build_agent_inputs(args.task, data, mode=args.mode)

api_key_path = os.path.join(HERE, "..", "LaMMA-P", "api_key.txt")
client = OpenAI(api_key=open(api_key_path).read().strip())

agent_lines = []
for label, info in agents.items():
    agent_lines.append(f"- {label} ({info['room_type']}): {info['capability']}")
    if info["hidden_info"]:
        agent_lines.append(f"  (not visible in screenshot, may exist: {', '.join(info['hidden_info'])})")

AGENT_INFO = "\n".join(agent_lines)

prompt = f"""
You are a centralized planner with FULL visibility of ALL rooms and ALL agents.
Generate a coordinated natural language plan for ALL agents to complete the task.

## Task
{task_text}

## Agents
{AGENT_INFO}

## Output Format
[<agent_id> - <room> / <type>]
1. action
2. action

Consider collaboration between agents (passing objects between rooms via doors).
"""

print(f"Task: {args.task}  (robots: {len(agents)}, mode: {args.mode})")
print("Centralized 플랜 생성 중...")

response = client.chat.completions.create(
    model=args.gpt_version, temperature=0.0,
    messages=[{"role": "user", "content": prompt}],
)
result = response.choices[0].message.content.strip()

print("\n완료\n")
print(result)

results_dir = os.path.join(HERE, "results")
os.makedirs(results_dir, exist_ok=True)
out_path = os.path.join(results_dir, f"{args.task}_central_result.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump({
        "task_n": args.task,
        "method": "central",
        "mode": args.mode,
        "task_text": task_text,
        "plan_text": result,
    }, f, ensure_ascii=False, indent=2)

print(f"\n저장: {out_path}")
