"""
experiment: task1~10 전체를 모든 방법론으로 순차 실행
"""
import argparse
import subprocess
import sys
import os
import time
import json

HERE = os.path.dirname(os.path.abspath(__file__))

ALL_TASKS = [
    "task1_abstract", "task2_abstract", "task3_abstract", "task4_abstract",
    "task5_abstract", "task6_abstract", "task7_abstract", "task8_abstract",
    "task9_abstract", "task10_abstract",
]
ALL_METHODS = ["cda", "central", "independent", "lamma_p", "smart_llm"]

USD_IN  = 2.5   # per 1M prompt tokens
USD_OUT = 10.0  # per 1M completion tokens
KRW     = 1400  # per USD

parser = argparse.ArgumentParser()
parser.add_argument("--tasks", nargs="*", default=ALL_TASKS)
parser.add_argument("--skip", nargs="*", default=[], choices=ALL_METHODS)
parser.add_argument("--mode", default="multi_room", choices=["multi_room", "single_room"])
parser.add_argument("--model", default="gpt-4o")
parser.add_argument("--run", type=int, default=1)
parser.add_argument("--no-proposal", action="store_true")
parser.add_argument("--no-graph-llm", action="store_true")
parser.add_argument("--rounds", type=int, default=2)
parser.add_argument("--dry-run", action="store_true")
args = parser.parse_args()

tasks = args.tasks
total = len(tasks)

print(f"총 {total}개 task, 방법론: {[m for m in ALL_METHODS if m not in args.skip]}")
print(f"model={args.model}, mode={args.mode}, run={args.run}" + (" [DRY-RUN]" if args.dry_run else ""))


def load_log():
    path = os.path.join(HERE, "usage_log.json")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return []


def calc_cost(entries):
    """entries 리스트에서 방법론별 토큰/비용 집계"""
    by_method = {}
    for e in entries:
        m = e.get("method", "unknown")
        base = m.replace("_convert", "").replace("_grounding", "").replace("_judge", "")
        if base not in by_method:
            by_method[base] = {"prompt": 0, "completion": 0, "calls": 0}
        by_method[base]["prompt"]     += e.get("prompt_tokens", 0)
        by_method[base]["completion"] += e.get("completion_tokens", 0)
        by_method[base]["calls"]      += e.get("calls", 1)
    return by_method


def to_krw(p, c):
    return ((p / 1_000_000) * USD_IN + (c / 1_000_000) * USD_OUT) * KRW


def print_usage(entries, label="사용량"):
    if not entries:
        print(f"  [{label}] 기록 없음")
        return
    by_method = calc_cost(entries)
    total_p = sum(v["prompt"] for v in by_method.values())
    total_c = sum(v["completion"] for v in by_method.values())
    total_t = total_p + total_c
    total_w = to_krw(total_p, total_c)

    print(f"\n  📊 [{label}]")
    for m, v in sorted(by_method.items()):
        t = v["prompt"] + v["completion"]
        w = to_krw(v["prompt"], v["completion"])
        print(f"     {m:<15} {t:>8} tokens  ({v['calls']}회)  약 {w:>7.1f}원")
    print(f"     {'합계':<15} {total_t:>8} tokens          약 {total_w:>7.1f}원")


def run_cmd(label, cmd):
    if label in args.skip:
        print(f"  ⏭️  skip: {label}")
        return
    print(f"  --- [{label}] ---")
    t0 = time.time()
    result = subprocess.run(cmd, cwd=HERE)
    elapsed = int(time.time() - t0)
    if result.returncode != 0:
        print(f"  ⚠️  실패: {label} (code={result.returncode}, {elapsed}초)")
    else:
        print(f"  ✅ 완료: {label} ({elapsed//60}분 {elapsed%60}초)")


batch_start = time.time()
log_before_batch = load_log()
log_idx_before_batch = len(log_before_batch)

for i, task in enumerate(tasks, 1):
    task_start = time.time()
    log_idx_before_task = len(load_log())

    print(f"\n{'='*55}")
    print(f" [{i}/{total}] {task}")
    print(f"{'='*55}")

    # C-DA
    cda_cmd = [
        sys.executable, "run_cda.py",
        "--task", task, "--mode", args.mode, "--model", args.model,
        "--run", str(args.run), "--rounds", str(args.rounds),
    ]
    if args.no_proposal:  cda_cmd.append("--no-proposal")
    if args.no_graph_llm: cda_cmd.append("--no-graph-llm")
    if args.dry_run:      cda_cmd.append("--dry-run")
    run_cmd("cda", cda_cmd)

    if args.dry_run:
        print("  ⏭️  dry-run: central/independent/lamma_p/smart_llm skip")
        continue

    # Central
    run_cmd("central", [
        sys.executable, "run_central.py",
        "--task", task, "--mode", args.mode,
        "--gpt-version", args.model, "--run", str(args.run),
    ])

    # Independent
    run_cmd("independent", [
        sys.executable, "run_independent.py",
        "--task", task, "--mode", args.mode,
        "--gpt-version", args.model, "--run", str(args.run),
    ])

    # LaMMA-P
    run_cmd("lamma_p", [
        sys.executable, "run_lamma_p.py",
        "--task", task, "--gpt-version", args.model, "--run", str(args.run),
    ])
    if "lamma_p" not in args.skip:
        run_cmd("lamma_p_convert", [
            sys.executable, "convert_to_joint_plan.py",
            "--task", task, "--method", "lamma_p",
            "--gpt-version", args.model, "--run", str(args.run),
        ])

    # SMART-LLM
    run_cmd("smart_llm", [
        sys.executable, "run_smart_llm.py",
        "--task", task, "--gpt-version", args.model, "--run", str(args.run),
    ])
    if "smart_llm" not in args.skip:
        run_cmd("smart_llm_convert", [
            sys.executable, "convert_to_joint_plan.py",
            "--task", task, "--method", "smart_llm",
            "--gpt-version", args.model, "--run", str(args.run),
        ])

    elapsed = int(time.time() - task_start)
    log_after_task = load_log()
    task_entries = log_after_task[log_idx_before_task:]
    print(f"\n  ⏱️  소요시간: {elapsed//60}분 {elapsed%60}초")
    print_usage(task_entries, f"{task} 이번 실행")

# 전체 배치 요약
batch_elapsed = int(time.time() - batch_start)
log_after_batch = load_log()
batch_entries = log_after_batch[log_idx_before_batch:]

print(f"\n{'='*55}")
print(f" 전체 {total}개 task 완료!  총 소요시간: {batch_elapsed//60}분 {batch_elapsed%60}초")
print_usage(batch_entries, "이번 실행 전체")
print(f" 결과: experiment/results/run{args.run}/")
print(f"{'='*55}")
