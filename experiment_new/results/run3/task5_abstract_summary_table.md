# task5_abstract 통합 평가 결과

## Track A — LLM Judge (5개 방법론 공통, OC=정보제약 준수 여부 엄격 평가)

| 방법 | TF | PF | OC | SC | Final |
|---|---|---|---|---|---|
| Ours (CDA) | 4 | 5 | 7 | 3 | 5.1 |
| Centralized | 2 | 2 | 2 | 2 | 2.0 |
| Independent | 2 | 1 | 5 | 2 | 2.85 |
| LaMMA-P | 3 | 1 | 2 | 3 | 2.25 |
| SMART-LLM | 7 | 1 | 2 | 4 | 3.6 |

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
| Ours (CDA) | 0.636 | cushion, blanket, media console, pear |
| Centralized | 0.455 | item, coffeetable, cushion, blanket, light switch, furniture |
| Independent | 0.4 | coffeemaker, lemon, glass, appliance, tv, seating area, coffeetable, light, sound system, mobile light, window, bathroom light |
| LaMMA-P | 0.4 | tv, device, drink, light, blanket, temperature |
| SMART-LLM | 0.4 | streaming device, popcorn, soda, coffeetable, light switch, light |