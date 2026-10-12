# task3_abstract 통합 평가 결과

## Track A — LLM Judge (5개 방법론 공통, OC=정보제약 준수 여부 엄격 평가)

| 방법 | TF | PF | OC | SC | Final |
|---|---|---|---|---|---|
| Ours (CDA) | 2 | 2 | 2 | 2 | 2.0 |
| Centralized | 3 | 2 | 2 | 2 | 2.3 |
| Independent | 4 | 3 | 2 | 2 | 2.8 |
| LaMMA-P | 2 | 1 | 2 | 3 | 1.95 |
| SMART-LLM | 2 | 1 | 1 | 2 | 1.45 |

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
| Ours (CDA) | 0.323 | table lamp, bowl, tray, device, sheet of paper, dining table, marker, pen, pad, monitor, smartphone, cup, chessboard, wastebasket, potted plant, baseball bat, stick, bed, broom, bedding, blanket |
| Centralized | 0.538 | item, couch, pen, phone, bed, window |
| Independent | 0.714 | mobile light, pen |
| LaMMA-P | 0.0 | clutter, light, computer, door, window, camera, microphone |
| SMART-LLM | 0.667 | clutter, window |