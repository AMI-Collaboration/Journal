# task8_abstract 통합 평가 결과

## Track A — LLM Judge (5개 방법론 공통, OC=정보제약 준수 여부 엄격 평가)

| 방법 | TF | PF | OC | SC | Final |
|---|---|---|---|---|---|
| Ours (CDA) | 2 | 9 | 8 | 3 | 5.65 |
| Centralized | 2 | 3 | 2 | 2 | 2.2 |
| Independent | 1 | 1 | 1 | 1 | 1.0 |
| LaMMA-P | 2 | 1 | 3 | 3 | 2.3 |
| SMART-LLM | 4 | 2 | 3 | 2 | 2.95 |

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
| Ours (CDA) | 0.591 | pump bottle, guitar, floor item, fabric item, mattress, sheet, blanket, garment, waste bin |
| Centralized | 0.706 | blanket, medical supply, tape, container, trash bin |
| Independent | 0.654 | light, fan, air conditioning, magazine, fruit, tv, curtain, counter, trash bin |
| LaMMA-P | 0.0 | cleaning supply, medical supply, air purifier, room door |
| SMART-LLM | 0.2 | ventilation, medicalsupply, linen, communicationdevice |