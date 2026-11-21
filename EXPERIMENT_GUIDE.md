# 실험 실행 가이드 (실전 러닝북)

방법론/설치/기본 실행 명령은 [`README.md`](README.md)를 먼저 봐라. 이 문서는 **새 task를 추가하는
법**과 **실행하면서 실제로 부딪히는 문제들**을 다룬다.

> 이 문서는 예전 `journal_co/` 저장소·`task6~10` 개별 폴더·GT(`goal_states.json`) 기반 채점
> (Track A/B/D, GC/SG/IC) 구조를 설명했었다. 그 구조는 전부 폐기됐다 — 지금은 `experiment/task/task.json`
> 하나에 모든 task가 들어있고, 채점은 `judge_v19.py`의 LLM judge(TF/PF/CQ/SC) 하나로 통일됐다.
> LaMMA-P도 더 이상 robot을 수동으로 추가하거나 FloorPlan JSON을 손으로 안 써도 된다 —
> `run_lamma_p.py --task ... --n-robots ...`가 전부 자동으로 처리한다.

---

## 1. 새 task 추가하는 법

### 1-1. `experiment/task/task.json`에 항목 추가

각 task는 다음을 가진다 (기존 항목들을 참고해서 같은 스키마로 추가):

```json
{
  "task_n": "task11_abstract",
  "task": "자연어로 쓴 task 설명 (deadline, 요구사항 포함)",
  "deadline": 20,
  "rooms": { "FP304": {"main_room": true}, "FP14": {} },
  "configs": {
    "4": [{"robot_n": 0, "room": "FP304"}, {"robot_n": 1, "room": "FP304"},
          {"robot_n": 2, "room": "FP14"}, {"robot_n": 1, "room": "FP14"}]
  }
}
```

- `robot_n`은 `experiment/robot/`에 정의된 타입 번호(0=Gripper, 1=Mobile_Light, 2=Mobile_Heavy)다.
- `configs`는 로봇 수(2/3/4/6/8)별로 따로 정의한다 — 전부 만들 필요 없고, 실제로 돌릴 로봇 수만
  있으면 된다.
- `rooms`에 쓴 FloorPlan이 `experiment/scene/room.json`에 이미 있는지 먼저 확인해라 (room.json은
  AI2-THOR 전체 FloorPlan 카탈로그라서 어지간한 방은 이미 있다).

### 1-2. 씬 이미지 캡처 (필요한 FloorPlan이 아직 `experiment/image/`에 없을 때만)

Linux/Mac에서(README.md의 AI2-THOR 설치 참고):

```bash
cd ai2thor_sim
python a.py --task task11_abstract --n 4 --room FP304
```

로봇마다 `c`로 이미지 몇 장 캡처하면 `experiment/image/abstract/task11/n_4/`에 저장된다.
(task에 안 묶고 그냥 방만 둘러보고 싶으면 `b.py --fp 304` 사용.)

### 1-3. 돌려서 확인

```bash
cd experiment
python run_cda_stage.py --task task11_abstract --n-robots 4 --run 1 --dry-run   # loader만 먼저 검증
python run_cda_stage.py --task task11_abstract --n-robots 4 --run 1             # 실제 실행
```

---

## 2. 알려진 이슈 / 주의사항

### 2-1. task 문구가 모호하면 LLM이 씬에 없는 물체를 상상해낸다

동일한 로봇 구성·같은 추상적 문구("20분 뒤 홈트레이닝, 공간 비우고 세팅해줘")로 반복 실행해도
실행마다 완전히 다르게 해석되는 현상이 실제로 관측됐다 (한 번은 의자를 치우는 걸로, 다른 번은
씬에 있지도 않은 요가매트/덤벨을 상상해서 목표로 설정). 반대로 **"Push the CoffeeTable...",
"Clear the living room, move pillows and items off the coffee table and sofa"처럼 구체적으로
쓰면** 실제 씬의 물체를 정확히 참조한다. **재현성이 필요하면 task 문구를 구체적으로 써라.**
(반대로 "모호한 지시에서 LLM 플래너가 씬 그라운딩에 실패한다"는 것 자체가 리포트에 쓸 수 있는
유의미한 관찰 결과이기도 하다 — 일부러 추상적 문구로 이 현상을 실험할 수도 있다.)

이건 CDA_stage의 Stage 1(Offer)에도 똑같이 적용된다 — `object_catalog`(scene/object.json에서
가져온 ground-truth 물체 목록)를 Stage 1 프롬프트에 넣어주는 이유가 바로 이 환각을 줄이기
위해서다.

### 2-2. LaMMA-P의 PDDL 어휘는 실행마다 바뀐다

GPT-4o가 predicate 이름(`object-at`/`at-location`/`located-at`)과 타입 이름(`item`/`object`/`thing`)을
실행마다 자유롭게 바꿔 쓴다 (로봇 수와 무관하게 관측됨). `convert_to_joint_plan.py`가 LaMMA-P
결과를 자연어로 바꿀 때 이 변동을 흡수하지만, 결과가 이상하게 나오면 먼저 원본 PDDL을 직접 열어서
predicate 이름이 뭔지부터 확인해라.

### 2-3. JSON에 Python `None`을 쓰지 말 것

데이터 파일(`task.json`, `room.json` 등)에 Python `None`이 그대로 들어가면 JSON 파싱 에러가 난다.
반드시 `null`로 써야 한다.

### 2-4. AI2-THOR 해상도

AI2-THOR Controller를 너무 큰 해상도(`height=1000, width=1000` 등)로 띄우면 디스플레이 환경에
따라 실패할 수 있다. `ai2thor_sim/a.py`/`b.py`는 기본 `width=640, height=480`으로 띄운다 — 그래도
안 되면 더 낮춰봐라.

### 2-5. 토큰/비용 로그

모든 실행은 `experiment/results/usage_log.json`에 누적 기록된다 (`loader.log_usage_from_metrics`).
배치로 여러 task를 돌리기 전에 대략적인 호출 수 x 비용을 가늠하고 싶으면 이 파일의 최근 항목들을
먼저 봐라.

---

## 3. 전체 파이프라인을 한 번에 돌리고 싶을 때

현재 "전체 자동 실행" 단일 스크립트(`run_all.py`)는 없다 — task/로봇수/run 번호 조합마다
`run_cda_stage.py`/`run_central.py`/`run_independent.py`/`run_lamma_p.py`/`run_smart_llm.py`를
반복 호출하는 bash 루프를 그때그때 짜서 쓴다. 예:

```bash
cd experiment
for n in 1 2 3 4 5 6 7 8 9 10; do
  python run_cda_stage.py --task task${n}_abstract --n-robots 4 --run 1
done
```

채점은 `judge_v19.py --specs ... --out result.json --reps 2 --kinds abstract --tasks 1 2 ... 10`처럼
한 번에 여러 task/방법을 묶어서 돌리는 게 효율적이다 (README.md 4.3절 참고).
