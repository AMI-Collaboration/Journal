"""
통합 평가 스크립트 (jabung 버전).

Track A (LLM Judge) 전용: 5개 방법론 전체, joint_plan_text 기반 TF/GF/SC/CQ 채점 (0-10 척도)
    - object.json, room.json 활용하여 실제 존재하는 객체 목록을 judge 프롬프트에 포함
    - CDA는 jabung 결과 우선 로드, Blocked/Dropped 정보 포함
    - Track B(GC, goal_states.json 기반)와 Object Grounding은 평가에서 제외 (LLM judge만 사용)

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
from loader import load_all, log_usage, load_method_raw_result, save_method_judge, final_task_dir  # noqa: E402
from openai import OpenAI  # noqa: E402

METHODS = ["cda", "central", "independent", "lamma_p", "smart_llm"]
METHOD_NAMES = {
    "cda": "CDA",
    "central": "Centralized",
    "independent": "Independent",
    "lamma_p": "LaMMA-P",
    "smart_llm": "SMART-LLM",
}

parser = argparse.ArgumentParser()
parser.add_argument("--task", required=True)
parser.add_argument("--run", type=int, default=1, help="repetition index (1-3), NOT robot count")
parser.add_argument("--n-robots", type=int, default=4)
args = parser.parse_args()

data = load_all()
if args.task not in data["tasks"]:
    raise SystemExit(f"알 수 없는 task_n: {args.task}")

task = data["tasks"][args.task]
task_text = task["task"]

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

gemini_api_key_path = os.path.join(HERE, "..", "LaMMA-P", "gemini_api_key.txt")
GEMINI_MODEL = "gemini-3.1-pro-preview"
judge_client = OpenAI(
    api_key=open(gemini_api_key_path).read().strip(),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

results_dir = os.path.join(HERE, "results", "matthor") if args.task.startswith("mat_") else None


def load_result(method):
    if args.task.startswith("mat_"):
        if method == "cda":
            for pattern in [f"{args.task}_multi_room_cda_jabung_result.json", f"{args.task}_multi_room_cda_result.json"]:
                p = os.path.join(results_dir, pattern)
                if os.path.exists(p):
                    return json.load(open(p, encoding="utf-8"))
            return None
        p = os.path.join(results_dir, f"{args.task}_{method}_result.json")
        return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None
    return load_method_raw_result(args.task, method, n_robots=args.n_robots, run=args.run)


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
print(f"\n{'─'*50}\n STEP 1/2  파일 로드\n{'─'*50}")

method_results = {}
for m in METHODS:
    r = load_result(m)
    method_results[m] = r
    has_plan = bool(r and r.get("joint_plan_text"))
    mark = "✅" if has_plan else "❌"
    suffix = " (jabung)" if m == "cda" and has_plan else ""
    print(f"  {mark} {METHOD_NAMES[m]}{suffix}")

print(f"\n{'─'*50}\n STEP 2/2  Track A -- LLM Judge (0-5 척도)\n{'─'*50}")

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

Score each criterion on a 0-5 scale. Each criterion below gives an explicit description for every
point from 0 to 5 -- find the single description that best matches the plan and use that score;
do not interpolate between two descriptions or average across them.

---

### TF: Task Fulfillment -- 0~5

Evaluate whether the plan fulfills the required goals of the task using real objects from the room list.

- 5: All required goals are achieved with concrete actions on real (non-hallucinated) objects, within the deadline.
- 4: Nearly all required goals are achieved; only one minor gap or a small, non-blocking hallucination remains.
- 3: Most required goals are achieved, but with a clear gap, inefficiency, or a minor deadline slip.
- 2: Some required goals are achieved, but notable gaps, hallucinations, or a deadline violation exist.
- 1: At most one required goal is achieved; most core actions are missing or the deadline is clearly exceeded.
- 0: No required goal is achieved, or the plan is absent or entirely irrelevant to the task.

Rules:
- Goals achieved via hallucinated objects (not in actual room list) count as NOT achieved.
- If the plan's total time clearly exceeds the task deadline (MISSED label), apply deduction.
- If two robots handle the same object redundantly, apply small deduction.
- Partial credit: correct intent and structure deserve credit even with minor hallucinations.
  A plan that correctly identifies goals and attempts relevant actions scores higher than
  one with no relevant actions, even if some object names are wrong.
- Cross-room collaboration moving objects toward the right destination deserves partial TF credit.
- A goal explicitly left undone because no robot present actually has the capability for it (a genuine
  capability gap, stated as such rather than silently ignored) is honest incompleteness, not a failure --
  score that single goal as merely unattempted. A plan that instead fabricates a workaround or a
  hallucinated action to paper over the same capability gap should score LOWER on that goal, not higher,
  since it falsely appears complete.

---

### GF: Grounded Feasibility -- 0~5

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
- 5: No capability or grounding violations; every action is physically executable using only
  legitimate local or received information.
- 4: At most one minor violation (e.g. one vague expression) that does not affect physical feasibility.
- 3: A few isolated violations exist, but the plan is still mostly executable as stated.
- 2: Several violations (hallucinated objects, a capability mismatch, or holding multiple objects
  at once) undermine multiple steps, though some of the plan remains executable.
- 1: Violations dominate the plan; most actions are not reliably executable given the stated capabilities.
- 0: The plan is entirely incompatible with the robots' stated capabilities/observations, or is absent.

---

### SC: Sequential Coherence -- 0~5

Evaluate whether the action sequence respects prerequisites and dependencies.

- 5: Every prerequisite action occurs before its dependent action; no ordering violations at all.
- 4: Exactly one minor ordering slip that does not prevent task completion.
- 3: A small number of minor ordering violations (roughly ≤20% of actions), none of them critical.
- 2: Several ordering violations, or one moderately disruptive violation, though the plan remains partly executable.
- 1: Most of the sequence is disordered, or a critical violation blocks execution of a core action.
- 0: The sequence is incoherent throughout, or no real action sequence is given.

Violations include:
- Object used before picked up or received.
- RECEIVE before corresponding PASS.
- Robot waits for help that never arrives.
- Repeated identical actions on the same object.
- Too many physical actions in one 5-minute block (physically unrealistic).

---

### CQ: Collaboration Quality -- 0~5

Evaluate whether inter-robot collaboration is necessary, appropriate, and effective given the task type.

First determine if collaboration is REQUIRED by this task:
- REQUIRED when: objects must move between rooms, capability constraints prevent solo completion,
  or the task explicitly involves multi-room coordination.
- NOT REQUIRED when: each room's goals are fully self-contained.

If NOT REQUIRED, a plan with ZERO collaboration is not missing anything -- correctly recognizing
that no robot needs another robot's help, and leaving collaboration out entirely, is itself the
right call and should score as high as any other criterion-satisfying plan (do not dock points
just because no PASS/RECEIVE/HELP/ASK_HELP appears). Only penalize the NOT-REQUIRED case when the
plan collaborates anyway (forced/unnecessary coordination), never for correctly staying solo.

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
- 5: Collaboration perfectly matches task needs -- either all collaborative actions are justified,
  correct, and completed successfully, OR collaboration was correctly recognized as unnecessary
  and the plan has none at all.
- 4: Collaboration (or correctly having none) is appropriate with only one very minor issue,
  such as slight redundancy that doesn't affect the outcome.
- 3: Collaboration is mostly appropriate but has one clear minor issue (a slightly wrong target,
  one redundant transfer).
- 2: Notable issues -- unnecessary collaboration for the task type, a self-pass, or one key
  required collaboration missing, though the rest of the plan is otherwise reasonable.
- 1: Collaboration is largely absent when required, or is mostly inappropriate/circular throughout.
- 0: Collaboration is completely absent despite being clearly required, or is severely
  circular/nonsensical throughout the plan.

---

Output JSON only:
{{"TF":<0-5>,"TF_reason":"...","GF":<0-5>,"GF_reason":"...","SC":<0-5>,"SC_reason":"...","CQ":<0-5>,"CQ_reason":"..."}}
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

lines = [f"# {args.task} 통합 평가 결과 - jabung (0-5 척도)\n"]
lines.append("## Track A -- LLM Judge\n")
lines.append("| 방법 | TF | GF | SC | CQ |")
lines.append("|---|---|---|---|---|")
for m in METHODS:
    r = judge_results.get(m)
    if not r:
        lines.append(f"| {METHOD_NAMES[m]} | - | - | - | - |")
    else:
        lines.append(f"| {METHOD_NAMES[m]} | {r['TF']} | {r['GF']} | {r['SC']} | {r['CQ']} |")

if args.task.startswith("mat_"):
    out_json = os.path.join(results_dir, f"{args.task}_summary_jabung.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({m: {"name": METHOD_NAMES[m], "track_a_llm_judge": judge_results.get(m) or "N/A"} for m in METHODS},
                   f, ensure_ascii=False, indent=2)
    out_md = os.path.join(results_dir, f"{args.task}_summary_jabung_table.md")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    saved_paths = f"{out_json}, {out_md}"
else:
    saved_paths = []
    for m in METHODS:
        if m in judge_results:
            saved_paths.append(save_method_judge(args.task, m, judge_results[m], n_robots=args.n_robots, run=args.run))
    task_dir = final_task_dir(args.task, n_robots=args.n_robots, run=args.run)
    out_md = os.path.join(task_dir, "judge_summary_table.md")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    saved_paths.append(out_md)
    saved_paths = ", ".join(saved_paths)

print(f"\n{'='*55}\n 최종 결과\n{'='*55}")
print(f"저장: {saved_paths}\n")
print("\n".join(lines))
