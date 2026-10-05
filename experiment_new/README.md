# experiment_new

멀티로봇 협업 계획 실험을 위한 통합 데이터 구조 및 실행 스크립트 모음.
기존 `experiment/` 폴더(task별로 흩어진 구조)를 정규화해서, 공통 데이터는
한 곳에 모으고 task는 그걸 참조만 하도록 재설계한 버전.

## 폴더 구조
experiment_new/
├── loader.py # 공통 데이터 로더 (모든 run_*.py가 이걸 사용)
├── run_ours.py # ours_new 파이프라인 실행 (reasoning 제외)
├── run_ours_reasoning.py # ours_new 파이프라인 실행 (reasoning 포함)
├── run_central.py # Centralized 베이스라인
├── run_independent.py # Independent 베이스라인
├── run_lamma_p.py # LaMMA-P 실행 (WSL 전용, 아래 참고)
├── run_smart_llm.py # SMART-LLM 실행 (WSL 전용, 아래 참고)
├── run_pddl_eval.py # 자연어 계획 -> PDDL 변환 + PS/PV 검증
├── run_all.py # 5개 방법론 통합 실행
│
├── scene/
│ ├── room.json # 전역 방(FloorPlan) 카탈로그: floorplan_n, floorplan_type, object_n
│ └── object.json # 전역 물건 카탈로그: object_n, object_name, object_state, object_type, is_furniture
├── robot/
│ └── robot.json # 로봇 타입 카탈로그: robot_n(0=Gripper,1=Mobile_Light,2=Mobile_Heavy), robot_can/cannot
├── task/
│ └── task.json # 전체 task 정의 (abstract 10개 + simple 10개, 각 task별 robot/room/invisible_list/single_room)
├── ground_truth/
│ └── goal_states.json # task별 목표 상태 (abstract만 채움, simple은 빈 틀)
├── pddl/
│ └── domain_typed.pddl # PDDL 변환에 쓰는 고정 도메인 파일
├── image/
│ ├── multi_room/{abstract,simple}/task{N}/ # 로봇별 2장 (자기 방 시점)
│ └── single_room/{abstract,simple}/task{N}/ # 로봇별 1장 (main_room 기준, LaMMA-P/SMART-LLM 이론상 용)
└── results/
└── {task_n}_{method}_result.json # 모든 실행 결과 저장 위치

## 핵심 설계

### task.json 하나로 통합
기존엔 task마다 폴더가 따로 있었지만(`experiment/task6/input/scene/task.json`),
`experiment_new`는 **모든 task를 `task/task.json` 안에 배열로 통합**했다.
각 task는 `task_n`(예: `task1_abstract`)으로 식별되고, `room`(로봇이 multi_room에서
어느 FloorPlan에 있는지), `single_room`(LaMMA-P/SMART-LLM 비교용으로 로봇
전체가 main_room 하나에 모였다고 가정했을 때의 구성), `invisible_list`(로봇별로
이미지에 안 보이는 물건의 object_n)를 갖는다.

### 이미지 파일명 규칙
multi_room: task{N}{abstract|simple}{FP}{R}{1,2}.png (로봇당 2장)
single_room: task{N}{abstract|simple}{FP}_{R}_1.png (로봇당 1장, FP는 항상 main_room 기준)
FP 번호 자릿수로 방 타입이 결정된다 (한두자리=kitchen, 200대=living_room,
300대=bedroom, 400대=bathroom). `loader.py`의 `fp_to_room_type()`이 이 규칙을 구현한다.

### 5개 방법론
| 방법 | 실행 환경 | 입력 | 비고 |
|---|---|---|---|
| ours | Windows/WSL 무관 | multi_room 이미지 기반 capability | ours_new 파이프라인(Offer->LocalPlan->GraphReasoning) 그대로 사용 |
| central | Windows/WSL 무관 | multi_room, 모든 agent 정보를 한 번에 중앙 집중 | 1회 LLM 호출 |
| independent | Windows/WSL 무관 | multi_room, agent별 독립 LLM 호출 | 서로 다른 agent 정보 공유 없음 |
| LaMMA-P | **WSL 전용** | single_room의 robot list -> AI2-THOR 직접 조회 | PDDL 기반, fast-downward로 실제 플래닝 |
| SMART-LLM | **WSL 전용** | single_room의 robot list -> AI2-THOR 직접 조회 | Python 코드 생성 방식 |

LaMMA-P/SMART-LLM은 이미지를 쓰지 않고, AI2-THOR 씬에서 직접 물건 목록을 가져온다
(원본 설계를 그대로 유지하기로 결정 - VLM으로 바꾸는 수정은 하지 않음).

## 실행 환경 설정

### Windows (ours, central, independent)
```powershell
cd experiment_new
python run_ours.py --task task1_abstract
python run_central.py --task task1_abstract
python run_independent.py --task task1_abstract
```

### WSL (LaMMA-P, SMART-LLM) - ai2thor 2.7.2가 Windows를 지원하지 않아 WSL 필요
```bash
# 최초 1회 설정
python3.10 -m venv ~/ai2thor_env
source ~/ai2thor_env/bin/activate
pip install ai2thor==2.7.2 openai Pillow

# fast-downward 빌드 (LaMMA-P/downward 안에서)
sudo apt install -y cmake g++ build-essential
cd LaMMA-P/downward && python build.py release

# VAL 빌드 (PDDL 검증용, 레포 루트에서)
git clone https://github.com/KCL-Planning/VAL.git
cd VAL && cmake . -DCMAKE_BUILD_TYPE=Release -DCMAKE_POLICY_VERSION_MINIMUM=3.5 && make -j2

# 실행
cd experiment_new
source ~/ai2thor_env/bin/activate
python run_lamma_p.py --task task1_abstract
python run_smart_llm.py --task task1_abstract
```

**주의**: ai2thor 2.7.2가 Linux 전용 모듈(`tty`, `termios`, `fcntl`)을 import하므로
Windows에서는 실행 불가. `LaMMA-P/scripts/pddlrun_llmseparate.py`와
`SMART-LLM/scripts/run_llm.py` 상단에 더미 모듈 등록 코드가 패치되어 있다.
또한 `ai2thor.controller`의 `find_build()`가 Windows(`platform.system()`)를
인식하지 못해 Windows에서는 애초에 동작하지 않는다.

### PDDL 변환 검증 (run_pddl_eval.py)
ours/central/independent의 자연어 계획을 GPT-4o로 PDDL로 변환한 뒤,
fast-downward(PS: Plan Solvability)와 VAL(PV: Plan Validity)로 검증한다.
먼저 해당 방법론의 run_*.py를 실행해서 results/ 에 결과가 있어야 한다.

```bash
python run_pddl_eval.py --task task1_abstract --method ours
python run_pddl_eval.py --task task1_abstract --method central
```

independent는 계획 자체가 느슨해서(agent 간 협업 부재) PDDL 변환 시
타입 불일치(예: object-at의 두 번째 인자에 room 대신 agent id가 들어가는 등)가
발생해 PS가 실패하는 경우가 있음 - 이는 변환기 버그가 아니라 independent
방법론 자체의 특성으로 추정.

## 알려진 이슈 / TODO
- simple task의 image 캡처가 아직 미완료 (abstract만 완료)
- `goal_states.json`의 simple task 항목이 전부 빈 틀
- task.json의 task10은 multi_room(8대)과 single_room(6대)의 로봇 수가 달라
  실험 시 유의 필요
- aggregate_results.py(Track A LLM Judge, Track PDDL PS/PV)는 아직
  experiment_new 버전으로 재작성 전
