# task6_abstract 통합 평가 결과

## Track A — LLM Judge (5개 방법론 공통, OC=정보제약 준수 여부 엄격 평가)

| 방법 | TF | PF | OC | SC | Final |
|---|---|---|---|---|---|
| Ours (P2P) | 4 | 7 | 5 | 3 | 4.8 |
| Centralized | 5 | 8 | 4 | 6 | 5.4 |
| Independent | 3 | 5 | 2 | 4 | 3.2 |
| LaMMA-P | 7 | 8 | 5 | 6 | 6.35 |
| SMART-LLM | 6 | 7 | 4 | 5 | 5.35 |

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
| Ours (P2P) | 0.625 | trash bin, keys, magazine |
| Centralized | 0.667 | object, furniture |
| Independent | 0.7 | counter, light, bath mat |
| LaMMA-P | 0.667 | item, fan, light |
| SMART-LLM | 0.938 | light |