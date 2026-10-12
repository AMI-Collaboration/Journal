# task3_abstract 통합 평가 결과

## Track A — LLM Judge (5개 방법론 공통, OC=정보제약 준수 여부 엄격 평가)

| 방법 | TF | PF | OC | SC | Final |
|---|---|---|---|---|---|
| Ours (CDA) | 2 | 3 | 7 | 2 | 3.95 |
| Centralized | 3 | 3 | 2 | 3 | 2.65 |
| Independent | 3 | 2 | 2 | 2 | 2.3 |
| LaMMA-P | 4 | 1 | 3 | 4 | 3.05 |
| SMART-LLM | 3 | 1 | 1 | 2 | 1.75 |

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
| Ours (CDA) | 0.31 | bottle, vase, sheet of paper, cup, lid, dish, bowl, monitor, game board, piece, keyboard, writing tool, mouse, device, bottle, item, wastebasket, broom, blanket, bed |
| Centralized | 0.636 | pen, phone, bed, cover |
| Independent | 0.8 | mobile light |
| LaMMA-P | 0.143 | clutter, light, computer, door, camera, microphone |
| SMART-LLM | 0.667 | clutter, window blinds |