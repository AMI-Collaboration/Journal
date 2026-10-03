# baseline_central.py
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
# room -> [robot_type, ...] 매핑에서 agent 번호 순서대로 배정
agents = {}  # agent_id -> {room, type, capabilities}
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

# scene info 생성
def parse_scene(scene, invisible):
    lines = ["## Scene Information"]
    for room, data in scene.items():
        agent_id = data.get("agent", "?")
        if agent_id in agents:
            rtype = agents[agent_id]["type"]
        else:
            rtype = "?"
        lines.append(f"\n### {room} — {agent_id} ({rtype})")
        visible = [o for o in data.get("objects", []) if o not in invisible.get(room, [])]
        lines.append(f"  visible: {', '.join(visible) if visible else '(none)'}")
        if invisible.get(room):
            lines.append(f"  not visible (may exist): {', '.join(invisible[room])}")
    return "\n".join(lines)

# agent info 생성
def parse_agents(agents, robot_types):
    lines = ["## Agent Configuration"]
    for aid, info in agents.items():
        caps = info["caps"]
        cap_str = ", ".join(k for k, v in caps.items() if v is True)
        lines.append(f"- {aid.upper()}: {info['room']} / {info['type']} — {cap_str}")
    return "\n".join(lines)

SCENE_INFO = parse_scene(scene, invisible)
AGENT_INFO = parse_agents(agents, robot_types)

prompt = f"""
You are a centralized planner with FULL visibility of ALL rooms and ALL agents.
Generate a coordinated natural language plan for ALL agents to complete the task.

## Task
{TASK}

{SCENE_INFO}

{AGENT_INFO}

## Output Format
[<agent_id> - <room> / <type>]
1. action
2. action

Consider collaboration between agents (passing objects between rooms via doors).
"""

print("🔄 Centralized 플랜 생성 중...")
response = client.chat.completions.create(
    model=args.gpt_version, temperature=0.0,
    messages=[{"role": "user", "content": prompt}]
)
result = response.choices[0].message.content.strip()
print("✅ 완료\n")
print(result)

out_dir = TASK_DIR / "results/central"
os.makedirs(out_dir, exist_ok=True)
with open(out_dir / "central_nl.txt", "w") as f:
    f.write(result)
print(f"\n✅ 저장: {out_dir}/central_nl.txt")