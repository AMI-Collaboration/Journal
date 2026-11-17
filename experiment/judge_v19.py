"""Judge with judge_rubric_point_prompt.txt (B rubric: TF / GF / SC / CQ), all methods of one task in ONE call.

Fixes over aggregate_results_jabung.judge_plan (one plan per call):
- every plan of a task is judged in the same call, under anonymous shuffled labels (PLAN_A, ...), so the
  same rubric and the same context apply to every method
- the task text, agent configuration and object inventory are rebuilt for EACH task
- scores must be integers 0-5; an answer with a missing label or an out-of-range score is asked again
- each task is judged --reps times with a different label order; the per-method score is the mean

usage:
  python judge_v19.py --specs cda=run4:ours_cda lamma=run4:baseline_lamma_p cda6=run6:ours_cda \
      --out /tmp/judge_v19.json --reps 2
A spec is NAME=RUN:FILE or NAME=RUN:ablation#VARIANT (file without .json, in
results/final/RUN/4robot/{abstract,simple}/taskN/).
Results are written to --out only; no result file in the repo is modified.
"""
import argparse
import ast
import json
import os
import random
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ap = argparse.ArgumentParser()
ap.add_argument("--specs", nargs="+", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--reps", type=int, default=2)
ap.add_argument("--n-robots", type=int, default=4)
ap.add_argument("--template", default="judge_rubric_point_prompt.txt", help="prompt file in experiment/")
ap.add_argument("--crit", nargs="+", default=["TF", "GF", "SC", "CQ"], help="criteria the template asks for")
ap.add_argument("--lenient", action="store_true", help="prepend a mild calibration note (same text for every plan)")
ap.add_argument("--strict", action="store_true", help="prepend a strict calibration note (same text for every plan)")
ap.add_argument("--kinds", nargs="+", default=["abstract", "simple"])
ap.add_argument("--tasks", type=int, nargs="+", default=list(range(1, 11)))
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
    return not (isinstance(n, ast.Expr) and s.startswith("print("))


SETUP = ast.unparse(ast.Module(body=[n for n in _tree.body if _ok(n)], type_ignores=[]))
TEMPLATE = open(os.path.join(HERE, a.template), encoding="utf-8").read()
CRIT = tuple(a.crit)
BASE = os.path.join(HERE, "results", "final")
_SETUP_LOCK = threading.Lock()      # the setup reads sys.argv: build one task at a time
from loader import load_all  # noqa: E402
TASKS = load_all()["tasks"]
CALIBRATION = """## CALIBRATION NOTE (applies identically to every plan below)
- Judge what the plan plausibly achieves. A reasonable synonym of a listed object is a valid reference;
  deduct for an object or place only when no listed object plausibly matches.
- Redundant but harmless steps (extra pick-ups, repeated moves) are minor: deduct only if they block a
  goal, break a prerequisite, or push a goal past the deadline.
- Finishing a goal within one 5-minute slot after the deadline is partial credit for that goal, not zero.
- When the evidence is ambiguous between two adjacent scores, choose the higher one.
Do not change anything else in the rubric below.

"""
STRICT_CALIBRATION = """## CALIBRATION NOTE (applies identically to every plan below)
- Score 5 only if the plan achieves every required goal with concrete, real objects and places, has no
  ordering or prerequisite violation, and finishes every goal within the deadline. Any single
  unsupported object or place, missing prerequisite, or unaddressed goal caps that criterion at 4.
- Vague actions (help, prepare, tidy, arrange, ensure) do not count as achieving a goal.
- No-op or circular steps (picking something up and putting it back in place, repeated moves of the same
  object, passing an object back and forth) are deducted under SC and PF.
- A goal finished after the deadline does not count for TF.
- When the evidence is ambiguous between two adjacent scores, choose the lower one.
Do not change anything else in the rubric below.

"""
SPECS = dict(s.split("=", 1) for s in a.specs)


def normalize(text):
    """Same surface for every method: only CDA plans carry a task-id/deadline-verdict title, a
    '### Robots:' line and code fences. The robot configuration is given to the judge separately
    (AGENT_CONFIG) for all methods, and the judge must derive the deadline from the plan itself."""
    text = re.sub(r"```\w*\n?", "", text or "").strip()
    out = []
    for line in text.splitlines():
        if line.startswith("### Robots:"):
            continue
        out.append("### Joint Plan" if line.startswith("### Joint Plan") else line)
    return "\n".join(out).strip()


def plan_text(path, variant=None):
    d = json.load(open(path, encoding="utf-8"))
    r = d["variants"].get(variant, {}).get("raw_result", {}) if variant else d.get("raw_result", d)
    return normalize(r.get("joint_plan_text"))


def agent_config(ns, task, n_robots):
    """The upstream AGENT_CONFIG reads task['robot'], which does not exist (it is empty). Build it from
    configs[n]: labels R1..Rn follow the config order, which is also the label order of every plan."""
    robots = load_all()["robots"]
    lines = []
    for i, ref in enumerate(TASKS[task]["configs"][str(n_robots)]):
        rt = robots[ref["robot_n"]]
        room = ns["room_map"].get(ref["room"], {}).get("floorplan_type", ref["room"])
        can = ", ".join(rt.get("robot_can", []))
        cannot = ", ".join(rt.get("robot_cannot", [])) or "none specified"
        lines.append(f"- R{i + 1}: {rt['robot_name']} (starts in {room}, {ref['room']}) -- CAN: {can} | CANNOT: {cannot}")
    return "\n".join(lines)


def valid(res, labels):
    try:
        for lab in labels:
            for c in CRIT:
                v = res[lab][c]
                if isinstance(v, bool) or int(v) != v or not 0 <= int(v) <= 5:
                    return False
        return True
    except (KeyError, TypeError, ValueError):
        return False


def judge_task(kind, t, rep):
    task = f"task{t}_{kind}"
    with _SETUP_LOCK:
        sys.argv = ["x", "--task", task, "--run", "1", "--n-robots", str(a.n_robots)]
        ns = {"__name__": "agg_partial", "__file__": AGG}
        exec(compile(SETUP, AGG, "exec"), ns)
    assert ns["task_text"] == TASKS[task]["task"], f"wrong task text for {task}"
    ns["AGENT_CONFIG"] = agent_config(ns, task, a.n_robots)
    plans = {}
    for name, spec in SPECS.items():
        run, f = spec.split(":")
        f, _, var = f.partition("#")          # FILE#VARIANT reads one variant of ablation.json
        p = os.path.join(BASE, run, f"{a.n_robots}robot", kind, f"task{t}", f + ".json")
        if os.path.exists(p) and plan_text(p, var or None):
            plans[name] = plan_text(p, var or None)
    names = sorted(plans)
    random.Random(f"{task}-{rep}").shuffle(names)
    labels = {f"PLAN_{chr(65 + i)}": n for i, n in enumerate(names)}
    block = "\n\n".join(f"### {lab}\n{plans[n]}" for lab, n in labels.items())
    prompt = TEMPLATE.format(task_text=ns["task_text"], AGENT_CONFIG=ns["AGENT_CONFIG"],
                             ROOM_OBJECTS_TEXT=ns["ROOM_OBJECTS_TEXT"], plans_block=block)
    if a.lenient:
        prompt = CALIBRATION + prompt
    elif a.strict:
        prompt = STRICT_CALIBRATION + prompt
    err = ""
    for _ in range(3):
        try:
            resp = ns["judge_client"].chat.completions.create(
                model=ns["GEMINI_MODEL"], temperature=0.0,
                messages=[{"role": "system", "content": ns["JUDGE_SYSTEM"]}, {"role": "user", "content": prompt}],
                response_format={"type": "json_object"})
            res = json.loads(re.sub(r"```(json)?", "", resp.choices[0].message.content.strip()).strip())
            if valid(res, labels):
                return f"{kind}|{t}|{rep}", {"labels": labels, "scores": {
                    labels[lab]: {c: int(res[lab][c]) for c in CRIT} | {c + "_reason": res[lab].get(c + "_reason", "")
                                                                       for c in CRIT} for lab in labels}}
            err = "invalid scores"
        except Exception as e:  # noqa: BLE001
            err = str(e)[:150]
    return f"{kind}|{t}|{rep}", {"error": err}


jobs = [(k, t, r) for k in a.kinds for t in a.tasks for r in range(a.reps)]
out = {}
with ThreadPoolExecutor(6) as ex:
    for key, res in ex.map(lambda j: judge_task(*j), jobs):
        out[key] = res
json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved", a.out, "errors:", sum("error" in v for v in out.values()), "of", len(out))
