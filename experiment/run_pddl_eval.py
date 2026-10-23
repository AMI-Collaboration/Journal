"""
ours(또는 다른 방법)의 자연어 계획을 PDDL로 변환하고,
fast-downward(PS: 풀리는지)와 VAL(PV: 규칙 위반 없는지)로 검증한다.

사용법:
    python run_pddl_eval.py --task task1_abstract --method ours
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from loader import load_all, build_agent_inputs  # noqa: E402

from openai import OpenAI  # noqa: E402

FD_BIN = os.path.join(HERE, "..", "LaMMA-P", "downward", "fast-downward.py")
VAL_BIN = os.path.join(HERE, "..", "VAL", "bin", "Validate")
DOMAIN_FILE = os.path.join(HERE, "pddl", "domain_typed.pddl")

parser = argparse.ArgumentParser()
parser.add_argument("--task", required=True, help="예: task1_abstract")
parser.add_argument("--method", default="ours", choices=["ours", "central", "independent"], help="PDDL 변환할 대상")
parser.add_argument("--mode", default="multi_room", choices=["multi_room", "single_room"])
parser.add_argument("--gpt-version", default="gpt-4o")
args = parser.parse_args()

data = load_all()
if args.task not in data["tasks"]:
    raise SystemExit(f"알 수 없는 task_n: {args.task}")

task_text = data["tasks"][args.task]["task"]
agents = build_agent_inputs(args.task, data, mode=args.mode)

if args.method == "ours":
    result_path = os.path.join(HERE, "results", f"{args.task}_result.json")
else:
    result_path = os.path.join(HERE, "results", f"{args.task}_{args.method}_result.json")

if not os.path.exists(result_path):
    raise SystemExit(f"{args.method} 결과 파일이 없습니다: {result_path}")

with open(result_path, encoding="utf-8") as f:
    method_result = json.load(f)
nl_plan = method_result.get("joint_plan_text") or method_result.get("plan_text")

api_key_path = os.path.join(HERE, "..", "LaMMA-P", "api_key.txt")
client = OpenAI(api_key=open(api_key_path).read().strip())


def parse_scene_and_agents():
    lines_agent = ["## Agent Configuration"]
    all_rooms = sorted(set(info["room_type"] for info in agents.values()))

    for label, info in agents.items():
        atype_raw = info["capability"].split(" in ")[0].strip()
        atype = {"Gripper": "gripper", "Mobile_Light": "mobile_light", "Mobile_Heavy": "mobile_heavy"}.get(atype_raw, "mobile_light")
        access = "fixed -- cannot move, NO can-access" if atype == "gripper" else ", ".join(all_rooms)
        lines_agent.append(f"  - {label}: {info['room_type']} / {atype} / can-access: {access} / type-annotation: {label} - {atype}")

    return "\n".join(lines_agent), all_rooms


AGENT_INFO, ALL_ROOMS = parse_scene_and_agents()

RULES = f"""
## PDDL Writing Rules (STRICT -- violating these causes the plan to be unsolvable)

1. Domain name must be exactly: household-multiagent

2. TYPE SAFETY IS CRITICAL. Every predicate has a fixed argument type. NEVER mix types:
   - (is-on ?o - item), (is-off ?o - item), (is-open ?o - item), (is-closed ?o - item),
     (is-sliced ?o - item), (is-filled ?o - item), (is-cooked ?o - item),
     (is-ready ?o - item), (is-clean ?o - item)
     --> the argument MUST be an object of type "item" (a physical object like bread, cup, remote).
     --> NEVER apply these predicates to a room name (kitchen, living_room, bedroom, bathroom).
         "Clean the living room" / "tidy up the room" / "organize the space" means:
         pick 1-3 concrete items that are actually in that room (from the Scene/Plan)
         and mark EACH of them (is-clean <item>) individually. Do NOT invent
         (is-clean living_room) -- rooms are never valid arguments for these predicates.
   - (agent-at ?a - agent ?r - room): first argument is an agent id (r1, r2...), second is a room.
   - (object-at ?o - item ?r - room): first argument is an item, second is a room.
   - (can-access ?a - agent ?r - room): first argument is a MOBILE agent only (never a gripper).

3. :objects must include ALL of the following WITH type annotations:
   - Agents with their types (from Agent Configuration type-annotation field)
   - All rooms mentioned in the plan: room_name - room
   - Task-relevant objects only: obj_name - item
   - Containers used as destinations (fridge, cabinet): container_name - item
   - Do NOT include other receptacles (countertop, table, shelf, holder, sofa, etc.) as separate objects
     unless the plan explicitly manipulates them as items.
   - All object names must be lowercase with underscores
   - If the same object type exists in multiple rooms, append room id as suffix
   - Each object name must be unique -- no duplicates allowed

4. :init must include:
   - Agent positions: (agent-at ?a ?r) for each agent, matching the Agent Configuration's room
   - Agent hand states: (agent-free ?a) for each agent
   - Navigation permissions: for EVERY mobile agent (mobile_light or mobile_heavy), you MUST add
     (can-access ?a ?r) for every room listed in its "can-access" field above
     (this is required or the agent can never move -- this is the most common mistake, do not skip it).
     Gripper agents get NO can-access facts at all.
   - Object positions: (object-at ?o ?r) -- ?r must be a ROOM only, never a receptacle
   - Containers initial state: (is-closed ?container) if initially closed
   - Powered objects currently ON: (is-on ?o)
   - Objects currently OPEN: (is-open ?o)
   - Do NOT include is_gripper, is_mobile, is_mobile_heavy

5. :goal must:
   - Be wrapped in (and ...)
   - Include ONLY final states that are DIFFERENT from the initial state. Do NOT repeat facts
     that are already true in :init and never change (e.g. if bread stays in the kitchen the whole
     plan, do not list (object-at bread kitchen) as a goal -- only list objects that actually MOVE
     or CHANGE STATE as a result of the plan).
   - Every goal predicate must satisfy the type rules in section 2 above. In particular, never write
     (is-clean <room_name>); always use a concrete item.
   - NEVER use (not ...) anywhere in :goal -- use positive predicates only:
       (is-off ?o) for toggled-off objects
       (is-closed ?o) for closed objects
       (inside ?o ?container) for objects stored inside a container
       (object-at ?o ?r) for moved objects -- ?r must be a ROOM only
       (is-clean ?o) for a specific item that was wiped/tidied/put away
   - Do NOT include: passed, received, object-at-door
   - If after removing unchanged facts the goal would be empty, pick the single most important
     state change implied by the task and plan, and include that.

6. Before finalizing, re-check every literal in :init and :goal against the predicate
   signatures in rule 2. If a literal's argument type does not match, fix or remove it.

7. Output PDDL code only. No explanations, no comments, no markdown.
"""

PROMPT = f"""
You are a PDDL generator for a multi-agent household environment.
Read the natural language plan carefully and generate a problem.pddl.

## Task
{task_text}

## Natural Language Plan
{nl_plan}

{AGENT_INFO}

All rooms in this scenario: {', '.join(ALL_ROOMS)}

{RULES}

## Step-by-step
1. Read the plan and identify which SPECIFIC ITEMS change state or location. Ignore vague
   room-level phrases ("tidy the room") -- translate them into the concrete items involved.
2. Generate :goal with only those changed final states using (and ...), following all type rules.
3. Generate :objects with type annotations and :init from the Agent Configuration, including
   can-access for every mobile agent.
4. Output the complete problem.pddl starting with (define (problem {args.task}) ...)
"""

print(f"Task: {args.task} (method={args.method})")
print("GPT-4o로 PDDL 변환 중...")

response = client.chat.completions.create(
    model=args.gpt_version, temperature=0.0,
    messages=[{"role": "user", "content": PROMPT}],
)
pddl_out = response.choices[0].message.content.strip()
pddl_out = re.sub(r"```(pddl)?", "", pddl_out).strip()
pddl_out = re.sub(r"\(define\s+\(problem\s+\S+\)", f"(define (problem {args.task})", pddl_out)

problem_path = os.path.join(HERE, "pddl", f"{args.task}_problem.pddl")
with open(problem_path, "w", encoding="utf-8") as f:
    f.write(pddl_out)
print(f"PDDL 저장: {problem_path}")
print(pddl_out)

print("\nfast-downward로 Plan Solvability(PS) 검증 중...")
pddl_dir = os.path.join(HERE, "pddl")
for f in glob.glob(os.path.join(pddl_dir, "sas_plan*")) + [os.path.join(pddl_dir, "output.sas")]:
    if os.path.exists(f):
        os.remove(f)

result = subprocess.run(
    ["python3", FD_BIN, "--alias", "lama-first", DOMAIN_FILE, problem_path],
    capture_output=True, text=True, timeout=120, cwd=pddl_dir,
)
print(result.stdout[-1500:])
if result.returncode not in (0, 12):
    print("--- STDERR ---")
    print(result.stderr[-1000:])

plan_files = sorted(glob.glob(os.path.join(pddl_dir, "sas_plan*")))
plan_found = bool(plan_files)
actions = []
plan_file = None
if plan_found:
    plan_file = plan_files[0]
    with open(plan_file) as f:
        plan_content = f.read()
    actions = [l.strip() for l in plan_content.strip().splitlines() if l.strip() and not l.startswith(";")]
    print(f"PS 성공! ({len(actions)}개 액션)")
    for i, a in enumerate(actions, 1):
        print(f"  {i:2d}. {a}")
else:
    print("PS 실패 (unsolvable)")

val_valid = val_invalid = False
violations = []
if plan_found and os.path.exists(VAL_BIN):
    print("\nVAL로 Plan Validity(PV) 검증 중...")
    r = subprocess.run([VAL_BIN, "-v", DOMAIN_FILE, problem_path, plan_file], capture_output=True, text=True)
    val_out = r.stdout + r.stderr
    print(val_out)
    val_valid = "Plan valid" in val_out
    val_invalid = "Plan invalid" in val_out or "Failed" in val_out
    violations = re.findall(r"(Error|Warning|Failed)[^\n]+", val_out)
elif plan_found:
    print("VAL 바이너리를 찾지 못함 -- PV 생략")
else:
    print("Plan 없음 -- VAL 생략")

g = re.search(r":goal\s*\(and(.+)", pddl_out, re.DOTALL)
goal_count = len(re.findall(r"\(\w", g.group(1))) if g else 1

if not plan_found:
    pf, notes = 1, ["Plan 탐색 실패 (PS=0)"]
else:
    pf = 5
    notes = ["PS: Plan 탐색 성공 (+5)"]
    if val_valid:
        pf += 3
        notes.append("PV: VAL 검증 통과 (+3)")
    elif val_invalid:
        pf -= 2
        notes.append(f"PV: VAL 위반 {len(violations)}건 (-2)")
    else:
        notes.append("PV: VAL 결과 불명확")
    pf += 2 if len(actions) <= goal_count * 1.5 else 1
    notes.append(f"액션 효율: {len(actions)}개 / goal {goal_count}개")
    pf = max(1, min(10, pf))

print("\n" + "=" * 55)
print(f"  {args.task} ({args.method}) PDDL 검증 결과")
print("=" * 55)
print(f"  PS (Plan Solvability): {'성공' if plan_found else '실패'}")
print(f"  PV (Plan Validity)   : {'Valid' if val_valid else ('Invalid' if val_invalid else '불명확')}")
print(f"  PF-PDDL 점수         : {pf} / 10")
for n in notes:
    print(f"    - {n}")

result_record = {
    "task_n": args.task,
    "method": args.method,
    "pddl_problem": pddl_out,
    "ps_success": plan_found,
    "pv_valid": val_valid,
    "pv_invalid": val_invalid,
    "violations": violations,
    "actions": actions,
    "goal_count": goal_count,
    "pf_pddl_score": pf,
    "notes": notes,
}

results_dir = os.path.join(HERE, "results")
os.makedirs(results_dir, exist_ok=True)
out_path = os.path.join(results_dir, f"{args.task}_{args.method}_pddl_eval.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(result_record, f, ensure_ascii=False, indent=2)

print(f"\n저장: {out_path}")
