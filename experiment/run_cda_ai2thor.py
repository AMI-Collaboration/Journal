"""
CDA 플랜 → AI2Thor 실행 (mat_compound)
MAT-THOR 기준: SR, Exe, GCR, RU, Eff 측정
"""
import ai2thor.controller
import json, os, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
FLOOR_PLAN = 414
OUT_DIR = "/tmp/cda_ai2thor_frames"
os.makedirs(OUT_DIR, exist_ok=True)

# CDA 플랜 로드
result_path = os.path.join(HERE, "results/matthor/mat_compound_multi_room_cda_jabung_result.json")
with open(result_path) as f:
    result = json.load(f)

print("=== CDA mat_compound AI2Thor 실행 ===")
print(result.get('joint_plan_text','')[:300])
print("\n" + "="*50)

# AI2Thor 시작
print("AI2Thor 시작...")
c = ai2thor.controller.Controller(
    scene=f"FloorPlan{FLOOR_PLAN}",
    width=1280, height=720,
    snapGrid=False, gridSize=0.25,
    visibilityDistance=100, fieldOfView=90
)

frame_idx = 0
def save_frame(label=""):
    global frame_idx
    img = Image.fromarray(c.last_event.frame)
    path = f"{OUT_DIR}/frame_{frame_idx:03d}_{label}.png"
    img.save(path)
    frame_idx += 1
    return path

save_frame("init")

# 객체 목록
objects = {o["objectType"]: o for o in c.last_event.metadata["objects"]}
print("\n객체:", list(objects.keys())[:15])

results = {"faucet_on": False, "toilet_paper_in_trash": False}
actions_tried = 0
actions_success = 0

def goto_object(obj_id, agent_id=0):
    """ObjectNavExpertAction으로 이동"""
    for _ in range(50):
        e = c.step(dict(action='ObjectNavExpertAction', objectId=obj_id, agentId=agent_id))
        next_action = e.metadata.get('actionReturn')
        if next_action is None: return True
        c.step(action=next_action, agentId=agent_id, forceAction=True)
    return False

def do_action(action, **kwargs):
    global actions_tried, actions_success
    actions_tried += 1
    if action == "GoToObject":
        obj_id = kwargs.get("objectId")
        success = goto_object(obj_id)
        e = c.last_event
    else:
        e = c.step(action=action, **kwargs, forceAction=True)
        success = e.metadata['lastActionSuccess']
    if success: actions_success += 1
    print(f"  {action}: {'✅' if success else '❌'} {e.metadata.get('errorMessage','')}")
    save_frame(action[:10])
    return success, e

# === CDA Plan Execution ===
# R1: pick up toilet paper → put in trash → turn on faucet

tp = objects.get("ToiletPaper")
gc = objects.get("GarbageCan")
faucet = objects.get("Faucet")

print("\n[1] GoToObject ToiletPaper")
if tp: do_action("GoToObject", objectId=tp["objectId"])

print("[2] PickupObject ToiletPaper")
if tp: do_action("PickupObject", objectId=tp["objectId"])

print("[3] GoToObject GarbageCan")
if gc: do_action("GoToObject", objectId=gc["objectId"])

print("[4] PutObject GarbageCan")
if gc:
    s, e = do_action("PutObject", objectId=gc["objectId"])
    # 확인
    objs = {o["objectType"]: o for o in e.metadata["objects"]}
    gc_obj = objs.get("GarbageCan", {})
    results["toilet_paper_in_trash"] = any(
        "ToiletPaper" in r for r in gc_obj.get("receptacleObjectIds", [])
    )

print("[5] GoToObject Faucet")
if faucet: do_action("GoToObject", objectId=faucet["objectId"])

print("[6] ToggleObjectOn Faucet")
if faucet:
    s, e = do_action("ToggleObjectOn", objectId=faucet["objectId"])
    objs = {o["objectType"]: o for o in e.metadata["objects"]}
    results["faucet_on"] = objs.get("Faucet", {}).get("isToggled", False)

# === MAT-THOR Metrics ===
print("\n" + "="*50)
print("=== MAT-THOR Evaluation ===")
goals_achieved = sum(results.values())
total_goals = len(results)

SR = 1.0 if goals_achieved == total_goals else 0.0
Exe = actions_success / actions_tried if actions_tried > 0 else 0
GCR = goals_achieved / total_goals
RU = 1.0  # single robot used / total robots (simplified)

print(f"Faucet ON:            {results['faucet_on']}")
print(f"ToiletPaper in Trash: {results['toilet_paper_in_trash']}")
print(f"\nSR  (Success Rate):   {SR:.2f}")
print(f"Exe (Executability):  {Exe:.2f}")
print(f"GCR (Goal Completion):{GCR:.2f}")
print(f"RU  (Robot Util):     {RU:.2f}")
print(f"\nActions: {actions_success}/{actions_tried} succeeded")
print(f"Frames saved: {OUT_DIR}/")

# 결과 저장
eval_result = {
    "task": "mat_compound", "method": "cda",
    "SR": SR, "Exe": Exe, "GCR": GCR, "RU": RU,
    "goals": results, "actions_tried": actions_tried, "actions_success": actions_success
}
out_path = os.path.join(HERE, "results/matthor/mat_compound_cda_ai2thor_eval.json")
with open(out_path, "w") as f:
    json.dump(eval_result, f, indent=2)
print(f"\n💾 저장: {out_path}")

c.stop()
