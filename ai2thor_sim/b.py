"""a.py와 조작/기능은 동일하지만 task.json에 묶이지 않고, FloorPlan 번호만 지정하면 바로 돌아가는 버전.
스크린샷은 라벨/프리픽스 없이 FP{방번호}_{n번째 사진}.jpg 로 ai2thor_sim/screenshot 폴더에 저장된다.
"""
from ai2thor.controller import Controller
from PIL import Image
import cv2
import glob
import json
import os
import re
import sys

TOPDOWN_WINDOW = "topdown"

HERE = os.path.dirname(os.path.abspath(__file__))
SCREENSHOT_DIR = os.path.join(HERE, "screenshot")

if sys.platform == "win32":
    import msvcrt

    def get_key():
        ch = msvcrt.getch()
        if ch in (b"\x00", b"\xe0"):   # arrow/function key prefix: swallow the second byte, no mapped action
            msvcrt.getch()
            return ""
        try:
            return ch.decode()
        except UnicodeDecodeError:
            return ""
else:
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


def teleport_to_can(controller, current_agent):
    """가까운 오브젝트를 가장 가까운 GarbageCan 안으로 이동"""
    event = controller.last_event
    agent_pos = event.events[current_agent].metadata["agent"]["position"]

    cans = [o for o in event.metadata["objects"] if "GarbageCan" in o["objectId"]]
    if not cans:
        print("GarbageCan을 찾을 수 없습니다")
        return

    def dist(o):
        p = o["position"]
        return (p["x"] - agent_pos["x"]) ** 2 + (p["z"] - agent_pos["z"]) ** 2

    nearest_can = min(cans, key=dist)
    can_pos = nearest_can["position"]

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


def _next_shot_index(fp_number: str) -> int:
    """screenshot 폴더에 이미 FP{fp_number}_{i}.jpg 가 있으면 그 다음 번호부터 이어서 찍는다."""
    existing = glob.glob(os.path.join(SCREENSHOT_DIR, f"FP{fp_number}_*.jpg"))
    nums = []
    for p in existing:
        m = re.search(rf"FP{fp_number}_(\d+)\.jpg$", os.path.basename(p))
        if m:
            nums.append(int(m.group(1)))
    return (max(nums) + 1) if nums else 1


def _add_topdown_camera(controller):
    event = controller.step(action="GetMapViewCameraProperties")
    pose = event.metadata["actionReturn"].copy()
    pose["orthographic"] = True
    return controller.step(action="AddThirdPartyCamera", **pose)


def _show_topdown(controller):
    frames = controller.last_event.third_party_camera_frames
    if not frames:
        return
    frame = cv2.cvtColor(frames[0], cv2.COLOR_RGB2BGR)
    cv2.imshow(TOPDOWN_WINDOW, frame)
    cv2.waitKey(1)


def interactive_capture(fp_number: str, agent_count: int, width=640, height=480,
                        random_spawn=False, dirty_all=False, topdown=True):
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    scene = f"FloorPlan{fp_number}"
    controller = Controller(scene=scene, agentCount=agent_count, width=width, height=height)

    if topdown:
        _add_topdown_camera(controller)
        _show_topdown(controller)

    if random_spawn:
        controller.step(action="InitialRandomSpawn", randomSeed=0, forceVisible=True, numPlacementAttempts=5)

    if dirty_all:
        event = controller.last_event
        dirtyable_ids = [o["objectId"] for o in event.metadata["objects"] if o.get("dirtyable")]
        for obj_id in dirtyable_ids:
            controller.step(action="DirtyObject", objectId=obj_id, forceAction=True)
        print(f"더럽게 만든 물건 수: {len(dirtyable_ids)}개")

    current_agent = 0
    shot_count = _next_shot_index(fp_number) - 1   # 다음 캡처에서 +1 되어 올바른 번호가 됨
    held = {i: None for i in range(agent_count)}

    print(f"\n씬: {scene}  로봇 수: {agent_count}  스크린샷 폴더: {SCREENSHOT_DIR}")
    print(f"현재 조작 중인 로봇: R{current_agent + 1}")
    print("숫자키(1~9): 로봇 전환 | w/a/s/d: 이동 | i/k: 고개 위/아래 | j/l: 좌/우 회전")
    print("o: 열기/닫기 | t: 켜기/끄기 | p: 집기/내려놓기 | b: 깨뜨리기 | v: 더럽히기/닦기")
    print("c: 캡처 | x: 종료\n")

    while True:
        key = get_key()

        if key.isdigit():
            idx = int(key) - 1
            if 0 <= idx < agent_count:
                current_agent = idx
                print(f"현재 조작 중인 로봇: R{current_agent + 1}")
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
            event = controller.last_event
            target = get_nearest(event, current_agent, "openable")
            if target:
                action = "CloseObject" if target.get("isOpen") else "OpenObject"
                r = controller.step(action=action, objectId=target["objectId"], agentId=current_agent, forceAction=True)
                print(f"열기/닫기: {target['objectId']} ({action}) -> 성공={r.metadata['lastActionSuccess']}")
            else:
                print("열고 닫을 수 있는(보이는) 물건이 없습니다")

        elif key == "t":
            event = controller.last_event
            target = get_nearest(event, current_agent, "toggleable")
            if target:
                action = "ToggleObjectOff" if target.get("isToggled") else "ToggleObjectOn"
                r = controller.step(action=action, objectId=target["objectId"], agentId=current_agent, forceAction=True)
                print(f"켜기/끄기: {target['objectId']} ({action}) -> 성공={r.metadata['lastActionSuccess']}")
            else:
                print("켜고 끌 수 있는(보이는) 물건이 없습니다")

        elif key == "p":
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
            event = controller.last_event
            target = get_nearest(event, current_agent, "breakable")
            if target:
                r = controller.step(action="BreakObject", objectId=target["objectId"], agentId=current_agent, forceAction=True)
                print(f"깨뜨리기: {target['objectId']} -> 성공={r.metadata['lastActionSuccess']}")
            else:
                print("깨뜨릴 수 있는(보이는) 물건이 없습니다")

        elif key == "v":
            event = controller.last_event
            target = get_nearest(event, current_agent, "dirtyable")
            if target:
                action = "CleanObject" if target.get("isDirty") else "DirtyObject"
                r = controller.step(action=action, objectId=target["objectId"], agentId=current_agent, forceAction=True)
                print(f"더럽히기/닦기: {target['objectId']} ({action}) -> 성공={r.metadata['lastActionSuccess']}")
            else:
                print("더럽히거나 닦을 수 있는(보이는) 물건이 없습니다")

        elif key == "c":
            shot_count += 1
            event = controller.last_event
            agent_event = event.events[current_agent]
            path = os.path.join(SCREENSHOT_DIR, f"FP{fp_number}_{shot_count}.jpg")
            Image.fromarray(agent_event.frame).convert("RGB").save(path, "JPEG")

            agent_meta = agent_event.metadata["agent"]
            print(f"saved: {path}  pos={agent_meta['position']} rot={agent_meta['rotation']}")

        elif key == "m":
            teleport_to_can(controller, current_agent)
        elif key == "x":
            break
        elif key == "\x03":
            break

        if topdown:
            _show_topdown(controller)

    cv2.destroyAllWindows()
    controller.stop()


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--fp", required=True, help="FloorPlan 번호 (예: 324 또는 FP324)")
    ap.add_argument("--n", type=int, default=1, help="로봇(agent) 수 (기본 1)")
    ap.add_argument("--random-spawn", action="store_true")
    ap.add_argument("--dirty-all", action="store_true")
    ap.add_argument("--no-topdown", action="store_true", help="실시간 탑뷰 창을 띄우지 않음")
    args = ap.parse_args()

    fp_number = args.fp.upper().removeprefix("FP")
    print(f"=== FloorPlan{fp_number}  로봇 수: {args.n} ===")

    interactive_capture(
        fp_number=fp_number,
        agent_count=args.n,
        random_spawn=args.random_spawn,
        dirty_all=args.dirty_all,
        topdown=not args.no_topdown,
    )
