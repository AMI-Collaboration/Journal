# task5_abstract 통합 평가 결과

## Track A — LLM Judge (5개 방법론 공통, OC=정보제약 준수 여부 엄격 평가)

| 방법 | TF | PF | OC | SC | Final |
|---|---|---|---|---|---|
| Ours (CDA) | 8 | 7 | 4 | 5 | 5.95 |
| Centralized | 4 | 2 | 3 | 2 | 2.95 |
| Independent | 3 | 1 | 2 | 2 | 2.1 |
| LaMMA-P | 5 | 1 | 1 | 4 | 2.65 |
| SMART-LLM | 3 | 1 | 2 | 2 | 2.1 |

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
| Ours (CDA) | 0.818 | cushion, blanket |
| Centralized | 0.5 | drink, snack, blanket, item, trashbin, door, furniture |
| Independent | 0.35 | coffeemaker, lemon, glass, appliance, tv, seating area, lighting, coffeetable, mobile light, window, computer, trash bin, bathroom light |
| LaMMA-P | 0.375 | snack, seating, sound system, light switch, light |
| SMART-LLM | 0.75 | popcorn, drink |