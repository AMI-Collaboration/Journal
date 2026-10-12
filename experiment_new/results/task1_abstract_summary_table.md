# task1_abstract 통합 평가 결과

## Track A — LLM Judge (5개 방법론 공통, OC=정보제약 준수 여부 엄격 평가)

| 방법 | TF | PF | OC | SC | Final |
|---|---|---|---|---|---|
| Ours (CDA) | 2 | 4 | 5 | 3 | 3.6 |
| Centralized | 3 | 2 | 2 | 2 | 2.3 |
| Independent | 7 | 2 | 2 | 3 | 3.65 |
| LaMMA-P | 3 | 1 | 1 | 2 | 1.75 |
| SMART-LLM | 4 | 1 | 2 | 2 | 2.4 |

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
| Ours (CDA) | 0.733 | banana, cushion, orange, coffee maker |
| Centralized | 0.562 | fruit, drink, container, keys, wallet, phone, door |
| Independent | 0.867 | couch, tv |
| LaMMA-P | 0.312 | ingredient, sandwich, cereal, utensil, coffeeground, item, workbag, clothing, device, wallet, phone |
| SMART-LLM | 0.438 | countertop, wardrobe, clothes, bed, wallet, phone, door, window, umbrella |