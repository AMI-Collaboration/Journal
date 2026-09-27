# 실험 실행 가이드

멀티에이전트 협업 태스크(Task6~10)를 4가지 방법(**Ours / Centralized / Independent / LaMMA-P**)으로
수행시키고, 통합 평가 프레임워크(`aggregate_results.py`)로 비교하는 실험입니다.

---

## 0. 사전 환경 세팅 (한 번만)

### 0-1. WSL2 + Python 가상환경

```bash
wsl
sudo apt install python3.9 python3.9-venv python3.9-dev -y
cd ~/journal_co/LaMMA-P
python3.9 -m venv lammap
source lammap/bin/activate
pip install --upgrade pip
pip install openai scipy numpy opencv-python pathlib ai2thor
```

### 0-2. Fast Downward 빌드

```bash
sudo apt install -y cmake g++ python3-dev
git submodule update --init --recursive
cd downward
./build.py
cd ..
./downward/fast-downward.py --help   # 정상 출력되면 성공
```

### 0-3. OpenAI API 키

```bash
echo "sk-xxxxxxxxxxxxxxxx" > api_key.txt
```

### 0-4. 폴더 구조 확인

```
journal_co/
├── LaMMA-P/                 ← LaMMA-P 원본 재현 코드
└── experiment/
    ├── common/
    │   ├── object_categories.json
    │   ├── robot_types.json
    │   ├── robot_configs.json
    │   └── object_lists/
    │       └── master_object_list.json   ← AI2-THOR 실제 씬 오브젝트 (사실 확인용)
    ├── task6/  (~task10)
    │   ├── task_scene/
    │   │   ├── task.json                 ← 태스크 정의
    │   │   ├── scene/scene.json           ← 각 방 실제 오브젝트
    │   │   └── images/input_image/        ← 로봇 시점 스크린샷 + invisible_objects.json
    │   ├── ground_truth/
    │   │   ├── gt_pddl.txt                ← 참고용 GT PDDL
    │   │   └── goal_states.json           ← ⭐ 실제 채점 기준 (가중 목표상태)
    │   └── results/
    │       ├── ours/ours_nl.txt, ours_pddl.txt
    │       ├── central/central_nl.txt
    │       ├── independent/independent_nl.txt
    │       └── lamma_p/lamma_p_nl.txt, lamma_p_pddl.txt
    ├── baseline_central.py
    ├── baseline_independent.py
    ├── sync_to_experiment.py (LaMMA-P 폴더 안)
    └── aggregate_results.py
```

---

## 1. GT(Ground Truth) 만드는 법

각 task 폴더의 `ground_truth/goal_states.json`이 **실제 채점 기준**입니다.
`gt_pddl.txt`는 참고용 예시일 뿐이고, 채점은 오직 `goal_states.json`으로 이루어집니다.

### 1-1. goal_states.json 작성 규칙

목표는 **"태스크가 요구하는 최종 상태"만** 적습니다 (과정/경로는 목표 아님).
특정 오브젝트 이름 하나로 고정하지 말고, **기능적으로 동등한 물체들을 동의어군으로 묶습니다.**

```json
{
  "S1_workout_space_cleared": {
    "weight": 30,
    "type": "unary",
    "predicate": "is-clean",
    "object_synonyms": ["coffeetable", "table", "diningtable"]
  },
  "S2_hydration_object_ready": {
    "weight": 20,
    "type": "object_at",
    "object_synonyms": ["mug", "cup", "waterbottle", "bottle", "glass"],
    "location": "living_room"
  },
  "S3_wiping_object_ready": {
    "weight": 20,
    "type": "object_at",
    "object_synonyms": ["handtowel", "towel", "cloth", "napkin", "dishsponge", "bathmat"],
    "location": "living_room"
  },
  "S4_lighting_on": {
    "weight": 15,
    "type": "unary",
    "predicate": "is-on",
    "object_synonyms": ["floorlamp", "lamp", "light"]
  },
  "S5_floor_clutter_cleared": {
    "weight": 15,
    "type": "unary_or_relocated",
    "predicate": "is-clean",
    "object_synonyms": ["pillow", "box", "item", "floor", "sofa"],
    "relocated_to_synonyms": ["storage", "shelf", "closet", "cabinet"]
  }
}
```
(위는 task6 확정본입니다. 새 task를 만들 땐 이 구조를 참고해 목표 개수·가중치만 조정합니다.)

- `type: "unary"` → `(predicate 물체)` 형태 목표 (예: `is-clean coffeetable`)
- `type: "object_at"` → `(object-at 물체 위치)` 형태 목표
- `type: "unary_or_relocated"` → `(predicate 물체)` 또는 `(object-at 물체 storage류)` 둘 중 하나만
  만족해도 인정 (예: "치워짐"을 "is-clean"으로 표현하든 "storage로 옮김"으로 표현하든 동일하게 봄)
- `passed`/`received` 같은 **과정(process) predicate는 목표로 쓰지 않습니다.** relay가 일어났는지는
  "어떻게 했는가"이지 "무엇을 만들었는가"가 아니므로, goal_states.json에는 최종 상태만 적습니다.
- `weight`의 합이 100이 되도록 맞춥니다.
- `object_synonyms`에 최대한 많은 후보를 넣어야, 방법마다 다른 이름을 써도 공정하게 채점됩니다.

### 1-2. gt_pddl.txt (참고용, 대표 예시 하나)

```
(define (problem home-training-setup)
  (:domain household-multiagent)
  (:objects
    r1 - gripper
    r2 - mobile_heavy
    ...
  )
  (:init ... )
  (:goal (and (is-clean coffeetable) ... ))
)
```

이 파일은 사람이 읽기 위한 예시이며, 실제 SG(잉여 목표) 계산 시
`goal_states.json`의 동의어 조합으로 자동 확장되어 사용됩니다.

---

## 2. 스크린샷 + Invisible 객체 넣는 법

### 2-1. 스크린샷 저장

각 방(kitchen/living_room/bedroom/bathroom)마다 로봇 시점 스크린샷 2장씩,
총 8장을 아래 경로에 넣습니다.

```
task6/task_scene/images/input_image/
├── kitchen1.png, kitchen2.png
├── livingroom1.png, livingroom2.png
├── bedroom1.png, bedroom2.png
└── bathroom1.png, bathroom2.png
```

### 2-2. invisible_objects.json 작성

스크린샷을 보고, `master_object_list.json`에는 있지만
**화면에 실제로 안 보이는 물체**를 방마다 나열합니다.

```json
{
  "kitchen": ["ButterKnife", "Ladle", "Microwave", ...],
  "living_room": ["CellPhone", "CreditCard", ...],
  "bedroom": [...],
  "bathroom": [...]
}
```

이 파일은 `baseline_central.py`, `baseline_independent.py`가 프롬프트를 만들 때
"이 물체는 실제 존재하지만 네 시야엔 안 보인다"는 조건을 부여하는 데 씁니다.

---

## 3. 각 방법 실행하는 법

### 3-1. Ours

Ours는 **자체 파이프라인이 아직 없어서, NL/PDDL 결과를 직접 만들어 넣습니다.**

```
task6/results/ours/ours_nl.txt    ← 자연어 플랜 (사람이 작성 또는 자체 시스템 출력)
task6/results/ours/ours_pddl.txt  ← PDDL (goal_states.json과 같은 predicate 스키마 사용 권장:
                                      object-at, is-clean, - item)
```

> ⚠️ predicate 이름은 `object-at`, `is-clean` 등 **`goal_states.json`에서 쓰는 이름과 일치**시켜야
> 자동 채점이 정확합니다. (`at-location`처럼 다른 이름을 써도 동의어 정규화 레이어가 일부 흡수하지만,
> 가능하면 표준 이름을 쓰는 게 안전합니다.)

### 3-2. Centralized / Independent (GPT-4o 자동 생성)

```bash
cd ~/journal_co/experiment
source ../LaMMA-P/lammap/bin/activate

python baseline_central.py       # → task6/results/central/central_nl.txt 생성
python baseline_independent.py   # → task6/results/independent/independent_nl.txt 생성
```

이 두 방법은 **NL만 생성하고 PDDL은 만들지 않습니다** (설계상 순수 LLM 베이스라인이라
Track B/D 평가 대상에서 제외됨. `aggregate_results.py`의 `PDDL_EVAL_METHODS`에서 확인 가능).

다른 task를 실행하려면 스크립트 상단의 `TASK_DIR = "task6"`를 원하는 task로 바꿉니다.

### 3-3. LaMMA-P (living_room 단일 공간, 로봇 4대)

**중요 제약**: LaMMA-P는 아키텍처상 **한 번에 하나의 FloorPlan(=하나의 방)만** 다룰 수 있습니다.
그래서 4개 방 태스크 중 **living_room 서브셋만** 담당하도록 재구성해서 실행합니다.

**로봇 구성** (`Ours`의 4개 역할에 최대한 대응):

| LaMMA-P 로봇 번호 | 역할 | 비고 |
|---|---|---|
| robot29 | Gripper 대응(고정, 이동 불가) | `resources/robots.py`에 직접 추가한 커스텀 로봇 (GoToObject 없음) |
| robot9 | Mobile Heavy | mass_capacity 5 |
| robot8 ×2 | Mobile Light | mass_capacity 0.4 |

**1) robot29가 없다면 추가 (최초 1회만)**

`~/journal_co/LaMMA-P/resources/robots.py`에서 `robots = [...]` 리스트 **위에** 추가:

```python
robot29 = {'name': 'robot29',  'skills': ['OpenObject', 'CloseObject', 'SwitchOn', 'SwitchOff', 'PickupObject', 'PutObject'], 'mass' : 100}

robots = [robot1, ..., robot28, robot29]
```

> ⚠️ 반드시 `robot29 = {...}` 정의가 `robots = [...]` 리스트보다 **위(앞)**에 있어야 합니다.

**2) 태스크 정의**

```bash
cd ~/journal_co/LaMMA-P
cat > data/final_test/FloorPlan204.json << 'EOF'
{"task": "Clear the living room for home training, move pillows and items off the coffee table and sofa", "robot list": [29,9,8,8], "object_states": [{"name": "CoffeeTable", "contains": [], "state": "None"}, {"name": "Pillow", "contains": [], "state": "None"}], "trans": 2, "min_trans": 8}
EOF
```

> `task` 문구는 **최대한 Ours와 같은 의미가 되도록 구체적으로** 씁니다.
> 너무 추상적인 문구("공간 비우고 세팅해줘" 등)를 주면 GPT-4o가 씬에 없는 물체를
> 상상해서 만들어내는 환각(hallucination)이 발생할 수 있습니다 (실제 관측된 현상).

**3) 실행**

```bash
rm -rf logs/*        # 이전 결과와 섞이지 않도록 정리 (선택사항)
source lammap/bin/activate
python scripts/pddlrun_llmseparate.py --floor-plan 204 --gpt-version gpt-4o
```

**4) 결과를 experiment 폴더로 자동 동기화**

```bash
python sync_to_experiment.py
```

이 스크립트는 가장 최근 로그에서:
- `combined_plan.py` → `task6/results/lamma_p/lamma_p_nl.txt`
- `validated_subtask/*_problem.pddl` (모든 로봇) → `task6/results/lamma_p/lamma_p_pddl.txt`

로 자동 저장합니다.

---

## 4. 통합 평가 실행

```bash
cd ~/journal_co/experiment
python aggregate_results.py
```

### 평가 구조

| Track | 내용 | 평가 대상 | 기준 |
|---|---|---|---|
| **A: LLM Judge** | GPT-4o가 NL 플랜을 TF/PF/OC/SC(1~10점)로 채점 | 4개 방법 전부 | 기준 없음(정성 평가) |
| **B: GT 비교** | 가중 목표상태 달성률(GC), 잉여 목표 비율(SG) | Ours, LaMMA-P만 (`PDDL_EVAL_METHODS`) | `goal_states.json` |
| **D: Scene 일치도** | PDDL이 언급한 물체가 실제 씬에 존재하는 비율(IC) | Ours, LaMMA-P만 | `master_object_list.json` |

Central/Independent가 Track B/D에서 제외되는 이유는 **파일이 없어서가 아니라
"순수 NL 베이스라인"이라는 실험 설계**입니다 (`PDDL_EVAL_METHODS = {"ours", "lamma_p"}`).

### 결과 확인

```bash
cat task6/results/summary.json         # 전체 결과 (기계 판독용)
cat task6/results/summary_table.md      # 표 형태 (사람이 읽기용)
```

---

## 5. 다른 Task(7~10 등)로 확장하는 법

1. `task7/task_scene/task.json`, `scene/scene.json` 작성
2. `task7/task_scene/images/input_image/`에 스크린샷 8장 + `invisible_objects.json` 작성
3. `task7/ground_truth/goal_states.json` 작성 (섹션 1 규칙 그대로)
4. `baseline_central.py`, `baseline_independent.py`, `aggregate_results.py` 상단의
   `TASK_DIR = "task6"` → `"task7"`로 변경 후 동일하게 실행
5. LaMMA-P는 task7이 다루는 방에 맞는 FloorPlan 번호로 `data/final_test/FloorPlan{N}.json` 새로 작성 후 동일 절차

---

## 6. 알려진 이슈 / 주의사항

- **AI2-THOR 해상도 문제**: WSL 디스플레이 해상도가 낮으면 `Controller(height=1000, width=1000)`이
  실패합니다. `LaMMA-P/data/aithor_connect/aithor_connect.py`에서 `height=300, width=300`으로 낮춰두었습니다.
- **JSON의 Python `None`**: 데이터 파일에 `None`이 들어가면 JSON 파싱 에러가 납니다. `null`로 써야 합니다.
- **LaMMA-P PDDL 어휘 비일관성**: GPT-4o가 predicate 이름(`object-at`/`at-location`)과 타입 이름
  (`- item`/`- object`)을 실행마다 자유롭게 바꿔 씁니다. **동일한 로봇 구성·태스크 문구로 여러 번
  돌려도 predicate 어휘 자체가 매번 달라지는 것이 실제로 관측됐습니다** (로봇 수와는 무관한 현상).
  `aggregate_results.py`에 동의어 정규화 레이어가 있어 이를 일부 흡수합니다:
  ```python
  PREDICATE_SYNONYMS = {
      "at-location": "object-at", "located-at": "object-at", "is-at": "object-at",
      "in-location": "object-at", "switch-on": "is-on", "turned-on": "is-on",
      "powered-on": "is-on", "cleaned": "is-clean", "clean": "is-clean",
      "tidy": "is-clean", "clear": "is-clean",
  }
  TYPE_SYNONYMS = {"object": "item", "obj": "item", "thing": "item"}
  ```
  새로운 어휘 변형이 발견되면 이 딕셔너리에 추가하면 됩니다. 완전하지 않을 수 있으니,
  평가 후 GC/IC가 예상과 다르게 낮으면 `task6/results/lamma_p/lamma_p_pddl.txt`를 직접 열어
  predicate 이름이 무엇인지 먼저 확인하세요.

- **모호한 태스크 문구 위험**: LaMMA-P에게 추상적 지시("20분 뒤 홈트레이닝, 공간 비우고
  세팅해줘"처럼 목적만 있고 대상 물체가 안 나온 문구)를 주면, 실행마다 완전히 다른 방식으로
  태스크를 해석하는 현상이 실제로 관측됐습니다. 동일 조건(로봇 4대, 같은 추상적 문구)으로
  반복 실행한 예:
  - 1회차: Chair 4개를 창고로 옮기는 것으로 해석
  - 2회차: 씬에 존재하지도 않는 YogaMat/Dumbbells/ResistanceBands를 상상해 목표로 설정
  반면 태스크 문구를 구체적으로 쓰면("Push the CoffeeTable...", "Clear the living room,
  move pillows and items off the coffee table and sofa") 실제 씬의 물체(CoffeeTable, Pillow,
  Sofa)를 정확히 참조했습니다. **재현성이 필요하면 반드시 구체적인 태스크 문구를 사용하세요.**
  이 자체도 "모호한 지시에서 LLM 플래너가 씬 그라운딩에 실패한다"는 유의미한 관찰 결과이므로,
  일부러 추상적 문구로 실험해 이 현상을 리포트에 활용할 수도 있습니다.
