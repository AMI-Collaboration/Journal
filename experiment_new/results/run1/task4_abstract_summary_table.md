# task4_abstract 통합 평가 결과

## Track A — LLM Judge (5개 방법론 공통, OC=정보제약 준수 여부 엄격 평가)

| 방법 | TF | PF | OC | SC | Final |
|---|---|---|---|---|---|
| Ours (CDA) | 7 | 9 | 9 | 5 | 7.8 |
| Centralized | 2 | 2 | 2 | 2 | 2.0 |
| Independent | 3 | 1 | 5 | 2 | 3.15 |
| LaMMA-P | 2 | 1 | 2 | 1 | 1.65 |
| SMART-LLM | 2 | 1 | 2 | 1 | 1.65 |

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
| Ours (CDA) | 0.783 | utensil, teddy bear, object, item, cushion |
| Centralized | 0.7 | item, trashbin, furniture |
| Independent | 0.733 | mobile light, bed, blanket, countertop |
| LaMMA-P | 0.4 | clutter, item, dishwasher, surface, countertop, bed, cutlery, glass, light |
| SMART-LLM | 0.9 | lightswitch |