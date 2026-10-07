from ai2thor.controller import Controller
from PIL import Image
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


def interactive_capture(scene, agent_count, out_dir, prefix, robot_labels, width=640, height=480, random_spawn=False, dirty_all=False):
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
            print(f"saved: {path}")

        elif key == "x":
            break
        elif key == "\x03":
            break

    controller.stop()

if __name__ == "__main__":
    interactive_capture(
        scene="FloorPlan320",
        agent_count=1,
        out_dir="/home/user/journal_co/experiment_new/image/multi_room/abstract/task5",
        prefix="task5_abstract_bedroom",
        robot_labels=["R3"],
    )