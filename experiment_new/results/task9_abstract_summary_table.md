# task9_abstract 통합 평가 결과

## Track A — LLM Judge (5개 방법론 공통, OC=정보제약 준수 여부 엄격 평가)

| 방법 | TF | PF | OC | SC | Final |
|---|---|---|---|---|---|
| Ours (P2P) | - | - | - | - | N/A |
| Centralized | 5 | 7 | 4 | 6 | 5.2 |
| Independent | 6 | 5 | 8 | 7 | 6.65 |
| LaMMA-P | 5 | 8 | 4 | 6 | 5.4 |
| SMART-LLM | 5 | 6 | 3 | 4 | 4.35 |

## Track B — GC (ours, LaMMA-P만)

| 방법 | GC |
|---|---|
| Ours (P2P) | 0.0 |
| Centralized | N/A (설계상 제외) |
| Independent | N/A (설계상 제외) |
| LaMMA-P | 0.0 |
| SMART-LLM | N/A (설계상 제외) |

## Object Grounding — 실제 존재하는 물건 사용 여부 (참고용, 점수 미반영)

| 방법 | Grounding Rate | Hallucinated |
|---|---|---|
| Ours (P2P) | N/A | N/A |
| Centralized | 0.909 | door |
| Independent | 0.5 | coffeemaker, stove, light, ceiling light, window blind |
| LaMMA-P | 0.25 | light, door, thermostat |
| SMART-LLM | 0.583 | livingroomlight, kitchenlight, livingroomwindow, frontdoor, backdoor |