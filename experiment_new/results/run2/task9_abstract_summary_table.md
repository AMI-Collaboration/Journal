# task9_abstract 통합 평가 결과

## Track A — LLM Judge (5개 방법론 공통, OC=정보제약 준수 여부 엄격 평가)

| 방법 | TF | PF | OC | SC | Final |
|---|---|---|---|---|---|
| Ours (CDA) | 4 | 7 | 2 | 3 | 3.75 |
| Centralized | 2 | 2 | 2 | 2 | 2.0 |
| Independent | 4 | 2 | 2 | 3 | 2.75 |
| LaMMA-P | 3 | 1 | 2 | 2 | 2.1 |
| SMART-LLM | 4 | 1 | 1 | 3 | 2.2 |

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
| Ours (CDA) | 0.655 | tray, cushion, hutch, item, holder, wastebasket, organizer, rack, sheet, blanket |
| Centralized | 0.667 | pitcher, glass, blanket, trash can, toothbrush |
| Independent | 0.611 | coffeemaker, stove, kitchen light, ceiling light, overhead light, window blind, bathroom light |
| LaMMA-P | 0.571 | lightswitch, door, window |
| SMART-LLM | 0.667 | light, door |