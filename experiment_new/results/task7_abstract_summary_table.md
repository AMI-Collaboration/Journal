# task7_abstract 통합 평가 결과

## Track A — LLM Judge (5개 방법론 공통, OC=정보제약 준수 여부 엄격 평가)

| 방법 | TF | PF | OC | SC | Final |
|---|---|---|---|---|---|
| Ours (P2P) | - | - | - | - | N/A |
| Centralized | 3 | 5 | 4 | 4 | 3.9 |
| Independent | 5 | 4 | 3 | 6 | 4.25 |
| LaMMA-P | 6 | 8 | 5 | 7 | 6.2 |
| SMART-LLM | 5 | 8 | 4 | 6 | 5.4 |

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
| Centralized | 0.5 | object, metal rack, trash bin |
| Independent | 0.5 | window, dishwasher, window blind, light |
| LaMMA-P | 0.0 | window, loose object, light object, door, heavy object |
| SMART-LLM | 0.0 | window, door |