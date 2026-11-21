# AAMAS — CDA: Collaborative Decentralized Architecture

멀티로봇 가정용 협업 계획(task planning) 연구 프로젝트. 우리 방법(CDA)과 4개 baseline
(Centralized, Independent, LaMMA-P, SMART-LLM)을 LLM judge로 비교 평가한다.

## 1. 방법론 — CDA_stage (현재 메인 코드)

`CDA_stage/`가 현재 공식 방법론 구현이다. CDA는 **고수준(high-level) 플래너**다 — 로봇의 이동 경로,
손의 움직임, 이동 소요 시간을 직접 추적하지 않는다. 한 스텝은 짧은 자연어 문장 + 몇 개의 필드
(타입, 방, 아이템, 상대 로봇, enables)로 표현된다.

### 파이프라인 (4단계)

```
Stage 1  Offer            각 로봇이 "내가 뭘 할 수 있는지"를 동시에 선언 (can_do / can_help / 
                          need_from_others / has_items)
Stage 2  Local Plan       각 로봇이 자기 역할의 계획을 동시에 작성 (LOCAL/PASS/RECEIVE/ASK_HELP)
Stage 3  Edge Proposal    각 로봇이 다른 로봇의 요청(ASK_HELP/RECEIVE)에 YES/NO로 답함
Stage 4  Graph Alignment  코드가 그래프를 분석하고, LLM 1회 호출로 정렬(링크/순서/중복 제거)을
                          결정하면 규칙이 그 결정을 검증한다 → Joint Plan 렌더링
```

Stage 1~3은 로봇마다 병렬(asyncio.gather)로 실행되고, 각 단계 사이에 배리어가 있다. Stage 4는
중앙에서 한 번만 실행된다.

### 핵심 설계 원칙

- **"LLM이 결정하고, 규칙은 검증만 한다."** 규칙은 LLM의 결정을 다시 쓰지 않는다 — 받아들이거나,
  거부하고 그 이유를 기록할 뿐이다.
- 무엇이든 조용히 사라지지 않는다 — 모든 제거(drop/remove)는 이유와 함께 리포트에 남는다.
- 스텝 id(`r2_s3`)는 코드만 만들고 절대 바뀌지 않는다. 실행 순서는 `Plan.order`에 별도로 관리되어,
  Stage 3에서 새 스텝이 끼어들어도 기존 id가 밀리지 않는다.

### Step 종류

| 타입 | 의미 |
|---|---|
| `LOCAL` | 자기 방에서 혼자 하는 일 |
| `PASS` | 로봇 j에게 물건 o를 줌 (집고 운반하는 것까지 포함; 둘 중 이동 가능한 쪽이 움직임) |
| `RECEIVE` | 로봇 i가 가진 물건 o를 원함 |
| `ASK_HELP` | 도움이 필요함. 특정 로봇을 지명하지 않고 조건만 말함 ("소파를 들 수 있는 사람") |
| `HELP` | 로봇 j의 방으로 가서 j의 일을 대신 해줌 |

순서 규칙: `PASS → RECEIVE` 엣지, `HELP → ASK_HELP` 엣지, 한 로봇 자신의 스텝은 작성한 순서대로
(SEQ 엣지), Stage 4가 로봇 간 `ORDER` 엣지를 추가로 걸 수 있다.

### Ablation 옵션 (`run_pipeline`의 키워드 인자)

| 옵션 | 끄면(False) | 의미 |
|---|---|---|
| `share_offers` | "no offer" | Stage 2가 다른 로봇의 offer를 못 봄 |
| `use_edge_proposal` | "no edge proposal" | 로봇이 응답하지 않고, 코드가 가능한 모든 답을 만들어 Graph LLM이 중앙에서 결정 |
| `use_graph_llm` | "no graph reasoning" | 규칙만 사용 — 요청마다 첫 번째로 유효한 답을 그대로 채택 |

이전 버전 `CDA-1116_SHJ/`(세부 pick_up/move_to 단위 액션, precondition/effect 추적, 능력 태그
시스템 등)는 비교/참고용으로 저장소에 남아 있지만 더 이상 메인 경로가 아니다.

## 2. 저장소 구조

```
CDA_stage/        현재 메인 방법론 코드 (core/llm/pipeline/render/stage1-4)
CDA-1116_SHJ/     이전 버전 (세부 액션 단위, 더 이상 메인 아님)
LaMMA-P/          LaMMA-P baseline (PDDL 기반, Fast Downward 플래너 필요)
SMART-LLM/        SMART-LLM baseline
VAL/              PDDL 플랜 검증기 (LaMMA-P가 사용, C++ 빌드)
ai2thor_sim/      AI2-THOR 씬을 직접 조작/캡처하는 도구 (a.py: task 기반, b.py: FloorPlan 번호만으로)
experiment/       실행 스크립트, task/scene/robot 데이터, 실험 결과
  ├── run_cda_stage.py       CDA_stage 실행 (현재 메인)
  ├── run_cda_gc.py          CDA-1116_SHJ 실행 (이전 버전, CDA_DIR_NAME 환경변수로 폴더 선택 가능)
  ├── run_central.py / run_independent.py / run_lamma_p.py / run_smart_llm.py   baseline 실행
  ├── judge_v19.py           공식 LLM judge (TF/PF/CQ/SC, 한 번의 호출에 여러 방법을 익명 비교)
  ├── loader.py              task.json/room.json/robot.json/이미지 로더
  ├── task/task.json         10개 abstract + 10개 simple task 정의
  ├── scene/{room,object}.json   방/물건 카탈로그 (ground truth)
  ├── image/                 사전 캡처된 씬 이미지 (abstract/simple × task × 로봇수)
  └── results/final/runN/    실험 결과 (대부분 gitignore 대상, 코드는 아님)
```

## 3. 설치

### 3.1 Python 환경

Python 3.12 기준.

```bash
pip install openai networkx pillow
```

### 3.2 AI2-THOR (선택 사항)

**이미 정의된 10+10개 task를 그대로 돌리는 거라면 AI2-THOR 설치가 필요 없다** — 필요한 씬
이미지(`experiment/image/`)가 이미 저장소에 캡처되어 있다. AI2-THOR는 **새로운 방(FloorPlan)이나
새 task를 추가해서 직접 스크린샷을 찍을 때만** 필요하다.

```bash
pip install ai2thor opencv-python
```

**중요: AI2-THOR는 Linux/Mac 빌드만 존재한다 (네이티브 Windows 빌드 자체가 없음).** Windows에서
돌리고 싶으면 반드시 WSL이나 실제 Linux/Mac 머신을 써야 한다. WSL일 경우 `ai2thor_sim/b.py`의
실시간 탑뷰 창(cv2)까지 쓰려면 WSLg(X11) 디스플레이가 정상 동작해야 한다 — 안 되면
`--no-topdown`으로 꺼도 캡처 자체는 된다.

### 3.3 API 키

API 키 2개가 필요하고, 둘 다 git에 올라가지 않는다 (`.gitignore`) — 각자 직접 만들어야 한다.

```
LaMMA-P/api_key.txt          ← OpenAI API key (CDA/baseline 생성용)
LaMMA-P/gemini_api_key.txt   ← Gemini API key (judge_v19.py 채점용)
```

파일이 없어도 `OPENAI_API_KEY` 환경변수가 설정되어 있으면 생성 스크립트는 그걸 우선 사용한다.

### 3.4 (baseline까지 전부 돌릴 경우만) LaMMA-P 추가 설치

LaMMA-P baseline은 PDDL 플래너(Fast Downward)와 VAL 플랜 검증기가 필요하다. `LaMMA-P/README.md`,
`VAL/README.md` 참고. CDA_stage만 테스트하는 거라면 이 단계는 건너뛰어도 된다.

## 4. 실행 방법

전부 `experiment/` 안에서 실행한다.

### 4.1 CDA_stage (메인 방법) 실행

```bash
cd experiment
python run_cda_stage.py --task task1_abstract --n-robots 4 --run 1
```

주요 옵션:

| 옵션 | 기본값 | 설명 |
|---|---|---|
| `--task` | (필수) | 예: `task1_abstract`, `task3_simple` |
| `--n-robots` | 4 | 2/3/4/6/8 중 하나 (task.json에 해당 설정이 있어야 함) |
| `--model` | gpt-4o | 사용할 OpenAI 모델 |
| `--run` | 1 | 결과 저장 슬롯 번호 (반복 실험 구분용) |
| `--no-offer` / `--no-proposal` / `--no-graph-llm` | - | ablation 플래그 |
| `--dry-run` | - | API 호출 없이 loader만 테스트 |

결과는 `experiment/results/final/run{N}/{n}robot/{abstract|simple}/task{K}/ours_cda.json`에 저장된다.

### 4.2 Baseline 실행 (같은 패턴)

```bash
python run_central.py --task task1_abstract --n-robots 4 --run 1
python run_independent.py --task task1_abstract --n-robots 4 --run 1
python run_lamma_p.py --task task1_abstract --n-robots 4 --run 1
python run_smart_llm.py --task task1_abstract --n-robots 4 --run 1
```

### 4.3 채점 (judge_v19.py)

한 번의 호출로 같은 task의 여러 방법 결과를 익명 라벨(PLAN_A, PLAN_B, ...)로 섞어서 동일한
기준으로 채점한다.

```bash
python judge_v19.py \
  --specs cda=run1:ours_cda central=run1:baseline_central independent=run1:baseline_independent \
          lamma=run1:baseline_lamma_p smart=run1:baseline_smart_llm \
  --out judge_result.json --reps 2 --n-robots 4 --kinds abstract simple --tasks 1 2 3
```

채점 기준: **TF**(Task Fulfillment) / **PF**(Plan Feasibility) / **CQ**(Collaboration Quality) /
**SC**(Sequential Coherence), 각 0~5점.

### 4.4 새 씬 캡처 (선택, Linux/Mac에서만)

```bash
cd ai2thor_sim
python b.py --fp 21          # FloorPlan21을 직접 조작/캡처 (task 설정에 안 묶임)
python a.py --task task1_abstract --n 4 --room FP304   # 특정 task의 특정 방만
```

조작키: `w/a/s/d` 이동, `i/k` 고개 위/아래, `j/l` 좌/우 회전, `o` 열기/닫기, `t` 켜기/끄기,
`p` 집기/내려놓기, `b` 깨뜨리기, `v` 더럽히기/닦기, `c` 캡처, 숫자키 로봇 전환, `x` 종료.

## 5. 참고

- `experiment/README.md`: experiment 폴더 안 파일/데이터 형식 세부 설명
- `experiment/results/`는 대부분 실험 결과(스크래치)라 커밋에서 의도적으로 제외하는 경우가 많다 —
  재현 가능한 코드 변경이 아니면 결과 폴더를 git에 올리지 않는다.
