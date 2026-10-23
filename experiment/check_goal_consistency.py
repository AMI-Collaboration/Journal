"""
각 task의 goal_states.json에 나오는 object_synonyms가
그 task에 배정된 room들의 실제 object_n 목록(object.json 이름 기준)에
존재하는지 검증한다.

사용법:
    python check_goal_consistency.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from loader import load_all, fp_to_room_type  # noqa: E402

data = load_all()
tasks = data["tasks"]
rooms = data["rooms"]
objects = data["objects"]
goal_states = data["goal_states"]

print(f"{'='*70}")
print(f" Goal States vs Room 구성 일치도 검증 ({len(tasks)}개 task)")
print(f"{'='*70}\n")

problem_tasks = []

for task_n, task in tasks.items():
    gstates = goal_states.get(task_n, {})
    if not gstates:
        continue  # simple task 등 빈 틀은 스킵

    # 이 task의 room들에 실제로 존재하는 물건 이름(소문자) 전부 모으기
    task_fps = list(task["room"].keys())
    room_types_used = sorted(set(fp_to_room_type(fp) for fp in task_fps))

    available_object_names = set()
    for fp in task_fps:
        room = rooms.get(fp)
        if not room:
            continue
        for oid in room.get("object_n", []):
            obj = objects.get(oid)
            if obj:
                available_object_names.add(obj["object_name"].lower())

    # 각 goal_state의 object_synonyms 중 하나라도 available에 있으면 OK
    unmatched_states = []
    for sid, sdef in gstates.items():
        syns = [s.lower() for s in sdef.get("object_synonyms", [])]
        if sdef.get("type") == "unary" and sdef.get("predicate") in ("is-ready", "is-clear"):
            # 추상적 predicate(is-ready/is-clear)는 방 전체를 가리킬 수 있어 완화 검사
            # (room_type 이름 자체가 synonym에 들어있는지만 체크)
            if any(rt.replace("_", "") in "".join(syns).replace("_", "") for rt in room_types_used):
                continue
        matched = any(any(syn in name or name in syn for name in available_object_names) for syn in syns)
        if not matched:
            unmatched_states.append((sid, syns))

    if unmatched_states:
        problem_tasks.append((task_n, room_types_used, unmatched_states))

# ── 출력 ──────────────────────────────────────────
if not problem_tasks:
    print("모든 task의 goal_states가 room 구성과 일치합니다.")
else:
    for task_n, room_types_used, unmatched in problem_tasks:
        print(f"[{task_n}]  rooms={room_types_used}")
        for sid, syns in unmatched:
            print(f"    - {sid}: synonyms={syns}  -> 이 room들에서 매칭되는 물건 없음")
        print()

    print(f"{'='*70}")
    print(f" 총 {len(problem_tasks)}개 task에서 불일치 발견 (전체 {len([t for t in tasks if goal_states.get(t)])}개 중)")
    print(f"{'='*70}")

# JSON으로도 저장
out_path = os.path.join(HERE, "goal_consistency_report.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(
        [{"task_n": t, "rooms": r, "unmatched": [{"state": s, "synonyms": syn} for s, syn in u]} for t, r, u in problem_tasks],
        f, ensure_ascii=False, indent=2
    )
print(f"\n저장: {out_path}")
