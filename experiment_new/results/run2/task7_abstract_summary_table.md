# task7_abstract 통합 평가 결과

## Track A — LLM Judge (5개 방법론 공통, OC=정보제약 준수 여부 엄격 평가)

| 방법 | TF | PF | OC | SC | Final |
|---|---|---|---|---|---|
| Ours (CDA) | 1 | 3 | 7 | 2 | 3.65 |
| Centralized | 2 | 2 | 3 | 2 | 2.35 |
| Independent | 2 | 1 | 2 | 2 | 1.8 |
| LaMMA-P | 2 | 1 | 2 | 1 | 1.65 |
| SMART-LLM | 5 | 1 | 2 | 3 | 2.85 |

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
| Ours (CDA) | 0.6 | window, blanket, blind, cart, sheet, door |
| Centralized | 0.857 | cushion |
| Independent | 0.25 | window, light, blind |
| LaMMA-P | 0.0 | window, object, door, appliance |
| SMART-LLM | 0.0 | window, frontdoor, backdoor, sidedoor, vent, skylight |