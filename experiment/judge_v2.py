"""LLM judge v2 — step executability / grounding / subgoal coverage 를 명시적으로 반영.
기존 judge_plan(v1)은 수정하지 않음. 결과는 *_summary_jabung_v2.json 에 별도 저장.

usage:
    python judge_v2.py --task task1_abstract --run 2
    python judge_v2.py --task task1_abstract --run 2 --methods cda lamma_p smart_llm central
    python judge_v2.py --task task1_abstract --run 2 --ablation --variants no_offer no_edge no_graph
"""
import ast
import json
import os
import re
import sys
import argparse

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("--task", required=True)
ap.add_argument("--run", type=int, default=1)
ap.add_argument("--methods", nargs="+", default=None,
                help="subset of [cda central independent lamma_p smart_llm]; default = all present")
ap.add_argument("--ablation", action="store_true")
ap.add_argument("--variants", nargs="+", default=["no_offer", "no_edge", "no_graph"])
a = ap.parse_args()

AGG = os.path.join(HERE, "aggregate_results_jabung.py")
_tree = ast.parse(open(AGG, encoding="utf-8").read())
_jp = next(n for n in _tree.body if isinstance(n, ast.FunctionDef) and n.name == "judge_plan")


def _ok(n):
    if n.lineno > _jp.end_lineno:
        return False
    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return True
    s = ast.unparse(n)
    if "judge_plan(" in s or "completions.create" in s:
        return False
    if isinstance(n, ast.Expr) and s.startswith("print("):
        return False
    return True


_keep = [n for n in _tree.body if _ok(n)]
src = ast.unparse(ast.Module(body=_keep, type_ignores=[]))

sys.argv = ["aggregate_results_jabung.py", "--task", a.task, "--run", str(a.run)]
ns = {"__name__": "agg_partial", "__file__": AGG}
exec(compile(src, AGG, "exec"), ns)

task_text = ns["task_text"]
AGENT_CONFIG = ns["AGENT_CONFIG"]
ROOM_OBJECTS_TEXT = ns["ROOM_OBJECTS_TEXT"]
judge_client = ns["judge_client"]
GEMINI_MODEL = ns["GEMINI_MODEL"]
log_usage = ns["log_usage"]
results_dir = ns["results_dir"]
method_results = ns["method_results"]
METHOD_NAMES = ns["METHOD_NAMES"]
METHODS = ns["METHODS"]

JUDGE_SYSTEM_V2 = "You are a strict, meticulous evaluator for multi-agent household task planning. Respond in valid JSON only."


def judge_plan_v2(plan_text, deadline_min=None, makespan_min=None):
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
Accept descriptive synonyms as valid references to listed objects (e.g. "silver faucet handle" -> Faucet,
"white trash bin" -> GarbageCan). Do NOT mark an object as hallucinated if a reasonable synonym maps to
a listed object. But generic/unspecified words like "ingredients", "items", "things", "something",
"supplies", "belongings" do NOT count as grounded, even if a listed object could plausibly fit --
the robot must name a specific object to be grounded.

## Natural Language Plan
{plan_text}

## Step 1 -- Step Analysis (do this BEFORE scoring)

Go through every numbered/tagged step in the plan (ignore section headers, Warnings/Dropped/Blocked/
Unresolved notes). For each step decide:

- atomic: is this a single verb + one concrete, specific object + a location/target, immediately
  executable by a robot with no further decomposition needed?
  - Steps bundling multiple sub-actions or using vague composite verbs (e.g. "Gather ingredients",
    "Assemble sandwich", "Clean the table", "Make a sandwich", "Tidy the room", "Prepare breakfast")
    are NON-ATOMIC, even if they sound reasonable at a glance.
  - A pure movement step ("Go to kitchen") is atomic, but does not count toward goal-accomplishing
    actions below.
- grounded: does the object in this step match a specific entry in "Actual Objects in Each Room"
  (via exact name or a reasonable descriptive synonym)? Generic/unspecified nouns are NOT grounded.

Count and list (by step id, e.g. r1_s2):
- n_steps: total number of actionable steps (LOCAL/PASS/RECEIVE/HELP/ASK_HELP), excluding pure
  movement-only steps if the plan separates them, excluding Dropped/Blocked/Unresolved entries.
- non_atomic_step_ids: ids of all non-atomic steps, n_non_atomic_steps: their count.
- ungrounded_step_ids: ids of all steps referencing an ungrounded object, n_ungrounded_steps: their count.

## Step 2 -- Subgoal Coverage (do this BEFORE scoring)

List the concrete subgoals required to fulfill the task (subgoals_required: short strings, e.g.
"toast bread", "move laptop to shelf"). Derive these directly from the task description and what a
literal completion of it requires -- do not invent subgoals the task doesn't ask for.

For each subgoal, mark it covered (add to subgoals_covered) ONLY if at least one ATOMIC and GROUNDED
step in the plan concretely accomplishes it. A non-atomic step that merely gestures at a subgoal in
words (e.g. "Make a sandwich" claiming to cover "slice bread" and "add filling" and "assemble") does
NOT count as covering those subgoals.

## Step 3 -- Scoring (0-10 scale, using the counts above)

- 9-10: Fully satisfies the criterion. 5-8: Partially satisfies. 0-4: Fails to satisfy.

### TF: Task Fulfillment -- 0~10
Let coverage_ratio = len(subgoals_covered) / len(subgoals_required) (0 if no subgoals required).
- coverage_ratio >= 0.8 and deadline respected: 8-10 range (adjust within range for execution quality).
- coverage_ratio in [0.5, 0.8): cap TF at 7.
- coverage_ratio < 0.5: cap TF at 4.
- If the plan's total time clearly exceeds the task deadline, apply additional deduction regardless
  of coverage_ratio.
- Goals "achieved" only via hallucinated/ungrounded objects do not count toward coverage.

### GF: Grounded Feasibility -- 0~10
Let non_atomic_ratio = n_non_atomic_steps / n_steps, ungrounded_ratio = n_ungrounded_steps / n_steps
(0 if n_steps is 0).
- If non_atomic_ratio >= 0.3 OR ungrounded_ratio >= 0.3: GF is capped at 4, regardless of how
  reasonable the plan sounds overall.
- If non_atomic_ratio >= 0.15 OR ungrounded_ratio >= 0.15 (but below the caps above): GF is capped
  at 7.
- Within whatever cap applies, further adjust down for: capability violations (robot acting outside
  its CAN list), a robot acting on information it cannot legitimately observe/receive, a robot
  holding multiple objects simultaneously.

### SC: Sequential Coherence -- 0~10
(unchanged from prior rubric) Evaluate prerequisite/dependency ordering violations as a ratio of
violating steps to total steps: ratio <= 20% with no critical blocker -> 5-8; >20% or any violation
that makes execution impossible -> 0-4; no violations -> 9-10.

### CQ: Collaboration Quality -- 0~10
(unchanged from prior rubric) First decide if collaboration is REQUIRED by the task (objects must
move between rooms / capability constraints prevent solo completion / explicit multi-room
coordination), then judge necessity, appropriateness (correct targets, no self-pass, no circular
requests), efficiency, and completeness of any PASS/RECEIVE/HELP/ASK_HELP-style exchanges. For CDA
plans specifically, "Blocked" steps are a safety feature (automatically skipped), not a failure --
penalize only if the core collaboration goal is unachievable.

---

Output JSON only, in this exact key order:
{{"n_steps":<int>,"non_atomic_step_ids":[...],"n_non_atomic_steps":<int>,
"ungrounded_step_ids":[...],"n_ungrounded_steps":<int>,
"subgoals_required":[...],"subgoals_covered":[...],
"TF":<0-10>,"TF_reason":"...","GF":<0-10>,"GF_reason":"...",
"SC":<0-10>,"SC_reason":"...","CQ":<0-10>,"CQ_reason":"..."}}
"""
    response = judge_client.chat.completions.create(
        model=GEMINI_MODEL, temperature=0.0,
        messages=[{"role": "system", "content": JUDGE_SYSTEM_V2}, {"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    log_usage("judge_jabung_v2", a.task, response)
    raw = re.sub(r"```(json)?", "", response.choices[0].message.content.strip()).strip()
    return json.loads(raw)


def clean(text):
    return re.sub(r"```\w*\n?", "", text or "").strip()


results_v2 = {}

if a.ablation:
    abl_path = os.path.join(HERE, "results", "ablation", f"{a.task}_ablation_run{a.run}.json")
    if not os.path.exists(abl_path):
        raise SystemExit(f"ablation 파일 없음: {abl_path}")
    abl = json.load(open(abl_path, encoding="utf-8"))
    for v in a.variants:
        r = abl.get(v, {})
        text = clean(r.get("joint_plan_text"))
        if not text:
            print(f"  {v}: plan 없음, 건너뜀")
            continue
        j = judge_plan_v2(text)
        results_v2[v] = j
        print(f"  {v:10}: TF={j['TF']} GF={j['GF']} SC={j['SC']} CQ={j['CQ']}  "
              f"(n_steps={j['n_steps']} non_atomic={j['n_non_atomic_steps']} "
              f"ungrounded={j['n_ungrounded_steps']} coverage={len(j['subgoals_covered'])}/{len(j['subgoals_required'])})")
    out_path = os.path.join(HERE, "results", "ablation", f"ablation_judge_results_run{a.run}_v2.json")
    all_results = json.load(open(out_path, encoding="utf-8")) if os.path.exists(out_path) else {}
    all_results.setdefault(a.task, {})
    all_results[a.task].update(results_v2)
    json.dump(all_results, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"저장: {out_path}")
else:
    methods = a.methods or METHODS
    for m in methods:
        r = method_results.get(m)
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
        plan_text = clean(plan_text)
        if not plan_text:
            print(f"  {METHOD_NAMES.get(m, m):14} -- plan 없음, 건너뜀")
            continue
        j = judge_plan_v2(plan_text)
        results_v2[m] = j
        print(f"  {METHOD_NAMES.get(m, m):14}: TF={j['TF']} GF={j['GF']} SC={j['SC']} CQ={j['CQ']}  "
              f"(n_steps={j['n_steps']} non_atomic={j['n_non_atomic_steps']} "
              f"ungrounded={j['n_ungrounded_steps']} coverage={len(j['subgoals_covered'])}/{len(j['subgoals_required'])})")

    out_path = os.path.join(results_dir, f"{a.task}_summary_jabung_v2.json")
    existing = json.load(open(out_path, encoding="utf-8")) if os.path.exists(out_path) else {}
    for m, j in results_v2.items():
        existing[m] = {"name": METHOD_NAMES.get(m, m), "track_a_llm_judge_v2": j}
    json.dump(existing, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"저장: {out_path}")
