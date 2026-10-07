"""
experiment_new 구조의 통합 평가 스크립트.

Track A (LLM Judge): 5개 방법론 전체, joint_plan_text 기반 TF/PF/OC/SC 채점
    OC는 "정보 제약(자기 방 정보만 사용)을 실제로 지켰는가"를 엄격히 평가.
    중앙집중형(central)처럼 전지적 시점으로 설계된 방법론은 OC에서 낮게 나옴.
Track B (GC): ours, lamma_p만 -- PDDL :goal 파싱 후 goal_states.json과 비교
Object Grounding: 5개 방법론 전체 -- 계획에 언급된 물건이 실제 room에 존재하는지

사용법:
    python aggregate_results.py --task task1_abstract
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

METHODS = ["ours", "central", "independent", "lamma_p", "smart_llm"]
METHOD_NAMES = {
    "ours": "Ours (P2P)",
    "central": "Centralized",
    "independent": "Independent",
    "lamma_p": "LaMMA-P",
    "smart_llm": "SMART-LLM",
}
GC_SG_METHODS = {"ours", "lamma_p"}

parser = argparse.ArgumentParser()
parser.add_argument("--task", required=True, help="예: task1_abstract")
parser.add_argument("--gpt-version", default="gpt-4o")
parser.add_argument("--skip-grounding", action="store_true", help="Object Grounding 검증 생략(비용 절감)")
args = parser.parse_args()

data = load_all()
if args.task not in data["tasks"]:
    raise SystemExit(f"알 수 없는 task_n: {args.task}")

task = data["tasks"][args.task]
task_text = task["task"]
goal_states = data["goal_states"].get(args.task, {})

api_key_path = os.path.join(HERE, "..", "LaMMA-P", "api_key.txt")
client = OpenAI(api_key=open(api_key_path).read().strip())

results_dir = os.path.join(HERE, "results")


def load_result(method):
    path = os.path.join(results_dir, f"{args.task}_{method}_result.json")
    if method == "ours":
        alt_path = os.path.join(results_dir, f"{args.task}_result.json")
        if os.path.exists(alt_path):
            path = alt_path
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_agent_config_text():
    agents = task.get("robot", {})
    lines = []
    for label, ref in agents.items():
        robot_type = data["robots"][ref["robot_n"]]
        can = ", ".join(robot_type.get("robot_can", []))
        lines.append(f"- {label}: {robot_type['robot_name']} — CAN: {can}")
    return "\n".join(lines)


AGENT_CONFIG = build_agent_config_text()

# ─────────────────────────────────────────────
# STEP 1: 파일 로드
# ─────────────────────────────────────────────
print(f"\n{'='*55}\n {args.task} 평가 시작\n{'='*55}")
print(f"\n{'─'*50}\n STEP 1/4  파일 로드\n{'─'*50}")

method_results = {}
for m in METHODS:
    r = load_result(m)
    method_results[m] = r
    has_plan = bool(r and r.get("joint_plan_text"))
    mark = "✅" if has_plan else "❌"
    print(f"  {mark} {METHOD_NAMES[m]}")

# ─────────────────────────────────────────────
# STEP 2: Track A — LLM Judge (OC 엄격화)
# ─────────────────────────────────────────────
print(f"\n{'─'*50}\n STEP 2/4  Track A — LLM Judge\n{'─'*50}")

JUDGE_SYSTEM = "You are an expert evaluator for multi-agent household task planning. Respond in valid JSON only."


def judge_plan(plan_text):
    prompt = f"""Evaluate the multi-agent natural language plan.

## Task
{task_text}

## Agent Configuration
{AGENT_CONFIG}

## Natural Language Plan
{plan_text}

Score each 1-10:

TF: Task Fulfillment — does the plan fully achieve the task's goal?

PF: Plan Feasibility — is it executable given each agent's capabilities?

OC: Observability Consistency — Does this plan reflect a TRUE DISTRIBUTED
setting where each robot only knows its own room and cannot see other
rooms unless explicitly told via a message/request? A plan where any
robot's actions depend on knowledge of another room it was never told
about (including knowledge of hidden/invisible objects in another
robot's room, or coordination that implies one mind sees everything at
once) should score LOW on OC, regardless of how well-organized or
efficient the plan looks. A single centralized planner writing for all
robots at once, with full visibility into every room including hidden
objects, should score LOW here even if the resulting plan reads well --
OC measures whether the INFORMATION CONSTRAINT of a distributed system
was respected, not whether the plan is well-organized. A plan with
explicit ASK_HELP/HELP/PASS/RECEIVE-style requests between robots (each
robot only acting on messages it actually received) should score HIGH.

SC: Sequential Coherence — is the step ordering logically correct, and
does the plan reach a fully resolved conclusion (no unresolved/pending
requests left hanging)?

IMPORTANT -- do not be misled by confident or polished narration. Before
scoring TF and SC, check each individual action line for:
- Does it reference a SPECIFIC object actually available in that robot's
  room/scene? Or does it use vague, hedging, or non-committal language
  ("standby", "assist as necessary", "if needed", "might be needed",
  "wait in case") that commits to no concrete action?
- Is the object's claimed location plausible for that room type, or does
  the plan assume an object exists without any evidence (e.g. moving
  something to "the desk" in a room where no desk was ever mentioned)?
A plan padded with vague standby/assist steps, or that references objects
with no evidence they exist in that room, should score LOW on TF and SC
even if the overall narrative sounds coherent, confident, and complete.
Fluent, well-formatted writing is not evidence of a good plan.

Output JSON only:
{{"TF":<1-10>,"TF_reason":"...","PF":<1-10>,"PF_reason":"...",
  "OC":<1-10>,"OC_reason":"...","SC":<1-10>,"SC_reason":"..."}}
"""
    response = client.chat.completions.create(
        model=args.gpt_version, temperature=0.0,
        messages=[{"role": "system", "content": JUDGE_SYSTEM}, {"role": "user", "content": prompt}],
    )
    log_usage("judge", args.task, response)
    raw = re.sub(r"```(json)?", "", response.choices[0].message.content.strip()).strip()
    r = json.loads(raw)
    r["final_score"] = round(r["TF"] * 0.30 + r["PF"] * 0.20 + r["OC"] * 0.35 + r["SC"] * 0.15, 2)
    return r


judge_results = {}
for m in METHODS:
    r = method_results[m]
    plan_text = r.get("joint_plan_text") if r else None
    if not plan_text:
        print(f"  {METHOD_NAMES[m]:14} — plan 없음, 건너뜀")
        continue
    try:
        judge_results[m] = judge_plan(plan_text)
        print(f"  {METHOD_NAMES[m]:14} Score={judge_results[m]['final_score']}  (TF={judge_results[m]['TF']} PF={judge_results[m]['PF']} OC={judge_results[m]['OC']} SC={judge_results[m]['SC']})")
    except Exception as e:
        print(f"  {METHOD_NAMES[m]:14} ❌ 오류: {e}")

# ─────────────────────────────────────────────
# STEP 3: Track B — GC (ours+lamma_p만)
# ─────────────────────────────────────────────
print(f"\n{'─'*50}\n STEP 3/4  Track B — GC (ours, LaMMA-P만)\n{'─'*50}")


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


def get_pddl_for_method(method, result):
    if method == "ours":
        pddl_eval_path = os.path.join(results_dir, f"{args.task}_ours_pddl_eval.json")
        if os.path.exists(pddl_eval_path):
            with open(pddl_eval_path, encoding="utf-8") as f:
                return json.load(f).get("pddl_problem", "")
        return ""
    elif method == "lamma_p":
        return result.get("code_planpddl_py", "") if result else ""
    return ""


total_weight = sum(s["weight"] for s in goal_states.values()) if goal_states else 0

track_b = {}
for m in GC_SG_METHODS:
    r = method_results.get(m)
    pddl_text = get_pddl_for_method(m, r)
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
        print(f"  {METHOD_NAMES[m]:14} — (설계상 제외)")

# ─────────────────────────────────────────────
# STEP 4: Object Grounding (5개 전체, 참고용)
# ─────────────────────────────────────────────
print(f"\n{'─'*50}\n STEP 4/4  Object Grounding (실제 존재하는 물건 사용 여부)\n{'─'*50}")

existing_objects = set()
for fp in task["room"]:
    room = data["rooms"].get(fp)
    if not room:
        continue
    for oid in room.get("object_n", []):
        obj = data["objects"].get(oid)
        if obj:
            existing_objects.add(obj["object_name"].lower())


def normalize(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


existing_norm = {normalize(n) for n in existing_objects}

EXTRACT_PROMPT_TMPL = """
Read the following multi-robot plan and extract every physical object
(item, furniture, appliance) that is mentioned as something a robot
picks up, uses, moves, opens, closes, turns on/off, or otherwise
interacts with.

Rules:
- Only include concrete physical objects, not abstract concepts.
- Do NOT count the contents of a container as a separate object (e.g. if
  a cup is "filled" or "poured", count only "cup", not "water"/"drink"/"coffee").
- Normalize each object to its singular base form in lowercase
  (e.g. "the cups" -> "cup", "a Coffee Table" -> "coffeetable").
- Do not include robot labels (R1, R2...) or room names (kitchen, etc.).
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
            print(f"  {METHOD_NAMES[m]:14} — plan 없음, 건너뜀")
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
                "mentioned_objects": mentioned, "grounded_objects": grounded,
                "hallucinated_objects": hallucinated, "grounding_rate": rate,
            }
            print(f"  {METHOD_NAMES[m]:14} Grounding={rate}  (hallucinated: {hallucinated if hallucinated else '없음'})")
        except Exception as e:
            print(f"  {METHOD_NAMES[m]:14} ❌ 오류: {e}")
else:
    print("  (--skip-grounding 지정됨, 생략)")

# ─────────────────────────────────────────────
# 결과 저장
# ─────────────────────────────────────────────
final = {}
for m in METHODS:
    final[m] = {
        "name": METHOD_NAMES[m],
        "track_a_llm_judge": judge_results.get(m) or "N/A",
        "track_b_gc": track_b.get(m, {}).get("GC", "N/A (설계상 제외)"),
        "track_b_state_detail": track_b.get(m, {}).get("state_detail", "N/A (설계상 제외)"),
        "object_grounding": grounding_results.get(m, "N/A"),
    }

out_json = os.path.join(results_dir, f"{args.task}_summary.json")
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(final, f, ensure_ascii=False, indent=2)

lines = [f"# {args.task} 통합 평가 결과\n"]
lines.append("## Track A — LLM Judge (5개 방법론 공통, OC=정보제약 준수 여부 엄격 평가)\n")
lines.append("| 방법 | TF | PF | OC | SC | Final |")
lines.append("|---|---|---|---|---|---|")
for m in METHODS:
    r = judge_results.get(m)
    if not r:
        lines.append(f"| {METHOD_NAMES[m]} | - | - | - | - | N/A |")
    else:
        lines.append(f"| {METHOD_NAMES[m]} | {r['TF']} | {r['PF']} | {r['OC']} | {r['SC']} | {r['final_score']} |")

lines.append("\n## Track B — GC (ours, LaMMA-P만)\n")
lines.append("| 방법 | GC |")
lines.append("|---|---|")
for m in METHODS:
    gc = track_b.get(m, {}).get("GC")
    lines.append(f"| {METHOD_NAMES[m]} | {gc if gc is not None else 'N/A (설계상 제외)'} |")

lines.append("\n## Object Grounding — 실제 존재하는 물건 사용 여부 (참고용, 점수 미반영)\n")
lines.append("| 방법 | Grounding Rate | Hallucinated |")
lines.append("|---|---|---|")
for m in METHODS:
    g = grounding_results.get(m)
    if not g:
        lines.append(f"| {METHOD_NAMES[m]} | N/A | N/A |")
    else:
        hall = ", ".join(g["hallucinated_objects"]) if g["hallucinated_objects"] else "없음"
        lines.append(f"| {METHOD_NAMES[m]} | {g['grounding_rate']} | {hall} |")

out_md = os.path.join(results_dir, f"{args.task}_summary_table.md")
with open(out_md, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"\n{'='*55}\n 최종 결과\n{'='*55}")
print(f"저장: {out_json}, {out_md}\n")
print("\n".join(lines))
