# task2_abstract 통합 평가 결과

## Track A — LLM Judge (5개 방법론 공통, OC=정보제약 준수 여부 엄격 평가)

| 방법 | TF | PF | OC | SC | Final |
|---|---|---|---|---|---|
| Ours (CDA) | 1 | 3 | 7 | 1 | 3.5 |
| Centralized | 4 | 2 | 3 | 2 | 2.95 |
| Independent | 2 | 2 | 2 | 2 | 2.0 |
| LaMMA-P | 8 | 2 | 2 | 6 | 4.4 |
| SMART-LLM | 9 | 2 | 2 | 9 | 5.15 |

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
| Ours (CDA) | 0.588 | bathmat, wastebasket, holder, bathtub, drain, controls, appliance |
| Centralized | 0.667 | bathtub, bathmat, shampoo, shelf |
| Independent | 0.583 | bathtub, tub, bathmat, shampoo, shelf |
| LaMMA-P | 0.5 | bathtub, light switch, music player |
| SMART-LLM | 0.75 | bathtub |