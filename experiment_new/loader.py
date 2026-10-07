"""
experiment_new 구조를 읽어들이는 공통 로더.
"""
import base64
import io
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))

ROBOT_CODE_MAP = {
    "Gripper": 29,
    "Mobile_Heavy": 9,
    "Mobile_Light": 8,
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


def load_all():
    with open(os.path.join(BASE, "task", "task.json"), encoding="utf-8-sig") as f:
        tasks = json.load(f)["tasks"]
    with open(os.path.join(BASE, "scene", "room.json"), encoding="utf-8-sig") as f:
        rooms = {r["floorplan_n"]: r for r in json.load(f)["rooms"]}
    with open(os.path.join(BASE, "scene", "object.json"), encoding="utf-8-sig") as f:
        objects = {o["object_n"]: o for o in json.load(f)["objects"]}
    with open(os.path.join(BASE, "robot", "robot.json"), encoding="utf-8-sig") as f:
        robots = {r["robot_n"]: r for r in json.load(f)["robots"]}
    with open(os.path.join(BASE, "ground_truth", "goal_states.json"), encoding="utf-8-sig") as f:
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

    folder = os.path.join(BASE, "image", mode, task_type, f"task{task_num}")
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


def build_agent_inputs(task_n: str, data: dict, mode: str = "multi_room"):
    task = data["tasks"][task_n]
    agents = {}

    if mode == "single_room":
        single = task["single_room"]
        main_fp = single["main_room"]
        robot_map = single["robot"]

        for robot_label, robot_ref in robot_map.items():
            robot_type = data["robots"][robot_ref["robot_n"]]

            can = robot_type.get("robot_can", [])
            cannot = robot_type.get("robot_cannot", [])

            mobility_note = ""
            if "can_navigate" in cannot:
                mobility_note = (
                    " This robot is FIXED IN PLACE and can never move to another room. "
                    "To pass an item to another robot, that other robot must come to "
                    "this robot's own room first -- this robot can never travel "
                    "elsewhere to deliver anything."
                )

            capability = (
                f"{robot_type['robot_name']} in {fp_to_room_type(main_fp)}. "
                f"CAN: {', '.join(can) if can else 'none'}. "
                f"CANNOT: {', '.join(cannot) if cannot else 'none'}."
                f"{mobility_note}"
            )

            invisible_ids = task["invisible_list"].get(robot_label, [])
            hidden_info = [data["objects"][oid]["object_name"] for oid in invisible_ids if oid in data["objects"]]

            images = get_image_paths(task_n, robot_label, main_fp, mode=mode)

            agents[robot_label] = {
                "capability": capability,
                "images": images,
                "hidden_info": hidden_info,
                "fp": main_fp,
                "room_type": fp_to_room_type(main_fp),
            }

    else:
        for robot_label, robot_ref in task["robot"].items():
            robot_type = data["robots"][robot_ref["robot_n"]]
            fp = find_robot_fp(task, robot_label)

            can = robot_type.get("robot_can", [])
            cannot = robot_type.get("robot_cannot", [])

            mobility_note = ""
            if "can_navigate" in cannot:
                mobility_note = (
                    " This robot is FIXED IN PLACE and can never move to another room. "
                    "To pass an item to another robot, that other robot must come to "
                    "this robot's own room first -- this robot can never travel "
                    "elsewhere to deliver anything."
                )

            capability = (
                f"{robot_type['robot_name']} in {fp_to_room_type(fp)}. "
                f"CAN: {', '.join(can) if can else 'none'}. "
                f"CANNOT: {', '.join(cannot) if cannot else 'none'}."
                f"{mobility_note}"
            )

            invisible_ids = task["invisible_list"].get(robot_label, [])
            hidden_info = [data["objects"][oid]["object_name"] for oid in invisible_ids if oid in data["objects"]]

            images = get_image_paths(task_n, robot_label, fp, mode=mode)

            agents[robot_label] = {
                "capability": capability,
                "images": images,
                "hidden_info": hidden_info,
                "fp": fp,
                "room_type": fp_to_room_type(fp),
            }

    return agents


def build_lamma_p_input(task_n: str, data: dict) -> dict:
    task = data["tasks"][task_n]
    single = task["single_room"]
    main_fp = single["main_room"]
    robot_map = single["robot"]

    robot_list = []
    for robot_label, robot_ref in robot_map.items():
        robot_type = data["robots"][robot_ref["robot_n"]]
        robot_name = robot_type["robot_name"]
        code = ROBOT_CODE_MAP.get(robot_name)
        if code is None:
            raise ValueError(f"robot_code_map에 없는 로봇 타입: {robot_name}")
        robot_list.append(code)

    return {
        "task": task["task"],
        "robot list": robot_list,
        "object_states": [],
        "trans": 0,
        "max_trans": 0,
        "_main_room_fp": main_fp,
    }


# ---------------------------------------------------------------------------
# 이미지 다운그레이드 (API 비용 절감용)
# ---------------------------------------------------------------------------
def encode_image_resized(path: str, max_side: int = 512, quality: int = 70) -> str:
    """
    이미지를 리사이즈 + JPEG 재압축한 뒤 base64로 인코딩해서 반환.
    OpenAI Vision API에 보낼 data URL 문자열(prefix 포함)을 돌려준다.
    max_side: 가로/세로 중 긴 쪽을 이 값으로 맞춤 (비율 유지)
    """
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


def build_image_content_blocks(image_paths, max_side: int = 512, quality: int = 70):
    """
    이미지 경로 리스트를 받아, OpenAI chat API의 content 블록 리스트(이미지 부분)로 변환.
    """
    blocks = []
    for p in image_paths:
        if not os.path.exists(p):
            continue
        data_url = encode_image_resized(p, max_side=max_side, quality=quality)
        blocks.append({"type": "image_url", "image_url": {"url": data_url}})
    return blocks


# ---------------------------------------------------------------------------
# API 사용량 누적 추적
# ---------------------------------------------------------------------------
def log_usage(method: str, task_n: str, response):
    """
    OpenAI 응답 객체(response.usage)에서 토큰 사용량을 뽑아
    experiment_new/usage_log.json에 누적 기록하고, 이번 호출/누적 합계를 출력한다.
    """
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
        print("  [usage] 토큰 정보를 가져올 수 없음 (response.usage 없음)")
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
    by_method = {}
    for e in log:
        by_method[e["method"]] = by_method.get(e["method"], 0) + e["total_tokens"]

    print(f"  [usage] 이번 호출: {entry['total_tokens']} tokens  |  누적 총합: {total} tokens")
    print(f"  [usage] 방법론별 누적: " + ", ".join(f"{m}={t}" for m, t in by_method.items()))


def log_usage_from_metrics(method: str, task_n: str, metrics: dict):
    """
    ours_new pipeline이 반환하는 result["metrics"]["llm"] 딕셔너리
    ({"calls":.., "prompt_tokens":.., "completion_tokens":..})를 받아
    experiment_new/usage_log.json에 누적 기록한다.
    """
    usage_path = os.path.join(BASE, "usage_log.json")
    log = []
    if os.path.exists(usage_path):
        with open(usage_path, encoding="utf-8") as f:
            try:
                log = json.load(f)
            except json.JSONDecodeError:
                log = []

    llm_metrics = metrics.get("llm", {})
    prompt_tokens = llm_metrics.get("prompt_tokens", 0)
    completion_tokens = llm_metrics.get("completion_tokens", 0)
    total_tokens = prompt_tokens + completion_tokens

    entry = {
        "method": method,
        "task_n": task_n,
        "calls": llm_metrics.get("calls", 0),
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

    # GPT-4o 가격 기준 (2026 초 USD): input $2.5/1M, output $10/1M tokens
    # 환율은 대략 1 USD = 1,400 KRW로 고정 계산
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

    calls_n = entry["calls"]
    print(f"  [usage] 이번 실행: {calls_n}회 호출, {total_tokens} tokens (약 {this_cost:.1f}원)")
    print(f"  [usage] 누적 총합: {total} tokens (약 {total_cost:.1f}원)")
    print("  [usage] 방법론별 누적: " + ", ".join(f"{m}={t}" for m, t in by_method.items()))


if __name__ == "__main__":
    data = load_all()
    print("=== multi_room ===")
    agents = build_agent_inputs("task1_abstract", data, mode="multi_room")
    for label, info in agents.items():
        print(label, "->", info["room_type"], info["fp"], "images:", [os.path.basename(p) for p in info["images"]])
