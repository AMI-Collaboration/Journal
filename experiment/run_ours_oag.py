import os
import json, argparse, asyncio, sys
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--task", required=True, help="예: task6")
parser.add_argument("--config", default=None)
parser.add_argument("--gpt-version", default="gpt-4o")
parser.add_argument("--embedder", default="sbert", choices=["sbert", "hash"])
parser.add_argument("--mock", action="store_true")
parser.add_argument("--quiet", action="store_true")
args = parser.parse_args()

TASK_DIR = Path(args.task)
COMMON_DIR = Path("common")
IMAGES_DIR = Path("../images")
OURS_DIR = Path("../ours_oag")

sys.path.insert(0, str(OURS_DIR))

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
config_key = args.config or task_info["config"]
config = robot_configs[config_key]
total = config["total"]

TYPE_TO_FOLDER = {
    "Gripper": "gripper",
    "Mobile_Light": "Mobile(light)",
    "Mobile_Heavy": "Mobile(heavy)",
}

ROOM_ORDER = ["kitchen", "living_room", "bedroom", "bathroom"]
type_counters = {"Gripper": 1, "Mobile_Light": 1, "Mobile_Heavy": 1}

agents = []
for room in ROOM_ORDER:
    if room not in config:
        continue
    scene_data = scene.get(room, {})
    visible_objs = [o for o in scene_data.get("objects", []) if o not in invisible.get(room, [])]
    hidden_objs = invisible.get(room, [])

    for robot_type in config[room]:
        idx = type_counters[robot_type]
        type_counters[robot_type] += 1

        folder = f"{TYPE_TO_FOLDER[robot_type]}{idx}"
        task_id = task_info["task_id"]
        img_base = IMAGES_DIR / f"n={total}" / folder
        images = [
            str(img_base / f"task{task_id:02d}_01.png"),
            str(img_base / f"task{task_id:02d}_02.png"),
        ]

        caps = robot_types[robot_type]
        cap_str = ", ".join(k for k, v in caps.items() if v is True)
        capability = (
            f"{robot_type} in {room}. Capabilities: {cap_str}. "
            f"Visible objects: {', '.join(visible_objs) if visible_objs else 'none'}."
        )

        agents.append({
            "capability": capability,
            "images": images,
            "hidden_info": hidden_objs,
        })

task_config_json = {"task": TASK, "agents": agents}

print(f"📋 Config: {config_key}, total agents: {total}")
for i, a in enumerate(agents, 1):
    print(f"  agent_{i}: {a['images'][0]}")

from schemas import TaskConfig
from embedding import get_embedder
from pipeline import run_pipeline

if args.mock:
    from demo_script import DEMO_SCRIPT
    from llm import ScriptedClient
    llm = ScriptedClient(DEMO_SCRIPT)
else:
    from llm import OpenAIClient
    os.environ["OPENAI_API_KEY"] = open("../LaMMA-P/api_key.txt").read().strip()
    llm = OpenAIClient(model=args.gpt_version)

config_obj = TaskConfig.model_validate(task_config_json)
embedder = get_embedder(args.embedder)

print("\n🚀 ours 파이프라인 실행 중...")
result = asyncio.run(run_pipeline(
    config_obj, llm, embedder,
    verbose=not args.quiet,
    out_dir=str(TASK_DIR / "results/ours/run_output")
))

import os
out_dir = TASK_DIR / "results/ours"
os.makedirs(out_dir, exist_ok=True)
with open(out_dir / "ours_nl.txt", "w") as f:
    f.write(result["joint_plan_text"])
print(f"\n✅ 저장: {out_dir}/ours_nl.txt")
print(result["joint_plan_text"])
