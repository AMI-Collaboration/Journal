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
parser.add_argument("--task", required=True, help="예: task1_abstract")
parser.add_argument("--gpt-version", default="gpt-4o")
parser.add_argument("--skip-grounding", action="store_true", help="Object Grounding 검증 생략(비용 절감)")
parser.add_argument("--run", type=int, default=1, help="실험 반복 회차")
args = parser.parse_args()

data = load_all()
if args.task not in data["tasks"]:
    raise SystemExit(f"알 수 없는 task_n: {args.task}")

task = data["tasks"][args.task]
task_text = task["task"]
goal_states = data["goal_states"].get(args.task, {})

api_key_path = os.path.join(HERE, "..", "LaMMA-P", "api_key.txt")
client = OpenAI(api_key=open(api_key_path).read().strip())
# LLM Judge 전용: Gemini (OpenAI 호환 엔드포인트)
gemini_api_key_path = os.path.join(HERE, "..", "LaMMA-P", "gemini_api_key.txt")
GEMINI_MODEL = "gemini-3.1-pro-preview"
judge_client = OpenAI(
    api_key=open(gemini_api_key_path).read().strip(),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

results_dir = os.path.join(HERE, "results", f"run{args.run}")


def load_result(method):
    path = os.path.join(results_dir, f"{args.task}_{method}_result.json")
    if method == "cda":
        alt_path = os.path.join(results_dir, f"{args.task}_result.json")
        alt_path2 = os.path.join(results_dir, f"{args.task}_multi_room_cda_result.json")
        alt_path3 = os.path.join(results_dir, f"{args.task}_multi_room_cda_jabung_result.json")
        if os.path.exists(alt_path):
            path = alt_path
        elif os.path.exists(alt_path2):
            path = alt_path2
        elif os.path.exists(alt_path3):
            path = alt_path3
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

## Scoring Instructions

Score each criterion from 1 to 10. Evaluate the actual plan evidence, not the writing style, confidence, length, or formatting.

Use the following general scale consistently:
- 1–3: Poor. Major failures or violations prevent reliable task execution.
- 4–6: Partial. Some requirements are satisfied, but important omissions or problems remain.
- 7–8: Good. Most requirements are satisfied, with limited non-critical issues.
- 9–10: Excellent. The criterion is satisfied comprehensively, with no meaningful issues.

Do not award high scores merely because a plan claims to be complete. Identify concrete evidence and shortcomings in the plan before assigning each score.
### TF: Task Fulfillment

Evaluate Task Fulfillment (TF) according to the human evaluation rubric's criterion A1: Required Goal Fulfillment.

TF measures how completely the overall plan fulfills the required goals of the current task.

1. Identify the required goals.
- Use the ground-truth goals provided for the current task as the authoritative reference when available.
- If ground-truth goals are unavailable, identify required outcomes from the task description without inventing additional requirements.
- Interpret goal descriptions, predicates, and object synonyms semantically.
- Apply the same required goals and task constraints to every method being compared.
- Do not treat optional activities as required goals unless explicitly required by the task or ground truth.
- ALL required goals must be addressed. A plan that satisfies only part of the task goals should NOT receive a high TF score, even if the addressed portion is well-executed. Partial coverage of the main task is insufficient.

2. Evaluate the submitted plan.
- Evaluate the required goals using all relevant actions and communications included in the submitted plan.
- If the input contains plans for multiple agents, consider all provided agent plans and their explicitly documented communications when assessing each required goal.
- Assess each required goal based on the evidence contained in the submitted plan, regardless of how actions are distributed among agents.
- Do not assume unreported actions, communication, cooperation, or execution success.
- Do not count the same required goal multiple times when multiple actions or agents contribute to it.

3. Evaluate each required goal independently.
- Achieved: The combined plan provides a feasible course of action that sufficiently supports fulfillment of the required outcome within the task constraints.
- Partially achieved: The combined plan provides meaningful support, but the required outcome remains incomplete or an essential step is missing.
- Not achieved: The goal is omitted, unsupported, infeasible, or left unmet.
- Merely mentioning an object, stating an intention, assigning an agent, or claiming success does not establish goal fulfillment.
- If only a plan is provided and no execution record is available, evaluate whether the proposed actions support the expected outcome. Do not require proof of physical execution.
- Recognize semantically equivalent actions even when different methods express them using different wording or action sequences.

4. Respect task-specific constraints.
- Consider explicit deadlines, conditions, and restrictions in the current task.
- Assess whether the combined plan can plausibly fulfill the required goals within those constraints.
- Do not invent action durations, assume unreported execution success, or introduce unstated constraints.
- If a capability limitation, ordering problem, or missing dependency prevents a required goal from being fulfilled, reflect its effect in that goal's achievement status.
- Do not reduce TF merely because an issue affects PF, OC, or SC; reduce TF when the issue also affects required goal fulfillment.

5. Assign the overall TF score from 1 to 10.
- Consider the achievement status of every required goal in the combined plan.
- Use explicit ground-truth goal weights when provided. Otherwise, treat all required goals equally.
- Assign each required goal an achievement value:
  - Achieved = 1.0
  - Partially achieved = 0.5
  - Not achieved = 0.0

Calculate goal coverage as follows:

Coverage = sum(goal_weight * achievement_value) / sum(goal_weights)

If explicit goal weights are unavailable, use equal weights for all required goals.

Calculate the TF score using:

TF = round(1 + 9 * Coverage)

- A score of 1 indicates virtually no required goal fulfillment.
- A score of 10 requires all required goals to be achieved with sufficient supporting evidence and all explicit task constraints respected.
- For intermediate scores, follow the calculated coverage consistently.
- Do not apply an additional subjective score adjustment after calculating TF.
- Ensure the final TF score matches the calculation exactly.

6. Ensure fair comparison across methods.
- Apply identical goal interpretation, achievement standards, and calculation rules to every method.
- Neither the number of agents nor the planning strategy should affect the TF score by itself. Evaluate only how the submitted plan supports fulfillment of the required goals.
- Do not reward longer plans, additional agents, extra object mentions, or coordination language unless they contribute to required goal fulfillment.
- If two combined plans provide comparable evidence of goal fulfillment, their TF scores should be comparable.
- Do not adjust scores to favor a particular method or obtain a preferred ranking.

7. Explain the score.
In TF_reason, identify every required goal and report its achievement status and supporting evidence from the combined plan. Explain any relevant task constraints, list the goal weights when provided, calculate Coverage, and show how the final TF score is obtained. Ensure that the reasoning supports the assigned statuses and that the final score matches the calculation.
### PF: Plan Feasibility — is it executable given each agent's capabilities?

Evaluate whether the plan's actions are executable given each agent's capabilities.

Score anchors:
- 1-2: Most actions are infeasible given the assigned agents' capabilities. Major capability violations prevent execution of essential actions.
- 3-4: Several actions violate or exceed the assigned agents' known capabilities, substantially undermining execution.
- 5-6: Some actions are executable, but noticeable capability-related feasibility problems remain.
- 7-8: Most actions are executable by the assigned agents, with only minor feasibility concerns.
- 9-10: All or nearly all actions are executable given the assigned agents' capabilities, with no material capability violations.

Base PF on the actions and the capabilities specified in the evaluation input. Do not assume unsupported capabilities or penalize actions based on capabilities that are not specified.

### Additional PF Deductions — Vague Object and Location References
Penalize any of the following vague expressions, as they indicate the plan does not specify concrete, executable actions:
- "any ..." (e.g., "any items", "any small objects", "any clutter")
- "one of the ..." without naming the specific object
- "something" / "anything" / "some items" / "some objects"
- Generic terms without specific object names: "clutter", "mess", "stuff", "things", "items", "misplaced items"
- Vague food/snack references: "quick snack item", "snack", "food item" without naming the object
- Vague location references: "somewhere", "appropriate place", "within reach", "nearby", "reachable position", "close to", "near", "somewhere accessible"
- Object names that change throughout the plan (e.g., "bread" → "sandwich" → "food") — inconsistent object naming indicates ambiguity


### OC: Observability Consistency

Does this plan reflect a TRUE DISTRIBUTED setting where each robot only knows its own room and cannot see other rooms unless explicitly told via a message/request? A plan where any robot's actions depend on knowledge of another room it was never told about (including knowledge of hidden/invisible objects in another robot's room, or coordination that implies one mind sees everything at once) should score LOW on OC, regardless of how well-organized or efficient the plan looks. A single centralized planner writing for all robots at once, with full visibility into every room including hidden objects, should score LOW here even if the resulting plan reads well -- OC measures whether the INFORMATION CONSTRAINT of a distributed system was respected, not whether the plan is well-organized. A plan with explicit ASK_HELP/HELP/PASS/RECEIVE-style requests between robots (each robot only acting on messages it actually received) should score HIGH.

Score anchors:
- 1-2: The plan severely violates distributed information constraints. Agents repeatedly rely on unobserved cross-room information, hidden objects, or unjustified global knowledge. Essential actions depend on information never made available to the acting agent.
- 3-4: The plan contains frequent or significant information-boundary violations. Multiple actions depend on unsupported cross-room knowledge or treat unverified information as fact.
- 5-6: The plan shows mixed compliance. Some actions use valid local observations or communicated information, but meaningful unsupported assumptions or information-transfer gaps remain.
- 7-8: The plan mostly respects information boundaries. Agents generally act on local observations or information received through communication, with only minor unsupported assumptions.
- 9-10: The plan consistently respects distributed information constraints. Each robot acts only on its own observations or information explicitly received through valid communication. No material action depends on unjustified global knowledge or unverified cross-room information.

Score OC based on the information available to each agent and the communication evidence in the plan. Do not award a high score merely because the plan is well organized or contains coordination keywords.


### SC: Sequential Coherence

Evaluate whether the action sequence respects prerequisites and dependencies.

- Check whether required prerequisite actions occur before dependent actions.
- Check whether an action relies on information, an object, or assistance that has not yet become available.
- Penalize ordering violations that make later actions impossible, prevent task completion, or leave required dependencies unresolved.
- Distinguish minor ordering issues from critical violations that prevent execution.
- Check whether required requests, assistance, and information transfers are resolved when subsequent actions depend on them.

Score anchors:
- 1-2: The action sequence is largely incoherent. Critical prerequisite violations or unresolved dependencies prevent essential actions or make task completion infeasible.
- 3-4: The sequence contains major logical gaps. Several actions depend on prerequisites, objects, information, or assistance that are not yet available.
- 5-6: The sequence is generally logical but contains noticeable ordering problems or unresolved dependencies that may interfere with task completion.
- 7-8: The sequence is mostly coherent. Prerequisites and dependencies are generally respected, with only minor ordering issues that do not substantially undermine task completion.
- 9-10: The sequence respects all material prerequisites and dependencies. Required preparation, requests, assistance, and information transfers are resolved before dependent actions occur. Assign 10 when no material sequencing issue remains; assign 9 when only a minor issue remains.

Do not reward a plan merely for having a long or well-organized sequence. Evaluate whether the sequence can logically lead to the required outcomes.

### Additional SC Deductions
- Penalize repeated identical or near-identical actions (e.g., picking up the same object twice, going to the same location consecutively without purpose).
- Penalize inconsistent object naming throughout the plan (e.g., referring to the same object as "bread", then "sandwich", then "food"). Object references should remain consistent from start to finish.


### Cross-criterion consistency

Apply the same criteria to every evaluated method.

- Evaluate the actual plan rather than the method name or presumed strengths of the approach.
- Do not award points solely for fluent narration, detailed formatting, or coordination keywords.
- Avoid double-penalizing the same problem without considering its distinct consequences for each criterion. For example, an unsupported object claim may affect OC, while its effect on task achievement or execution may separately affect TF or PF.
- When evidence is insufficient, explain what cannot be verified rather than assuming successful execution.
- Provide concise, plan-specific reasons for every score.
- Apply the score anchors consistently. Comparable evidence should receive comparable scores across methods.
- Do not adjust scores to favor a particular method or obtain a preferred ranking.

Output JSON only:
{{"TF":<1-10>,"TF_reason":"...","PF":<1-10>,"PF_reason":"...","OC":<1-10>,"OC_reason":"...","SC":<1-10>,"SC_reason":"..."}}


"""
    response = judge_client.chat.completions.create(
        model=GEMINI_MODEL, temperature=0.0,
        messages=[{"role": "system", "content": JUDGE_SYSTEM}, {"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
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
    if method == "cda":
        pddl_eval_path = os.path.join(results_dir, f"{args.task}_ours_pddl_eval.json")
        if os.path.exists(pddl_eval_path):
            with open(pddl_eval_path, encoding="utf-8") as f:
                return json.load(f).get("pddl_problem", "")
        return ""
    elif method == "cda":
        pddl_eval_path = os.path.join(results_dir, f"{args.task}_cda_pddl_eval.json")
        if os.path.exists(pddl_eval_path):
            with open(pddl_eval_path, encoding="utf-8") as f:
                return json.load(f).get("pddl_problem", "")
        return ""  # 아직 변환 스크립트 없음 -> GC는 N/A로 처리됨
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
for fp in task["rooms"]:
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
