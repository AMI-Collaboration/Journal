"""
experiment_new 구조를 읽어들이는 공통 로더.
"""
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

    else:  # multi_room
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
    """
    LaMMA-P / SMART-LLM이 기대하는 입력 형식으로 변환.
    single_room 구성(main_room에 모든 로봇) 기준으로 robot list를 만든다.

    반환 예:
        {"task": "...", "robot list": [29,9,8,8], "object_states": [], "trans": 0, "max_trans": 0}
    """
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
        "_main_room_fp": main_fp,  # 내부적으로 FloorPlan 번호 찾을 때 사용, 실제 저장 시 제거 가능
    }


if __name__ == "__main__":
    data = load_all()

    print("=== multi_room ===")
    agents = build_agent_inputs("task1_abstract", data, mode="multi_room")
    for label, info in agents.items():
        print(label, "->", info["room_type"], info["fp"], "images:", [os.path.basename(p) for p in info["images"]])

    print("\n=== single_room ===")
    agents = build_agent_inputs("task1_abstract", data, mode="single_room")
    for label, info in agents.items():
        print(label, "->", info["room_type"], info["fp"], "images:", [os.path.basename(p) for p in info["images"]])

    print("\n=== lamma_p_input ===")
    lamma_input = build_lamma_p_input("task1_abstract", data)
    print(json.dumps(lamma_input, indent=2))
