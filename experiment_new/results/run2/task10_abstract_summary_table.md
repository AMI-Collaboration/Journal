# task10_abstract 통합 평가 결과

## Track A — LLM Judge (5개 방법론 공통, OC=정보제약 준수 여부 엄격 평가)

| 방법 | TF | PF | OC | SC | Final |
|---|---|---|---|---|---|
| Ours (CDA) | 3 | 2 | 2 | 3 | 2.45 |
| Centralized | 2 | 2 | 2 | 1 | 1.85 |
| Independent | 2 | 1 | 1 | 1 | 1.3 |
| LaMMA-P | 3 | 2 | 3 | 2 | 2.65 |
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
| Ours (CDA) | 0.696 | saucer, utensil, onion, lime, cucumber, fruit, jar |
| Centralized | 0.909 | utensil |
| Independent | 0.722 | counter, dishsoap, trashcan, magazine, item |
| LaMMA-P | 0.0 | item |
| SMART-LLM | 0.714 | countertop, item |