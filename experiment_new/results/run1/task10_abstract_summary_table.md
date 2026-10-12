# task10_abstract 통합 평가 결과

## Track A — LLM Judge (5개 방법론 공통, OC=정보제약 준수 여부 엄격 평가)

| 방법 | TF | PF | OC | SC | Final |
|---|---|---|---|---|---|
| Ours (CDA) | 3 | 9 | 9 | 3 | 6.3 |
| Centralized | 2 | 2 | 2 | 1 | 1.85 |
| Independent | 2 | 2 | 2 | 2 | 2.0 |
| LaMMA-P | 2 | 1 | 2 | 2 | 1.8 |
| SMART-LLM | 4 | 2 | 2 | 2 | 2.6 |

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
| Ours (CDA) | 0.583 | counter, recycling bin, stove, eating utensil, cutting board, saucer, onion, lime, pear, container |
| Centralized | 0.909 | magazine |
| Independent | 0.667 | counter, dishsoap, water, trashcan, item |
| LaMMA-P | 0.25 | item, surface, appliance |
| SMART-LLM | 1.0 | 없음 |