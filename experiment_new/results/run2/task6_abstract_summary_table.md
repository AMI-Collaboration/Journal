# task6_abstract 통합 평가 결과

## Track A — LLM Judge (5개 방법론 공통, OC=정보제약 준수 여부 엄격 평가)

| 방법 | TF | PF | OC | SC | Final |
|---|---|---|---|---|---|
| Ours (CDA) | 5 | 9 | 8 | 8 | 7.3 |
| Centralized | 2 | 3 | 2 | 2 | 2.2 |
| Independent | 2 | 1 | 4 | 2 | 2.5 |
| LaMMA-P | 2 | 3 | 2 | 2 | 2.2 |
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
| Ours (CDA) | 0.75 | drinking glass, pitcher, napkin |
| Centralized | 0.5 | item, notebook, teddy bear, book, furniture |
| Independent | 0.5 | counter, appliance, item, dumbbell, bed, tennis racket, book, trash can, light |
| LaMMA-P | 0.333 | object, workout equipment |
| SMART-LLM | 0.636 | yogamat, dumbbell, resistanceband, lighting |