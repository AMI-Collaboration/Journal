import os, json
from openai import OpenAI

client = OpenAI(api_key=open('../LaMMA-P/api_key.txt').read().strip())

TASK_DIR = "task6"

with open(f'{TASK_DIR}/task_scene/task.json') as f:
    TASK = json.load(f)['command_kr']

with open(f'{TASK_DIR}/task_scene/scene/scene.json') as f:
    SCENE_JSON = json.load(f)

with open(f'{TASK_DIR}/task_scene/images/input_image/invisible_objects.json') as f:
    INVISIBLE = json.load(f)

def parse_scene(scene_json, invisible):
    lines = ['## Scene Information (물체명은 AI2-THOR 기준)']
    for room, data in scene_json.items():
        agent = data.get('agent', '?')
        lines.append(f'\n### {room} — agent: {agent}')
        visible_objs = [o for o in data.get('objects', []) if o not in invisible.get(room, [])]
        lines.append(f"  visible objects: {', '.join(visible_objs) if visible_objs else '(none visible in screenshot)'}")
        if invisible.get(room):
            lines.append(f"  NOT visible in screenshot (but may exist): {', '.join(invisible[room])}")
    return '\n'.join(lines)

SCENE_INFO = parse_scene(SCENE_JSON, INVISIBLE)

AGENT_INFO = """
## Agent Configuration
- R1: kitchen / Gripper / FIXED (cannot move)
- R2: living_room / Mobile Heavy (can move, push furniture, carry heavy/light objects)
- R3: bedroom / Mobile Light (can move, carry light objects)
- R4: bathroom / Mobile Light (can move, carry light objects)
"""

prompt = f'''
You are a centralized planner with FULL visibility of ALL rooms and ALL agents.
Generate a coordinated natural language plan for ALL agents to complete the task.
Note: some objects are known to exist (from a master object list) but were not
visible in the agent's own screenshot — you may still use them if the task requires it,
since the object list is ground truth about what exists in the room.

## Task
{TASK}

{SCENE_INFO}

{AGENT_INFO}

## Output Format
[R<id> - <room> / <type>]
1. action
2. action

Consider collaboration between agents (passing objects between rooms via doors).
'''

print('🔄 Centralized 플랜 생성 중...')
response = client.chat.completions.create(model='gpt-4o', temperature=0.0,
    messages=[{'role': 'user', 'content': prompt}])
NL_PLAN_CENTRALIZED = response.choices[0].message.content.strip()
print('✅ 완료\n')
print(NL_PLAN_CENTRALIZED)

os.makedirs(f'{TASK_DIR}/results/central', exist_ok=True)
with open(f'{TASK_DIR}/results/central/central_nl.txt', 'w') as f:
    f.write(NL_PLAN_CENTRALIZED)
print(f'\n✅ 저장: {TASK_DIR}/results/central/central_nl.txt')
