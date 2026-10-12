# task8_abstract 통합 평가 결과

## Track A — LLM Judge (5개 방법론 공통, OC=정보제약 준수 여부 엄격 평가)

| 방법 | TF | PF | OC | SC | Final |
|---|---|---|---|---|---|
| Ours (CDA) | 3 | 9 | 9 | 3 | 6.3 |
| Centralized | 3 | 2 | 2 | 1 | 2.15 |
| Independent | 1 | 1 | 1 | 1 | 1.0 |
| LaMMA-P | 4 | 2 | 2 | 3 | 2.75 |
| SMART-LLM | 2 | 2 | 2 | 1 | 1.85 |

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
| Ours (CDA) | 0.561 | throw blanket, guitar, storage corner, toothbrush, cardboard piece, floor item, rod-like item, waste bin, bundle, dresser, fabric item, rod, blanket, duvet, mattress, computer, cable, writing utensil |
| Centralized | 0.8 | blanket, trash bin |
| Independent | 0.679 | light, magazine, package, cleaning wipe, solution, curtain, cushion, counter, trash bin |
| LaMMA-P | 0.333 | surface, isolation equipment |
| SMART-LLM | 0.25 | supply, ventilation, sign |