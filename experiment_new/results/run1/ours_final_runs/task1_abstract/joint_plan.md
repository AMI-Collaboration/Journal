### Joint Plan — task1_abstract  (about 20 min / deadline 10 min: MISSED)

[0-5 min]
- R1 [LOCAL] use the Bread to make a sandwich  (r1_s1)
- R2 [LOCAL] pick up the Banana for breakfast  (r2_s1)
- R3 [LOCAL] move the laptop from its current location to the coffee table  (r3_s1)
- R4 [LOCAL] move the cushion to ensure it is neatly placed on the sofa  (r4_s1)
- R1 [LOCAL] fill the Cup with water for a drink  (r1_s3)
- R2 [LOCAL] pick up the Orange for breakfast  (r2_s2)
- R4 [LOCAL] move the vase to ensure it is properly placed on the coffee table  (r4_s2)
- R1 [PASS] pass Cup to R2 (offered) (hands it over; R2 collects it)  (r1_s6)
- R2 [LOCAL] pick up the Bread for breakfast  (r2_s3)
- R4 [LOCAL] move the decorative statue to ensure it is properly placed on the shelf  (r4_s3)
- R2 [RECEIVE] receive Cup from R1 (collects it from the kitchen)  (r2_s8)
- R4 [LOCAL] move the lamp to ensure it is properly placed on the side table  (r4_s4)

[5-10 min]
- R2 [LOCAL] pass the Cup to R1 for pouring coffee  (r2_s9)
- R2 [PASS] pass Banana to R3 (offered) (brings it to the living room)  (r2_s5)
- R2 [PASS] pass Orange to R3 (offered) (brings it to the living room)  (r2_s6)

[10-15 min]
- R2 [PASS] pass Bread to R3 (offered) (brings it to the living room)  (r2_s7)
- R3 [RECEIVE] receive Bread from R2  (r3_s6)
- R3 [LOCAL] move the Bread to the coffee table for a quick breakfast  (r3_s7)
- R3 [RECEIVE] receive Orange from R2  (r3_s4)

[15-20 min]
- R3 [LOCAL] move the Orange to the coffee table for a quick breakfast  (r3_s5)
- R3 [RECEIVE] receive Banana from R2  (r3_s2)
- R3 [LOCAL] move the Banana to the coffee table for a quick breakfast  (r3_s3)

### Dropped
- R2 [ASK_HELP] pour coffee from the Coffee Maker into a cup — withdrawn in Stage 2: ASK_HELP 'pour coffee from the Coffee Maker into a cup' is about your own object. Handoffs go only one way: the robot that needs it writes RECEIVE; you write nothing about it now; ASK_HELP 'pour coffee from the Coffee Maker into a cup' must name in 'enables' the index of one of YOUR OWN later LOCAL steps that needs it (got 6). If none of your steps needs it, remove this request: that part belongs to whoever does it. (by stage2-check)
- R1 [PASS] pass Bread to R2 (Bread) — offer not taken by R2 (by rule)
- R1 [PASS] pass Egg to R2 (Egg) — offer not taken by R2 (by rule)
- R1 [LOCAL] cook the Egg for breakfast — prepared only for r1_s5, an offer R2 did not take (by rule)

### Not covered (from the robots' own checklists)
- R1: Bread: used to make a sandwich
- R2: Coffee Maker: coffee poured into a cup