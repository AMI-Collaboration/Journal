# task8_abstract 통합 평가 결과

## Track A — LLM Judge (5개 방법론 공통, OC=정보제약 준수 여부 엄격 평가)

| 방법 | TF | PF | OC | SC | Final |
|---|---|---|---|---|---|
| Ours (P2P) | - | - | - | - | N/A |
| Centralized | 3 | 6 | 4 | 4 | 4.1 |
| Independent | 4 | 6 | 7 | 5 | 5.6 |
| LaMMA-P | 4 | 5 | 3 | 6 | 4.15 |
| SMART-LLM | 8 | 9 | 5 | 9 | 7.3 |

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
| Centralized | 1.0 | 없음 |
| Independent | 0.538 | countertop, appliance, mobile light, couch, blanket, trash bin |
| LaMMA-P | 0.333 | cleaning supply, medical equipment |
| SMART-LLM | 0.0 | cleaning supply, medical supply, ventilation control, isolation signage, ventilation system |