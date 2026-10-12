# task3_abstract 통합 평가 결과

## Track A — LLM Judge (5개 방법론 공통, OC=정보제약 준수 여부 엄격 평가)

| 방법 | TF | PF | OC | SC | Final |
|---|---|---|---|---|---|
| Ours (CDA) | 2 | 8 | 1 | 4 | 3.15 |
| Centralized | 3 | 2 | 2 | 3 | 2.45 |
| Independent | 3 | 2 | 2 | 2 | 2.3 |
| LaMMA-P | 7 | 1 | 2 | 2 | 3.3 |
| SMART-LLM | 2 | 2 | 3 | 2 | 2.35 |

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
| Ours (CDA) | 0.333 | wastebasket, cup, sheet of paper, bowl, plate, monitor, tablet, checkerboard, writing implement, pen, keyboard, computer mouse, marker, usb-sized object, paper, eraser, device, broom, sheet, blanket |
| Centralized | 0.538 | vase, pen, phone, bed, cover, trash bin |
| Independent | 0.667 | mobile light, item |
| LaMMA-P | 0.111 | clutter, storage, light switch, light, computer, door, camera, microphone |
| SMART-LLM | 0.2 | workspace, lighting, internet connection, material |