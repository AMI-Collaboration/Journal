# task1_abstract 통합 평가 결과

## Track A — LLM Judge (5개 방법론 공통, OC=정보제약 준수 여부 엄격 평가)

| 방법 | TF | PF | OC | SC | Final |
|---|---|---|---|---|---|
| Ours (P2P) | - | - | - | - | N/A |
| Centralized | 3 | 7 | 4 | 5 | 4.45 |
| Independent | 4 | 7 | 5 | 6 | 5.25 |
| LaMMA-P | 4 | 3 | 5 | 4 | 4.15 |
| SMART-LLM | 6 | 8 | 4 | 7 | 5.85 |

## Track B — GC (ours, LaMMA-P만)

| 방법 | GC |
|---|---|
| Ours (P2P) | 0.0 |
| Centralized | N/A (설계상 제외) |
| Independent | N/A (설계상 제외) |
| LaMMA-P | 0.0 |
| SMART-LLM | N/A (설계상 제외) |

## Object Grounding — 실제 존재하는 물건 사용 여부 (참고용, 점수 미반영)

| 방법 | Grounding Rate | Hallucinated |
|---|---|---|
| Ours (P2P) | N/A | N/A |
| Centralized | 0.538 | container, door, fruit, jug, glass, couch |
| Independent | 0.875 | tv |
| LaMMA-P | 0.286 | outfit, clothes, essential, lunch, device |
| SMART-LLM | 0.571 | closet, clothes, bed, wallet, phone, door |