# Experiment — CDA 기반 멀티로봇 계획 실험

전체 방법론 설명, 설치, 실행 방법은 저장소 루트의 [`README.md`](../README.md)를 먼저 봐라. 이 문서는
`experiment/` 폴더 안의 파일/데이터 형식만 다룬다.

## 방법론

| 방법 | 설명 |
|------|------|
| **cda** | CDA_stage (ours) — 고수준 분산형 멀티로봇 협업 계획 (`run_cda_stage.py`) |
| **central** | Centralized — 중앙 LLM이 지시, 각 로봇이 실행 (`run_central.py`) |
| **independent** | Independent — 각 로봇이 독립적으로 계획 (`run_independent.py`) |
| **lamma_p** | LaMMA-P — PDDL 기반 baseline (`run_lamma_p.py`) |
| **smart_llm** | SMART-LLM — LLM 기반 baseline (`run_smart_llm.py`) |

## 실행 (요약 — 자세한 옵션은 루트 README)

```bash
python run_cda_stage.py --task task1_abstract --n-robots 4 --run 1
python run_central.py --task task1_abstract --n-robots 4 --run 1
python judge_v19.py --specs cda=run1:ours_cda --out out.json --reps 2 --n-robots 4 --kinds abstract --tasks 1
```

## 폴더 구조

```
experiment/
├── run_cda_stage.py          CDA_stage(현재 메인) 실행
├── run_cda_gc.py             CDA-1116_SHJ(이전 버전) 실행 — CDA_DIR_NAME 환경변수로 폴더 선택 가능
├── run_central.py            Central baseline
├── run_independent.py        Independent baseline
├── run_lamma_p.py            LaMMA-P baseline
├── run_smart_llm.py          SMART-LLM baseline
├── convert_to_joint_plan.py  LaMMA-P/SMART-LLM 결과를 자연어 Joint Plan으로 변환
├── judge_v19.py              공식 LLM judge (TF/PF/CQ/SC, 여러 방법을 한 호출에서 익명 비교)
├── aggregate_results_jabung.py  judge_v19.py가 재사용하는 judge_plan() 로직의 원본
├── loader.py                 데이터 로더 (task/scene/robot/image)
├── task/task.json            10개 abstract + 10개 simple task 정의
├── scene/{room,object}.json  방/물건 카탈로그 (ground truth)
├── robot/                    robot 타입 정의 JSON
├── image/                    사전 캡처된 씬 이미지 (abstract/simple × task × n_로봇수)
└── results/final/            실험 결과 (대부분 스크래치, 커밋 안 함)
    └── run{N}/{n}robot/{abstract|simple}/task{K}/
        ├── ours_cda.json             CDA_stage 결과 (joint_plan_text/joint_plan_full/offers/...)
        ├── ours_cda_io_log.json      LLM 호출 전체 로그
        ├── baseline_central.json
        ├── baseline_independent.json
        ├── baseline_lamma_p.json
        └── baseline_smart_llm.json
```

## 결과 파일 형식

| 키 | 내용 |
|---|---|
| `joint_plan_text` | judge가 보는 텍스트 (Provenance 이전까지) |
| `joint_plan_full` | Provenance/Report까지 포함한 전체 텍스트 |
| `offers` / `local_plans` | Stage 1/2 원본 출력 |
| `graph` / `report` | Stage 4 결과 그래프와 goal coverage 리포트 |
| `metrics` | 토큰 사용량, makespan, deadline 충족 여부 등 |
| `llm_judge` | judge_v19.py 등이 채워 넣는 TF/PF/CQ/SC 점수 (채점 전엔 `null`) |
