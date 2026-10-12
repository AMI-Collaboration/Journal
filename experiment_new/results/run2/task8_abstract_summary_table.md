# task8_abstract 통합 평가 결과

## Track A — LLM Judge (5개 방법론 공통, OC=정보제약 준수 여부 엄격 평가)

| 방법 | TF | PF | OC | SC | Final |
|---|---|---|---|---|---|
| Ours (CDA) | 2 | 7 | 8 | 3 | 5.25 |
| Centralized | 2 | 2 | 2 | 2 | 2.0 |
| Independent | 2 | 2 | 2 | 2 | 2.0 |
| LaMMA-P | 2 | 1 | 2 | 2 | 1.8 |
| SMART-LLM | 4 | 1 | 2 | 1 | 2.25 |

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
| Ours (CDA) | 0.632 | item, dresser, sheet, mattress, blanket, nightstand, handle |
| Centralized | 0.636 | blanket, medical supply, tape, container |
| Independent | 0.647 | counter, light, tv, curtain, cushion, trash bin |
| LaMMA-P | 0.0 | cleaning supply, furniture, supply |
| SMART-LLM | 0.222 | mask, glove, hand sanitizer, waste bag, linen, ventilation system, communication device |