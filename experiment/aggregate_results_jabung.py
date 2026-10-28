"""
통합 평가 스크립트 (jabung 버전).

Track A (LLM Judge): 5개 방법론 전체, joint_plan_text 기반 TF/GF/SC/CQ 채점 (0-10 척도)
    - object.json, room.json 활용하여 실제 존재하는 객체 목록을 judge 프롬프트에 포함
    - CDA는 jabung 결과 우선 로드, Blocked/Dropped 정보 포함

사용법:
    python aggregate_results_jabung.py --task task1_abstract --run 1
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

METHODS = ["cda", "central", "independent", "lamma_p", "smart_llm"]
METHOD_NAMES = {
    "cda": "CDA",
    "central": "Centralized",
    "independent": "Independent",
    "lamma_p": "LaMMA-P",
    "smart_llm": "SMART-LLM",
}
GC_SG_METHODS = {"cda", "lamma_p"}

parser = argparse.ArgumentParser()
parser.add_argument("--task", required=True)
parser.add_argument("--gpt-version", default="gpt-4o")
parser.add_argument("--skip-grounding", action="store_true")
parser.add_argument("--run", type=int, default=1)
args = parser.parse_args()

data = load_all()
if args.task not in data["tasks"]:
    raise SystemExit(f"알 수 없는 task_n: {args.task}")

task = data["tasks"][args.task]
task_text = task["task"]
goal_states = data["goal_states"].get(args.task, {})

SCENE_DIR = os.path.join(HERE, "scene")
with open(os.path.join(SCENE_DIR, "object.json"), encoding="utf-8-sig") as f:
    obj_data = json.load(f)
with open(os.path.join(SCENE_DIR, "room.json"), encoding="utf-8-sig") as f:
    room_data = json.load(f)

obj_map = {o["object_n"]: o["object_name"] for o in obj_data["objects"]}
room_map = {r["floorplan_n"]: r for r in room_data["rooms"]}

def get_room_objects(fp):
    room = room_map.get(fp, {})
    return [obj_map[oid] for oid in room.get("object_n", []) if oid in obj_map]

def build_room_objects_text():
    rooms = task.get("rooms", {})
    lines = []
    for fp, info in rooms.items():
        room_type = room_map.get(fp, {}).get("floorplan_type", fp)
        objects = get_room_objects(fp)
        lines.append(f"- {fp} ({room_type}): {', '.join(objects)}")
    return "\n".join(lines) if lines else "(없음)"

ROOM_OBJECTS_TEXT = build_room_objects_text()

api_key_path = os.path.join(HERE, "..", "LaMMA-P", "api_key.txt")
client = OpenAI(api_key=open(api_key_path).read().strip())

gemini_api_key_path = os.path.join(HERE, "..", "LaMMA-P", "gemini_api_key.txt")
GEMINI_MODEL = "gemini-3.1-pro-preview"
judge_client = OpenAI(
    api_key=open(gemini_api_key_path).read().strip(),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# abstract task는 abstract/runN/, simple task는 simple/ 또는 run1/
if args.task.startswith("mat_"):
    results_dir = os.path.join(HERE, "results", "matthor")
elif "abstract" in args.task:
    results_dir = os.path.join(HERE, "results", "abstract", f"run{args.run}")
elif "simple" in args.task:
    results_dir = os.path.join(HERE, "results", "simple")
    _simple_cda_dir = os.path.join(HERE, "results", "simple")
else:
    results_dir = os.path.join(HERE, "results", "run1")


def load_result(method):
    if method == "cda":
        # simple task는 simple 폴더에 저장됨
        if "simple" in args.task:
            p = os.path.join(HERE, "results", "simple", f"{args.task}_multi_room_cda_jabung_result.json")
            if os.path.exists(p):
                return json.load(open(p, encoding="utf-8"))
        for pattern in [
            f"{args.task}_multi_room_cda_jabung_result.json",
            f"{args.task}_multi_room_cda_result.json",
            f"{args.task}_result.json",
            f"{args.task}_cda_result.json",
        ]:
            p = os.path.join(results_dir, pattern)
            if os.path.exists(p):
                return json.load(open(p, encoding="utf-8"))
        return None
    else:
        p = os.path.join(results_dir, f"{args.task}_{method}_result.json")
        if not os.path.exists(p):
            return None
        return json.load(open(p, encoding="utf-8"))


def build_agent_config_text():
    agents = task.get("robot", {})
    lines = []
    for label, ref in agents.items():
        robot_type = data["robots"][ref["robot_n"]]
        can = ", ".join(robot_type.get("robot_can", []))
        cannot = ", ".join(robot_type.get("robot_cannot", [])) if robot_type.get("robot_cannot") else "none specified"
        lines.append(f"- {label}: {robot_type['robot_name']} -- CAN: {can} | CANNOT: {cannot}")
    return "\n".join(lines)


AGENT_CONFIG = build_agent_config_text()

print(f"\n{'='*55}\n {args.task} 평가 시작 (jabung)\n{'='*55}")
print(f"\n{'─'*50}\n STEP 1/4  파일 로드\n{'─'*50}")

method_results = {}
for m in METHODS:
    r = load_result(m)
    method_results[m] = r
    has_plan = bool(r and r.get("joint_plan_text"))
    mark = "✅" if has_plan else "❌"
    suffix = " (jabung)" if m == "cda" and has_plan else ""
    print(f"  {mark} {METHOD_NAMES[m]}{suffix}")

print(f"\n{'─'*50}\n STEP 2/4  Track A -- LLM Judge (0-10 척도)\n{'─'*50}")

JUDGE_SYSTEM = "You are an expert evaluator for multi-agent household task planning. Respond in valid JSON only."


def judge_plan(plan_text, deadline_min=None, makespan_min=None):
    prompt = f"""Evaluate the following multi-agent robot plan.

## Task
{task_text}

## Agent Configuration (CAN/CANNOT capabilities)
{AGENT_CONFIG}

## Actual Objects in Each Room
The following objects ACTUALLY EXIST in the rooms.
{ROOM_OBJECTS_TEXT}

IMPORTANT -- Object Name Matching:
Robots describe objects using natural language from images, which may differ from canonical names.
Accept descriptive synonyms as valid references to listed objects. Examples:
- "silver faucet handle", "shower knob", "water tap" → Faucet
- "white trash bin", "garbage bin", "rubbish can" → GarbageCan  
- "toilet paper roll", "white toilet paper" → ToiletPaper
- "bath towel", "beige towel" → Towel or HandTowel
- "white bathtub" → Bathtub
Do NOT mark an object as hallucinated if a reasonable synonym maps to a listed object.
Only mark as hallucinated if NO listed object could plausibly match the description.

## Natural Language Plan
{plan_text}

## Scoring Instructions

Score each criterion on a 0-10 scale:
- 9-10: Fully satisfies the criterion
- 5-8: Partially satisfies the criterion
- 0-4: Fails to satisfy the criterion

---

### TF: Task Fulfillment -- 0~10

Evaluate whether the plan fulfills the required goals of the task using real objects from the room list.

- 8-10: Most or all required goals are achieved with concrete actions using real objects. Deadline is respected.
- 5-7: Some required goals are achieved, but notable gaps, hallucinations, or deadline violations exist.
- 0-4: Required goals are largely not achieved -- core actions missing, or deadline clearly exceeded.

Rules:
- Goals achieved via hallucinated objects (not in actual room list) count as NOT achieved.
- If the plan's total time clearly exceeds the task deadline (MISSED label), apply deduction.
- If two robots handle the same object redundantly, apply small deduction.
- Partial credit: correct intent and structure deserve credit even with minor hallucinations.
  A plan that correctly identifies goals and attempts relevant actions scores higher than
  one with no relevant actions, even if some object names are wrong.
- Cross-room collaboration moving objects toward the right destination deserves partial TF credit.

---

### GF: Grounded Feasibility -- 0~10

Evaluate whether the plan is physically executable given each robot's capabilities AND whether
each robot acts only on information it can legitimately observe or receive.

Capability checks (from Agent Configuration):
- A Mobile_Light robot performing heavy furniture pushing = violation.
- A Gripper robot leaving its room without HELP/PASS context = violation.
- Any robot performing actions beyond its stated CAN list = violation.

Grounding checks:
- Hallucinated objects (not in actual room list) = violation.
- Vague expressions: "any ...", "something", "ensure", "check", "accessible location" = violation.
- Robot using information it cannot observe (objects in other rooms it never received) = violation.
- A robot holding multiple objects simultaneously = violation.

Scoring:
- 8-10: Actions respect robot capabilities and observations. Only legitimate local or received info used.
- 5-7: Noticeable violations exist but plan is partially executable.
- 0-4: Severe violations -- hallucinations dominate, capability ignored, or cross-room assumptions.

---

### SC: Sequential Coherence -- 0~10

Evaluate whether the action sequence respects prerequisites and dependencies.

- 9-10: All prerequisite actions occur before dependent actions. No ordering violations.
- 5-8: Minor ordering violations (≤20% of actions) that don't prevent task completion.
- 0-4: Critical violations make task execution impossible, or >20% of actions violate ordering.

Violations include:
- Object used before picked up or received.
- RECEIVE before corresponding PASS.
- Robot waits for help that never arrives.
- Repeated identical actions on the same object.
- Too many physical actions in one 5-minute block (physically unrealistic).

---

### CQ: Collaboration Quality -- 0~10

Evaluate whether inter-robot collaboration is necessary, appropriate, and effective given the task type.

First determine if collaboration is REQUIRED by this task:
- REQUIRED when: objects must move between rooms, capability constraints prevent solo completion,
  or the task explicitly involves multi-room coordination.
- NOT REQUIRED when: each room's goals are fully self-contained.

Then evaluate:
- Necessity: Collaboration is used when truly needed (e.g. object in another room, heavy furniture).
  For simple tasks, unnecessary collaboration is penalized.
- Appropriateness: PASS/RECEIVE/HELP/ASK_HELP targets correct robots with correct objects.
  No "self-pass" (robot passing to itself), no circular requests, no wrong targets.
- Efficiency: No redundant collaboration steps, no unnecessary intermediate transfers.
- Completeness: Requested collaborations are actually fulfilled. Note: for CDA plans,
  "Blocked" steps are automatically detected and skipped by the system -- this is a SAFETY
  FEATURE, not a failure. Penalize only if the CORE collaboration goal is unachievable,
  not for incidental blocked steps.
- Task-type fit: Multi-room abstract tasks should show meaningful cross-room collaboration.
  Simple single-room tasks should NOT force unnecessary collaboration.

Scoring:
- 9-10: Collaboration perfectly matches task needs. All collaborative actions are justified,
  correct, and completed successfully.
- 6-8: Collaboration is mostly appropriate with minor issues (small redundancy, minor target errors).
- 3-5: Collaboration has notable issues -- unnecessary for the task type, self-pass, or key
  required collaboration missing.
- 0-2: Collaboration is absent when clearly required, OR severely inappropriate/circular.

---

Output JSON only:
{{"TF":<0-10>,"TF_reason":"...","GF":<0-10>,"GF_reason":"...","SC":<0-10>,"SC_reason":"...","CQ":<0-10>,"CQ_reason":"..."}}
"""
    response = judge_client.chat.completions.create(
        model=GEMINI_MODEL, temperature=0.0,
        messages=[{"role": "system", "content": JUDGE_SYSTEM}, {"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    log_usage("judge_jabung", args.task, response)
    raw = re.sub(r"```(json)?", "", response.choices[0].message.content.strip()).strip()
    return json.loads(raw)


judge_results = {}
for m in METHODS:
    r = method_results[m]
    plan_text = r.get("joint_plan_text") if r else None
    if plan_text and r and r.get("joint_plan_full"):
        full = r["joint_plan_full"]
        extra = []
        if "### Blocked" in full:
            blocked = full.split("### Blocked")[1].split("###")[0].strip()
            extra.append(f"### Blocked (automatically detected & skipped by CDA safety system -- not a plan failure)\n{blocked}")
        if "### Unresolved" in full:
            unresolved = full.split("### Unresolved")[1].split("###")[0].strip()
            extra.append(f"### Unresolved\n{unresolved}")
        if extra:
            plan_text = plan_text + "\n\n" + "\n\n".join(extra)
    if not plan_text:
        print(f"  {METHOD_NAMES[m]:14} -- plan 없음, 건너뜀")
        continue
    try:
        judge_results[m] = judge_plan(plan_text)
        jr = judge_results[m]
        print(f"  {METHOD_NAMES[m]:14} TF={jr['TF']} GF={jr['GF']} SC={jr['SC']} CQ={jr['CQ']}")
    except Exception as e:
        print(f"  {METHOD_NAMES[m]:14} 오류: {e}")

print(f"\n{'─'*50}\n STEP 3/4  Track B -- GC (ours, LaMMA-P만)\n{'─'*50}")


def parse_goal(pddl):
    if not pddl:
        return set()
    idx = pddl.find(":goal")
    if idx == -1:
        return set()
    tail = pddl[idx:]
    preds = re.findall(r"\(([^()]+)\)", tail)
    return set(p.strip().lower() for p in preds)


def check_state(gen_goal_preds, state_def):
    syns = [s.lower() for s in state_def.get("object_synonyms", [])]
    t = state_def["type"]
    for pred in gen_goal_preds:
        tokens = pred.split()
        if not tokens:
            continue
        head = tokens[0]
        if t == "unary" and head == state_def["predicate"]:
            if len(tokens) >= 2 and any(syn in tokens[1] for syn in syns):
                return True
        elif t == "object_at" and head == "object-at":
            if len(tokens) >= 3 and any(syn in tokens[1] for syn in syns) and state_def["location"] in tokens[2]:
                return True
    return False


total_weight = sum(s["weight"] for s in goal_states.values()) if goal_states else 0

track_b = {}
for m in GC_SG_METHODS:
    r = method_results.get(m)
    pddl_text = r.get("code_planpddl_py", "") if r and m == "lamma_p" else ""
    gen_goal = parse_goal(pddl_text)
    achieved_detail = {}
    weighted_sum = 0
    if goal_states:
        for sid, sdef in goal_states.items():
            ok = check_state(gen_goal, sdef)
            achieved_detail[sid] = ok
            if ok:
                weighted_sum += sdef["weight"]
    gc = round(weighted_sum / total_weight, 3) if total_weight else 0
    track_b[m] = {"GC": gc, "state_detail": achieved_detail}
    print(f"  {METHOD_NAMES[m]:14} GC={gc}")

for m in METHODS:
    if m not in GC_SG_METHODS:
        print(f"  {METHOD_NAMES[m]:14} -- (설계상 제외)")

print(f"\n{'─'*50}\n STEP 4/4  Object Grounding\n{'─'*50}")

existing_objects = set()
for fp in task.get("rooms", {}):
    for obj_name in get_room_objects(fp):
        existing_objects.add(obj_name.lower())


def normalize(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


existing_norm = {normalize(n) for n in existing_objects}

EXTRACT_PROMPT_TMPL = """
Read the following multi-robot plan and extract every physical object
(item, furniture, appliance) that is mentioned as something a robot
picks up, uses, moves, opens, closes, turns on/off, or otherwise interacts with.

Rules:
- Only include concrete physical objects, not abstract concepts.
- Normalize each object to its singular base form in lowercase.
- Do not include robot labels (R1, R2...) or room names.
- List each distinct object only once.

## Plan
{plan_text}

Return JSON only: {{"objects": ["object1", "object2", ...]}}
"""

grounding_results = {}
if not args.skip_grounding:
    for m in METHODS:
        r = method_results[m]
        plan_text = r.get("joint_plan_text") if r else None
        if not plan_text:
            print(f"  {METHOD_NAMES[m]:14} -- plan 없음, 건너뜀")
            continue
        try:
            response = client.chat.completions.create(
                model=args.gpt_version, temperature=0.0,
                messages=[{"role": "user", "content": EXTRACT_PROMPT_TMPL.format(plan_text=plan_text)}],
            )
            log_usage(f"{m}_grounding", args.task, response)
            raw = re.sub(r"```(json)?", "", response.choices[0].message.content.strip()).strip()
            mentioned = [o.lower().strip() for o in json.loads(raw).get("objects", [])]
            grounded, hallucinated = [], []
            for obj in mentioned:
                obj_norm = normalize(obj)
                if any(obj_norm in en or en in obj_norm for en in existing_norm):
                    grounded.append(obj)
                else:
                    hallucinated.append(obj)
            rate = round(len(grounded) / len(mentioned), 3) if mentioned else 1.0
            grounding_results[m] = {
                "mentioned_objects": mentioned,
                "grounded_objects": grounded,
                "hallucinated_objects": hallucinated,
                "grounding_rate": rate,
            }
            print(f"  {METHOD_NAMES[m]:14} Grounding={rate}  (hallucinated: {hallucinated if hallucinated else '없음'})")
        except Exception as e:
            print(f"  {METHOD_NAMES[m]:14} 오류: {e}")
else:
    print("  (--skip-grounding 지정됨, 생략)")

final = {}
for m in METHODS:
    final[m] = {
        "name": METHOD_NAMES[m],
        "track_a_llm_judge": judge_results.get(m) or "N/A",
        "track_b_gc": track_b.get(m, {}).get("GC", "N/A (설계상 제외)"),
        "track_b_state_detail": track_b.get(m, {}).get("state_detail", "N/A (설계상 제외)"),
        "object_grounding": grounding_results.get(m, "N/A"),
    }

out_json = os.path.join(results_dir, f"{args.task}_summary_jabung.json")
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(final, f, ensure_ascii=False, indent=2)

lines = [f"# {args.task} 통합 평가 결과 - jabung (0-10 척도)\n"]
lines.append("## Track A -- LLM Judge\n")
lines.append("| 방법 | TF | GF | SC | CQ |")
lines.append("|---|---|---|---|---|")
for m in METHODS:
    r = judge_results.get(m)
    if not r:
        lines.append(f"| {METHOD_NAMES[m]} | - | - | - | - |")
    else:
        lines.append(f"| {METHOD_NAMES[m]} | {r['TF']} | {r['GF']} | {r['SC']} | {r['CQ']} |")

lines.append("\n## Track B -- GC (ours, LaMMA-P만)\n")
lines.append("| 방법 | GC |")
lines.append("|---|---|")
for m in METHODS:
    gc = track_b.get(m, {}).get("GC")
    lines.append(f"| {METHOD_NAMES[m]} | {gc if gc is not None else 'N/A (설계상 제외)'} |")

lines.append("\n## Object Grounding\n")
lines.append("| 방법 | Grounding Rate | Hallucinated |")
lines.append("|---|---|---|")
for m in METHODS:
    g = grounding_results.get(m)
    if not g:
        lines.append(f"| {METHOD_NAMES[m]} | N/A | N/A |")
    else:
        hall = ", ".join(g["hallucinated_objects"]) if g["hallucinated_objects"] else "없음"
        lines.append(f"| {METHOD_NAMES[m]} | {g['grounding_rate']} | {hall} |")

out_md = os.path.join(results_dir, f"{args.task}_summary_jabung_table.md")
with open(out_md, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"\n{'='*55}\n 최종 결과\n{'='*55}")
print(f"저장: {out_json}, {out_md}\n")
print("\n".join(lines))
