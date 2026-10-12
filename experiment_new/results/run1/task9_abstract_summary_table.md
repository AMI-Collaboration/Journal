# task9_abstract 통합 평가 결과

## Track A — LLM Judge (5개 방법론 공통, OC=정보제약 준수 여부 엄격 평가)

| 방법 | TF | PF | OC | SC | Final |
|---|---|---|---|---|---|
| Ours (CDA) | 3 | 3 | 2 | 2 | 2.5 |
| Centralized | 1 | 2 | 1 | 1 | 1.2 |
| Independent | 3 | 1 | 2 | 3 | 2.25 |
| LaMMA-P | 2 | 2 | 2 | 1 | 1.85 |
| SMART-LLM | 3 | 1 | 1 | 3 | 1.9 |

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
| Ours (CDA) | 0.526 | tray, remote-like device, throw cushion, sheet, mattress, pump bottle, saucer, console table, blanket, media device, bar of soap, tabletop device, hutch, cord, refrigerator, lights, door, table lamp |
| Centralized | 0.688 | decoration, trash can, toothbrush, toothpaste, laundry basket |
| Independent | 0.556 | coffeemaker, stove, door, light, ceilinglight, tv, tablelamp, windowblind |
| LaMMA-P | 0.375 | light switch, light, window, door, item |
| SMART-LLM | 0.455 | livingroomlight, kitchenlight, bathroomlight, livingroomwindow, frontdoor, backdoor |