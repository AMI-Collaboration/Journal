"""MAT-THOR AI2Thor execution eval for CDA / LaMMA-P across mat_compound/mat_complex/mat_vague.

Each (task, method) action list is a hand-translation of that method's ACTUAL joint_plan_text
(not a hardcoded 'oracle' solution) -- if a plan references a hallucinated/nonexistent object,
the corresponding action is recorded as attempted-and-failed (object not found), so execution
failures genuinely reflect plan quality. Single simulated agent executes all steps sequentially
regardless of R-label (multi-agent AI2Thor is not wired up here) -- RU is fixed at 1.0, matching
the existing simplification in run_cda_ai2thor.py.

Eff = min(1.0, MIN_ACTIONS[task] / actions_tried) -- MIN_ACTIONS is a hand-counted minimal action
sequence for that task (hardcoded, same simplification style as RU), not an optimal-planner result.

usage: python run_matthor_ai2thor.py --task mat_compound --method lamma_p
"""
import argparse
import json
import os

import ai2thor.controller
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

SCENES = {"mat_compound": 414, "mat_complex": 15, "mat_vague": 209}
MIN_ACTIONS = {"mat_compound": 6, "mat_complex": 15, "mat_vague": 8}

# Each step: ("GoTo"|"Pickup"|"Put"|"ToggleOn"|"ToggleOff"|"Open"|"Close", object_type_or_None)
# object_type_or_None = None marks a plan step referencing an object that doesn't exist in the
# scene (hallucination) -- recorded as a failed action, nothing is sent to the simulator.
PLANS = {
    ("mat_compound", "cda"): [
        ("GoTo", "ToiletPaper"), ("Pickup", "ToiletPaper"),
        ("GoTo", "GarbageCan"), ("Put", "GarbageCan"),
        ("GoTo", "Faucet"), ("ToggleOn", "Faucet"),
    ],
    ("mat_compound", "lamma_p"): [
        ("GoTo", "Faucet"), ("ToggleOn", "Faucet"),
        ("GoTo", "ToiletPaper"), ("Pickup", "ToiletPaper"),
        ("GoTo", "GarbageCan"), ("Put", "GarbageCan"),
    ],
    ("mat_vague", "cda"): [
        # task: "De-clutter the reading area" (FP209, living_room). Ground truth: Book+Newspaper -> GarbageCan.
        # CDA's actual plan never mentions GarbageCan/Newspaper at all -- it interprets "de-clutter" as
        # "tidy up" (put items back on shelf/sofa), not "throw away". Only 1 instance each of
        # Book/Pillow exists in FP209, but the plan references 2 of each ("blue book"+"red book",
        # "red pillow"+"green pillow"+"yellow pillow") -- a real quantity hallucination (both resolve
        # to the same tracked instance). "magazine"/"blanket"/"magazine rack" have no matching object
        # type in FP209 at all (hallucinated).
        ("GoTo", "Book"), ("Pickup", "Book"),               # R1 pick up blue book from coffee table
        ("GoTo", "Pillow"), ("Pickup", "Pillow"),           # R2 pick up red pillow from sofa
        ("GoTo", "Pillow"), ("Pickup", "Pillow"),           # R3 pick up green pillow from floor
        ("GoTo", "Book"), ("Pickup", "Book"),               # R4 pick up red book from coffee table
        ("GoTo", "Shelf"), ("Put", "Shelf"),                # R1 move blue book to bookshelf
        ("GoTo", "Sofa"), ("Put", "Sofa"),                  # R2 put red pillow on sofa
        ("GoTo", "Sofa"), ("Put", "Sofa"),                  # R3 place green pillow on sofa
        ("GoTo", "Shelf"), ("Put", "Shelf"),                # R4 move red book to bookshelf
        ("GoTo", None), ("Pickup", None),                   # R1 pick up red magazine (hallucinated)
        ("GoTo", None), ("Pickup", None),                   # R2 pick up white magazine (hallucinated)
        ("GoTo", None), ("Pickup", None),                   # R3 pick up yellow blanket (hallucinated)
        ("GoTo", "HousePlant"), ("Pickup", "HousePlant"),   # R4 pick up green plant from coffee table
        ("GoTo", "Shelf"), ("Put", "Shelf"),                # R2 put white magazine on bookshelf (hallucinated item)
        ("GoTo", "Sofa"), ("Put", "Sofa"),                  # R3 fold yellow blanket onto sofa (hallucinated item)
        ("GoTo", None), ("Put", None),                      # R1 move red magazine to magazine rack (both hallucinated)
        ("GoTo", "Shelf"), ("Put", "Shelf"),                # R4 move green plant to bookshelf
        ("GoTo", "Pillow"), ("Pickup", "Pillow"),           # R1 pick up yellow pillow from floor
        ("GoTo", "Sofa"), ("Put", "Sofa"),                  # R2 arrange purple blanket on sofa (hallucinated item)
        ("GoTo", None), ("Pickup", None),                   # R4 pick up stack of magazines (hallucinated)
        ("GoTo", "Sofa"), ("Put", "Sofa"),                  # R1 move yellow pillow to sofa
        ("GoTo", "CoffeeTable"), ("Put", "CoffeeTable"),    # R4 move stack of magazines to coffee table (hallucinated item)
    ],
    ("mat_vague", "lamma_p"): [
        # Translated directly from the raw PDDL plan (code_planpddl_py), not the naturalized text --
        # "clutter1"/"clutter2"/"furniture1"/"furniture2" are symbolic placeholders that are never
        # grounded to any real FP209 object anywhere in LaMMA-P's own output (hallucinated reference).
        # "book1" is put on the shelf despite never being picked up anywhere in the plan (SC violation).
        # GarbageCan/Newspaper are never referenced at all -- the goal is unreachable by construction.
        ("GoTo", "SideTable"),                              # 0.0 gotoobject robot4 sidetable
        ("GoTo", "Shelf"),                                  # 0.0 gotoobject robot4 shelf
        ("Pickup", None),                                   # 1.0 pickupobject robot4 clutter1 sidetable
        ("Put", "Shelf"),                                   # 2.0 putobject robot4 book1 shelf (never picked up)
        ("GoTo", "CoffeeTable"),                            # 3.0 gotoobject robot4 coffeetable
        ("Pickup", None),                                   # 4.0 pickupobject robot4 clutter2 coffeetable
        ("GoTo", "Shelf"),                                  # 5.0 gotoobject robot4 shelf
        ("Put", "Shelf"),                                   # 6.0 putobject robot4 clutter1 shelf
        ("Put", "Shelf"),                                   # 7.0 putobject robot4 clutter2 shelf
        ("GoTo", "SideTable"),                              # 8.0 gotoobject robot4 sidetable
        ("GoTo", None),                                     # 8.0 gotoobject robot4 furniture1 (hallucinated)
        ("Clean", "SideTable"),                             # 9.0 cleanobject robot4 sidetable (no AI2Thor equivalent)
        ("Push", None),                                     # 10.0 pushobject robot4 furniture1 target-location1
        ("GoTo", "CoffeeTable"),                            # 11.0 gotoobject robot4 coffeetable
        ("Clean", "CoffeeTable"),                           # 12.0 cleanobject robot4 coffeetable
        ("GoTo", None),                                     # 13.0 gotoobject robot4 furniture2 (hallucinated)
        ("Pull", None),                                     # 14.0 pullobject robot4 furniture2 target-location2
        ("GoTo", "Shelf"),                                  # 15.0 gotoobject robot4 shelf
        ("Clean", "Shelf"),                                 # 16.0 cleanobject robot4 shelf (no AI2Thor equivalent)
    ],
    ("mat_complex", "cda"): [
        ("GoTo", "Egg"), ("Pickup", "Egg"), ("GoTo", "Plate"), ("Put", "Plate"),
        ("GoTo", "Tomato"), ("Pickup", "Tomato"), ("GoTo", "Plate"), ("Put", "Plate"),
        ("GoTo", "Plate"), ("Pickup", "Plate"),
        ("GoTo", "Microwave"), ("Open", "Microwave"), ("Put", "Microwave"), ("Close", "Microwave"),
        ("ToggleOn", "Microwave"),
    ],
    ("mat_complex", "lamma_p"): [
        ("GoTo", "Plate"), ("Pickup", "Plate"),
        ("GoTo", "Egg"), ("Pickup", "Egg"),
        ("GoTo", "Plate"), ("Put", "Plate"),
        ("GoTo", "Tomato"), ("Pickup", "Tomato"),
        ("GoTo", "Plate"), ("Put", "Plate"),
        ("GoTo", "Microwave"), ("Open", "Microwave"),
        ("Pickup", "Plate"), ("Put", "Microwave"),
        ("ToggleOn", "Microwave"), ("ToggleOff", "Microwave"), ("Close", "Microwave"),
    ],
}


def by_id(e, object_id):
    for o in e.metadata["objects"]:
        if o["objectId"] == object_id:
            return o
    return {}


def goal_check_compound(e, acted_ids):
    """acted_ids: {obj_type: objectId actually acted upon during execution}.
    Scenes can contain multiple objects of the same type (e.g. 2 Faucets in FP414 --
    sink + bathtub); checking by type via a dict would silently pick the wrong instance,
    so we check the SPECIFIC object actually touched by an action."""
    gc_id = acted_ids.get("GarbageCan")
    gc = by_id(e, gc_id) if gc_id else {}
    tp_id = acted_ids.get("ToiletPaper")
    tp_in_trash = bool(tp_id) and tp_id in (gc.get("receptacleObjectIds") or [])
    faucet_id = acted_ids.get("Faucet")
    faucet_on = by_id(e, faucet_id).get("isToggled", False) if faucet_id else False
    return {"faucet_on": faucet_on, "toilet_paper_in_trash": tp_in_trash}


def goal_check_vague(e, acted_ids):
    """Ground truth (LaMMA-P final_test/FloorPlan209pddlvague.json, entry 3):
    GarbageCan must end up containing Book and Newspaper."""
    gc_id = acted_ids.get("GarbageCan")
    gc = by_id(e, gc_id) if gc_id else {}
    book_id = acted_ids.get("Book")
    news_id = acted_ids.get("Newspaper")
    book_in_trash = bool(book_id) and book_id in (gc.get("receptacleObjectIds") or [])
    news_in_trash = bool(news_id) and news_id in (gc.get("receptacleObjectIds") or [])
    return {"book_in_trash": book_in_trash, "newspaper_in_trash": news_in_trash}


def goal_check_complex(e, acted_ids, microwave_activated):
    plate_id = acted_ids.get("Plate")
    microwave_id = acted_ids.get("Microwave")
    egg_id = acted_ids.get("Egg")
    tomato_id = acted_ids.get("Tomato")
    plate = by_id(e, plate_id) if plate_id else {}
    microwave = by_id(e, microwave_id) if microwave_id else {}
    plate_in_microwave = bool(plate_id) and plate_id in (microwave.get("receptacleObjectIds") or [])
    egg_on_plate = bool(egg_id) and egg_id in (plate.get("receptacleObjectIds") or [])
    tomato_on_plate = bool(tomato_id) and tomato_id in (plate.get("receptacleObjectIds") or [])
    return {
        "egg_on_plate": egg_on_plate, "tomato_on_plate": tomato_on_plate,
        "plate_in_microwave": plate_in_microwave, "microwave_activated": microwave_activated,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True, choices=["mat_compound", "mat_complex", "mat_vague"])
    ap.add_argument("--method", required=True, choices=["cda", "lamma_p"])
    args = ap.parse_args()

    plan = PLANS[(args.task, args.method)]
    floor_plan = SCENES[args.task]
    # Saved directly under results/matthor/ai2thor_frames (Windows-visible path via the WSL /mnt/c
    # mount) so frames are viewable immediately after every run without a manual copy step.
    out_dir = os.path.join(HERE, "results", "matthor", "ai2thor_frames", f"{args.task}_{args.method}")
    os.makedirs(out_dir, exist_ok=True)
    for f in os.listdir(out_dir):
        os.remove(os.path.join(out_dir, f))

    print(f"=== {args.task} / {args.method} -- AI2Thor 실행 (FloorPlan{floor_plan}) ===")
    c = ai2thor.controller.Controller(
        scene=f"FloorPlan{floor_plan}", width=1280, height=720,
        snapToGrid=False, gridSize=0.05, rotateStepDegrees=10, visibilityDistance=100, fieldOfView=90,
    )

    frame_idx = 0

    def save_frame(label=""):
        nonlocal frame_idx
        img = Image.fromarray(c.last_event.frame)
        img.save(f"{out_dir}/frame_{frame_idx:03d}_{label}.png")
        frame_idx += 1

    save_frame("init")

    def get_obj(obj_type):
        """Resolve a type to one specific object instance, and stick to that same
        instance on every later call (scenes can have duplicates, e.g. 2 Faucets)."""
        if obj_type is None:
            return None
        if obj_type in acted_ids:
            return by_id(c.last_event, acted_ids[obj_type])
        for o in c.last_event.metadata["objects"]:
            if o["objectType"] == obj_type:
                return o
        return None

    def goto(obj_type):
        obj = get_obj(obj_type)
        if obj is None:
            return False
        for _ in range(400):
            e = c.step(dict(action="ObjectNavExpertAction", objectId=obj["objectId"]))
            next_action = e.metadata.get("actionReturn")
            if next_action is None:
                return True
            c.step(action=next_action, forceAction=True)
            save_frame(f"nav_{obj_type}_{next_action}")
        return False

    actions_tried = 0
    actions_success = 0
    microwave_activated = False
    acted_ids = {}
    log = []

    for i, (verb, obj_type) in enumerate(plan):
        actions_tried += 1
        obj = get_obj(obj_type)
        if obj is None:
            print(f"  [{i}] {verb} {obj_type}: FAIL (object not found in scene -- hallucinated reference)")
            log.append({"step": i, "verb": verb, "object": obj_type, "success": False, "reason": "object_not_found"})
            continue
        if obj_type is not None:
            acted_ids.setdefault(obj_type, obj["objectId"])
        success = False
        if verb == "GoTo":
            success = obj is not None and goto(obj_type)
            e = c.last_event
        elif verb == "Pickup":
            e = c.step(action="PickupObject", objectId=obj["objectId"], forceAction=True)
            success = e.metadata["lastActionSuccess"]
        elif verb == "Put":
            e = c.step(action="PutObject", objectId=obj["objectId"], forceAction=True)
            success = e.metadata["lastActionSuccess"]
        elif verb == "ToggleOn":
            e = c.step(action="ToggleObjectOn", objectId=obj["objectId"], forceAction=True)
            success = e.metadata["lastActionSuccess"]
            if success and obj_type == "Microwave":
                microwave_activated = True
        elif verb == "ToggleOff":
            e = c.step(action="ToggleObjectOff", objectId=obj["objectId"], forceAction=True)
            success = e.metadata["lastActionSuccess"]
        elif verb == "Open":
            e = c.step(action="OpenObject", objectId=obj["objectId"], forceAction=True)
            success = e.metadata["lastActionSuccess"]
        elif verb == "Close":
            e = c.step(action="CloseObject", objectId=obj["objectId"], forceAction=True)
            success = e.metadata["lastActionSuccess"]
        elif verb in ("Clean", "Push", "Pull"):
            # No matching AI2Thor action for these (iTHOR has no generic "clean"; Push/Pull need a
            # direction we have no principled way to pick from the plan text) -- recorded as
            # attempted-and-failed rather than silently dropped, same as an object-not-found step.
            success = False
            e = c.last_event
        else:
            raise ValueError(verb)

        if success:
            actions_success += 1
        print(f"  [{i}] {verb} {obj_type}: {'OK' if success else 'FAIL'} {e.metadata.get('errorMessage', '')}")
        log.append({"step": i, "verb": verb, "object": obj_type, "success": success,
                     "error": e.metadata.get("errorMessage", "")})
        save_frame(f"{i}_{verb}")

    e = c.last_event
    if args.task == "mat_compound":
        goals = goal_check_compound(e, acted_ids)
    elif args.task == "mat_vague":
        goals = goal_check_vague(e, acted_ids)
    else:
        goals = goal_check_complex(e, acted_ids, microwave_activated)

    goals_achieved = sum(1 for v in goals.values() if v)
    total_goals = len(goals)
    SR = 1.0 if goals_achieved == total_goals else 0.0
    Exe = actions_success / actions_tried if actions_tried else 0.0
    GCR = goals_achieved / total_goals if total_goals else 0.0
    RU = 1.0
    Eff = min(1.0, MIN_ACTIONS[args.task] / actions_tried) if actions_tried else 0.0

    print("\n" + "=" * 50)
    print("=== MAT-THOR Evaluation ===")
    print("goals:", goals)
    print(f"SR={SR:.2f}  Exe={Exe:.2f}  GCR={GCR:.2f}  RU={RU:.2f}  Eff={Eff:.2f}")
    print(f"actions: {actions_success}/{actions_tried} succeeded")

    eval_result = {
        "task": args.task, "method": args.method,
        "SR": SR, "Exe": Exe, "GCR": GCR, "RU": RU, "Eff": Eff,
        "goals": goals, "actions_tried": actions_tried, "actions_success": actions_success,
        "min_actions_hardcoded": MIN_ACTIONS[args.task], "action_log": log,
    }
    out_path = os.path.join(HERE, "results", "matthor", f"{args.task}_{args.method}_ai2thor_eval.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(eval_result, f, indent=2)
    print(f"\n저장: {out_path}")

    c.stop()


if __name__ == "__main__":
    main()
