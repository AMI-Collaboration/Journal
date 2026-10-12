# task1_abstract 통합 평가 결과

## Track A — LLM Judge (5개 방법론 공통, OC=정보제약 준수 여부 엄격 평가)

| 방법 | TF | PF | OC | SC | Final |
|---|---|---|---|---|---|
| Ours (CDA) | 4 | 7 | 9 | 3 | 6.2 |
| Centralized | 3 | 2 | 2 | 2 | 2.3 |
| Independent | 3 | 2 | 3 | 2 | 2.65 |
| LaMMA-P | 3 | 1 | 2 | 2 | 2.1 |
| SMART-LLM | 1 | 1 | 1 | 1 | 1.0 |

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
| Ours (CDA) | 0.625 | object, appliance, glass |
| Centralized | 0.571 | fruit, drink, pitcher, glass, phone, furniture |
| Independent | 0.917 | tv |
| LaMMA-P | 0.312 | item, container, appliance, wardrobe, clothes, charger, document, toothbrush, towel, device, door |
| SMART-LLM | 1.0 | 없음 |