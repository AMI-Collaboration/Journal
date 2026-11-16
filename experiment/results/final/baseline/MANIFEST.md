# baseline 결과 (LaMMA-P, SMART-LLM, Central, Independent)

이 폴더는 `results/final/run*`에서 **올바른 baseline 결과만 복사**해 모은 것이다. 원본은 그대로 있다.
구조는 run 폴더와 같다: `baseline/run{R}/{N}robot/{abstract|simple}/task{K}/baseline_{method}.json`.
(`run`은 반복 번호이고 로봇 수가 아니다.)

심사에 쓰는 법 (코드 수정 없이 동작):

```
python judge_v19.py --specs lamma=baseline/run1:baseline_lamma_p smart=baseline/run1:baseline_smart_llm \
    central=baseline/run1:baseline_central indep=baseline/run1:baseline_independent ...
```

## 들어 있는 것

| 폴더 | 구성 | 과제 | 방법 | 파일 수 |
|---|---|---|---|---|
| `run1`, `run2`, `run3` | 4대 | abstract 1-10, simple 1-10 | 4종 전부 | 각 80 |
| `run5` | 2대 | abstract 2, 3, 9 | 4종 전부 | 12 |
| `run5` | 6대 | abstract 2, 3, 9 | 4종 전부 | 12 |

- **`run2`, `run3`의 4대 LaMMA-P와 SMART-LLM(abstract와 simple, 각 10개씩 총 80개)에는 자연어 플랜(`joint_plan_text`)이 없다.**
  심사하려면 `convert_to_joint_plan.py --run 2|3`로 변환을 먼저 돌려야 한다. 같은 run의 Central, Independent와
  `run1`의 네 방법, `run5`의 네 방법은 모두 자연어 플랜이 있다(이 폴더에서 확인).
  파일 수 확인은 `_copied_counts.json` 참고.
- run5의 2대와 6대는 `n_robots`를 입력에 넘기도록 고친 코드(`run_lamma_p.py`, `run_smart_llm.py`,
  `run_central.py`, `run_independent.py`)로 다시 돌린 결과다. 최종 계획의 로봇 라벨 번호가
  구성 크기(R2, R6)와 일치하는 것을 확인했다.

## 일부러 뺀 것 (원본은 run 폴더에 그대로 있음)

| 원본 위치 | 이유 |
|---|---|
| `run1`~`run3`의 `6robot`, `8robot` (4종 전부) | 입력이 항상 4대였다. 네 방법 모두 로봇 라벨이 R4를 넘은 적이 없다(LaMMA-P, SMART-LLM은 `build_lamma_p_input`, Central, Independent는 `build_agent_inputs`가 `n_robots`를 받지 않았다). 폴더 이름만 6/8대였다. |
| `run4` | `run1`의 baseline과 raw 결과가 80개 모두 동일한 복사본이다. |
| `run5`의 이전 2/6대 Central, Independent | 같은 이유(4대 입력). 12개 파일을 `_excluded_4robot_input/run5/...`에 백업해 두었다. 새로 돌린 결과가 `run5/`에 들어 있다. |

## 알려진 한계

- 2/6대 baseline은 abstract task 2, 3, 9 한 번씩뿐이다(반복 1회).
- LaMMA-P, SMART-LLM의 자연어 플랜(`joint_plan_text`)은 `convert_to_joint_plan.py`가 GPT-4o로 코드를 변환한 것이다.
  `[0-5 min]` 같은 시간 블록은 원본 계획에 없고 변환 단계에서 붙는다.
- 6/8대 baseline을 쓰려면 고친 러너로 다시 돌려야 한다 (현재는 2/6대의 task 2, 3, 9만 있음).
- 위 러너 수정은 아직 커밋되지 않았다.
