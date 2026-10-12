### Joint Plan — task10_abstract  (about 20 min / deadline 15 min: MISSED)

[0-5 min]
- R1 [LOCAL] White mug beside the stove: move it from beside the stove to the sink wash queue  (r1_s1)
- R2 [LOCAL] move the Stacked white dishes to the sink area for washing  (r2_s1)
- R5 [LOCAL] pick up the Gray translucent bowl from the bedroom desk  (r5_s1)
- R6 [LOCAL] pick up the Clear bowl in the bedroom for return to the kitchen  (r6_s1)
- R1 [LOCAL] White plate in the sink area: move it into the sink wash queue  (r1_s2)
- R2 [LOCAL] move the Orange mug to the sink area for washing  (r2_s2)
- R5 [PASS] pass Gray translucent bowl to R6 (offered) (hands it over; R6 collects it)  (r5_s2)
- R6 [PASS] pass Clear bowl to R2 (offered) (brings it to the kitchen)  (r6_s2)
- R1 [LOCAL] move the White cup from the counter to the sink wash queue  (r1_s3)
- R2 [LOCAL] move the Black cooking pot to the sink area for washing  (r2_s3)
- R6 [LOCAL] pick up the White cup or mug in the bedroom for return to the kitchen  (r6_s3)
- R1 [LOCAL] move the White saucer from the counter to the sink wash queue  (r1_s4)
- R1 [LOCAL] White plates on the island (top plate): move it from the island to the sink wash queue  (r1_s5)

[5-10 min]
- R2 [LOCAL] move the Frying pan to the sink area for washing  (r2_s4)
- R6 [PASS] pass White cup or mug to R2 (offered) (brings it to the kitchen)  (r6_s4)
- R2 [LOCAL] place the Blue sponge beside the sink for dishwashing  (r2_s5)
- R6 [RECEIVE] receive Gray translucent bowl from R5 (collects it from the bedroom)  (r6_s5)
- R1 [LOCAL] White plates on the island (bottom plate): move it from the island to the sink wash queue  (r1_s6)
- R2 [LOCAL] place the White dish towel beside the dishwashing area for drying  (r2_s6)
- R6 [LOCAL] move Gray translucent bowl from the bedroom to the kitchen  (r6_s6)
- R1 [LOCAL] Utensil beside the island plates: move it from beside the island plates to the sink wash queue  (r1_s7)
- R2 [RECEIVE] receive Clear bowl (one bowl returned from the bedroom) from R6  (r2_s9)
- R1 [LOCAL] Knife on the counter: move it from the counter to the sink wash queue  (r1_s8)
- R1 [LOCAL] move the Onion from the counter to nearby produce storage  (r1_s13)
- R1 [LOCAL] move the Green apple from the counter to nearby produce storage  (r1_s14)

[10-15 min]
- R2 [LOCAL] move the Clear bowl to the sink area for washing  (r2_s10)
- R2 [RECEIVE] receive White cup or mug (one cup or mug returned from the bedroom) from R6  (r2_s11)
- R2 [LOCAL] move the White cup or mug to the sink area for washing  (r2_s12)
- R1 [LOCAL] move the Lime from the counter to nearby produce storage  (r1_s15)
- R2 [LOCAL] move the Bread loaf into appropriate kitchen food storage  (r2_s13)
- R1 [LOCAL] move the Cucumber or zucchini from the counter to nearby produce storage  (r1_s16)
- R2 [LOCAL] move the Green fruit to the stored fruit area  (r2_s14)
- R1 [LOCAL] move the Cardboard box from the counter to the kitchen recycling area  (r1_s18)
- R1 [LOCAL] move the Two seasoning shakers (first shaker) from the counter to nearby seasoning storage  (r1_s19)

[15-20 min]
- R2 [LOCAL] move the Green bottle or jar into appropriate kitchen storage  (r2_s15)
- R1 [LOCAL] move the Two seasoning shakers (second shaker) from the counter to nearby seasoning storage  (r1_s20)
- R1 [LOCAL] move the Green spray bottle from the counter to nearby cleaning-supply storage  (r1_s21)

### Warnings
- {'issue': 'DUPLICATE_WORK kept', 'nodes': ['r1_s1', 'r2_s12'], 'why': 'not duplicate'}
- {'issue': 'DUPLICATE_WORK kept', 'nodes': ['r1_s3', 'r2_s12'], 'why': 'not duplicate'}
- {'issue': 'DUPLICATE_WORK kept', 'nodes': ['r5_s1', 'r6_s6'], 'why': 'not duplicate'}

### Dropped
- R1 [LOCAL] move the received Clear bowl to the sink wash queue — graph: Duplicate Clear bowl transfer; this copy cannot run, while r2_s10 can run using the confirmed delivery. (by graph)
- R1 [RECEIVE] receive Clear bowl (one bowl returned from the bedroom) (Clear bowl) — withdrawn: the step it enabled (r1_s10) was released (by graph)
- R1 [LOCAL] move the received White cup or mug to the sink wash queue — graph: Duplicate White cup or mug transfer; this copy cannot run, while r2_s12 can run using the confirmed delivery. (by graph)
- R1 [RECEIVE] receive White cup or mug (one cup or mug returned from the bedroom) (White cup or mug) — withdrawn: the step it enabled (r1_s12) was released (by graph)
- R1 [LOCAL] move the Loaf of bread from the counter to nearby bread storage — graph: Same bread loaf and storage destination; keep r2_s13 on the robot with the shorter plan. (by graph)
- R2 [LOCAL] move the Gray translucent bowl to the sink area for washing — redundant: r2_s10 (R2) does the same work and can run (by rule)
- R2 [RECEIVE] receive Gray translucent bowl (one bowl returned from the bedroom) (Gray translucent bowl) — withdrawn: the step it enabled (r2_s8) was released (by rule)

### Not covered (from the robots' own checklists)
- R1: White mug beside the stove: moved from beside the stove to the sink wash queue
- R1: White plate in the sink area: staged in the sink wash queue
- R1: White plates on the island (top plate): moved from the island to the sink wash queue
- R1: White plates on the island (bottom plate): moved from the island to the sink wash queue
- R1: Knife on the counter: moved from the counter to the sink wash queue