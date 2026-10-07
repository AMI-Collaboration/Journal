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


def capture_topdown(controller, out_dir, prefix, top_shot_count):
    """에이전트 0을 임시로 위로 올려서 탑뷰 찍고 복귀"""
    event = controller.last_event
    # 현재 에이전트 0 위치 저장
    pos = event.events[0].metadata["agent"]["position"]
    rot = event.events[0].metadata["agent"]["rotation"]

    # 위로 텔레포트해서 아래 보기
    controller.step(
        action="Teleport",
        position=dict(x=pos["x"], y=pos["y"] + 4.0, z=pos["z"]),
        agentId=0
    )
    controller.step(action="LookDown", degrees=90, agentId=0)

    # 탑뷰 캡처
    event = controller.last_event
    frame = event.events[0].frame
    path = os.path.join(out_dir, f"{prefix}_topdown_{top_shot_count}.png")
    Image.fromarray(frame).save(path)
    print(f"saved (topdown): {path}")

    # 원래 위치로 복귀
    controller.step(
        action="Teleport",
        position=dict(x=pos["x"], y=pos["y"], z=pos["z"]),
        agentId=0
    )
    controller.step(action="Rotate", rotation=rot["y"], agentId=0)


def interactive_capture(scene, agent_count, out_dir, prefix, robot_labels, width=640, height=480, random_spawn=False):
    os.makedirs(out_dir, exist_ok=True)
    controller = Controller(scene=scene, agentCount=agent_count, width=width, height=height)

    if random_spawn:
        controller.step(action="InitialRandomSpawn", randomSeed=0, forceVisible=True, numPlacementAttempts=5)

    current_agent = 0
    shot_count = {i: 0 for i in range(agent_count)}
    top_shot_count = 0

    print(f"\n현재 조작 중인 로봇: {robot_labels[current_agent]}")
    print("숫자키(1~9): 로봇 전환 | w/a/s/d: 이동 | i/k: 고개 위/아래 | j/l: 좌/우 회전 | c: 캡처 | t: 탑뷰 캡처 | x: 종료\n")

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
        elif key == "c":
            shot_count[current_agent] += 1
            event = controller.last_event
            agent_event = event.events[current_agent]
            label = robot_labels[current_agent]
            path = os.path.join(out_dir, f"{prefix}_{label}_{shot_count[current_agent]}.png")
            Image.fromarray(agent_event.frame).save(path)
            print(f"saved: {path}")
        elif key == "t":
            top_shot_count += 1
            capture_topdown(controller, out_dir, prefix, top_shot_count)
        elif key == "x":
            break
        elif key == "\x03":
            break

    controller.stop()


if __name__ == "__main__":
    interactive_capture(
        scene="FloorPlan1",
        agent_count=2,
        out_dir="images/task1",
        prefix="task1_abstract_kitchen",
        robot_labels=["R1", "R2"],
        random_spawn=True,
    )
