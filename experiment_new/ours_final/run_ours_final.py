"""
run_ours_final.py

ours (CDA: "Collaborate, Don't Assign" -- Offer -> Local Plan -> Edge Proposal ->
Graph Reasoning -> Joint Plan) 파이프라인을 experiment_new의 공통 데이터 구조
(task.json / room.json / object.json / robot.json)로 실행한다.

실제 협업 알고리즘은 이 저장소 루트의 C-DA/ 패키지(원본: egggbeee-dev/Collaboration-journal,
Code_03/cda)를 그대로 가져다 쓰고, 이 스크립트는 "데이터 변환 -> 실행 -> 결과 저장"만 담당한다.
C-DA/ 패키지 내부 알고리즘은 수정하지 않는다 (그래야 노트북 버전과 항상 동일하게 유지됨).

사용법:
    python run_ours_final.py --task task1_abstract
    python run_ours_final.py --task task6_simple --model gpt-4o
    python run_ours_final.py --task task1_abstract --mode single_room
"""
from __future__ import annotations

import argparse
import asyncio
import importlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))              # .../experiment_new/ours_final
EXPERIMENT_NEW = os.path.dirname(HERE)                          # .../experiment_new
REPO_ROOT = os.path.dirname(EXPERIMENT_NEW)                     # C-DA/ 가 있는 리포지토리 루트

sys.path.insert(0, EXPERIMENT_NEW)   # loader.py
sys.path.insert(0, REPO_ROOT)        # C-DA 패키지

from loader import load_all, build_agent_inputs  # noqa: E402

# "C-DA"는 하이픈이 있어 `import C-DA`가 불가능하므로 importlib로 로드한다.
cda_schemas = importlib.import_module("C-DA.schemas")
cda_pipeline = importlib.import_module("C-DA.pipeline")
cda_llm = importlib.import_module("C-DA.llm")

TaskConfig = cda_schemas.TaskConfig
run_pipeline = cda_pipeline.run_pipeline
OpenAILLM = cda_llm.OpenAILLM
MockLLM = cda_llm.MockLLM


# ---------------------------------------------------------------------------
# robot_name -> (mobile, payload_kg): cda.TaskConfig.from_notebook이 요구하는 필드.
# room.json/robot.json에는 kg 값이 없으므로, 로봇 유형별 대표값을 둔다.
# ---------------------------------------------------------------------------
ROBOT_MOBILITY = {
    "Gripper": {"mobile": False, "payload_kg": 2.0},
    "Mobile_Light": {"mobile": True, "payload_kg": 3.0},
    "Mobile_Heavy": {"mobile": True, "payload_kg": 15.0},
}

# loader.fp_to_room_type()은 "living_room"(언더바)을 쓰지만, cda 쪽 문구/비교 로직은
# 사람이 쓰는 자연어 room 이름("living room", 공백)을 기대하므로 여기서 변환해준다.
ROOM_TYPE_DISPLAY = {
    "kitchen": "kitchen",
    "living_room": "living room",
    "bedroom": "bedroom",
    "bathroom": "bathroom",
}

USAGE_LOG_PATH = os.path.join(EXPERIMENT_NEW, "usage_log.json")

# central.py와 동일한 방식으로 API 키를 파일에서 읽어 환경변수로 설정
_API_KEY_PATH = os.path.join(REPO_ROOT, "LaMMA-P", "api_key.txt")
if os.path.exists(_API_KEY_PATH) and not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = open(_API_KEY_PATH).read().strip()


def log_usage_dict(method: str, task_n: str, usage: dict) -> None:
    """cda LLM의 usage() ({'llm_calls','prompt_tokens','completion_tokens'})를
    experiment_new 공통 usage_log.json 포맷으로 변환해 누적 기록한다."""
    entry = {
        "method": method,
        "task_n": task_n,
        "calls": usage.get("llm_calls", 0),
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
        "total_tokens": usage.get("prompt_tokens", 0) + usage.get("completion_tokens", 0),
    }
    logs = []
    if os.path.exists(USAGE_LOG_PATH):
        with open(USAGE_LOG_PATH, encoding="utf-8") as f:
            logs = json.load(f)
    logs.append(entry)
    with open(USAGE_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
    print(f"  [usage] {method}/{task_n}: calls={entry['calls']} total_tokens={entry['total_tokens']}")


def parse_deadline_min(task_text: str, default: int = 15) -> int:
    """'... in 10 minutes.' 같은 시간 제한을 task 문구에서 뽑는다.
    simple task처럼 시간이 없으면 default를 쓴다."""
    m = re.search(r"(\d+)\s*minutes?", task_text, re.IGNORECASE)
    return int(m.group(1)) if m else default


def _robot_label_sort_key(label: str) -> int:
    return int(label.lstrip("Rr"))


def build_cda_task_config(task_n: str, data: dict, mode: str = "multi_room"):
    """experiment_new 데이터(task.json/room.json/object.json/robot.json)를
    cda.schemas.TaskConfig로 변환한다."""
    task = data["tasks"][task_n]
    agent_info = build_agent_inputs(task_n, data, mode=mode)  # loader.py 공통 함수

    robot_map = task["single_room"]["robot"] if mode == "single_room" else task["robot"]

    agents_payload = []
    for label in sorted(agent_info.keys(), key=_robot_label_sort_key):
        info = agent_info[label]

        robot_ref = robot_map[label]
        robot_name = data["robots"][robot_ref["robot_n"]]["robot_name"]
        mobility = ROBOT_MOBILITY.get(robot_name, {"mobile": True, "payload_kg": None})

        agents_payload.append({
            "room": ROOM_TYPE_DISPLAY.get(info["room_type"], info["room_type"]),
            "mobile": mobility["mobile"],
            "payload_kg": mobility["payload_kg"],
            "capability": info["capability"],
            "images": info["images"],
            "hidden_info": info["hidden_info"],
        })

    deadline_min = parse_deadline_min(task["task"])
    return TaskConfig.from_notebook(
        task["task"], agents_payload, deadline_min=deadline_min, task_id=task_n,
    )


async def run_one(task_n: str, model: str, mode: str, use_edge_proposal: bool,
                  use_graph_llm: bool, max_graph_rounds: int, out_dir: str,
                  run_n: int = 1, mock_script: str | None = None):
    data = load_all()
    cfg = build_cda_task_config(task_n, data, mode=mode)

    if mock_script:
        llm = MockLLM(mock_script)
        print(f"MOCK 모드로 실행합니다 (스크립트: {mock_script})")
    else:
        llm = OpenAILLM(model=model, max_concurrency=4, image_detail="low")

    print(f"Task: {task_n}  (robots: {len(cfg.agents)}, deadline: {cfg.deadline_min} min, mode: {mode})")
    result = await run_pipeline(
        cfg, llm,
        use_edge_proposal=use_edge_proposal,
        use_graph_llm=use_graph_llm,
        max_graph_rounds=max_graph_rounds,
        out_dir=out_dir,
        verbose=True,
    )

    if not mock_script:
        log_usage_dict("ours_final", task_n, llm.usage())

    results_dir = os.path.join(EXPERIMENT_NEW, "results", f"run{run_n}")
    os.makedirs(results_dir, exist_ok=True)
    out_path = os.path.join(results_dir, f"{task_n}_ours_final_result.json")

    save_payload = {
        "task_n": task_n,
        "method": "ours_final",
        "mode": mode,
        "task_text": data["tasks"][task_n]["task"],
        "deadline_min": cfg.deadline_min,
        "offers": result["offers"],
        "local_plans": result["local_plans"],
        "plan_meta": result["plan_meta"],
        "judgments": result["judgments"],
        "graph": result["graph"],
        "joint_plan_text": result["joint_plan_text"],
        "metrics": {k: v for k, v in result["metrics"].items() if k != "config"},
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(save_payload, f, ensure_ascii=False, indent=2)

    print("\n완료\n")
    print(result["joint_plan_text"])
    print(f"\n저장: {out_path}")
    return save_payload


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True, help="예: task1_abstract")
    ap.add_argument("--model", default="gpt-4o")
    ap.add_argument("--mode", default="multi_room", choices=["multi_room", "single_room"])
    ap.add_argument("--no-proposal", action="store_true", help="ablation: Stage3(Edge Proposal) 생략")
    ap.add_argument("--no-graph-llm", action="store_true", help="ablation: Stage4를 규칙만으로")
    ap.add_argument("--rounds", type=int, default=2)
    ap.add_argument("--mock", default=None, help="API 호출 없이 테스트할 mock_script.json 경로")
    ap.add_argument("--run", type=int, default=1, help="실험 반복 회차 (results/run{N}/에 저장)")
    args = ap.parse_args()

    out_dir = os.path.join(EXPERIMENT_NEW, "results", f"run{args.run}", "ours_final_runs", args.task)
    asyncio.run(run_one(
        args.task, args.model, args.mode,
        use_edge_proposal=not args.no_proposal,
        use_graph_llm=not args.no_graph_llm,
        max_graph_rounds=args.rounds,
        out_dir=out_dir,
        run_n=args.run,
        mock_script=args.mock,
    ))


if __name__ == "__main__":
    main()
