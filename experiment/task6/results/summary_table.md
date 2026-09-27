# task6 통합 평가 결과

## Track A — LLM Judge (NL 기반, 모든 방법 공통)

| 방법 | TF | PF | OC | SC | Final |
|---|---|---|---|---|---|
| Ours (P2P) | 7 | 8 | 9 | 9 | 8.05 |
| LaMMA-P | 6 | 7 | 8 | 9 | 7.2 |
| Centralized | 8 | 9 | 9 | 9 | 8.65 |
| Independent | 5 | 4 | 7 | 6 | 5.4 |

## Track B — GT 비교 (PDDL 평가 대상만: Ours, LaMMA-P)

| 방법 | GC(가중) | SG |
|---|---|---|
| Ours (P2P) | 0.85 | 0.0 |
| LaMMA-P | 0.0 | 0 |
| Centralized | N/A (설계상 제외) | N/A (설계상 제외) |
| Independent | N/A (설계상 제외) | N/A (설계상 제외) |

## Track B 상세 — 목표상태 달성 여부

| 방법 | S1_workout_space_cleared | S2_hydration_object_ready | S3_wiping_object_ready | S4_lighting_on | S5_floor_clutter_cleared |
|---|---|---|---|---|---|
| Ours (P2P) | ✅ | ✅ | ✅ | ✅ | ❌ |
| LaMMA-P | ❌ | ❌ | ❌ | ❌ | ❌ |
| Centralized | N/A | N/A | N/A | N/A | N/A |
| Independent | N/A | N/A | N/A | N/A | N/A |

## Track D — Scene 일치도 IC (PDDL 평가 대상만: Ours, LaMMA-P)

| 방법 | IC | matched/mentioned |
|---|---|---|
| Ours (P2P) | 1.0 | 4/4 |
| LaMMA-P | 0.667 | 2/3 |
| Centralized | N/A (설계상 제외) | N/A (설계상 제외) |
| Independent | N/A (설계상 제외) | N/A (설계상 제외) |