"""
experiment 공통 로더.
experiment_new 구조(task/, scene/, robot/, image/)를 읽어
C-DA의 TaskConfig 형식으로 변환한다.
"""
import base64
import io
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))

# experiment_new 데이터 폴더 (상위 폴더에 있다고 가정)
# 실행 위치: C:\Users\shin\Desktop\AAMAS\experiment\
# 데이터:   C:\Users\shin\Desktop\AAMAS\experiment_new\
EXPERIMENT_NEW_DIR = BASE


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


def load_all():
    """experiment_new의 JSON 데이터를 모두 읽어 반환."""
    with open(os.path.join(EXPERIMENT_NEW_DIR, "task", "task.json"), encoding="utf-8-sig") as f:
        tasks = json.load(f)["tasks"]
    with open(os.path.join(EXPERIMENT_NEW_DIR, "scene", "room.json"), encoding="utf-8-sig") as f:
        rooms = {r["floorplan_n"]: r for r in json.load(f)["rooms"]}
    with open(os.path.join(EXPERIMENT_NEW_DIR, "scene", "object.json"), encoding="utf-8-sig") as f:
        objects = {o["object_n"]: o for o in json.load(f)["objects"]}
    with open(os.path.join(EXPERIMENT_NEW_DIR, "robot", "robot.json"), encoding="utf-8-sig") as f:
        robots = {r["robot_n"]: r for r in json.load(f)["robots"]}
    with open(os.path.join(EXPERIMENT_NEW_DIR, "ground_truth", "goal_states.json"), encoding="utf-8-sig") as f:
        goal_states = json.load(f)

    return {
        "tasks": {t["task_n"]: t for t in tasks},
        "rooms": rooms,
        "objects": objects,
        "robots": robots,
        "goal_states": goal_states,
    }


def get_image_paths(task_n: str, robot_label: str, fp: str, mode: str = "multi_room"):
    parts = task_n.split("_")
    task_num = parts[0].replace("task", "")
    task_type = parts[1]

    folder = os.path.join(EXPERIMENT_NEW_DIR, "image", mode, task_type, f"task{task_num}")
    prefix = f"task{task_num}_{task_type}_{fp}_{robot_label}"

    if mode == "single_room":
        return [os.path.join(folder, f"{prefix}_1.png")]
    else:
        return [
            os.path.join(folder, f"{prefix}_1.png"),
            os.path.join(folder, f"{prefix}_2.png"),
        ]


def find_robot_fp(task: dict, robot_label: str) -> str:
    for fp, info in task["room"].items():
        if robot_label in info["robots"]:
            return fp
    raise ValueError(f"{robot_label} not found in task room mapping")


def build_cda_task_config(task_n: str, data: dict, mode: str = "multi_room",
                          deadline_min: int = 20) -> dict:
    """
    experiment_new 데이터를 C-DA TaskConfig.from_notebook() 형식으로 변환.

    반환값:
        {
            "task_id": str,
            "task": str,
            "deadline_min": int,
            "agents": [
                {
                    "room": str,          # C-DA Profile.room
                    "mobile": bool,       # C-DA Profile.mobile
                    "capability": str,    # C-DA Profile.embodiment
                    "payload_kg": float|None,
                    "images": [str],
                    "hidden_info": str,
                }
            ]
        }
    """
    task = data["tasks"][task_n]
    agents = []

    if mode == "single_room":
        single = task["single_room"]
        main_fp = single["main_room"]
        robot_map = single["robot"]

        for robot_label in sorted(robot_map.keys()):
            robot_ref = robot_map[robot_label]
            robot_type = data["robots"][robot_ref["robot_n"]]
            fp = main_fp
            agents.append(_build_agent(task_n, task, robot_label, robot_type, fp, data, mode))

    else:  # multi_room
        for robot_label in sorted(task["robot"].keys()):
            robot_ref = task["robot"][robot_label]
            robot_type = data["robots"][robot_ref["robot_n"]]
            fp = find_robot_fp(task, robot_label)
            agents.append(_build_agent(task_n, task, robot_label, robot_type, fp, data, mode))

    return {
        "task_id": task_n,
        "task": task["task"],
        "deadline_min": deadline_min,
        "agents": agents,
    }


def _build_agent(task_n, task, robot_label, robot_type, fp, data, mode):
    can = robot_type.get("robot_can", [])
    cannot = robot_type.get("robot_cannot", [])

    mobile = "can_navigate" in can
    robot_name = robot_type["robot_name"]

    # payload_kg: Mobile_Heavy=20, Mobile_Light=5, Gripper=None(fixed)
    payload_map = {"Mobile_Heavy": 20.0, "Mobile_Light": 5.0, "Gripper": None}
    payload_kg = payload_map.get(robot_name)

    # embodiment: capability 설명 (can/cannot 기반)
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

    # hidden_info
    invisible_ids = task.get("invisible_list", {}).get(robot_label, [])
    hidden_lines = [data["objects"][oid]["object_name"] for oid in invisible_ids if oid in data["objects"]]
    hidden_info = "\n".join(hidden_lines)

    # images
    images = get_image_paths(task_n, robot_label, fp, mode=mode)

    return {
        "room": fp_to_room_type(fp),
        "mobile": mobile,
        "capability": capability,
        "payload_kg": payload_kg,
        "images": images,
        "hidden_info": hidden_info,
    }


# ---------------------------------------------------------------------------
# 이미지 리사이즈 + base64 인코딩 (API 비용 절감)
# ---------------------------------------------------------------------------
def encode_image_resized(path: str, max_side: int = 512, quality: int = 70) -> str:
    from PIL import Image
    img = Image.open(path).convert("RGB")
    w, h = img.size
    scale = max_side / max(w, h)
    if scale < 1:
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality)
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"


# ---------------------------------------------------------------------------
# API 사용량 누적 추적
# ---------------------------------------------------------------------------
def log_usage_from_metrics(method: str, task_n: str, metrics: dict):
    """
    C-DA pipeline의 result["metrics"] 딕셔너리를 받아
    experiment/usage_log.json에 누적 기록한다.
    """
    usage_path = os.path.join(BASE, "usage_log.json")
    log = []
    if os.path.exists(usage_path):
        with open(usage_path, encoding="utf-8") as f:
            try:
                log = json.load(f)
            except json.JSONDecodeError:
                log = []

    # C-DA metrics 구조: metrics["llm_calls"], metrics["prompt_tokens"], metrics["completion_tokens"]
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

    total = sum(e["total_tokens"] for e in log)
    by_method = {}
    for e in log:
        by_method[e["method"]] = by_method.get(e["method"], 0) + e["total_tokens"]

    # GPT-4o 가격 기준: input $2.5/1M, output $10/1M tokens, 1 USD = 1,400 KRW
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
    print(f"  [usage] 누적 총합: {total} tokens (약 {total_cost:.1f}원)")
    print("  [usage] 방법론별 누적: " + ", ".join(f"{m}={t}" for m, t in by_method.items()))


def build_agent_inputs(task_n: str, data: dict, mode: str = "multi_room") -> dict:
    """
    central/independent 베이스라인용 agent 입력 생성.
    experiment_new/loader.py의 build_agent_inputs와 동일한 인터페이스.
    """
    task = data["tasks"][task_n]
    agents = {}

    if mode == "single_room":
        single = task["single_room"]
        main_fp = single["main_room"]
        robot_map = single["robot"]
        for robot_label in sorted(robot_map.keys()):
            robot_ref = robot_map[robot_label]
            robot_type = data["robots"][robot_ref["robot_n"]]
            fp = main_fp
            a = _build_agent(task_n, task, robot_label, robot_type, fp, data, mode)
            agents[robot_label] = {
                "capability": a["capability"],
                "images": a["images"],
                "hidden_info": a["hidden_info"].split("\n") if a["hidden_info"] else [],
                "fp": fp,
                "room_type": a["room"],
            }
    else:
        for robot_label in sorted(task["robot"].keys()):
            robot_ref = task["robot"][robot_label]
            robot_type = data["robots"][robot_ref["robot_n"]]
            fp = find_robot_fp(task, robot_label)
            a = _build_agent(task_n, task, robot_label, robot_type, fp, data, mode)
            agents[robot_label] = {
                "capability": a["capability"],
                "images": a["images"],
                "hidden_info": a["hidden_info"].split("\n") if a["hidden_info"] else [],
                "fp": fp,
                "room_type": a["room"],
            }
    return agents


ROBOT_CODE_MAP = {
    "Gripper": 29,
    "Mobile_Heavy": 9,
    "Mobile_Light": 8,
}


def build_lamma_p_input(task_n: str, data: dict) -> dict:
    """LaMMA-P / SMART-LLM 입력 생성."""
    task = data["tasks"][task_n]
    single = task["single_room"]
    main_fp = single["main_room"]
    robot_map = single["robot"]

    robot_list = []
    for robot_label in sorted(robot_map.keys()):
        robot_ref = robot_map[robot_label]
        robot_type = data["robots"][robot_ref["robot_n"]]
        robot_name = robot_type["robot_name"]
        code = ROBOT_CODE_MAP.get(robot_name)
        if code is None:
            raise ValueError(f"ROBOT_CODE_MAP에 없는 로봇 타입: {robot_name}")
        robot_list.append(code)

    return {
        "task": task["task"],
        "robot list": robot_list,
        "object_states": [],
        "trans": 0,
        "max_trans": 0,
        "_main_room_fp": main_fp,
    }


def log_usage(method: str, task_n: str, response):
    """OpenAI 응답 객체에서 토큰 사용량을 뽑아 usage_log.json에 누적 기록."""
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
        print("  [usage] 토큰 정보를 가져올 수 없음")
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


if __name__ == "__main__":
    data = load_all()
    print("=== tasks ===")
    for k in list(data["tasks"].keys())[:3]:
        print(k)
    print("\n=== multi_room agent inputs (task1_abstract) ===")
    cfg_dict = build_cda_task_config("task1_abstract", data, mode="multi_room")
    for a in cfg_dict["agents"]:
        print(f"  room={a['room']}  mobile={a['mobile']}  payload={a['payload_kg']}  images={[os.path.basename(p) for p in a['images']]}")
