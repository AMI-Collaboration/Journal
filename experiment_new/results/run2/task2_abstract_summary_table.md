# task2_abstract 통합 평가 결과

## Track A — LLM Judge (5개 방법론 공통, OC=정보제약 준수 여부 엄격 평가)

| 방법 | TF | PF | OC | SC | Final |
|---|---|---|---|---|---|
| Ours (CDA) | 1 | 3 | 8 | 2 | 4.0 |
| Centralized | 3 | 3 | 2 | 2 | 2.5 |
| Independent | 2 | 2 | 2 | 1 | 1.85 |
| LaMMA-P | 3 | 1 | 2 | 2 | 2.1 |
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
| Ours (CDA) | 0.529 | bathtub, wastebasket, pedal waste bin, bath mat, holder, bar of soap, pump bottle, bathtub drain |
| Centralized | 0.583 | bathtub, shampoo, door, shelf, bathmat |
| Independent | 0.556 | tub, bath mat, shampoo, shelf |
| LaMMA-P | 0.444 | mirror, floor, bathtub, shampoo, conditioner |
| SMART-LLM | 0.5 | bathtub, shampoo, light switch |