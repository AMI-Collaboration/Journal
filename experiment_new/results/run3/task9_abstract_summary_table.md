# task9_abstract 통합 평가 결과

## Track A — LLM Judge (5개 방법론 공통, OC=정보제약 준수 여부 엄격 평가)

| 방법 | TF | PF | OC | SC | Final |
|---|---|---|---|---|---|
| Ours (CDA) | 3 | 5 | 9 | 3 | 5.5 |
| Centralized | 2 | 4 | 2 | 2 | 2.4 |
| Independent | 5 | 1 | 5 | 3 | 3.9 |
| LaMMA-P | 2 | 1 | 1 | 2 | 1.45 |
| SMART-LLM | 2 | 1 | 1 | 2 | 1.45 |

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
| Ours (CDA) | 0.712 | white dish-like object, checkered sheet, mattress, coffee-maker carafe, black coffee maker, blue blanket, striped cushion, wooden nightstand, yellow-and-green sponge, pink bar of soap, toothbrush holder, toothbrushes, round black clock, stove, oven |
| Centralized | 0.8 | trash can, item |
| Independent | 0.625 | stove, coffeemaker, light, ceilinglight, overheadlight, windowblind |
| LaMMA-P | 0.556 | lightswitch, window, door, alarmsystem |
| SMART-LLM | 0.3 | livingroomlight, kitchenlight, hallwaylight, livingroomcurtain, livingroomwindow, frontdoor, backdoor |