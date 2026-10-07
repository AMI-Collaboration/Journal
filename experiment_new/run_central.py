"""
experiment_new 구조를 사용해 Central(중앙집중형) 베이스라인을 실행.
중앙 LLM이 모든 로봇의 room 이미지를 한 번에 보고, 각 로봇에게 내릴 명령을 생성한다.

사용법:
    python run_central.py --task task1_abstract
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


# 전체 agent 정보 + 이미지를 한 번에 프롬프트에 담음 (중앙집중형)
agent_lines = []
image_blocks = []
for label, info in agents.items():
    agent_lines.append(f"- {label} ({info['room_type']}): {info['capability']}")
    if info["hidden_info"]:
        agent_lines.append(f"  (not visible in screenshot, may exist: {', '.join(info['hidden_info'])})")
    agent_lines.append(f"  (see attached image(s) labeled [{label}] below for this robot's room)")

    for img_path in info["images"]:
        if os.path.exists(img_path):
            image_blocks.append({"type": "text", "text": f"[{label} room image]"})
            image_blocks.append({"type": "image_url", "image_url": {"url": encode_image(img_path)}})

AGENT_INFO = "\n".join(agent_lines)

prompt_text = f"""
You are a centralized planner with FULL visibility of ALL rooms and ALL agents.
You can see every robot's room through the attached images below.
Generate a coordinated natural language plan for ALL agents to complete the task,
grounding every action in objects you can actually SEE in the images -- do not
invent or guess at objects that might be needed; only use what is visible.

## Task
{task_text}

## Agents
{AGENT_INFO}

## Output Format
[<agent_id> - <room> / <type>]
1. action (name a concrete object you actually saw in that robot's image)
2. action

Consider collaboration between agents (passing objects between rooms via doors).
"""

content_blocks = [{"type": "text", "text": prompt_text}] + image_blocks

print(f"📋 Task: {args.task}  (robots: {len(agents)}, mode: {args.mode}, images: {len(image_blocks)//2})")
print("🔄 Centralized 플랜 생성 중...")

response = client.chat.completions.create(
    model=args.gpt_version, temperature=0.0,
    messages=[{"role": "user", "content": content_blocks}],
)
log_usage("central", args.task, response)
result = response.choices[0].message.content.strip()

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
        "joint_plan_text": result,
    }, f, ensure_ascii=False, indent=2)

print(f"\n📁 저장: {out_path}")
