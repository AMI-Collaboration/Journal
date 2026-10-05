"""
AI2-THOR을 이용해 로봇(에이전트) 시점 스크린샷을 찍는 스크립트.
여러 에이전트를 한 씬에 배치하고, 각 에이전트 시점에서 이미지를 저장한다.
"""
from ai2thor.controller import Controller
from PIL import Image
import os


def capture(scene: str, agent_count: int, out_dir: str, prefix: str, width: int = 640, height: int = 480):
    """
    scene: FloorPlan 이름 (예: "FloorPlan14")
    agent_count: 씬에 배치할 로봇(에이전트) 수
    out_dir: 이미지 저장 폴더
    prefix: 저장 파일명 접두사 (예: "task1_abstract_R1")
    """
    os.makedirs(out_dir, exist_ok=True)

    controller = Controller(
        scene=scene,
        agentCount=agent_count,
        width=width,
        height=height,
    )

    event = controller.step(action="Pass")

    # event.events는 각 에이전트별 결과를 담고 있음
    for i, agent_event in enumerate(event.events, start=1):
        frame = agent_event.frame
        path = os.path.join(out_dir, f"{prefix}_agent{i}_01.png")
        Image.fromarray(frame).save(path)
        print(f"saved: {path}")

    controller.stop()


if __name__ == "__main__":
    # 예시: task1_abstract의 kitchen(FP14), 로봇 2대(R1, R2)
    capture(
        scene="FloorPlan14",
        agent_count=2,
        out_dir=r"C:\Users\shin\Desktop\AAMAS\experiment_new\image\multi_room\abstract\task1",
        prefix="task1_abstract_kitchen",
    )
