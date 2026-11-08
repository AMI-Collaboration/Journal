"""ablation variant LLM judge (aggregate_results_jabung.judge_plan 재사용)
usage: python judge_ablation.py --run 2 --tasks 1 2 3
"""
import json, os, sys, re, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from loader import load_ablation_raw, save_ablation_judge  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('--run', type=int, default=2, help='repetition index (1-3), NOT robot count')
ap.add_argument('--n-robots', type=int, default=4)
ap.add_argument('--tasks', type=int, nargs='+', default=list(range(1, 11)))
ap.add_argument('--variants', nargs='+', default=['no_offer', 'no_edge', 'no_graph'])
a = ap.parse_args()

AGG = os.path.join(HERE, 'aggregate_results_jabung.py')
import ast
_tree = ast.parse(open(AGG, encoding='utf-8').read())
_jp = next(n for n in _tree.body if isinstance(n, ast.FunctionDef) and n.name == 'judge_plan')
def _ok(n):
    if n.lineno > _jp.end_lineno: return False
    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)): return True
    s = ast.unparse(n)
    if 'judge_plan(' in s or 'completions.create' in s: return False
    if isinstance(n, ast.Expr) and s.startswith('print('): return False
    return True
_keep = [n for n in _tree.body if _ok(n)]
src = ast.unparse(ast.Module(body=_keep, type_ignores=[]))

saved_paths = []

for t in a.tasks:
    task = f'task{t}_abstract'

    sys.argv = ['aggregate_results_jabung.py', '--task', task, '--run', str(a.run), '--n-robots', str(a.n_robots)]
    ns = {'__name__': 'agg_partial', '__file__': AGG}
    exec(compile(src, AGG, 'exec'), ns)

    for v in a.variants:
        r = load_ablation_raw(task, v, n_robots=a.n_robots, run=a.run)
        text = re.sub(r'```\w*\n?', '', (r or {}).get('joint_plan_text') or '').strip()
        if not text:
            print(f'  {task} {v}: plan 없음'); continue
        m = (r or {}).get('metrics', {})
        j = ns['judge_plan'](text, deadline_min=m.get('deadline'), makespan_min=m.get('makespan_min'))
        if isinstance(j, dict) and 'TF' in j:
            print(f"  {task} {v:9}: TF={j['TF']} GF={j['GF']} SC={j['SC']} CQ={j['CQ']}")
            saved_paths.append(save_ablation_judge(task, v, j, n_robots=a.n_robots, run=a.run))
        else:
            print(f'  {task} {v}: judge 실패 {str(j)[:80]}')

print('💾', ', '.join(saved_paths))
