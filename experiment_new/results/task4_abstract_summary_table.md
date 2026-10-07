# task4_abstract 통합 평가 결과

## Track A — LLM Judge (5개 방법론 공통, OC=정보제약 준수 여부 엄격 평가)

| 방법 | TF | PF | OC | SC | Final |
|---|---|---|---|---|---|
| Ours (P2P) | - | - | - | - | N/A |
| Centralized | 5 | 8 | 6 | 7 | 6.25 |
| Independent | 4 | 3 | 5 | 4 | 4.15 |
| LaMMA-P | 5 | 6 | 3 | 4 | 4.35 |
| SMART-LLM | 5 | 6 | 3 | 4 | 4.35 |

## Track B — GC (ours, LaMMA-P만)

| 방법 | GC |
|---|---|
| Ours (P2P) | 0.0 |
| Centralized | N/A (설계상 제외) |
| Independent | N/A (설계상 제외) |
| LaMMA-P | 0.0 |
| SMART-LLM | N/A (설계상 제외) |

## Object Grounding — 실제 존재하는 물건 사용 여부 (참고용, 점수 미반영)

| 방법 | Grounding Rate | Hallucinated |
|---|---|---|
| Ours (P2P) | N/A | N/A |
| Centralized | 0.533 | snack, drink, bed, blanket, teddy bear, counter, trash can |
| Independent | 0.714 | bed, trash can |
| LaMMA-P | 0.429 | surface, item, light, music |
| SMART-LLM | 0.417 | clutter, cushion, light, storage, snack, drink, countertop |