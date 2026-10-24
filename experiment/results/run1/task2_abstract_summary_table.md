# task2_abstract 통합 평가 결과

## Track A — LLM Judge (5개 방법론 공통, OC=정보제약 준수 여부 엄격 평가)

| 방법 | TF | PF | OC | SC | Final |
|---|---|---|---|---|---|
| CDA | - | - | - | - | N/A |
| Centralized | 8 | 9 | 2 | 3 | 5.35 |
| Independent | 4 | 9 | 6 | 3 | 5.55 |
| LaMMA-P | 10 | 10 | 10 | 10 | 10.0 |
| SMART-LLM | 6 | 10 | 10 | 10 | 8.8 |

## Track B — GC (ours, LaMMA-P만)

| 방법 | GC |
|---|---|
| CDA | 0.0 |
| Centralized | N/A (설계상 제외) |
| Independent | N/A (설계상 제외) |
| LaMMA-P | 0.0 |
| SMART-LLM | N/A (설계상 제외) |

## Object Grounding — 실제 존재하는 물건 사용 여부 (참고용, 점수 미반영)

| 방법 | Grounding Rate | Hallucinated |
|---|---|---|
| CDA | N/A | N/A |
| Centralized | 0.429 | shelf, thermostat, bathmat, tub |
| Independent | 0.5 | door, tap, bathtub, rack |
| LaMMA-P | 0.4 | heater, bathtub, rack |
| SMART-LLM | 0.6 | bathtub, heater |