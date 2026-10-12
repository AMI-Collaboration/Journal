# task7_abstract 통합 평가 결과

## Track A — LLM Judge (5개 방법론 공통, OC=정보제약 준수 여부 엄격 평가)

| 방법 | TF | PF | OC | SC | Final |
|---|---|---|---|---|---|
| Ours (CDA) | 1 | 5 | 7 | 1 | 3.9 |
| Centralized | 1 | 3 | 2 | 2 | 1.9 |
| Independent | 1 | 1 | 1 | 2 | 1.15 |
| LaMMA-P | 2 | 1 | 2 | 2 | 1.8 |
| SMART-LLM | 5 | 2 | 1 | 3 | 2.7 |

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
| Ours (CDA) | 0.5 | window, latch, metal rolling storage cart, window blind, range-exhaust damper, kitchen vent, door, metal tray, drying rack, clear plastic ruler, strip, small red object, console table |
| Centralized | 0.667 | counter, window, door |
| Independent | 0.25 | window, cabinet door, window blind |
| LaMMA-P | 0.0 | window, door, object, appliance |
| SMART-LLM | 0.0 | window, frontdoor, backdoor, sidedoor, vent, skylight |