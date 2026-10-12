# task4_abstract 통합 평가 결과

## Track A — LLM Judge (5개 방법론 공통, OC=정보제약 준수 여부 엄격 평가)

| 방법 | TF | PF | OC | SC | Final |
|---|---|---|---|---|---|
| Ours (CDA) | 9 | 9 | 10 | 9 | 9.35 |
| Centralized | 2 | 3 | 2 | 1 | 2.05 |
| Independent | 3 | 1 | 3 | 3 | 2.6 |
| LaMMA-P | 3 | 1 | 2 | 2 | 2.1 |
| SMART-LLM | 1 | 1 | 1 | 1 | 1.0 |

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
| Ours (CDA) | 0.629 | cushion, bedding, duvet, bed, vanity, vase, item, wastebasket, fabric, hamper, laundry hamper, teddy bear, decorative object |
| Centralized | 0.7 | item, trashcan, trashbin |
| Independent | 0.857 | bed, countertop |
| LaMMA-P | 0.353 | light switch, clutter, dirty dish, cutlery, napkin, light, dishwasher, drink, snack, surface, countertop |
| SMART-LLM | 0.0 | surface, refreshment, lighting |