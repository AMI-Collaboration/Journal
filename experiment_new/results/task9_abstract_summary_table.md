# task9_abstract 통합 평가 결과

## Track A — LLM Judge (5개 방법론 공통, OC=정보제약 준수 여부 엄격 평가)

| 방법 | TF | PF | OC | SC | Final |
|---|---|---|---|---|---|
| Ours (P2P) | - | - | - | - | N/A |
| Centralized | 4 | 7 | 3 | 5 | 4.4 |
| Independent | 6 | 5 | 3 | 7 | 4.9 |
| LaMMA-P | 4 | 5 | 3 | 4 | 3.85 |
| SMART-LLM | 7 | 8 | 4 | 6 | 6.0 |

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
| Centralized | 0.688 | decoration, trash can, toothbrush, toothpaste, laundry basket |
| Independent | 0.55 | coffeemaker, stove, door, light, ceilinglight, tv, tablelamp, windowblind, bathroomlight |
| LaMMA-P | 0.375 | light switch, light, window, door, item |
| SMART-LLM | 0.455 | livingroomlight, kitchenlight, bathroomlight, livingroomwindow, frontdoor, backdoor |