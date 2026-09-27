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

def generate_independent_plan(room, data, invisible, task):
    agent = data.get('agent', '?')
    visible_objs = [o for o in data.get('objects', []) if o not in invisible.get(room, [])]
    local_scene = f"### {room} — {agent}\n  visible objects (from your camera): {', '.join(visible_objs) if visible_objs else '(none)'}\n"

    prompt = f'''
You are agent {agent} in a {room}.
You can ONLY see your own room, and only what your camera shows you below.
You do NOT know what other agents are doing or seeing.

## Task
{task}

## Your Room
{local_scene}

## Your Capabilities
- Gripper: FIXED (cannot move). Can toggle/open/close/pick-up objects in own room.
- Mobile Light: Can move between rooms, carry light objects, pass/receive at door.
- Mobile Heavy: Can move between rooms, push furniture, carry heavy/light objects.

## Output Format
[{agent} - {room}]
1. action
2. action

If nothing relevant in your room, output: [No action needed]
'''
    response = client.chat.completions.create(model='gpt-4o', temperature=0.0,
        messages=[{'role': 'user', 'content': prompt}])
    return response.choices[0].message.content.strip()

print('🔄 Independent 플랜 생성 중...')
plans = {}
for room, data in SCENE_JSON.items():
    agent = data.get('agent', '?')
    print(f'  - {agent} ({room})...')
    plans[agent] = generate_independent_plan(room, data, INVISIBLE, TASK)

NL_PLAN_INDEPENDENT = '\n\n'.join(plans.values())
print('\n✅ 완료\n')
print(NL_PLAN_INDEPENDENT)

os.makedirs(f'{TASK_DIR}/results/independent', exist_ok=True)
with open(f'{TASK_DIR}/results/independent/independent_nl.txt', 'w') as f:
    f.write(NL_PLAN_INDEPENDENT)
print(f'\n✅ 저장: {TASK_DIR}/results/independent/independent_nl.txt')
