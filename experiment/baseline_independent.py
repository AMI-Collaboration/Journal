# baseline_independent.py
import os, json, argparse
from pathlib import Path
from openai import OpenAI

parser = argparse.ArgumentParser()
parser.add_argument("--task", required=True, help="예: task6")
parser.add_argument("--gpt-version", default="gpt-4o")
args = parser.parse_args()

TASK_DIR = Path(args.task)
COMMON_DIR = Path("common")
client = OpenAI(api_key=open('../LaMMA-P/api_key.txt').read().strip())

# 데이터 로드
with open(TASK_DIR / "input/scene/task.json") as f:
    task_info = json.load(f)
with open(TASK_DIR / "input/scene/scene.json") as f:
    scene = json.load(f)
with open(TASK_DIR / "input/scene/invisible_objects.json") as f:
    invisible = json.load(f)
with open(COMMON_DIR / "robot_configs.json") as f:
    robot_configs = json.load(f)
with open(COMMON_DIR / "robot_types.json") as f:
    robot_types = json.load(f)

TASK = task_info["command_en"]
config_key = task_info["config"]
config = robot_configs[config_key]

# agent 정보 자동 생성
agents = {}
agent_counter = 1
ROOM_ORDER = ["kitchen", "living_room", "bedroom", "bathroom"]
for room in ROOM_ORDER:
    if room not in config:
        continue
    for robot_type in config[room]:
        agent_id = f"r{agent_counter}"
        agents[agent_id] = {
            "room": room,
            "type": robot_type,
            "caps": robot_types[robot_type]
        }
        agent_counter += 1

# scene에서 agent_id로 room 데이터 찾기
room_by_agent = {data["agent"]: (room, data) for room, data in scene.items()}

def generate_independent_plan(agent_id, agent_info):
    room = agent_info["room"]
    rtype = agent_info["type"]
    caps = agent_info["caps"]

    # scene에서 해당 방 오브젝트 가져오기
    scene_data = scene.get(room, {})
    visible = [o for o in scene_data.get("objects", []) if o not in invisible.get(room, [])]
    invis = invisible.get(room, [])

    cap_str = "\n".join(f"  - {k}: {v}" for k, v in caps.items())

    prompt = f"""
You are agent {agent_id} ({rtype}) located in the {room}.
You can ONLY see your own room. You do NOT know what other agents are doing or seeing.

## Task
{TASK}

## Your Room: {room}
  visible objects (from your camera): {', '.join(visible) if visible else '(none)'}
  not visible in screenshot (but may exist): {', '.join(invis) if invis else '(none)'}

## Your Capabilities
{cap_str}

## Output Format
[{agent_id} - {room} / {rtype}]
1. action
2. action

If nothing relevant in your room, output: [{agent_id} - No action needed]
"""
    response = client.chat.completions.create(
        model=args.gpt_version, temperature=0.0,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

print("🔄 Independent 플랜 생성 중...")
plans = {}
for agent_id, agent_info in agents.items():
    print(f"  - {agent_id} ({agent_info['room']} / {agent_info['type']})...")
    plans[agent_id] = generate_independent_plan(agent_id, agent_info)

result = "\n\n".join(plans.values())
print("\n✅ 완료\n")
print(result)

out_dir = TASK_DIR / "results/independent"
os.makedirs(out_dir, exist_ok=True)
with open(out_dir / "independent_nl.txt", "w") as f:
    f.write(result)
print(f"\n✅ 저장: {out_dir}/independent_nl.txt")