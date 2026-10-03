"""
통합 평가 프레임워크
실험 설계: Ours/LaMMA-P만 PDDL 평가(Track B/D) 대상.
Central/Independent/SMART-LLM은 순수 NL 베이스라인이라 설계상 PDDL 트랙 제외.
"""
import os, re, json, argparse
from pathlib import Path
from openai import OpenAI

parser = argparse.ArgumentParser()
parser.add_argument("--task", required=True, help="예: task6")
args = parser.parse_args()

TASK_ID = args.task
BASE = Path(__file__).parent
TASK_DIR = BASE / TASK_ID
RESULTS_DIR = TASK_DIR / "results"
GT_DIR = TASK_DIR / "ground_truth"
MASTER_LIST_PATH = BASE / "common" / "object_lists" / "master_object_list.json"

client = OpenAI(api_key=open(BASE.parent / "LaMMA-P" / "api_key.txt").read().strip())

METHODS = ["ours", "lamma_p", "central", "independent", "smart_llm"]
METHOD_NAMES = {"ours": "Ours (P2P)", "lamma_p": "LaMMA-P", "central": "Centralized", "independent": "Independent", "smart_llm": "SMART-LLM"}
PDDL_EVAL_METHODS = {"ours", "lamma_p"}

with open(TASK_DIR / "input/scene/task.json") as f:
    task_info = json.load(f)
with open(BASE / "common" / "robot_configs.json") as f:
    robot_configs = json.load(f)
with open(BASE / "common" / "robot_types.json") as f:
    robot_types = json.load(f)

TASK = task_info["command_en"]
config = robot_configs[task_info["config"]]
ROOM_ORDER = ["kitchen", "living_room", "bedroom", "bathroom"]
MAIN_ROOM = task_info.get("main_room_name", "living_room")

def build_agent_config_text():
    lines = []
    idx = 1
    for room in ROOM_ORDER:
        if room not in config:
            continue
        for rtype in config[room]:
            caps = robot_types[rtype]
            cap_str = ", ".join(k for k, v in caps.items() if v is True)
            lines.append(f"- R{idx}: {room.title()} / {rtype} — {cap_str}")
            idx += 1
    return "\n".join(lines)

AGENT_CONFIG = build_agent_config_text()

FLOORPLANS = {room: str(config.get("rooms", 4)) for room in ROOM_ORDER if room in config}

# ─────────────────────────────────────────────────────────
# 콘솔 출력 헬퍼 (깔끔한 섹션 헤더 + 한 줄 요약만)
# ─────────────────────────────────────────────────────────
def section(title):
    print(f"\n{'─'*50}\n {title}\n{'─'*50}")

def status_line(label, ok, extra=""):
    mark = "✅" if ok else "❌"
    print(f"  {mark} {label}{('  ' + extra) if extra else ''}")

print(f"\n{'='*50}")
print(f" {TASK_ID} 평가 시작  (task: {TASK[:50]}...)")
print(f"{'='*50}")

def load_text(path):
    p = Path(path)
    return p.read_text().strip() if p.exists() and p.stat().st_size > 0 else None

def load_json(path):
    p = Path(path)
    return json.loads(p.read_text()) if p.exists() else None

# ── STEP 1: 파일 로드 ──────────────────────────
section("STEP 1/4  파일 로드")
nl_plans, pddl_plans = {}, {}
for m in METHODS:
    nl_plans[m] = load_text(RESULTS_DIR / m / f"{m}_nl.txt")
    pddl_plans[m] = load_text(RESULTS_DIR / m / f"{m}_pddl.txt") if m in PDDL_EVAL_METHODS else None
    pddl_tag = "PDDL✅" if pddl_plans[m] else ("PDDL⬜(제외)" if m not in PDDL_EVAL_METHODS else "PDDL❌")
    status_line(METHOD_NAMES[m], nl_plans[m] is not None, pddl_tag)

gt_pddl = load_text(GT_DIR / "gt_pddl.txt")
goal_states = load_json(GT_DIR / "goal_states.json")
master_list = load_json(MASTER_LIST_PATH)
status_line("Ground Truth PDDL", gt_pddl is not None)
status_line("Goal States", goal_states is not None)
status_line("Master Object List", master_list is not None)

# ── PDDL 파싱 함수 ────────────────
def parse_goal(pddl):
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

PREDICATE_SYNONYMS = {
    "at-location": "object-at", "located-at": "object-at", "is-at": "object-at", "in-location": "object-at",
    "switch-on": "is-on", "turned-on": "is-on", "powered-on": "is-on",
    "cleaned": "is-clean", "clean": "is-clean", "tidy": "is-clean", "clear": "is-clean",
}
TYPE_SYNONYMS = {"object": "item", "obj": "item", "thing": "item"}

def normalize_predicate(pred):
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
section("STEP 2/4  Track B — GT 비교 (GC / SG)")
track_b = {}
for m in METHODS:
    if m not in PDDL_EVAL_METHODS:
        track_b[m] = None
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

    def is_main_room_state_pred(pred):
        tokens = pred.split()
        if not tokens:
            return False
        head = tokens[0]
        if head in ("passed", "received", "agent-at", "agent-free", "can-access"):
            return False
        if head == "is-clean":
            return True
        if head == "object-at":
            return len(tokens) >= 3 and tokens[2] == MAIN_ROOM
        return False

    gen_goal_main_room_only = {p for p in gen_goal if is_main_room_state_pred(p)}
    spurious = gen_goal_main_room_only - gt_valid_preds
    sg = round(len(spurious) / len(gen_goal_main_room_only), 3) if gen_goal_main_room_only else 0
    track_b[m] = {"GC": gc, "SG": sg, "state_detail": achieved_detail, "spurious": list(spurious)}
    print(f"  {METHOD_NAMES[m]:14} GC={gc:<6} SG={sg}")

for m in METHODS:
    if m not in PDDL_EVAL_METHODS:
        print(f"  {METHOD_NAMES[m]:14} — (설계상 제외)")

# ── STEP 3: Track D — Scene 일치도 ─────────
section("STEP 3/4  Track D — Scene 일치도 (IC)")
def get_all_scene_objects(master_list, floorplans):
    all_objs = set()
    for room, fp_num in floorplans.items():
        objs = master_list.get(room, {}).get(fp_num, [])
        all_objs.update(o.lower() for o in objs)
    return all_objs

scene_objects = get_all_scene_objects(master_list, FLOORPLANS) if master_list else set()

track_d = {}
for m in METHODS:
    if m not in PDDL_EVAL_METHODS:
        track_d[m] = None
        continue
    gen_objs = parse_init_objects(pddl_plans[m])
    matched = gen_objs & scene_objects
    ic = round(len(matched) / len(gen_objs), 3) if gen_objs else 0
    track_d[m] = {"IC": ic, "matched": len(matched), "total_mentioned": len(gen_objs)}
    print(f"  {METHOD_NAMES[m]:14} IC={ic:<6} ({len(matched)}/{len(gen_objs)})")

for m in METHODS:
    if m not in PDDL_EVAL_METHODS:
        print(f"  {METHOD_NAMES[m]:14} — (설계상 제외)")

# ── STEP 4: Track A — LLM Judge ─────────────────
section("STEP 4/4  Track A — LLM Judge")
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
for m in METHODS:
    if not nl_plans[m]:
        print(f"  {METHOD_NAMES[m]:14} — NL 없음, 건너뜀")
        continue
    try:
        judge_results[m] = judge_nl(nl_plans[m])
        print(f"  {METHOD_NAMES[m]:14} Score={judge_results[m]['final_score']}")
    except Exception as e:
        print(f"  {METHOD_NAMES[m]:14} ❌ 오류: {e}")

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

# ── 최종 출력: 깔끔한 표만 ──────────────────────
section("최종 결과")
print(f"저장: {out_json.relative_to(BASE)}, {out_md.relative_to(BASE)}\n")
print("\n".join(lines))