# Experiment — C-DA 기반 멀티로봇 계획 실험

## 개요
C-DA(Collaborative Decentralized Architecture) 파이프라인과 4개 베이스라인을 비교하는 실험 코드.

## 방법론
| 방법 | 설명 |
|------|------|
| **cda** | C-DA (ours) — 분산형 멀티로봇 협업 계획 |
| **central** | Centralized — 중앙 LLM이 지시, 각 로봇이 실행 |
| **independent** | Independent — 각 로봇이 독립적으로 계획 |
| **lamma_p** | LaMMA-P — PDDL 기반 baseline |
| **smart_llm** | SMART-LLM — LLM 기반 baseline |

---

## 환경 설정 (최초 1회)

### 1. WSL + 가상환경
```bash
python3 -m venv ~/ai2thor_env
source ~/ai2thor_env/bin/activate
pip install openai networkx pillow ai2thor
```

### 2. python 심링크
```bash
mkdir -p ~/.local/bin
ln -s /usr/bin/python3 ~/.local/bin/python
export PATH="$HOME/.local/bin:$PATH"
```

### 3. API 키
```
AAMAS/LaMMA-P/api_key.txt          ← OpenAI API key
AAMAS/LaMMA-P/gemini_api_key.txt   ← Gemini API key (평가용)
```

---

## 매번 시작 시

```bash
source ~/ai2thor_env/bin/activate
cd /mnt/c/Users/shin/Desktop/AAMAS/experiment
```

---

## 실험 실행

### 전체 실행
```bash
# task1~10, 5개 방법론 전체
python run_all.py

# 특정 task만
python run_all.py --tasks task1_abstract task2_abstract

# lamma_p/smart_llm 제외 (빠름)
python run_all.py --skip lamma_p smart_llm

# API 호출 없이 설정만 테스트
python run_all.py --dry-run

# 2번째 실험 round
python run_all.py --run 2

# 모델 변경
python run_all.py --model gpt-4o-mini
```

### 개별 방법론 실행
```bash
python run_cda.py --task task1_abstract
python run_central.py --task task1_abstract
python run_independent.py --task task1_abstract
python run_lamma_p.py --task task1_abstract
python run_smart_llm.py --task task1_abstract
```

---

## 평가

```bash
# 전체 task 평가 (LLM Judge + GC + Object Grounding)
bash run_eval_all.sh

# 단일 task 평가
python aggregate_results.py --task task1_abstract

# 결과 리포트 출력
python show_report.py --task task1_abstract
```

---

## 폴더 구조

```
experiment/
├── run_all.py               # 전체 실행
├── run_cda.py               # C-DA 실행
├── run_central.py           # Central baseline
├── run_independent.py       # Independent baseline
├── run_lamma_p.py           # LaMMA-P baseline
├── run_smart_llm.py         # SMART-LLM baseline
├── convert_to_joint_plan.py # LaMMA-P/SMART-LLM 결과 변환
├── aggregate_results.py     # 평가 (LLM Judge + GC + Grounding)
├── show_report.py           # 결과 리포트 출력
├── run_eval_all.sh          # 전체 평가 배치
├── loader.py                # 데이터 로더 (task/scene/robot/image)
├── task/                    # task 정의 JSON
├── scene/                   # room/object 정보 JSON
├── robot/                   # robot 타입 정의 JSON
├── image/                   # 실험 이미지 (multi_room / single_room)
├── ground_truth/            # goal states JSON
├── pddl/                    # PDDL domain 파일
└── results/                 # 실험 결과 (gitignore)
    └── run1/
        ├── task1_abstract_multi_room_cda_result.json
        ├── task1_abstract_central_result.json
        ├── task1_abstract_independent_result.json
        ├── task1_abstract_lamma_p_result.json
        ├── task1_abstract_smart_llm_result.json
        ├── task1_abstract_summary.json
        └── task1_abstract_summary_table.md
```

---

## 결과 파일 형식

| 파일 | 내용 |
|------|------|
| `{task}_{mode}_{method}_result.json` | 계획 결과 (joint_plan_text 포함) |
| `{task}_summary.json` | 평가 점수 (TF/PF/OC/SC/GC/Grounding) |
| `{task}_summary_table.md` | 평가 점수 테이블 |
