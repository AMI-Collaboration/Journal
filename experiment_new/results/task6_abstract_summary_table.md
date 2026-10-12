# task6_abstract 통합 평가 결과

## Track A — LLM Judge (5개 방법론 공통, OC=정보제약 준수 여부 엄격 평가)

| 방법 | TF | PF | OC | SC | Final |
|---|---|---|---|---|---|
| Ours (CDA) | 3 | 4 | 4 | 2 | 3.4 |
| Centralized | 2 | 3 | 2 | 2 | 2.2 |
| Independent | 2 | 1 | 2 | 1 | 1.65 |
| LaMMA-P | 3 | 2 | 2 | 3 | 2.45 |
| SMART-LLM | 4 | 1 | 2 | 4 | 2.7 |

## Track B — GC (ours, LaMMA-P만)

| 방법 | GC |
|---|---|
| Ours (CDA) | 0.0 |
| Centralized | N/A (설계상 제외) |
| Independent | N/A (설계상 제외) |
| LaMMA-P | 0.0 |
| SMART-LLM | N/A (설계상 제외) |

## Object Grounding — 실제 존재하는 물건 사용 여부 (참고용, 점수 미반영)

| 방법 | Grounding Rate | Hallucinated |
|---|---|---|
| Ours (CDA) | 0.7 | container, rug, hazard |
| Centralized | 0.667 | magazine, furniture |
| Independent | 0.429 | counter, appliance, item, corner, book, surface, mobile_light, yoga mat, resistance band, door, trash can, light |
| LaMMA-P | 0.286 | lighter workout equipment, small electronics, lighting, music, timer |
| SMART-LLM | 0.333 | yogamat, dumbbell, light, speaker |