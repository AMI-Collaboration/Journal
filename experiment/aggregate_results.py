"""
통합 평가 프레임워크 (task6 기준)
실험 설계: Ours/LaMMA-P만 PDDL 평가(Track B/D) 대상.
Central/Independent는 순수 NL 베이스라인이라 설계상 PDDL 트랙 제외.
목표(S1~S3)는 특정 오브젝트명이 아닌 "기능적 동의어군" 기반으로 채점.
"""
import os, re, json
from pathlib import Path
from openai import OpenAI

TASK_ID = "task6"
BASE = Path(__file__).parent
TASK_DIR = BASE / TASK_ID
RESULTS_DIR = TASK_DIR / "results"
GT_DIR = TASK_DIR / "ground_truth"
MASTER_LIST_PATH = BASE / "common" / "object_lists" / "master_object_list.json"

client = OpenAI(api_key=open(BASE.parent / "LaMMA-P" / "api_key.txt").read().strip())

METHODS = ["ours", "lamma_p", "central", "independent", "smart_llm"]
METHOD_NAMES = {"ours": "Ours (P2P)", "lamma_p": "LaMMA-P", "central": "Centralized", "independent": "Independent", "smart_llm": "SMART-LLM"}

# 실험 설계: PDDL 평가(Track B/D) 대상 방법. 파일 존재 여부가 아니라 실험 설계로 고정.
# SMART-LLM은 Pythonic 코드만 생성하고 PDDL을 만들지 않는 방법론이라 Central/Independent와 같은 카테고리.
PDDL_EVAL_METHODS = {"ours", "lamma_p"}

TASK6_FLOORPLANS = {"kitchen": "4", "living_room": "4", "bedroom": "4", "bathroom": "4"}

TASK = "I need to prepare for a home workout in 20 minutes. Clear the space and set it up."
AGENT_CONFIG = """
- R1: Kitchen / Gripper / Fixed (cannot move)
- R2: Living room / Mobile Heavy (can move, push furniture)
- R3: Bedroom / Mobile Light (standby)
- R4: Bathroom / Mobile Light (can move, carry light objects)
"""

def progress(step, total, label):
    pct = int(step / total * 100)
    bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
    print(f"[{bar}] {pct:3d}%  {label}", flush=True)

def load_text(path):
    p = Path(path)
    return p.read_text().strip() if p.exists() and p.stat().st_size > 0 else None

def load_json(path):
    p = Path(path)
    return json.loads(p.read_text()) if p.exists() else None

print("=" * 60)
print(f"{TASK_ID} 통합 평가 시작")
print("=" * 60)

# ── STEP 1: 파일 로드 ──────────────────────────
nl_plans, pddl_plans = {}, {}
for i, m in enumerate(METHODS, 1):
    nl_plans[m] = load_text(RESULTS_DIR / m / f"{m}_nl.txt")
    pddl_plans[m] = load_text(RESULTS_DIR / m / f"{m}_pddl.txt") if m in PDDL_EVAL_METHODS else None
    has_nl = "✅" if nl_plans[m] else "❌"
    has_pddl = "✅" if pddl_plans[m] else ("⬜(설계상 제외)" if m not in PDDL_EVAL_METHODS else "❌")
    progress(i, len(METHODS), f"[STEP 1/4] 파일 로드 — {METHOD_NAMES[m]} (NL:{has_nl} PDDL:{has_pddl})")

gt_pddl = load_text(GT_DIR / "gt_pddl.txt")
goal_states = load_json(GT_DIR / "goal_states.json")
master_list = load_json(MASTER_LIST_PATH)
print(f"  GT PDDL: {'✅' if gt_pddl else '❌'}  goal_states: {'✅' if goal_states else '❌'}  master_list: {'✅' if master_list else '❌'}\n")

# ── PDDL 파싱 함수 (버그 수정됨) ────────────────
def parse_goal(pddl):
    """':goal' 이후 전체 텍스트에서 predicate 추출.
    이전 버전은 non-greedy 정규식이 '))' 패턴을 조기에 만나
    마지막 목표 조건을 통째로 유실하는 버그가 있었음 — 수정됨."""
    if not pddl: return set()
    idx = pddl.find(':goal')
    if idx == -1: return set()
    tail = pddl[idx:]
    preds = re.findall(r'\(([^()]+)\)', tail)
    return set(p.strip().lower() for p in preds)

def parse_init(pddl):
    if not pddl: return set()
    m = re.search(r':init(.+?):goal', pddl, re.DOTALL)
    if not m: return set()
    preds = re.findall(r'\(([^()]+)\)', m.group(1))
    return set(p.strip().lower() for p in preds)

def parse_init_objects(pddl):
    """:objects 섹션에서 물체 타입(item 및 동의어)으로 선언된 이름만 추출.
    로봇/방 타입(robot, room 등)은 제외하고, 'item'과 동의어(object, obj, thing)만
    실제 물체로 인정한다."""
    if not pddl:
        return set()
    m = re.search(r':objects(.+?)\)\s*(?:\(:init|\(:goal)', pddl, re.DOTALL)
    if not m:
        return set()
    body = m.group(1)
    items = set()
    item_types = {"item"} | set(TYPE_SYNONYMS.keys())
    for line in body.split('\n'):
        line = line.strip()
        tm = re.search(r'-\s*(\w+)\s*$', line)
        if not tm:
            continue
        type_name = tm.group(1).lower()
        if type_name in item_types:
            names = re.sub(r'-\s*\w+\s*$', '', line).strip()
            items.update(n.lower() for n in names.split())
    return items

# ── Predicate/Type 동의어 정규화 레이어 ─────────
# LaMMA-P를 포함한 여러 LLM 생성 PDDL은 predicate/타입 이름을
# 매 실행마다 자유롭게 바꿔 쓰므로(예: at-location vs object-at),
# 채점 전 표준 스키마로 정규화한다.
PREDICATE_SYNONYMS = {
    "at-location": "object-at",
    "located-at": "object-at",
    "is-at": "object-at",
    "in-location": "object-at",
    "switch-on": "is-on",
    "turned-on": "is-on",
    "powered-on": "is-on",
    "cleaned": "is-clean",
    "clean": "is-clean",
    "tidy": "is-clean",
    "clear": "is-clean",
}

TYPE_SYNONYMS = {
    "object": "item",
    "obj": "item",
    "thing": "item",
}

def normalize_predicate(pred):
    """predicate 문자열의 head(첫 단어)를 표준 이름으로 치환"""
    tokens = pred.split()
    if not tokens:
        return pred
    head = tokens[0]
    if head in PREDICATE_SYNONYMS:
        tokens[0] = PREDICATE_SYNONYMS[head]
    return " ".join(tokens)

def normalize_predicate_set(preds):
    return set(normalize_predicate(p) for p in preds)

def check_state(gen_goal_preds, state_def):
    """생성된 goal predicate 집합 안에서 이 목표상태가 (동의어 허용) 달성됐는지 확인"""
    syns = [s.lower() for s in state_def.get("object_synonyms", [])]
    t = state_def["type"]
    for pred in gen_goal_preds:
        tokens = pred.split()
        if not tokens: continue
        head = tokens[0]
        if t == "unary" and head == state_def["predicate"]:
            if len(tokens) >= 2 and tokens[1] in syns:
                return True
        elif t == "object_at" and head == "object-at":
            if len(tokens) >= 3 and tokens[1] in syns and tokens[2] == state_def["location"]:
                return True
        elif t == "passed" and head == "passed":
            if len(tokens) >= 4 and tokens[1] in syns and tokens[2] == state_def["from"] and tokens[3] == state_def["to"]:
                return True
    return False

def build_gt_valid_preds(goal_states):
    """goal_states.json의 모든 동의어 조합으로 '허용되는 GT predicate' 집합을 만듦
    (SG 계산 시, 동의어를 쓴 것까지 '잉여'로 잘못 판정하지 않기 위함)"""
    valid = set()
    for sdef in goal_states.values():
        syns = [s.lower() for s in sdef.get("object_synonyms", [])]
        if sdef["type"] == "unary":
            for syn in syns:
                valid.add(f"{sdef['predicate']} {syn}")
        elif sdef["type"] == "object_at":
            for syn in syns:
                valid.add(f"object-at {syn} {sdef['location']}")
        elif sdef["type"] == "passed":
            for syn in syns:
                valid.add(f"passed {syn} {sdef['from']} {sdef['to']}")
    return valid

gt_valid_preds = build_gt_valid_preds(goal_states) if goal_states else set()
total_weight = sum(s["weight"] for s in goal_states.values()) if goal_states else 0

# ── STEP 2: Track B — 가중 GC + SG ──────────────
track_b = {}
for i, m in enumerate(METHODS, 1):
    if m not in PDDL_EVAL_METHODS:
        track_b[m] = None
        progress(i, len(METHODS), f"[STEP 2/4] Track B — {METHOD_NAMES[m]} (설계상 PDDL 평가 제외)")
        continue
    gen_goal = normalize_predicate_set(parse_goal(pddl_plans[m]))
    achieved_detail = {}
    weighted_sum = 0
    if goal_states:
        for sid, sdef in goal_states.items():
            ok = check_state(gen_goal, sdef)
            achieved_detail[sid] = ok
            if ok:
                weighted_sum += sdef["weight"]
    gc = round(weighted_sum / total_weight, 3) if total_weight else 0

    # SG는 "메인룸(living_room) 상태" predicate만 대상으로 계산.
    # passed/received처럼 다른 방을 오가는 과정(process) predicate는
    # 목표가 아니라 실행 경로이므로 SG 판정 대상에서 제외.
    MAIN_ROOM = "living_room"
    def is_main_room_state_pred(pred):
        tokens = pred.split()
        if not tokens:
            return False
        head = tokens[0]
        if head in ("passed", "received", "agent-at", "agent-free", "can-access"):
            return False  # 과정/설정성 predicate는 애초에 상태 목표가 아님
        if head == "is-clean":
            return True
        if head == "object-at":
            return len(tokens) >= 3 and tokens[2] == MAIN_ROOM
        return False

    gen_goal_main_room_only = {p for p in gen_goal if is_main_room_state_pred(p)}
    spurious = gen_goal_main_room_only - gt_valid_preds
    sg = round(len(spurious) / len(gen_goal_main_room_only), 3) if gen_goal_main_room_only else 0
    track_b[m] = {"GC": gc, "SG": sg, "state_detail": achieved_detail, "spurious": list(spurious)}
    progress(i, len(METHODS), f"[STEP 2/4] Track B — {METHOD_NAMES[m]} (GC={gc}, SG={sg})")
print()

# ── STEP 3: Track D — Scene 일치도 (IC) ─────────
def get_all_scene_objects(master_list, floorplans):
    all_objs = set()
    for room, fp_num in floorplans.items():
        objs = master_list.get(room, {}).get(fp_num, [])
        all_objs.update(o.lower() for o in objs)
    return all_objs

scene_objects = get_all_scene_objects(master_list, TASK6_FLOORPLANS) if master_list else set()

track_d = {}
for i, m in enumerate(METHODS, 1):
    if m not in PDDL_EVAL_METHODS:
        track_d[m] = None
        progress(i, len(METHODS), f"[STEP 3/4] Track D — {METHOD_NAMES[m]} (설계상 PDDL 평가 제외)")
        continue
    gen_objs = parse_init_objects(pddl_plans[m])
    matched = gen_objs & scene_objects
    ic = round(len(matched) / len(gen_objs), 3) if gen_objs else 0
    track_d[m] = {"IC": ic, "matched": len(matched), "total_mentioned": len(gen_objs)}
    progress(i, len(METHODS), f"[STEP 3/4] Track D — {METHOD_NAMES[m]} (IC={ic})")
print()

# ── STEP 4: Track A — LLM Judge ─────────────────
JUDGE_SYSTEM = "You are an expert evaluator for multi-agent household task planning. Respond in valid JSON only."

def judge_nl(nl_plan):
    prompt = f"""Evaluate the multi-agent natural language plan.

## Task
{TASK}

## Agent Configuration
{AGENT_CONFIG}
Capability rules:
- Gripper: FIXED (cannot move). Can toggle/open/close/pick-up objects in own room.
- Mobile Light: Can move, carry light objects, pass/receive at door.
- Mobile Heavy: Can move, push furniture, carry heavy/light objects.

## Natural Language Plan
{nl_plan}

Score each 1-10:
TF: Task Fulfillment — fully achieve goal?
PF: Plan Feasibility — executable given capabilities and scene?
OC: Observability Consistency — each agent uses only its own room info?
SC: Sequential Coherence — logically correct order?

Output JSON only:
{{"TF":<1-10>,"TF_reason":"...","PF":<1-10>,"PF_reason":"...",
  "OC":<1-10>,"OC_reason":"...","SC":<1-10>,"SC_reason":"..."}}
"""
    resp = client.chat.completions.create(
        model="gpt-4o", temperature=0.0,
        messages=[{"role":"system","content":JUDGE_SYSTEM}, {"role":"user","content":prompt}]
    )
    raw = re.sub(r'```(json)?', '', resp.choices[0].message.content.strip()).strip()
    r = json.loads(raw)
    r["final_score"] = round(r["TF"]*0.35 + r["PF"]*0.25 + r["OC"]*0.25 + r["SC"]*0.15, 2)
    return r

judge_results = {}
valid_methods = [m for m in METHODS if nl_plans[m]]
for i, m in enumerate(valid_methods, 1):
    progress(i-1, len(valid_methods), f"[STEP 4/4] LLM Judge 진행 중 — {METHOD_NAMES[m]}...")
    try:
        judge_results[m] = judge_nl(nl_plans[m])
        progress(i, len(valid_methods), f"[STEP 4/4] LLM Judge 완료 — {METHOD_NAMES[m]} (Score={judge_results[m]['final_score']})")
    except Exception as e:
        print(f"  ❌ {METHOD_NAMES[m]} 오류: {e}")
print()

# ── 결과 통합 저장 ────────────────────────────────
final = {}
for m in METHODS:
    final[m] = {
        "name": METHOD_NAMES[m],
        "pddl_eval_target": m in PDDL_EVAL_METHODS,
        "track_a_llm_judge": judge_results.get(m) or "N/A",
        "track_b_gt_comparison": (
            {k: v for k, v in track_b[m].items() if k not in ("state_detail", "spurious")} if track_b.get(m) else "N/A (설계상 제외)"
        ),
        "track_b_state_detail": track_b[m]["state_detail"] if track_b.get(m) else "N/A (설계상 제외)",
        "track_b_spurious": track_b[m]["spurious"] if track_b.get(m) else "N/A (설계상 제외)",
        "track_d_scene_consistency": track_d.get(m) or "N/A (설계상 제외)",
    }

out_json = RESULTS_DIR / "summary.json"
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(final, f, ensure_ascii=False, indent=2)
print(f"✅ JSON 저장: {out_json}")

# ── 표 저장 ────────────────────────────────────
lines = [f"# {TASK_ID} 통합 평가 결과\n"]
lines.append("## Track A — LLM Judge (NL 기반, 모든 방법 공통)\n")
lines.append("| 방법 | TF | PF | OC | SC | Final |")
lines.append("|---|---|---|---|---|---|")
for m in METHODS:
    r = judge_results.get(m)
    if not r:
        lines.append(f"| {METHOD_NAMES[m]} | - | - | - | - | N/A |"); continue
    lines.append(f"| {METHOD_NAMES[m]} | {r['TF']} | {r['PF']} | {r['OC']} | {r['SC']} | {r['final_score']} |")

lines.append("\n## Track B — GT 비교 (PDDL 평가 대상만: Ours, LaMMA-P)\n")
lines.append("| 방법 | GC(가중) | SG |")
lines.append("|---|---|---|")
for m in METHODS:
    r = track_b.get(m)
    if r is None:
        lines.append(f"| {METHOD_NAMES[m]} | N/A (설계상 제외) | N/A (설계상 제외) |")
    else:
        lines.append(f"| {METHOD_NAMES[m]} | {r['GC']} | {r['SG']} |")

lines.append("\n## Track B 상세 — 목표상태 달성 여부\n")
if goal_states:
    header = "| 방법 | " + " | ".join(goal_states.keys()) + " |"
    lines.append(header)
    lines.append("|---" * (len(goal_states)+1) + "|")
    for m in METHODS:
        if track_b.get(m) is None:
            row = "| " + METHOD_NAMES[m] + " | " + " | ".join("N/A" for _ in goal_states) + " |"
        else:
            detail = track_b[m]["state_detail"]
            row = "| " + METHOD_NAMES[m] + " | " + " | ".join("✅" if detail.get(k) else "❌" for k in goal_states.keys()) + " |"
        lines.append(row)

lines.append("\n## Track D — Scene 일치도 IC (PDDL 평가 대상만: Ours, LaMMA-P)\n")
lines.append("| 방법 | IC | matched/mentioned |")
lines.append("|---|---|---|")
for m in METHODS:
    r = track_d.get(m)
    if r is None:
        lines.append(f"| {METHOD_NAMES[m]} | N/A (설계상 제외) | N/A (설계상 제외) |")
    else:
        lines.append(f"| {METHOD_NAMES[m]} | {r['IC']} | {r['matched']}/{r['total_mentioned']} |")

out_md = RESULTS_DIR / "summary_table.md"
with open(out_md, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(f"✅ 표 저장: {out_md}")
print()
print("=" * 60)
print("           📊 최종 결과")
print("=" * 60)
print("\n".join(lines))
