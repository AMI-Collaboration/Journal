# task4_abstract 통합 평가 결과

## Track A — LLM Judge (5개 방법론 공통, OC=정보제약 준수 여부 엄격 평가)

| 방법 | TF | PF | OC | SC | Final |
|---|---|---|---|---|---|
| Ours (CDA) | 4 | 9 | 8 | 3 | 6.25 |
| Centralized | 3 | 2 | 2 | 2 | 2.3 |
| Independent | 4 | 2 | 2 | 4 | 2.9 |
| LaMMA-P | 3 | 1 | 1 | 1 | 1.6 |
| SMART-LLM | 2 | 1 | 2 | 2 | 1.8 |

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
| Ours (CDA) | 0.543 | bedcover, mattress, item, slipper, waste bin, hamper, cutting board, utensil, book, notebook, container, tray, cookware lid, table lamp, alarm clock, coffeemaker |
| Centralized | 0.667 | snack, item, trashbin |
| Independent | 0.786 | countertop, bed, sheet |
| LaMMA-P | 0.294 | clutter, item, cutlery, glass, light switch, thermostat, beverage, dishwasher, tray, surface, countertop, bed |
| SMART-LLM | 0.0 | light, refreshment, temperature |