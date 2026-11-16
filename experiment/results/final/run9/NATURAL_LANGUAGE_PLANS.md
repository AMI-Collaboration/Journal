# CDA-1116_SHJ 자연어 플랜 (run9, abstract task2/3/9 × 2/4/6대)

## task2 (마감 5분)

> I want to take a bath in 5 minutes. The bathroom should be ready — bathtub filled with warm water, and I'll need something to dry off with nearby.

### 2대

```
### Joint Plan — task2_abstract  (about 5 min / deadline 5 min: OK)
### Robots: R1:Mobile_Light(bedroom), R2:Mobile_Heavy(bathroom)

[0-5 min]
- R1 [LOCAL] pick up the pillow from the bedroom bed to R1  (r1_s1)
- R2 [LOCAL] put down the hand towel from R2 to the bathroom bathtub  (r2_s3)
- R1 [LOCAL] put down the pillow from R1 to the bedroom bed  (r1_s3)
```

### 4대

```
### Joint Plan — task2_abstract  (about 5 min / deadline 5 min: OK)
### Robots: R1:Gripper(bedroom), R2:Mobile_Light(bedroom), R3:Gripper(bathroom), R4:Mobile_Heavy(bathroom)

[0-5 min]
- R4 [LOCAL] pick up the towel from the bathroom shelf to R4  (r4_s1)
- R4 [LOCAL] put down the towel from R4 to the bathroom bathtub  (r4_s2)
```

### 6대

```
### Joint Plan — task2_abstract  (about 5 min / deadline 5 min: OK)
### Robots: R1:Gripper(bedroom), R2:Mobile_Light(bedroom), R3:Mobile_Light(bedroom), R4:Gripper(bathroom), R5:Mobile_Light(bathroom), R6:Mobile_Heavy(bathroom)

[0-5 min]
- R1 [LOCAL] pick up the pillow from the bed to R1  (r1_s1)
- R2 [LOCAL] pick up the laundry hamper from the bedroom floor to R2  (r2_s1)
- R3 [LOCAL] pick up the laundry hamper from the bedroom floor to R3  (r3_s1)
- R4 [LOCAL] pour the faucet from the bathroom bathtub to the bathroom bathtub  (r4_s1)
- R5 [LOCAL] pick up the towel from the bathroom shelf to R5  (r5_s2)
- R6 [LOCAL] pick up the towel from the bathroom rack to R6  (r6_s1)
- R1 [LOCAL] put down the pillow from R1 to the bed  (r1_s3)
- R2 [LOCAL] move the laundry hamper from R2 to the bathroom  (r2_s2)
- R3 [LOCAL] put down the laundry hamper from R3 to the bedroom floor  (r3_s3)
- R4 [LOCAL] pick up the towel from the bathroom rack to R4  (r4_s2)
- R2 [LOCAL] put down the laundry hamper from R2 to the bathroom floor  (r2_s3)
- R4 [LOCAL] put down the towel from R4 to the bathroom bathtub  (r4_s3)
```

## task3 (마감 10분)

> I have a video call starting in 5 minutes. My desk area needs to look presentable and I should be able to see and hear clearly. The bedroom light is off.

### 2대

```
### Joint Plan — task3_abstract  (about 5 min / deadline 10 min: OK)
### Robots: R1:Mobile_Light(living_room), R2:Mobile_Heavy(bedroom)

[0-5 min]
- R1 [LOCAL] turn on the floor lamp  (r1_s1)
- R2 [LOCAL] turn on the desk lamp  (r2_s1)
- R1 [LOCAL] turn off the television  (r1_s2)
- R2 [LOCAL] move the remote control from the desk to the floor  (r2_s2)
```

### 4대

```
### Joint Plan — task3_abstract  (about 5 min / deadline 10 min: OK)
### Robots: R1:Gripper(living_room), R2:Mobile_Light(living_room), R3:Gripper(bedroom), R4:Mobile_Heavy(bedroom)

[0-5 min]
- R1 [LOCAL] turn on the floor lamp from the living room corner to the living room corner  (r1_s1)
- R3 [LOCAL] turn on the desk lamp from the bedroom desk to the bedroom desk  (r3_s1)
- R4 [LOCAL] move the garbage can from the bedroom floor to the bedroom corner  (r4_s3)
```

### 6대

```
### Joint Plan — task3_abstract  (about 5 min / deadline 10 min: OK)
### Robots: R1:Gripper(living_room), R2:Mobile_Light(living_room), R3:Mobile_Light(living_room), R4:Gripper(bedroom), R5:Mobile_Light(bedroom), R6:Mobile_Heavy(bedroom)

[0-5 min]
- R1 [LOCAL] turn on the floor lamp from the living room sofa  (r1_s1)
- R2 [LOCAL] move the box from the living room table to the living room dresser  (r2_s2)
- R3 [LOCAL] pick up the laptop from the living room sofa to R3  (r3_s2)
- R4 [LOCAL] turn on the desk lamp from the bedroom desk to the bedroom desk  (r4_s1)
- R6 [LOCAL] move the watering can from the bedroom desk to the garbage can  (r6_s3)
- R1 [LOCAL] pick up the box from the living room table to R1  (r1_s2)
- R3 [LOCAL] put down the laptop from R3 to the living room side table  (r3_s3)
- R6 [LOCAL] move the house plant from the bedroom desk to the bedroom floor  (r6_s4)
- R1 [LOCAL] put down the box from R1 to the living room sofa  (r1_s3)
- R3 [LOCAL] pick up the remote control from the living room sofa to R3  (r3_s4)
- R1 [LOCAL] pick up the credit card from the living room table to R1  (r1_s4)
- R3 [LOCAL] put down the remote control from R3 to the living room side table  (r3_s5)
- R1 [LOCAL] put down the credit card from R1 to the living room sofa  (r1_s5)
```

## task9 (마감 15분)

> I'm heading to bed in 15 minutes. The house should be quiet and settled — lights down, things put away, and the bedroom ready to sleep in.

### 2대

```
### Joint Plan — task9_abstract  (about 5 min / deadline 15 min: OK)
### Robots: R1:Mobile_Light(living_room), R2:Mobile_Heavy(bedroom)

[0-5 min]
- R1 [LOCAL] turn off the desk lamp from the living room side table  (r1_s1)
- R2 [LOCAL] pick up the mug from the bedroom side table to R2  (r2_s1)
- R1 [LOCAL] turn off the floor lamp from the living room floor  (r1_s2)
- R2 [LOCAL] put down the mug from R2 to the bedroom desk  (r2_s2)
- R2 [LOCAL] pick up the laptop from the bedroom desk to R2  (r2_s3)
- R2 [LOCAL] put down the laptop from R2 to the bedroom side table  (r2_s4)
```

### 4대

```
### Joint Plan — task9_abstract  (about 10 min / deadline 15 min: OK)
### Robots: R1:Mobile_Light(kitchen), R2:Mobile_Light(living_room), R3:Mobile_Heavy(bedroom), R4:Mobile_Light(bathroom)

[0-5 min]
- R1 [LOCAL] pick up the mug from the kitchen counter  (r1_s1)
- R2 [LOCAL] turn off the floor lamp in the living room  (r2_s1)
- R3 [LOCAL] pick up the laptop from the bedroom desk  (r3_s2)
- R4 [LOCAL] pick up the red soap bar from the bathroom bathtub  (r4_s1)
- R1 [LOCAL] put down the mug on the kitchen shelf  (r1_s2)
- R2 [LOCAL] turn off the desk lamp in the living room  (r2_s2)
- R3 [LOCAL] put down the laptop in the drawer  (r3_s3)
- R4 [LOCAL] put down the red soap bar on the bathroom counter  (r4_s2)
- R1 [LOCAL] pick up the tomato from the kitchen counter  (r1_s3)
- R2 [LOCAL] turn off the television in the living room  (r2_s3)
- R3 [LOCAL] pick up the cell phone from the bedroom desk  (r3_s4)
- R4 [LOCAL] pick up the pink soap bar from the bathroom counter  (r4_s3)
- R1 [LOCAL] put down the tomato in the kitchen pantry  (r1_s4)
- R2 [LOCAL] close the curtains in the living room  (r2_s4)
- R3 [LOCAL] put down the cell phone in the drawer  (r3_s5)
- R4 [LOCAL] put down the pink soap bar on the bathroom counter  (r4_s4)
- R3 [LOCAL] pick up the pencil from the bedroom desk  (r3_s6)
- R4 [LOCAL] pick up the green soap bottle from the bathroom counter  (r4_s5)

[5-10 min]
- R3 [LOCAL] put down the pencil in the drawer  (r3_s7)
- R4 [LOCAL] put down the green soap bottle on the bathroom counter  (r4_s6)
- R3 [LOCAL] pick up the alarm clock from the bedroom desk  (r3_s8)
- R3 [LOCAL] put down the alarm clock in the drawer  (r3_s9)
- R3 [LOCAL] pick up the pillow from the bedroom bed  (r3_s10)
- R3 [LOCAL] put down the pillow on the bed  (r3_s11)
```

### 6대

```
### Joint Plan — task9_abstract  (about 10 min / deadline 15 min: OK)
### Robots: R1:Gripper(kitchen), R2:Mobile_Light(kitchen), R3:Gripper(living_room), R4:Mobile_Light(living_room), R5:Mobile_Heavy(bedroom), R6:Mobile_Heavy(bathroom)

[0-5 min]
- R1 [LOCAL] pick up the red apple from the kitchen counter to R1  (r1_s1)
- R2 [LOCAL] pick up the paper towel roll from the kitchen counter to R2  (r2_s1)
- R3 [LOCAL] pick up the remote control from the sofa to R3  (r3_s1)
- R4 [LOCAL] turn off the Television_1 from the living room cabinet  (r4_s1)
- R5 [LOCAL] turn off the desk lamp from the bedroom desk  (r5_s1)
- R6 [LOCAL] pick up the red soap bar from the bathroom bathtub to R6  (r6_s1)
- R1 [LOCAL] put down the red apple from R1 to the kitchen shelf  (r1_s2)
- R2 [LOCAL] put down the paper towel roll from R2 to the kitchen shelf  (r2_s2)
- R3 [LOCAL] pick up the black laptop from the dining table to R3  (r3_s3)
- R4 [LOCAL] close the Curtains_1 from the living room window  (r4_s2)
- R5 [LOCAL] pick up the basketball from the bedroom floor to R5  (r5_s2)
- R6 [LOCAL] put down the red soap bar from R6 to the bathroom sink  (r6_s2)
- R1 [LOCAL] pick up the brown bread from the kitchen counter to R1  (r1_s3)
- R3 [LOCAL] put down the black laptop from R3 to the shelf  (r3_s4)
- R5 [LOCAL] put down the basketball from R5 to the box  (r5_s3)
- R6 [LOCAL] pick up the green towel from the bathroom wall to R6  (r6_s3)
- R1 [LOCAL] put down the brown bread from R1 to the kitchen shelf  (r1_s4)
- R3 [LOCAL] pick up the gold statue from the dining table to R3  (r3_s5)
- R5 [LOCAL] pick up the pillow from the bedroom bed to R5  (r5_s4)
- R6 [LOCAL] put down the green towel from R6 to the bathroom rack  (r6_s4)
- R1 [LOCAL] pick up the red tomato from the kitchen counter to R1  (r1_s5)
- R3 [LOCAL] put down the gold statue from R3 to the shelf  (r3_s6)
- R5 [LOCAL] put down the pillow from R5 to the bedroom bed  (r5_s5)
- R6 [LOCAL] pick up the shower curtain from the bathroom bathtub to R6  (r6_s5)

[5-10 min]
- R1 [LOCAL] put down the red tomato from R1 to the kitchen shelf  (r1_s6)
- R6 [LOCAL] put down the shower curtain from R6 to the bathroom rail  (r6_s6)
- R1 [LOCAL] pick up the butter knife from the kitchen counter to R1  (r1_s7)
- R6 [LOCAL] pick up the toilet paper from the bathroom toilet to R6  (r6_s7)
- R1 [LOCAL] put down the butter knife from R1 to the kitchen drawer  (r1_s8)
- R6 [LOCAL] put down the toilet paper from R6 to the bathroom holder  (r6_s8)
```

