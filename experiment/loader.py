"""
experiment 공통 로더.
task/, scene/, robot/, image/ 데이터를 읽어
C-DA의 TaskConfig 형식으로 변환한다.
"""
import base64
import io
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
EXPERIMENT_DIR = BASE


def load_all():
    """experiment 데이터를 모두 읽어 반환."""
    with open(os.path.join(EXPERIMENT_DIR, "task", "task.json"), encoding="utf-8-sig") as f:
        tasks = json.load(f)["tasks"]
    with open(os.path.join(EXPERIMENT_DIR, "scene", "room.json"), encoding="utf-8-sig") as f:
        rooms = {r["floorplan_n"]: r for r in json.load(f)["rooms"]}
    with open(os.path.join(EXPERIMENT_DIR, "scene", "object.json"), encoding="utf-8-sig") as f:
        objects = {o["object_n"]: o for o in json.load(f)["objects"]}
    with open(os.path.join(EXPERIMENT_DIR, "robot", "robot.json"), encoding="utf-8-sig") as f:
        robots = {r["robot_n"]: r for r in json.load(f)["robots"]}
    with open(os.path.join(EXPERIMENT_DIR, "ground_truth", "goal_states.json"), encoding="utf-8-sig") as f:
        goal_states = json.load(f)

    return {
        "tasks": {t["task_n"]: t for t in tasks},
        "rooms": rooms,
        "objects": objects,
        "robots": robots,
        "goal_states": goal_states,
    }


def fp_to_room_type(fp: str) -> str:
    num = int(fp.replace("FP", ""))
    if num >= 400:
        return "bathroom"
    elif num >= 300:
        return "bedroom"
    elif num >= 200:
        return "living_room"
    else:
        return "kitchen"


def get_image_paths(task_n: str, robot_label: str, fp: str, mode: str = "multi_room", n_robots: int = 4):
    parts = task_n.split("_")
    task_num = parts[0].replace("task", "")
    task_type = parts[1]
    folder_n = f"n_{n_robots}"

    folder = os.path.join(EXPERIMENT_DIR, "image", task_type, f"task{task_num}", folder_n)
    prefix = f"task{task_num}_{task_type}_{fp}_{robot_label}"

    if mode == "single_room":
        return [os.path.join(folder, f"{prefix}_1.png")]
    else:
        return [
            os.path.join(folder, f"{prefix}_1.png"),
            os.path.join(folder, f"{prefix}_2.png"),
        ]


def build_cda_task_config(task_n: str, data: dict, mode: str = "multi_room",
                          deadline_min: int = 20, n_robots: int = 4) -> dict:
    """
    task.json 데이터를 C-DA TaskConfig 형식으로 변환.
    n_robots: 사용할 로봇 수 설정 (configs의 키)
    """
    task = data["tasks"][task_n]
    agents = []

    # configs에서 해당 n_robots 설정 가져오기
    n_str = str(n_robots)
    if n_str not in task["configs"]:
        available = list(task["configs"].keys())
        raise ValueError(f"{task_n}에 n={n_robots} 설정 없음. 사용 가능: {available}")

    robot_list = task["configs"][n_str]

    # main_room 찾기 (single_room 모드용)
    main_fp = next(fp for fp, info in task["rooms"].items() if info["main_room"])

    for i, robot_ref in enumerate(robot_list, 1):
        robot_label = f"R{i}"
        robot_type = data["robots"][robot_ref["robot_n"]]
        fp = robot_ref["room"]

        if mode == "single_room":
            fp_for_image = main_fp
        else:
            fp_for_image = fp

        agents.append(_build_agent(
            task_n, task, robot_label, robot_type,
            fp, fp_for_image, data, mode, n_robots
        ))

    return {
        "task_id": task_n,
        "task": task["task"],
        "deadline_min": deadline_min,
        "agents": agents,
    }


def _build_agent(task_n, task, robot_label, robot_type, fp, fp_for_image, data, mode, n_robots):
    can = robot_type.get("robot_can", [])
    cannot = robot_type.get("robot_cannot", [])

    mobile = "can_navigate" in can
    robot_name = robot_type["robot_name"]

    payload_map = {"Mobile_Heavy": 20.0, "Mobile_Light": 5.0, "Gripper": None}
    payload_kg = payload_map.get(robot_name)

    mobility_note = ""
    if not mobile:
        mobility_note = (
            " This robot is FIXED IN PLACE and can never move to another room. "
            "To pass an item to another robot, that other robot must come to "
            "this robot's own room first."
        )

    can_str = ", ".join(c for c in can if c != "can_navigate") or "none"
    cannot_str = ", ".join(c for c in cannot if c != "can_navigate") or "none"
    capability = (
        f"{robot_name}. "
        f"CAN: {can_str}. "
        f"CANNOT: {cannot_str}."
        f"{mobility_note}"
    )

    # hidden_objects: rooms[fp]에서 가져오기
    room_info = task["rooms"].get(fp, {})
    hidden_objects = room_info.get("hidden_objects", {})
    hidden_lines = []
    for container, obj_ids in hidden_objects.items():
        for oid in obj_ids:
            if oid in data["objects"]:
                hidden_lines.append(f"{data['objects'][oid]['object_name']} (in {container})")
    hidden_info = "\n".join(hidden_lines)

    images = get_image_paths(task_n, robot_label, fp_for_image, mode=mode, n_robots=n_robots)

    return {
        "room": fp_to_room_type(fp),
        "mobile": mobile,
        "capability": capability,
        "payload_kg": payload_kg,
        "images": images,
        "hidden_info": hidden_info,
    }


def build_agent_inputs(task_n: str, data: dict, mode: str = "multi_room", n_robots: int = 4) -> dict:
    """central/independent 베이스라인용 agent 입력 생성."""
    task = data["tasks"][task_n]
    agents = {}

    n_str = str(n_robots)
    robot_list = task["configs"][n_str]
    main_fp = next(fp for fp, info in task["rooms"].items() if info["main_room"])

    for i, robot_ref in enumerate(robot_list, 1):
        robot_label = f"R{i}"
        robot_type = data["robots"][robot_ref["robot_n"]]
        fp = robot_ref["room"]
        fp_for_image = main_fp if mode == "single_room" else fp

        a = _build_agent(task_n, task, robot_label, robot_type,
                         fp, fp_for_image, data, mode, n_robots)
        agents[robot_label] = {
            "capability": a["capability"],
            "images": a["images"],
            "hidden_info": a["hidden_info"],
            "fp": fp,
            "room_type": a["room"],
        }
    return agents


ROBOT_CODE_MAP = {
    "Gripper": 29,
    "Mobile_Heavy": 9,
    "Mobile_Light": 8,
}


def build_lamma_p_input(task_n: str, data: dict, n_robots: int = 4) -> dict:
    """LaMMA-P / SMART-LLM 입력 생성."""
    task = data["tasks"][task_n]
    main_fp = next(fp for fp, info in task["rooms"].items() if info["main_room"])
    robot_list = task["configs"][str(n_robots)]

    robot_codes = []
    for robot_ref in robot_list:
        robot_type = data["robots"][robot_ref["robot_n"]]
        robot_name = robot_type["robot_name"]
        code = ROBOT_CODE_MAP.get(robot_name)
        if code is None:
            raise ValueError(f"ROBOT_CODE_MAP에 없는 로봇 타입: {robot_name}")
        robot_codes.append(code)

    return {
        "task": task["task"],
        "robot list": robot_codes,
        "object_states": [],
        "trans": 0,
        "max_trans": 0,
        "_main_room_fp": main_fp,
    }


def log_usage_from_metrics(method: str, task_n: str, metrics: dict):
    usage_path = os.path.join(BASE, "usage_log.json")
    log = []
    if os.path.exists(usage_path):
        with open(usage_path, encoding="utf-8") as f:
            try:
                log = json.load(f)
            except json.JSONDecodeError:
                log = []

    prompt_tokens = metrics.get("prompt_tokens", 0)
    completion_tokens = metrics.get("completion_tokens", 0)
    total_tokens = prompt_tokens + completion_tokens
    calls_n = metrics.get("llm_calls", 0)

    entry = {
        "method": method,
        "task_n": task_n,
        "calls": calls_n,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
    }
    log.append(entry)

    with open(usage_path, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

    USD_PER_1M_INPUT = 2.5
    USD_PER_1M_OUTPUT = 10.0
    KRW_PER_USD = 1400

    def tokens_to_krw(p_tok, c_tok):
        usd = (p_tok / 1_000_000) * USD_PER_1M_INPUT + (c_tok / 1_000_000) * USD_PER_1M_OUTPUT
        return usd * KRW_PER_USD

    this_cost = tokens_to_krw(prompt_tokens, completion_tokens)
    total_prompt = sum(e.get("prompt_tokens", 0) for e in log)
    total_completion = sum(e.get("completion_tokens", 0) for e in log)
    total_cost = tokens_to_krw(total_prompt, total_completion)

    print(f"  [usage] 이번 실행: {calls_n}회 호출, {total_tokens} tokens (약 {this_cost:.1f}원)")
    print(f"  [usage] 누적 총합: {total_prompt + total_completion} tokens (약 {total_cost:.1f}원)")


def log_usage(method: str, task_n: str, response):
    usage_path = os.path.join(BASE, "usage_log.json")
    log = []
    if os.path.exists(usage_path):
        with open(usage_path, encoding="utf-8") as f:
            try:
                log = json.load(f)
            except json.JSONDecodeError:
                log = []

    usage = getattr(response, "usage", None)
    if usage is None:
        return

    entry = {
        "method": method,
        "task_n": task_n,
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
        "total_tokens": usage.total_tokens,
    }
    log.append(entry)

    with open(usage_path, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

    total = sum(e["total_tokens"] for e in log)
    print(f"  [usage] 이번 호출: {entry['total_tokens']} tokens  |  누적 총합: {total} tokens")
