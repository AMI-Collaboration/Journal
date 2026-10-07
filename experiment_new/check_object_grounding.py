"""
최종 Joint Plan(joint_plan_text)에 언급된 물건이, 그 task에 배정된
모든 room의 실제 object_n 목록(= 존재하는 물건)에 있는지 검증한다.
(물건 이동은 고려하지 않음 - task 전체 room 물건을 합쳐서 하나의 풀로 봄)

사용법:
    python check_object_grounding.py --task task1_abstract --method ours
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from loader import load_all, log_usage  # noqa: E402

from openai import OpenAI  # noqa: E402

parser = argparse.ArgumentParser()
parser.add_argument("--task", required=True, help="예: task1_abstract")
parser.add_argument("--method", required=True,
                     choices=["ours", "central", "independent", "lamma_p", "smart_llm"])
parser.add_argument("--gpt-version", default="gpt-4o")
args = parser.parse_args()

data = load_all()
if args.task not in data["tasks"]:
    raise SystemExit(f"알 수 없는 task_n: {args.task}")

task = data["tasks"][args.task]

results_dir = os.path.join(HERE, "results")
if args.method == "ours":
    result_path = os.path.join(results_dir, f"{args.task}_result.json")
else:
    result_path = os.path.join(results_dir, f"{args.task}_{args.method}_result.json")

if not os.path.exists(result_path):
    raise SystemExit(f"결과 파일이 없습니다: {result_path}")

with open(result_path, encoding="utf-8") as f:
    method_result = json.load(f)

plan_text = method_result.get("joint_plan_text")
if not plan_text:
    raise SystemExit(f"{result_path}에 joint_plan_text가 없습니다.")

# ── task에 배정된 모든 room의 물건 이름을 합쳐서 "존재하는 물건 풀" 생성 ──
existing_objects = set()
for fp in task["room"]:
    room = data["rooms"].get(fp)
    if not room:
        continue
    for oid in room.get("object_n", []):
        obj = data["objects"].get(oid)
        if obj:
            existing_objects.add(obj["object_name"].lower())

print(f"Task: {args.task} (method={args.method})")
print(f"존재하는 물건 풀: {len(existing_objects)}개 (task에 배정된 모든 room 합산)")

# ── GPT로 plan_text에서 물건 이름 추출 ──
api_key_path = os.path.join(HERE, "..", "LaMMA-P", "api_key.txt")
client = OpenAI(api_key=open(api_key_path).read().strip())

EXTRACT_PROMPT = f"""
Read the following multi-robot plan and extract every physical object
(item, furniture, appliance) that is mentioned as something a robot
picks up, uses, moves, opens, closes, turns on/off, or otherwise
interacts with.

Rules:
- Only include concrete physical objects, not abstract concepts
  (ignore things like "the room", "the task", "the plan").
- Normalize each object to its singular base form in lowercase
  (e.g. "the cups" -> "cup", "a Coffee Table" -> "coffeetable").
- Do not include robot labels (R1, R2...) or room names (kitchen, etc.)
  themselves as objects.
- List each distinct object only once.

## Plan
{plan_text}

Return JSON only, in this exact format:
{{"objects": ["object1", "object2", ...]}}
"""

response = client.chat.completions.create(
    model=args.gpt_version, temperature=0.0,
    messages=[{"role": "user", "content": EXTRACT_PROMPT}],
)
log_usage(f"{args.method}_grounding", args.task, response)

raw = re.sub(r"```(json)?", "", response.choices[0].message.content.strip()).strip()
extracted = json.loads(raw)
mentioned_objects = [o.lower().strip() for o in extracted.get("objects", [])]

print(f"\n계획에서 추출된 물건: {len(mentioned_objects)}개")
print(f"  {mentioned_objects}")

# ── 대조: 부분일치 허용 (예: "coffeetable" vs "coffee table" 표기 차이 흡수) ──
def normalize(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())

existing_norm = {normalize(n): n for n in existing_objects}

grounded = []
hallucinated = []
for obj in mentioned_objects:
    obj_norm = normalize(obj)
    if any(obj_norm in en or en in obj_norm for en in existing_norm):
        grounded.append(obj)
    else:
        hallucinated.append(obj)

total = len(mentioned_objects)
grounding_rate = round(len(grounded) / total, 3) if total else 1.0

print(f"\n{'='*55}")
print(f"  Object Grounding 결과")
print(f"{'='*55}")
print(f"  Grounded (존재함)     : {len(grounded)}/{total}  {grounded}")
print(f"  Hallucinated (없음)   : {len(hallucinated)}/{total}  {hallucinated}")
print(f"  Grounding Rate        : {grounding_rate}")

result_record = {
    "task_n": args.task,
    "method": args.method,
    "existing_objects_pool_size": len(existing_objects),
    "mentioned_objects": mentioned_objects,
    "grounded_objects": grounded,
    "hallucinated_objects": hallucinated,
    "grounding_rate": grounding_rate,
}

out_path = os.path.join(results_dir, f"{args.task}_{args.method}_grounding.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(result_record, f, ensure_ascii=False, indent=2)

print(f"\n저장: {out_path}")
