"""
사용법:
    python run_capture.py --task task1_abstract --fp FP14 --n-robots 6
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai2thor_sim'))
from a import interactive_capture

parser = argparse.ArgumentParser()
parser.add_argument("--task", required=True)
parser.add_argument("--fp", required=True, help="촬영할 FloorPlan (예: FP14)")
parser.add_argument("--n-robots", type=int, required=True, choices=[4, 6, 8])
parser.add_argument("--dirty", action="store_true", help="오브젝트 더럽히기")
args = parser.parse_args()

EXP = os.path.join(os.path.dirname(__file__), '..', 'experiment')

with open(os.path.join(EXP, 'task', 'task.json'), encoding='utf-8') as f:
    task_data = {t['task_n']: t for t in json.load(f)['tasks']}

task = task_data[args.task]
task_num = args.task.replace('_abstract', '').replace('task', '')
task_type = args.task.split('_')[1]
n_str = str(args.n_robots)
robot_list = task['configs'][n_str]

# 해당 FP에 있는 로봇들만 필터
fp_robots = [(i+1, r) for i, r in enumerate(robot_list) if r['room'] == args.fp]
if not fp_robots:
    print(f"❌ {args.fp}에 배치된 로봇이 없습니다 (n={args.n_robots})")
    print(f"   배치: {[(i+1, r['room']) for i, r in enumerate(robot_list)]}")
    sys.exit(1)

agent_count = len(fp_robots)
robot_labels = [f"R{i}" for i, _ in fp_robots]

# 저장 경로
folder_n = f"n_{args.n_robots}"
out_dir = os.path.join(EXP, 'image', task_type, f'task{task_num}', folder_n)
prefix = f"task{task_num}_{task_type}_{args.fp}"

scene = f"FloorPlan{args.fp.replace('FP', '')}"

print(f"📋 {args.task} | {args.fp} | n={args.n_robots} | {args.mode}")
print(f"   scene: {scene} | agents: {agent_count}대 {robot_labels}")
print(f"   저장: {out_dir}")
print(f"   prefix: {prefix}")
print()

interactive_capture(
    scene=scene,
    agent_count=agent_count,
    out_dir=out_dir,
    prefix=prefix,
    robot_labels=robot_labels,
    dirty_all=args.dirty,
)
