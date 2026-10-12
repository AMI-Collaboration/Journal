# task2_abstract 통합 평가 결과

## Track A — LLM Judge (5개 방법론 공통, OC=정보제약 준수 여부 엄격 평가)

| 방법 | TF | PF | OC | SC | Final |
|---|---|---|---|---|---|
| Ours (CDA) | 2 | 3 | 8 | 2 | 4.3 |
| Centralized | 3 | 2 | 2 | 2 | 2.3 |
| Independent | 2 | 1 | 2 | 1 | 1.65 |
| LaMMA-P | 6 | 2 | 2 | 3 | 3.35 |
| SMART-LLM | 9 | 2 | 2 | 8 | 5.0 |

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
| Ours (CDA) | 0.615 | waste bin, bath mat, holder, container, bathtub |
| Centralized | 0.444 | shelf, bathtub, rack, shampoo, mat |
| Independent | 0.545 | bathtub, tub, bathmat, shampoo, shelf |
| LaMMA-P | 0.667 | bathtub, light switch |
| SMART-LLM | 0.75 | bathtub |