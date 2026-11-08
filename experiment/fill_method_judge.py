"""기존 summary_jabung.json에서 특정 method 하나만 (재)judge해서 채워넣음.
다른 method의 기존 judge 점수는 보존 (재실행 안 함).
usage: python fill_method_judge.py --task task1_abstract --run 2 --method smart_llm
"""
import ast
import json
import os
import re
import sys
import argparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from loader import load_method_raw_result, save_method_judge, final_task_dir  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--task", required=True)
ap.add_argument("--run", type=int, default=1, help="repetition index (1-3), NOT robot count")
ap.add_argument("--n-robots", type=int, default=4)
ap.add_argument("--method", required=True, choices=["cda", "central", "independent", "lamma_p", "smart_llm"])
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

if a.task.startswith("mat_"):
    results_dir = os.path.join(HERE, "results", "matthor")
    if a.method == "cda":
        candidates = [f"{a.task}_multi_room_cda_jabung_result.json", f"{a.task}_multi_room_cda_result.json"]
    else:
        candidates = [f"{a.task}_{a.method}_result.json"]
    method_path = next((os.path.join(results_dir, c) for c in candidates
                         if os.path.exists(os.path.join(results_dir, c))), None)
    if method_path is None:
        raise SystemExit(f"결과 파일 없음: {[os.path.join(results_dir, c) for c in candidates]}")
    method_result = json.load(open(method_path, encoding="utf-8"))
else:
    method_result = load_method_raw_result(a.task, a.method, n_robots=a.n_robots, run=a.run)
    if method_result is None:
        raise SystemExit(f"결과 파일 없음: {final_task_dir(a.task, n_robots=a.n_robots, run=a.run)}")

plan_text = method_result.get("joint_plan_text")
if not plan_text:
    raise SystemExit(f"joint_plan_text 없음: {a.task}/{a.method}")
plan_text = re.sub(r"```\w*\n?", "", plan_text).strip()

sys.argv = ["aggregate_results_jabung.py", "--task", a.task, "--run", str(a.run), "--n-robots", str(a.n_robots)]
ns = {"__name__": "agg_partial", "__file__": AGG}
exec(compile(src, AGG, "exec"), ns)

judge = ns["judge_plan"](plan_text)
print(f"{a.task} {a.method} (run{a.run}, {a.n_robots}robot): TF={judge.get('TF')} GF={judge.get('GF')} SC={judge.get('SC')} CQ={judge.get('CQ')}")

if a.task.startswith("mat_"):
    summary_path = os.path.join(results_dir, f"{a.task}_summary_jabung.json")
    summary = json.load(open(summary_path, encoding="utf-8")) if os.path.exists(summary_path) else {}
    summary.setdefault(a.method, {"name": a.method})
    summary[a.method]["track_a_llm_judge"] = judge
    json.dump(summary, open(summary_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"저장: {summary_path}")
else:
    out_path = save_method_judge(a.task, a.method, judge, n_robots=a.n_robots, run=a.run)
    print(f"저장: {out_path}")
