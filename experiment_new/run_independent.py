"""
experiment_new 구조를 사용해 Independent(독립형) 베이스라인을 실행.
각 로봇이 자기 room 이미지만 보고 독립적으로 계획을 짠다 (서로 공유 없음).

사용법:
    python run_independent.py --task task1_abstract
"""
import argparse
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


def generate_independent_plan(label, info):
    hidden_note = ""
    if info["hidden_info"]:
        hidden_note = f"\n  not visible in screenshot (but may exist): {', '.join(info['hidden_info'])}"

    prompt_text = f"""
You are agent {label} located in the {info['room_type']}.
You can ONLY see your own room (the attached image below). You do NOT know
what other agents are doing or seeing, and you cannot ask them for help or
send them anything -- you must act alone.

## Task
{task_text}

## Your Room: {info['room_type']}
{info['capability']}{hidden_note}

## Instructions
Look at the attached image of your room. Even though you cannot coordinate
with other robots, the shared task likely touches every room in the house.
Think concretely about what YOUR room contributes, using only objects you
can actually SEE in the image (or listed in HIDDEN INFO) and your own
capability:
- If your room plausibly needs something prepared, cleaned, turned on/off,
  opened/closed, or tidied for the task, DO IT with a concrete action naming
  a real object you can see.
- Do not describe a hypothetical action with words like "if needed" or
  "might be needed" -- decide definitively whether it is needed and act.
- Only output "No action needed" if you have genuinely looked at your room's
  image and concluded there is truly nothing relevant to the task.

## Output Format
If task has a time limit, use blocks spanning the FULL duration (e.g. 30 min
task -> [0-5 min]...[25-30 min], not just the first 10 min). Otherwise use
[Step N].

[0-5 min]  (or [Step 1])
- R<n> <action>  (r<n>_s<step>)

Rules:
- Step number resets per robot, starting at 1
- No tags like [LOCAL]/[PASS]/[HELP]
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
    plans[label] = generate_independent_plan(label, info)

result = "\n\n".join(plans.values())

print("\n✅ 완료\n")
print(result)

results_dir = os.path.join(HERE, "results")
os.makedirs(results_dir, exist_ok=True)
out_path = os.path.join(results_dir, f"{args.task}_independent_result.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump({
        "task_n": args.task,
        "method": "independent",
        "mode": args.mode,
        "task_text": task_text,
        "plans": plans,
        "joint_plan_text": result,
    }, f, ensure_ascii=False, indent=2)

print(f"\n📁 저장: {out_path}")
