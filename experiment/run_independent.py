"""
Independent(독립형) 베이스라인.
각 로봇이 자기 room 이미지만 보고 독립적으로 계획을 짠다.

사용법:
    python run_independent.py --task task1_abstract
"""
import argparse
import time as _time_module
_t0 = _time_module.time()
import base64
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from loader import load_all, build_agent_inputs, log_usage  # noqa: E402

from openai import OpenAI  # noqa: E402

parser = argparse.ArgumentParser()
parser.add_argument("--task", required=True)
parser.add_argument("--mode", default="multi_room", choices=["multi_room", "single_room"])
parser.add_argument("--gpt-version", default="gpt-4o")
parser.add_argument("--run", type=int, default=1)
parser.add_argument("--n-robots", type=int, default=4)
args = parser.parse_args()

data = load_all()
if args.task not in data["tasks"]:
    raise SystemExit(f"알 수 없는 task: {args.task}")

task_text = data["tasks"][args.task]["task"]
agents = build_agent_inputs(args.task, data, mode=args.mode)

api_key_path = os.path.join(HERE, "..", "LaMMA-P", "api_key.txt")
client = OpenAI(api_key=open(api_key_path).read().strip())


def encode_image(path, max_side=512, quality=70):
    from PIL import Image
    img = Image.open(path).convert("RGB")
    w, h = img.size
    scale = max_side / max(w, h)
    if scale < 1:
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/jpeg;base64,{b64}"


def generate_plan(label, info):
    hidden_note = ""
    if info["hidden_info"]:
        hidden_note = f"\n  not visible in screenshot (but may exist): {', '.join(info['hidden_info'])}"

    prompt_text = f"""
You are agent {label} located in the {info['room_type']}.
You can ONLY see your own room. You cannot coordinate with other robots.

## Task
{task_text}

## Your capability
{info['capability']}{hidden_note}

Look at the attached image of your room and write a concrete plan using
only objects you can actually see (or listed above).

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
- Step number is per robot, starting at 1 (r1_s1, r2_s1, ...)
- Use the full time range of the task
"""
    content_blocks = [{"type": "text", "text": prompt_text}]
    for img_path in info["images"]:
        if os.path.exists(img_path):
            content_blocks.append({"type": "image_url", "image_url": {"url": encode_image(img_path)}})

    response = client.chat.completions.create(
        model=args.gpt_version, temperature=0.0,
        messages=[{"role": "user", "content": content_blocks}],
    )
    log_usage("independent", args.task, response)
    return response.choices[0].message.content.strip()


print(f"📋 Task: {args.task}  (robots: {len(agents)}, mode: {args.mode})")
print("🔄 Independent 플랜 생성 중...")

plans = {}
for label, info in agents.items():
    print(f"  - {label} ({info['room_type']})...")
    plans[label] = generate_plan(label, info)

# 각 로봇 계획을 하나로 합치는 단계
newline = "\n"
merge_prompt = f"""
You are given individual robot plans. Merge them into a single joint plan sorted chronologically.

## Task
{task_text}

## Individual Plans
{newline.join(f"=== {label} ===" + newline + plan for label, plan in plans.items())}

## Output Format
Use time blocks. All robots actions are interleaved in chronological order within each block.

[0-5 min]
- R<n> [TAG] <action description>  (r<n>_s<step>)

Tags:
- [LOCAL]: robot acts on its own
- [PASS]: robot hands object to another robot
- [RECEIVE]: robot receives object from another robot
- [HELP]: robot helps another robot
- [ASK_HELP]: robot requests help from another robot

Rules:
- Merge ALL robots actions into ONE chronological plan
- Do NOT change any actions, only reorder by time
- Step number is per robot, starting at 1 (r1_s1, r2_s1, ...)
- Output ONLY the merged plan starting with ### Joint Plan
"""

_wall_time = __import__("time").time() - _t0
merge_r = client.chat.completions.create(
    model=args.gpt_version, temperature=0.0,
    messages=[{"role": "user", "content": merge_prompt}],
)
log_usage("independent", args.task, merge_r)
result = merge_r.choices[0].message.content.strip()
print("\n✅ 완료\n")
print(result)

if "simple" in args.task:
    results_dir = os.path.join(HERE, "results", "simple")
elif args.task.startswith("mat_"):
    results_dir = os.path.join(HERE, "results", "matthor")
elif "abstract" in args.task:
    results_dir = os.path.join(HERE, "results", "abstract", f"run{args.run}")
else:
    results_dir = os.path.join(HERE, "results", f"run{args.run}")
os.makedirs(results_dir, exist_ok=True)
out_path = os.path.join(results_dir, f"{args.task}_independent_result.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump({
        "task_n": args.task, "method": "independent", "mode": args.mode,
        "task_text": task_text, "plans": plans, "joint_plan_text": result,
        "metrics": {"wall_time_sec": _wall_time if "_wall_time" in dir() else 0, "prompt_tokens": merge_r.usage.prompt_tokens, "completion_tokens": merge_r.usage.completion_tokens},
    }, f, ensure_ascii=False, indent=2)
print(f"\n📁 저장: {out_path}")
