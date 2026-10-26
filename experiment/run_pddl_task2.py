"""
task2 CDA jabung 플랜 → PDDL 변환 → Fast Downward 검증
"""
import json, os, re, subprocess, glob
from openai import OpenAI

HERE = '/mnt/c/Users/shin/Desktop/AAMAS'
api_key = open(os.path.join(HERE, 'LaMMA-P/api_key.txt')).read().strip()
client = OpenAI(api_key=api_key)
FD_BIN = os.path.join(HERE, 'LaMMA-P/downward/fast-downward.py')

# task2 CDA 플랜
with open(os.path.join(HERE, 'experiment/results/run1/task2_abstract_multi_room_cda_jabung_result.json'), encoding='utf-8') as f:
    result = json.load(f)

TASK = result['task_text']
NL_PLAN = re.sub(r'```\w*\n?', '', result['joint_plan_text']).strip()

print(f"Task: {TASK}")
print(f"\nPlan:\n{NL_PLAN}\n")

# task2 scene (bathroom: R3=gripper, R4=mobile_light)
SCENE_INFO = """
## Scene Information
### bathroom (FP412) — R3(gripper), R4(mobile_light)
  - bathtub (at bathroom)
  - faucet (at bathroom)
  - towel (at bathroom)
  - handtowel (at bathroom)
  - cloth (at bathroom)
  - soapbar (at bathroom)
  - soapbottle (at bathroom)
  - showerhead (at bathroom)
  - showerdoor (at bathroom)
  - showerglass (at bathroom)
  - toilet (at bathroom)
  - toiletpaper (at bathroom)
  - plunger (at bathroom)
  - scrubbrush (at bathroom)
  - spraybottle (at bathroom)
  - garbagecan (at bathroom)
  - candle (at bathroom)
"""

AGENT_INFO = """
## Agent Configuration
  - r3: bathroom / gripper / can-access: NONE (fixed) / type-annotation: r3 - gripper
  - r4: bathroom / mobile_light / can-access: bathroom / type-annotation: r4 - mobile_light
"""

RULES = """
## PDDL Writing Rules
1. Domain name: household-multiagent
2. :objects — agents, rooms, task-relevant items only (lowercase with underscores)
3. :init — agent positions, agent-free, can-access, object-at, initial states
   - gripper has NO can-access
   - (is-filled bathtub) is the goal, so initially (is-off faucet) or no is-filled
4. :goal — wrap in (and ...), positive predicates only, NO (not ...)
   - (is-filled bathtub) — bathtub filled with warm water
   - (object-at towel bathroom) — towel near bathtub (already in room)
   - (is-clean bathtub) if bath mat positioned
5. Output PDDL only. No markdown, no comments.
"""

PROMPT = f"""
You are a PDDL generator for a multi-agent household environment.
Convert the following natural language plan to problem.pddl.

## Task
{TASK}

## Natural Language Plan
{NL_PLAN}

{SCENE_INFO}
{AGENT_INFO}
{RULES}

Generate complete problem.pddl starting with:
(define (problem task2-bathroom-prep)
"""

print("🔄 GPT-4o PDDL 변환 중...")
response = client.chat.completions.create(
    model='gpt-4o', temperature=0.0,
    messages=[{'role':'user','content':PROMPT}]
)
PDDL_OUT = response.choices[0].message.content.strip()
PDDL_OUT = re.sub(r'```(pddl)?', '', PDDL_OUT).strip()

# domain 저장
DOMAIN = """
(define (domain household-multiagent)
  (:requirements :strips :typing :negative-preconditions)
  (:types
    agent - object
    gripper mobile - agent
    mobile_light mobile_heavy - mobile
    room - object
    item - object
  )
  (:predicates
    (agent-at ?a - agent ?r - room)
    (object-at ?o - item ?r - room)
    (holding ?a - agent ?o - item)
    (agent-free ?a - agent)
    (can-access ?a - agent ?r - room)
    (is-on ?o - item)
    (is-off ?o - item)
    (is-filled ?o - item)
    (is-clean ?o - item)
    (is-open ?o - item)
    (is-closed ?o - item)
    (object-at-door ?o - item ?r - room)
    (passed ?o - item ?r_from - room ?r_to - room)
    (received ?o - item ?a - agent)
  )
  (:action pick-up
    :parameters (?a - agent ?o - item ?r - room)
    :precondition (and (agent-at ?a ?r) (object-at ?o ?r) (agent-free ?a))
    :effect (and (holding ?a ?o) (not (object-at ?o ?r)) (not (agent-free ?a))))
  (:action put-down
    :parameters (?a - agent ?o - item ?r - room)
    :precondition (and (agent-at ?a ?r) (holding ?a ?o))
    :effect (and (object-at ?o ?r) (not (holding ?a ?o)) (agent-free ?a)))
  (:action toggle-on
    :parameters (?a - agent ?o - item ?r - room)
    :precondition (and (agent-at ?a ?r) (object-at ?o ?r))
    :effect (and (is-on ?o) (not (is-off ?o))))
  (:action toggle-off
    :parameters (?a - agent ?o - item ?r - room)
    :precondition (and (agent-at ?a ?r) (object-at ?o ?r) (is-on ?o))
    :effect (and (not (is-on ?o)) (is-off ?o)))
  (:action fill-bathtub
    :parameters (?a - gripper ?o - item ?r - room)
    :precondition (and (agent-at ?a ?r) (object-at ?o ?r))
    :effect (is-filled ?o))
  (:action move-object
    :parameters (?a - agent ?o - item ?r - room)
    :precondition (and (agent-at ?a ?r) (object-at ?o ?r) (agent-free ?a))
    :effect (is-clean ?o))
  (:action move
    :parameters (?a - mobile ?r_from - room ?r_to - room)
    :precondition (and (agent-at ?a ?r_from) (can-access ?a ?r_to))
    :effect (and (agent-at ?a ?r_to) (not (agent-at ?a ?r_from))))
  (:action clean
    :parameters (?a - agent ?o - item ?r - room)
    :precondition (and (agent-at ?a ?r) (object-at ?o ?r))
    :effect (is-clean ?o))
)
"""

WORK_DIR = '/tmp/pddl_task2'
os.makedirs(WORK_DIR, exist_ok=True)

with open(f'{WORK_DIR}/domain.pddl', 'w') as f:
    f.write(DOMAIN)
with open(f'{WORK_DIR}/problem.pddl', 'w') as f:
    f.write(PDDL_OUT)

print("\n✅ PDDL 파일 생성 완료")
print("\n=== problem.pddl ===")
print(PDDL_OUT)

# Fast Downward 실행
print("\n🔄 Fast Downward 실행 중...")
for f in glob.glob(f'{WORK_DIR}/sas_plan*') + glob.glob(f'{WORK_DIR}/output.sas'):
    os.remove(f)

result = subprocess.run(
    ['python3', FD_BIN, '--alias', 'lama-first',
     f'{WORK_DIR}/domain.pddl', f'{WORK_DIR}/problem.pddl'],
    capture_output=True, text=True, timeout=120,
    cwd=WORK_DIR
)
print(result.stdout[-2000:] if result.stdout else '')
if result.stderr:
    print('--- stderr ---')
    print(result.stderr[-500:])

plan_files = sorted(glob.glob(f'{WORK_DIR}/sas_plan*'))
if plan_files:
    with open(plan_files[0]) as f:
        plan_content = f.read()
    actions = [l.strip() for l in plan_content.strip().splitlines()
               if l.strip() and not l.startswith(';')]
    print(f'\n{"="*55}')
    print(f'✅ Plan 탐색 성공! ({len(actions)}개 액션)')
    print('='*55)
    for i, a in enumerate(actions, 1):
        print(f'  {i:2d}. {a}')
else:
    print('\n❌ Plan 탐색 실패')
