from ai2thor.controller import Controller
from PIL import Image
import json
import os
import sys
import tty
import termios


def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def get_nearest(event, current_agent, attr):
    agent_pos = event.events[current_agent].metadata["agent"]["position"]
    visible_objs = [o for o in event.metadata["objects"] if o["visible"] and o.get(attr)]
    if not visible_objs:
        return None

    def dist(o):
        p = o["position"]
        return (p["x"] - agent_pos["x"]) ** 2 + (p["y"] - agent_pos["y"]) ** 2 + (p["z"] - agent_pos["z"]) ** 2

    return min(visible_objs, key=dist)


def interactive_capture(scene, agent_count, out_dir, prefix, robot_labels, robot_types=None, width=640, height=480, random_spawn=False, dirty_all=False):
    os.makedirs(out_dir, exist_ok=True)
    controller = Controller(scene=scene, agentCount=agent_count, width=width, height=height)

    if random_spawn:
        controller.step(action="InitialRandomSpawn", randomSeed=0, forceVisible=True, numPlacementAttempts=5)

    if dirty_all:
        event = controller.last_event
        dirtyable_ids = [o["objectId"] for o in event.metadata["objects"] if o.get("dirtyable")]
        for obj_id in dirtyable_ids:
            r = controller.step(action="DirtyObject", objectId=obj_id, forceAction=True)
        print(f"더럽게 만든 물건 수: {len(dirtyable_ids)}개")

    current_agent = 0
    shot_count = {i: 0 for i in range(agent_count)}
    held = {i: None for i in range(agent_count)}  # 현재 들고 있는 물건 objectId

    # 캡처할 때마다 로봇 위치/방향을 함께 기록 (PDDL 실행 시 초기 pose로 재사용 가능하도록)
    positions_path = os.path.join(out_dir, f"{prefix}_positions.json")
    if os.path.exists(positions_path):
        with open(positions_path, encoding="utf-8") as f:
            positions = json.load(f)
    else:
        positions = {}

    print(f"\n현재 조작 중인 로봇: {robot_labels[current_agent]}")
    print("숫자키(1~9): 로봇 전환 | w/a/s/d: 이동 | i/k: 고개 위/아래 | j/l: 좌/우 회전")
    print("o: 열기/닫기 | t: 켜기/끄기 | p: 집기/내려놓기 | b: 깨뜨리기 | v: 더럽히기/닦기")
    print("c: 캡처 | x: 종료\n")

    while True:
        key = get_key()

        if key.isdigit():
            idx = int(key) - 1
            if 0 <= idx < agent_count:
                current_agent = idx
                print(f"현재 조작 중인 로봇: {robot_labels[current_agent]}")
            else:
                print(f"로봇 {key}번은 존재하지 않습니다 (총 {agent_count}대)")
            continue

        if key == "w":
            controller.step(action="MoveAhead", agentId=current_agent)
        elif key == "s":
            controller.step(action="MoveBack", agentId=current_agent)
        elif key == "a":
            controller.step(action="MoveLeft", agentId=current_agent)
        elif key == "d":
            controller.step(action="MoveRight", agentId=current_agent)
        elif key == "i":
            controller.step(action="LookUp", degrees=30, agentId=current_agent)
        elif key == "k":
            controller.step(action="LookDown", degrees=30, agentId=current_agent)
        elif key == "j":
            controller.step(action="RotateLeft", degrees=45, agentId=current_agent)
        elif key == "l":
            controller.step(action="RotateRight", degrees=45, agentId=current_agent)

        elif key == "o":
            # 열기/닫기 (openable): 열려있으면 닫고, 닫혀있으면 연다
            event = controller.last_event
            target = get_nearest(event, current_agent, "openable")
            if target:
                action = "CloseObject" if target.get("isOpen") else "OpenObject"
                r = controller.step(action=action, objectId=target["objectId"], agentId=current_agent, forceAction=True)
                print(f"열기/닫기: {target['objectId']} ({action}) -> 성공={r.metadata['lastActionSuccess']}")
            else:
                print("열고 닫을 수 있는(보이는) 물건이 없습니다")

        elif key == "t":
            # 켜기/끄기 (toggleable)
            event = controller.last_event
            target = get_nearest(event, current_agent, "toggleable")
            if target:
                action = "ToggleObjectOff" if target.get("isToggled") else "ToggleObjectOn"
                r = controller.step(action=action, objectId=target["objectId"], agentId=current_agent, forceAction=True)
                print(f"켜기/끄기: {target['objectId']} ({action}) -> 성공={r.metadata['lastActionSuccess']}")
            else:
                print("켜고 끌 수 있는(보이는) 물건이 없습니다")

        elif key == "p":
            # 집기/내려놓기 (pickupable)
            event = controller.last_event
            if held[current_agent]:
                r = controller.step(action="DropHandObject", agentId=current_agent, forceAction=True)
                print(f"내려놓기: {held[current_agent]} -> 성공={r.metadata['lastActionSuccess']}")
                if r.metadata["lastActionSuccess"]:
                    held[current_agent] = None
            else:
                target = get_nearest(event, current_agent, "pickupable")
                if target:
                    r = controller.step(action="PickupObject", objectId=target["objectId"], agentId=current_agent, forceAction=True)
                    print(f"집기: {target['objectId']} -> 성공={r.metadata['lastActionSuccess']}")
                    if r.metadata["lastActionSuccess"]:
                        held[current_agent] = target["objectId"]
                else:
                    print("집을 수 있는(보이는) 물건이 없습니다")

        elif key == "b":
            # 깨뜨리기 (breakable)
            event = controller.last_event
            target = get_nearest(event, current_agent, "breakable")
            if target:
                r = controller.step(action="BreakObject", objectId=target["objectId"], agentId=current_agent, forceAction=True)
                print(f"깨뜨리기: {target['objectId']} -> 성공={r.metadata['lastActionSuccess']}")
            else:
                print("깨뜨릴 수 있는(보이는) 물건이 없습니다")

        elif key == "v":
            # 더럽히기/닦기 (dirtyable): 더러우면 닦고, 깨끗하면 더럽힌다
            event = controller.last_event
            target = get_nearest(event, current_agent, "dirtyable")
            if target:
                action = "CleanObject" if target.get("isDirty") else "DirtyObject"
                r = controller.step(action=action, objectId=target["objectId"], agentId=current_agent, forceAction=True)
                print(f"더럽히기/닦기: {target['objectId']} ({action}) -> 성공={r.metadata['lastActionSuccess']}")
            else:
                print("더럽히거나 닦을 수 있는(보이는) 물건이 없습니다")

        elif key == "c":
            shot_count[current_agent] += 1
            event = controller.last_event
            agent_event = event.events[current_agent]
            label = robot_labels[current_agent]
            path = os.path.join(out_dir, f"{prefix}_{label}_{shot_count[current_agent]}.png")
            Image.fromarray(agent_event.frame).save(path)

            agent_meta = agent_event.metadata["agent"]
            entry_key = f"{label}_{shot_count[current_agent]}"
            positions[entry_key] = {
                "image": os.path.basename(path),
                "robot_label": label,
                "robot_type": robot_types[current_agent] if robot_types else None,
                "position": agent_meta["position"],
                "rotation": agent_meta["rotation"],
                "cameraHorizon": agent_meta.get("cameraHorizon", 0),
            }
            with open(positions_path, "w", encoding="utf-8") as f:
                json.dump(positions, f, ensure_ascii=False, indent=2)

            print(f"saved: {path}  pos={agent_meta['position']} rot={agent_meta['rotation']}")

        elif key == "m":
            teleport_to_can(controller, current_agent)
        elif key == "x":
            break
        elif key == "\x03":
            break

    controller.stop()

ROBOT_NAME_BY_N = {0: "Gripper", 1: "Mobile_Light", 2: "Mobile_Heavy"}

EXPERIMENT_DIR = "/mnt/c/Users/shin/Desktop/AAMAS/experiment"


def load_task_config(task_n):
    with open(os.path.join(EXPERIMENT_DIR, "task", "task.json"), encoding="utf-8-sig") as f:
        tasks = {t["task_n"]: t for t in json.load(f)["tasks"]}
    t = tasks[task_n]
    floorplan_key = next(iter(t["rooms"]))  # e.g. "FP303"
    floorplan_n = floorplan_key[2:]
    robot_config = t["configs"]["4"]
    robot_types = [ROBOT_NAME_BY_N[r["robot_n"]] for r in robot_config]

    # task_n is "mat_compound" (-> task1) or "mat_compound_5" (-> task5)
    parts = task_n.rsplit("_", 1)
    if len(parts) == 2 and parts[1].isdigit():
        category, task_num = parts[0], parts[1]
    else:
        category, task_num = task_n, "1"

    return {
        "scene": f"FloorPlan{floorplan_n}",
        "agent_count": len(robot_config),
        "out_dir": os.path.join(EXPERIMENT_DIR, "image", "matthor", category, f"task{task_num}"),
        "prefix": f"{task_n}_{floorplan_key}",
        "robot_labels": [f"R{i+1}" for i in range(len(robot_config))],
        "robot_types": robot_types,
        "task_text": t["task"],
    }


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True, help="task.json 안의 task_n (예: mat_compound_5)")
    args = ap.parse_args()

    cfg = load_task_config(args.task)
    print(f"=== {args.task}: {cfg['task_text']}  (scene={cfg['scene']}) ===")
    print(f"robot_types: {cfg['robot_types']}")

    interactive_capture(
        scene=cfg["scene"],
        agent_count=cfg["agent_count"],
        out_dir=cfg["out_dir"],
        prefix=cfg["prefix"],
        robot_labels=cfg["robot_labels"],
        robot_types=cfg["robot_types"],
    )



def teleport_to_can(controller, current_agent):
    """가까운 오브젝트를 가장 가까운 GarbageCan 안으로 이동"""
    event = controller.last_event
    agent_pos = event.events[current_agent].metadata["agent"]["position"]

    # GarbageCan 찾기
    cans = [o for o in event.metadata["objects"] if "GarbageCan" in o["objectId"]]
    if not cans:
        print("GarbageCan을 찾을 수 없습니다")
        return

    def dist(o):
        p = o["position"]
        return (p["x"] - agent_pos["x"])**2 + (p["z"] - agent_pos["z"])**2

    nearest_can = min(cans, key=dist)
    can_pos = nearest_can["position"]

    # 가장 가까운 pickupable 오브젝트 찾기
    pickupable = [o for o in event.metadata["objects"] if o.get("pickupable") and o.get("visible")]
    if not pickupable:
        print("집을 수 있는 오브젝트가 없습니다")
        return

    target = min(pickupable, key=dist)
    new_pos = {"x": can_pos["x"], "y": can_pos["y"] + 0.1, "z": can_pos["z"]}

    r = controller.step(
        action="TeleportObject",
        rotation={"x": 0, "y": 0, "z": 0},
        objectId=target["objectId"],
        position=new_pos,
        forceAction=True
    )
    print(f"이동: {target['objectId']} → GarbageCan ({new_pos}) -> 성공={r.metadata['lastActionSuccess']}")
