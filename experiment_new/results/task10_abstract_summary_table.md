# task10_abstract 통합 평가 결과

## Track A — LLM Judge (5개 방법론 공통, OC=정보제약 준수 여부 엄격 평가)

| 방법 | TF | PF | OC | SC | Final |
|---|---|---|---|---|---|
| Ours (P2P) | - | - | - | - | N/A |
| Centralized | 7 | 9 | 5 | 8 | 6.85 |
| Independent | 5 | 8 | 4 | 6 | 5.4 |
| LaMMA-P | 5 | 7 | 4 | 6 | 5.2 |
| SMART-LLM | 6 | 9 | 4 | 7 | 6.05 |

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
| Centralized | 0.833 | counter |
| Independent | 1.0 | 없음 |
| LaMMA-P | 1.0 | 없음 |
| SMART-LLM | 0.8 | countertop |