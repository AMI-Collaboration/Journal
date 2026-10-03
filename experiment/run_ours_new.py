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
OURS_DIR = Path("../ours_new")

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
        can_list = [k for k, v in caps.items() if v is True]
        cannot_list = [k for k, v in caps.items() if v is False]

        mobility_note = ""
        if caps.get("can_navigate") is False:
            mobility_note = (
                " This robot is FIXED IN PLACE and can never move to "
                "another room. To pass an item to another robot, that "
                "other robot must come to this robot's own room first -- "
                "this robot can never travel elsewhere to deliver anything."
            )

        capability = (
            f"{robot_type} in {room}. "
            f"CAN: {', '.join(can_list) if can_list else 'none'}. "
            f"CANNOT: {', '.join(cannot_list) if cannot_list else 'none'}."
            f"{mobility_note} "
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
    llm = OpenAIClient(model=args.gpt_version, temperature=0)

config_obj = TaskConfig.model_validate(task_config_json)
embedder = get_embedder(args.embedder)

print("\n🚀 ours 파이프라인 실행 중...")
result = asyncio.run(run_pipeline(
    config_obj, llm, embedder,
    verbose=not args.quiet,
    out_dir=str(TASK_DIR / "results/ours_new/run_output")
))

import os
# ── R1, R2... 라벨을 "방/타입"으로 치환 (가독성) ──
label_map = {}
for i, a in enumerate(agents, 1):
    # a["capability"]는 "{robot_type} in {room}. ..." 형식
    first_sentence = a["capability"].split(".")[0]
    room_type_label = first_sentence.replace(" in ", "/").strip()
    label_map[f"R{i}"] = f"[{room_type_label}]"

import re as _re
readable_text = result["joint_plan_text"]
for rid, label in sorted(label_map.items(), key=lambda x: -len(x[0])):
    plain_label = label.strip("[]")
    # "[R1]" 형태 -> "[Gripper/kitchen]"
    readable_text = readable_text.replace(f"[{rid}]", label)
    # 문장 속 "R1" 단독 단어 -> "Gripper/kitchen" (단어 경계 기준)
    readable_text = _re.sub(rf"\b{rid}\b", plain_label, readable_text)

out_dir = TASK_DIR / "results/ours_new"
os.makedirs(out_dir, exist_ok=True)
with open(out_dir / "ours_nl.txt", "w") as f:
    f.write(readable_text)
print(f"\n✅ 저장: {out_dir}/ours_nl.txt")
print(readable_text)

# ── 단계별 reasoning 모아서 별도 txt로 저장 ──
reasoning_lines = ["### Reasoning Trace (Offer -> Local Plan -> Graph Reasoning)", ""]

reasoning_lines.append("## Stage 1: Offer")
for aid, offer in result["offers"].items():
    label = aid
    # label_map은 "R1" 형태 키를 쓰므로 agent_1 -> R1로 변환
    idx = aid.split("_")[-1]
    rid = f"R{idx}"
    if rid in label_map:
        label = label_map[rid].strip("[]")
    reasoning = offer.get("reasoning") or "(no reasoning given)"
    reasoning_lines.append(f"- [{label}] {reasoning}")
reasoning_lines.append("")

reasoning_lines.append("## Stage 2: Local Plan")
for aid, plan in result["local_plans"].items():
    label = aid
    idx = aid.split("_")[-1]
    rid = f"R{idx}"
    if rid in label_map:
        label = label_map[rid].strip("[]")
    reasoning = plan.get("reasoning") or "(no reasoning given)"
    reasoning_lines.append(f"- [{label}] {reasoning}")
reasoning_lines.append("")

reasoning_lines.append("## Stage 3: Graph Reasoning (ops)")
graph_ops = result.get("graph_ops", [])
if not graph_ops:
    reasoning_lines.append("- (no ops proposed; rule layer graph was already consistent)")
else:
    for op in graph_ops:
        op_name = op.get("op", "?")
        status = op.get("status", "?")
        reason = op.get("reason") or "(no reason given)"
        detail = {k: v for k, v in op.items() if k not in {"op", "status", "why", "reason"}}
        reasoning_lines.append(f"- [{op_name} / {status}] {detail} -- {reason}")
        if op.get("why"):
            reasoning_lines.append(f"    (system note: {op['why']})")
reasoning_lines.append("")

reasoning_text = "\n".join(reasoning_lines)
with open(out_dir / "ours_reasoning.txt", "w") as f:
    f.write(reasoning_text)
print(f"\n✅ 저장: {out_dir}/ours_reasoning.txt")
print(reasoning_text)

# ── 토큰 사용량 로그 (누적, 실행마다 append) ──
import datetime
usage_log_path = TASK_DIR / "results/ours_new/token_usage.jsonl"
usage_record = {
    "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
    "task": args.task,
    "config": config_key,
    "gpt_version": args.gpt_version,
    "mock": args.mock,
    **result["metrics"]["llm"],  # calls, prompt_tokens, completion_tokens, calls_by_stage
}
with open(usage_log_path, "a", encoding="utf-8") as f:
    f.write(json.dumps(usage_record, ensure_ascii=False) + "\n")

print(
    f"\n📊 토큰 사용: prompt={usage_record['prompt_tokens']}, "
    f"completion={usage_record['completion_tokens']}, "
    f"calls={usage_record['calls']}  "
    f"(누적 로그: {usage_log_path})"
)
