# task10_abstract 통합 평가 결과

## Track A — LLM Judge (5개 방법론 공통, OC=정보제약 준수 여부 엄격 평가)

| 방법 | TF | PF | OC | SC | Final |
|---|---|---|---|---|---|
| Ours (CDA) | 2 | 4 | 8 | 2 | 4.5 |
| Centralized | 2 | 2 | 2 | 2 | 2.0 |
| Independent | 3 | 2 | 2 | 2 | 2.3 |
| LaMMA-P | 2 | 2 | 2 | 2 | 2.0 |
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
| Ours (CDA) | 0.579 | saucer, utensil, cookware, loaf, board, fruit, napkin, item |
| Centralized | 1.0 | 없음 |
| Independent | 0.647 | counter, dishsoap, trashcan, recyclingbin, toothbrush, holder |
| LaMMA-P | 0.4 | item, countertop, appliance |
| SMART-LLM | 0.6 | countertop, item |