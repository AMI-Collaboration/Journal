# task7_abstract 통합 평가 결과

## Track A — LLM Judge (5개 방법론 공통, OC=정보제약 준수 여부 엄격 평가)

| 방법 | TF | PF | OC | SC | Final |
|---|---|---|---|---|---|
| Ours (CDA) | 1 | 4 | 9 | 2 | 4.55 |
| Centralized | 2 | 2 | 2 | 2 | 2.0 |
| Independent | 2 | 1 | 2 | 2 | 1.8 |
| LaMMA-P | 2 | 2 | 2 | 2 | 2.0 |
| SMART-LLM | 3 | 1 | 2 | 4 | 2.4 |

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
| Ours (CDA) | 0.474 | window, latch, hanger, cushion, wastebasket, cabinet, object, door, skylight, blanket |
| Centralized | 0.7 | counter, window, door |
| Independent | 0.5 | window, cabinet, blind |
| LaMMA-P | 0.2 | window, door, object, appliance |
| SMART-LLM | 0.0 | window, frontdoor, backdoor, vent, skylight |