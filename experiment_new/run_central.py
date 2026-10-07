"""
Central(중앙집중형 멀티에이전트) 베이스라인.
1단계: 중앙 LLM이 전체 상황을 보고 각 로봇에게 간단한 지시(명령)를 내림.
2단계: 각 로봇(에이전트)이 자기 몫의 지시 + 자기 방 이미지를 보고 구체적 계획을 세움.

사용법:
    python run_central.py --task task1_abstract
"""
import argparse
import base64
import io
import json
import os
import re
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


# ──────────────────────────────────────────
# STEP 1: 중앙 LLM이 로봇별 간단 지시를 생성
# ──────────────────────────────────────────
agent_lines = []
for label, info in agents.items():
    agent_lines.append(f"- {label} ({info['room_type']}): {info['capability']}")

AGENT_INFO = "\n".join(agent_lines)

central_prompt = f"""
You are a centralized dispatcher for a team of robots.

## Task
{task_text}

## Robots
{AGENT_INFO}

Give each robot a short, one-to-two sentence instruction describing its
role in completing the task, based on its room and capability. Keep each
instruction simple and high-level -- the robot itself will figure out the
specific actions.

Return JSON only:
{{"R1": "instruction", "R2": "instruction", ...}}
"""

print(f"📋 Task: {args.task}  (robots: {len(agents)}, mode: {args.mode})")
print("🔄 [1/2] 중앙 LLM이 로봇별 지시 생성 중...")

response = client.chat.completions.create(
    model=args.gpt_version, temperature=0.0,
    messages=[{"role": "user", "content": central_prompt}],
)
log_usage("central", args.task, response)
raw = re.sub(r"```(json)?", "", response.choices[0].message.content.strip()).strip()
instructions = json.loads(raw)

print("\n중앙 지시:")
for label, instr in instructions.items():
    print(f"  [{label}] {instr}")

# ──────────────────────────────────────────
# STEP 2: 각 로봇이 자기 지시 + 이미지를 보고 계획 수립
# ──────────────────────────────────────────
print("\n🔄 [2/2] 각 로봇이 자기 계획 수립 중...")

plans = {}
for label, info in agents.items():
    instruction = instructions.get(label, "No specific instruction given.")

    hidden_note = ""
    if info["hidden_info"]:
        hidden_note = f"\n(not visible in image but may exist: {', '.join(info['hidden_info'])})"

    agent_prompt = f"""
You are robot {label} in the {info['room_type']}.
Your capability: {info['capability']}

## Task
{task_text}

## Instruction from central dispatcher
{instruction}

## Your Room
Look at the attached image(s) of your room.{hidden_note}

Write a short concrete plan (2-5 steps) to carry out your instruction,
using only objects you can actually see or that are listed above.

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
        
    content_blocks = [{"type": "text", "text": agent_prompt}]
    for img_path in info["images"]:
        if os.path.exists(img_path):
            content_blocks.append({"type": "image_url", "image_url": {"url": encode_image(img_path)}})

    r = client.chat.completions.create(
        model=args.gpt_version, temperature=0.0,
        messages=[{"role": "user", "content": content_blocks}],
    )
    log_usage("central", args.task, r)
    plans[label] = r.choices[0].message.content.strip()
    print(f"  - {label} 완료")

result = "\n\n".join(plans.values())

print("\n✅ 완료\n")
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
        "central_instructions": instructions,
        "agent_plans": plans,
        "joint_plan_text": result,
    }, f, ensure_ascii=False, indent=2)

print(f"\n📁 저장: {out_path}")
