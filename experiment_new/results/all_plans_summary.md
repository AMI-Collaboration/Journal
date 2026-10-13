# 전체 Joint Plan 모음 (task1-10 x run1-3 x 5개 방법론, 플랜 본문만)

# task1_abstract

> I woke up late and need to leave for work in 10 minutes. Get everything ready for me.

## Run 1

### Ours (CDA) (TF=2 PF=4 OC=5 SC=3 Final=3.6)

```
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
```

### Centralized (TF=3 PF=2 OC=2 SC=2 Final=2.3)

```
[0-2 min]
- R1 Slice bread (r1_s1)

[2-4 min]
- R1 Slice tomato (r1_s2)

[4-6 min]
- R1 Pour water into cup (r1_s3)

[6-8 min]
- R1 Place sliced bread and tomato on plate (r1_s4)

[8-10 min]
- R1 Pass plate and cup to user (r1_s5)

[0-2 min]
- R2 navigate to the counter and pick up the apple. (r2_s1)

[2-4 min]
- R2 navigate to the dining table and place the apple. (r2_s2)

[4-6 min]
- R2 navigate back to the counter and pick up the cup. (r2_s3)

[6-8 min]
- R2 navigate to the dining table and place the cup. (r2_s4)

[8-10 min]
- R2 navigate back to the counter and pick up the spoon. (r2_s5)

[10-12 min]
- R2 navigate to the dining table and place the spoon. (r2_s6)

[Step 1]
- R3 PickupLightObject (r3_s1): Pick up the newspaper from the couch.

[Step 2]
- R3 SliceObject (r3_s2): Slice any fruit available on the table.

[Step 3]
- R3 PourObject (r3_s3): Pour a drink from any available container on the table.

[Step 4]
- R3 PassReceiveObject (r3_s4): Pass the newspaper and prepared items to another robot or person in the room.

[0-2 min]
- R4 can_navigate to the coffee table and PickupLightObject (e.g., keys, wallet) if present. (r4_s1)

[2-4 min]
- R4 can_navigate to the couch and PickupLightObject (e.g., phone, bag) if present. (r4_s2)

[4-6 min]
- R4 can_navigate to the door and place all collected items nearby for easy access. (r4_s3)

[6-8 min]
- R4 PushFurniture if any heavy objects are obstructing the path to the door. (r4_s4)

[8-10 min]
- R4 can_navigate to the exit and ensure the path is clear for departure. (r4_s5)
```

### Independent (TF=7 PF=2 OC=2 SC=3 Final=3.65)

```
[0-5 min]
- R1 Slice bread (r1_s1)
- R1 Pour coffee into cup (r1_s2)
- R1 Slice tomato (r1_s3)
- R1 Slice lettuce (r1_s4)
- R1 Place sliced bread, tomato, and lettuce on plate (r1_s5)

[5-10 min]
- R1 Fry egg on stove (r1_s6)
- R1 Place fried egg on plate (r1_s7)
- R1 Turn off stove (r1_s8)

[0-5 min]
- R2 picks up an apple from the counter (r2_s1)
- R2 picks up a cup from the counter (r2_s2)

[5-10 min]
- R2 places the apple and cup on the table for breakfast (r2_s3)

[0-5 min]
- R3 Turn on the lamp for better lighting. (r3_s1)

[5-10 min]
- R3 Close the laptop on the couch to tidy up. (r3_s2)

[0-5 min]
- R4 Turn off the TV to save energy. (r4_s1)

[5-10 min]
- R4 Tidy the coffee table by arranging the items neatly. (r4_s2)
```

### LaMMA-P (TF=3 PF=1 OC=1 SC=2 Final=1.75)

```
### Joint Plan

[0-5 min]
- R2 go to kitchen (r2_s1)
- R4 go to work bag location (r4_s1)
- R2 gather breakfast ingredients (r2_s2)
- R4 gather work items (r4_s2)
- R2 slice bread (r2_s3)
- R2 assemble sandwich or prepare cereal (r2_s4)
- R2 clean utensils (r2_s5)
- R2 go to coffee machine (r2_s6)
- R2 gather coffee grounds and water (r2_s7)
- R2 start coffee machine (r2_s8)
- R4 place items in work bag (r4_s3)
- R4 go to wardrobe (r4_s4)

[5-10 min]
- R2 turn off coffee machine (r2_s9)
- R2 pour coffee into cup (r2_s10)
- R4 select clothing (r4_s5)
- R4 wear clothing (r4_s6)
- R1 or R3 go to device for weather/traffic (r1_s1 or r3_s1)
- R1 or R3 turn on device (r1_s2 or r3_s2)
- R1 or R3 check weather and traffic (r1_s3 or r3_s3)
- R1 or R3 turn off device (r1_s4 or r3_s4)
- Any available robot gather personal items (keys, wallet, phone) (r1_s5 or r3_s5 or r4_s7)
```

### SMART-LLM (TF=4 PF=1 OC=2 SC=2 Final=2.4)

```
### Joint Plan

[0-5 min]
- R4 Go to Bread (r4_s1)
- R4 Pick up Bread (r4_s2)
- R4 Go to Toaster (r4_s3)
- R4 Put Bread in Toaster (r4_s4)
- R4 Switch on Toaster (r4_s5)
- R4 Wait for toast (r4_s6)
- R4 Switch off Toaster (r4_s7)
- R4 Pick up Toast (r4_s8)
- R4 Go to Plate (r4_s9)
- R4 Put Toast on Plate (r4_s10)

[0-5 min]
- R4 Go to Fridge (r4_s11)
- R4 Open Fridge (r4_s12)
- R4 Pick up LunchBox (r4_s13)
- R4 Close Fridge (r4_s14)
- R4 Go to CounterTop (r4_s15)
- R4 Put LunchBox on CounterTop (r4_s16)

[0-5 min]
- R3 Go to Wardrobe (r3_s1)
- R3 Open Wardrobe (r3_s2)
- R3 Pick up Clothes (r3_s3)
- R3 Close Wardrobe (r3_s4)
- R3 Go to Bed (r3_s5)
- R3 Put Clothes on Bed (r3_s6)

[0-5 min]
- R4 Go to KeyChain (r4_s17)
- R4 Pick up KeyChain (r4_s18)
- R4 Go to Wallet (r4_s19)
- R4 Pick up Wallet (r4_s20)
- R4 Go to Phone (r4_s21)
- R4 Pick up Phone (r4_s22)
- R4 Go to Door (r4_s23)
- R4 Put KeyChain near Door (r4_s24)
- R4 Put Wallet near Door (r4_s25)
- R4 Put Phone near Door (r4_s26)

[5-10 min]
- R4 Go to Window (r4_s27)
- R4 Check Weather (r4_s28)
- R4 Go to Umbrella (if needed) (r4_s29)
- R4 Pick up Umbrella (if needed) (r4_s30)
- R4 Go to Door (if needed) (r4_s31)
- R4 Put Umbrella near Door (if needed) (r4_s32)
```

## Run 2

### Ours (CDA) (TF=4 PF=3 OC=3 SC=2 Final=3.15)

```
### Joint Plan — task1_abstract  (about 15 min / deadline 10 min: MISSED)

[0-5 min]
- R1 [LOCAL] slice the Loaf of bread into quick breakfast portions  (r1_s1)
- R2 [LOCAL] move the Apple to the kitchen grab-and-go area  (r2_s1)
- R3 [PASS] pass Open laptop to R4 (offered) (hands it over; R4 collects it)  (r3_s2)
- R4 [LOCAL] pick up Cardboard boxes and packing pieces from the living-room walking route and place Cardboard boxes and packing pieces at a clear spot against the wall beside the Black cabinet or sideboard  (r4_s1)
- R1 [LOCAL] place the sliced Loaf of bread on the Plate  (r1_s2)
- R2 [LOCAL] move the Loaf of bread beside the Apple in the kitchen grab-and-go area  (r2_s2)
- R4 [RECEIVE] receive Open laptop from R3 (collects it from the living room)  (r4_s2)
- R1 [LOCAL] slice the Apple into quick breakfast portions  (r1_s3)
- R4 [LOCAL] move the Open laptop from the handoff point to the living-room departure point  (r4_s3)

[5-10 min]
- R1 [LOCAL] place the sliced Apple on the Plate  (r1_s4)
- R1 [LOCAL] fill the Cup with available drinking water  (r1_s5)
- R1 [PASS] fill the Cup with available drinking water and pass it to R2 in the kitchen -> R2 (hands it over; R2 collects it)  (r1_s6)

[10-15 min]
- R2 [RECEIVE] receive Cup (one Cup filled with available drinking water) from R1 (collects it from the kitchen)  (r2_s3)
- R2 [LOCAL] place the filled Cup beside the Apple and Loaf of bread in the kitchen grab-and-go area  (r2_s4)

### Warnings
- {'issue': 'DUPLICATE_WORK kept', 'nodes': ['r3_s1', 'r4_s3'], 'why': 'not duplicate'}
```

### Centralized (TF=3 PF=4 OC=2 SC=2 Final=2.7)

```
[0-2 min]
- R1 Slice bread using the knife. (r1_s1)

[2-4 min]
- R1 Pour water into the cup. (r1_s2)

[4-6 min]
- R1 Slice the tomato. (r1_s3)

[6-8 min]
- R1 Slice the lettuce. (r1_s4)

[8-10 min]
- R1 Pass sliced bread, tomato, lettuce, and cup to R2. (r1_s5)

[0-5 min]
- R2 navigate to R1 to collect prepared items. (r2_s1)

[5-10 min]
- R2 navigate to the living room to deliver items to R3. (r2_s2)

[Step 1]
- R3 waits for R2 to arrive with breakfast items.

[Step 2]
- R3 receives breakfast items from R2 (r3_s2).

[Step 3]
- R3 arranges the breakfast items on the coffee table for serving (r3_s3).

[0-2 min]
- R4 can_navigate to the coffee table (r4_s1).

[2-4 min]
- R4 PickupLightObject (vase) from the coffee table and place it on the shelf (r4_s2).

[4-6 min]
- R4 can_navigate to the couch area (r4_s3).

[6-8 min]
- R4 PickupHeavyObject (any misplaced cushions) and arrange them neatly on the couch (r4_s4).

[8-10 min]
- R4 PushFurniture (if necessary) to ensure the living room is tidy and organized (r4_s5).
```

### Independent (TF=4 PF=1 OC=1 SC=2 Final=2.05)

```
[0-5 min]
- R1 Slice bread (r1_s1)
- R1 Pour coffee into cup (r1_s2)
- R1 Slice tomato (r1_s3)
- R1 Slice lettuce (r1_s4)
- R1 Place sliced bread, tomato, and lettuce on plate (r1_s5)

[0-5 min]
- R2 PickupLightObject (Apple) and place it on the counter for breakfast. (r2_s1)

[5-10 min]
- R2 PickupLightObject (Cup) and place it next to the coffee machine for a quick drink. (r2_s2)

[0-5 min]
- R3 Turn on the lamp for better lighting. (r3_s1)
- R3 Close the laptop on the couch to tidy up. (r3_s2)

[0-5 min]
- R4 Turn off the TV to save energy. (r4_s1)
- R4 Tidy the coffee table by arranging the items neatly. (r4_s2)
- R4 Ensure the curtains are open to let in natural light. (r4_s3)
```

### LaMMA-P (TF=3 PF=1 OC=2 SC=1 Final=1.95)

```
### Joint Plan

[0-5 min]
- R4 goes to the kitchen (r4_s1)
- R4 opens the fridge (r4_s2)
- R4 picks up breakfast items (r4_s3)
- R4 slices items if necessary (r4_s4)
- R4 places items on a plate (r4_s5)
- R4 cleans up any mess (r4_s6)
- R4 goes to the fridge (r4_s7)
- R4 opens the fridge (r4_s8)
- R4 picks up lunch items (r4_s9)
- R4 places items in a lunchbox (r4_s10)
- R4 closes the fridge (r4_s11)

[0-5 min]
- R2 goes to the wardrobe (r2_s1)
- R2 picks up clothes (r2_s2)
- R2 places clothes on the bed (r2_s3)

[0-5 min]
- R3 goes to the desk (r3_s1)
- R3 picks up work essentials (r3_s2)
- R3 places items in a bag (r3_s3)

[0-5 min]
- R3 goes to the bathroom (r3_s1)
- R3 turns on the light (r3_s2)
- R3 turns off the light after use (r3_s3)

[0-5 min]
- R3 goes to the computer or smart device (r3_s1)
- R3 turns on the device (r3_s2)
- R3 checks weather and traffic (r3_s3)
- R3 turns off the device (r3_s4)

[5-10 min]
- R3 goes to the door (r3_s1)
- R3 locks the door (r3_s2)
```

### SMART-LLM (TF=3 PF=1 OC=1 SC=2 Final=1.75)

```
### Joint Plan

[0-5 min]
- R4 Go to Bread (r4_s1)
- R4 Pick up Bread (r4_s2)
- R4 Go to Toaster (r4_s3)
- R4 Put Bread in Toaster (r4_s4)
- R4 Switch on Toaster (r4_s5)
- R2 Go to Fridge (r2_s1)
- R2 Open Fridge (r2_s2)
- R2 Pick up LunchBox (r2_s3)
- R2 Close Fridge (r2_s4)
- R2 Go to CounterTop (r2_s5)
- R2 Put LunchBox on CounterTop (r2_s6)
- R3 Go to Closet (r3_s1)
- R3 Pick up Clothes (r3_s2)
- R3 Go to Bed (r3_s3)
- R3 Put Clothes on Bed (r3_s4)
- R5 Go to KeyChain (r5_s1)
- R5 Pick up KeyChain (r5_s2)
- R5 Go to Wallet (r5_s3)
- R5 Pick up Wallet (r5_s4)
- R5 Go to Phone (r5_s5)
- R5 Pick up Phone (r5_s6)
- R6 Go to Window (r6_s1)
- R6 Check weather (r6_s2)

[5-10 min]
- R4 Wait for toast (r4_s6)
- R4 Switch off Toaster (r4_s7)
- R4 Pick up Toast (r4_s8)
- R4 Go to Plate (r4_s9)
- R4 Put Toast on Plate (r4_s10)
- R5 Go to Door (r5_s7)
- R5 Put KeyChain near Door (r5_s8)
- R5 Put Wallet near Door (r5_s9)
- R5 Put Phone near Door (r5_s10)
- R6 If rainy, go to Umbrella (r6_s3)
- R6 If rainy, pick up Umbrella (r6_s4)
- R6 If rainy, go to Door (r6_s5)
- R6 If rainy, put Umbrella near Door (r6_s6)
```

## Run 3

### Ours (CDA) (TF=4 PF=7 OC=9 SC=3 Final=6.2)

```
### Joint Plan — task1_abstract  (about 10 min / deadline 10 min: OK)

[0-5 min]
- R2 [LOCAL] move the Red apple from its kitchen location to the kitchen exit as grab-and-go food  (r2_s1)
- R3 [LOCAL] stage the Open laptop within my reach for immediate handoff  (r3_s1)
- R3 [PASS] pass Open laptop to R4 (offered) (hands it over; R4 collects it)  (r3_s2)

[5-10 min]
- R4 [RECEIVE] receive Open laptop from R3 (collects it from the living room)  (r4_s1)
- R4 [LOCAL] place the received Open laptop at the living-room departure staging point  (r4_s2)
- R4 [LOCAL] move the Small brown object on the floor near the pedestal appliance from the walking route to the top of the low dark media cabinet  (r4_s3)
```

### Centralized (TF=3 PF=2 OC=2 SC=2 Final=2.3)

```
[0-2 min]
- R1 Slice bread (r1_s1)

[2-4 min]
- R1 Slice tomato (r1_s2)

[4-6 min]
- R1 Pour water into cup (r1_s3)

[6-8 min]
- R1 Place sliced bread and tomato on plate (r1_s4)

[8-10 min]
- R1 Pass plate and cup to user (r1_s5)

[0-2 min]
- R2 navigate to the counter and pick up the apple (r2_s1).

[2-4 min]
- R2 navigate to the dining table and place the apple (r2_s2).

[4-6 min]
- R2 navigate back to the counter and pick up the cup (r2_s3).

[6-8 min]
- R2 navigate to the dining table and place the cup (r2_s4).

[8-10 min]
- R2 navigate back to the counter and pick up the plate (r2_s5).

[10-12 min]
- R2 navigate to the dining table and place the plate (r2_s6).

[0-5 min]
- R3 PickupLightObject (r3_s1): Pick up the laptop from the couch.

[5-10 min]
- R3 SliceObject (r3_s2): Slice any fruit available on the table.
- R3 PourObject (r3_s3): Pour a drink from the pitcher on the table into a glass.

[0-2 min]
- R4 can_navigate to the coffee table. (r4_s1)

[2-4 min]
- R4 PickupLightObject (e.g., keys or phone) from the coffee table. (r4_s2)

[4-6 min]
- R4 can_navigate to the door. (r4_s3)

[6-8 min]
- R4 PassReceiveObject (e.g., hand over keys or phone). (r4_s4)

[8-10 min]
- R4 PushFurniture (e.g., adjust any obstructing furniture for easy exit). (r4_s5)
```

### Independent (TF=3 PF=2 OC=3 SC=2 Final=2.65)

```
[0-5 min]
- R1 SliceObject (bread) (r1_s1)
- R1 PourObject (coffee into cup) (r1_s2)
- R1 PickupLightObject (apple) (r1_s3)
- R1 PassReceiveObject (apple to another robot) (r1_s4)

[0-5 min]
- R2 PickupLightObject (Apple) (r2_s1)
- R2 PickupLightObject (Cup) (r2_s2)
- R2 PickupLightObject (Plate) (r2_s3)

[5-10 min]
- R2 PickupLightObject (Fork) (r2_s4)
- R2 PickupLightObject (Spoon) (r2_s5)

[0-5 min]
- R3 Turn on the lamp for better lighting. (r3_s1)
- R3 Close the laptop on the couch to tidy up. (r3_s2)

[0-5 min]
- R4 Turn off the TV to save energy. (r4_s1)
- R4 Tidy the coffee table by arranging the items neatly. (r4_s2)
- R4 Ensure the curtains are open to let in natural light. (r4_s3)
```

### LaMMA-P (TF=3 PF=1 OC=2 SC=2 Final=2.1)

```
### Joint Plan

[0-5 min]
- R4 goes to the kitchen (r4_s1)
- R4 picks up breakfast items (r4_s2)
- R4 slices items if necessary (r4_s3)
- R4 places items on a plate or in a container (r4_s4)
- R4 uses appliances if needed (r4_s5)

[0-5 min]
- R4 goes to the fridge or pantry (r4_s1)
- R4 picks up lunch items (r4_s2)
- R4 places items in a lunchbox (r4_s3)
- R4 uses fridge or containers as needed (r4_s4)

[0-5 min]
- R2 goes to the wardrobe (r2_s1)
- R2 selects clothes (r2_s2)
- R2 lays out clothes for easy access (r2_s3)

[0-5 min]
- R3 goes to the office area (r3_s1)
- R3 gathers items like a laptop, charger, and documents (r3_s2)
- R3 places items in a bag (r3_s3)

[5-10 min]
- R3 goes to the bathroom (r3_s1)
- R3 prepares items like a toothbrush and towel (r3_s2)
- R3 lays out items for easy access (r3_s3)

[5-10 min]
- R3 goes to a device (r3_s1)
- R3 turns on the device (r3_s2)
- R3 turns off the device after checking (r3_s3)

[10 min]
- R3 goes to the door (r3_s1)
- R3 locks the door (r3_s2)
```

### SMART-LLM (TF=1 PF=1 OC=1 SC=1 Final=1.0)

```
### Joint Plan

[0-5 min]
- R4 Prepare breakfast (r4_s1)
- R4 Pack lunch (r4_s2)
- R2 Get dressed (r2_s1)
- R2 Gather essentials (r2_s2)

[5-10 min]
- R2 Personal hygiene (r2_s3)
- R4 Check weather and traffic (r4_s3)
```

# task2_abstract

> I need to bath in 5 minutes. Get the bathroom ready and make sure I have what I need.

## Run 1

### Ours (CDA) (TF=2 PF=3 OC=8 SC=2 Final=4.3)

```
### Joint Plan — task2_abstract  (about 10 min / deadline 5 min: MISSED)

[0-5 min]
- R3 [LOCAL] move the Gray waste bin away from the route between the door and bathtub to the bathroom wall  (r3_s2)
- R4 [LOCAL] position the first striped bath mat securely beside the bathtub  (r4_s4)
- R3 [LOCAL] move the Black plunger away from the bathing route to beside the toilet  (r3_s3)
- R4 [LOCAL] position the second striped bath mat securely beside the bathtub  (r4_s5)
- R3 [LOCAL] move the Toilet brush and holder away from the bathing route to beside the toilet  (r3_s4)
- R4 [LOCAL] place the White hand/bath towel in a dry location within easy reach of the bathtub  (r4_s6)

[5-10 min]
- R3 [LOCAL] straighten the Green-and-white striped bath mat securely beside the bathtub  (r3_s5)
- R4 [LOCAL] place the Pink bar of soap within reach at the bathtub  (r4_s7)
- R3 [LOCAL] place the Brown bath towel in a dry location within easy reach of the bathtub  (r3_s7)
- R4 [LOCAL] place the Orange toiletry bottle within reach at the bathtub  (r4_s8)
- R4 [LOCAL] place the Dark pump toiletry bottle within reach at the bathtub  (r4_s9)
- R4 [LOCAL] place the Dark green toiletry container within reach at the bathtub  (r4_s10)
```

### Centralized (TF=3 PF=2 OC=2 SC=2 Final=2.3)

```
[0-5 min]
- R1 PickupLightObject (towel from the shelf) (r1_s1)
- R1 PassReceiveObject (towel to R2) (r1_s2)

[0-5 min]
- R2 navigate to the desk area (r2_s1)
- R2 pickup towel from the desk area (r2_s2)
- R2 navigate to the bathroom (r2_s3)
- R2 place towel in the bathroom (r2_s4)

[0-5 min]
- R3 can_navigate to the bathtub area (r3_s1)
- R3 PickupLightObject towel from the rack and place it near the bathtub (r3_s2)
- R3 can_navigate to the sink area (r3_s3)
- R3 PickupLightObject soap from the sink and place it on the bathtub edge (r3_s4)
- R3 can_navigate to the door area to be ready for further instructions (r3_s5)

[0-1 min]
- R4 can_navigate to the bathtub area (r4_s1).

[1-2 min]
- R4 can_navigate to the shelf and PickupLightObject (soap, shampoo) (r4_s2).

[2-3 min]
- R4 can_navigate to the bathtub and place the soap and shampoo nearby (r4_s3).

[3-4 min]
- R4 can_navigate to the bath mat and adjust it if necessary (r4_s4).

[4-5 min]
- R4 can_navigate to the towel rack and ensure a towel is accessible (r4_s5).
```

### Independent (TF=2 PF=1 OC=2 SC=1 Final=1.65)

```
[0-5 min]
- R1 PickupLightObject (towel from the chair) (r1_s1)

[0-5 min]
- R2 PickupLightObject towel from the chair (r2_s1)

[0-5 min]
- R3 turns on the bathtub faucet to fill the tub with water. (r3_s1)
- R3 ensures the bath mat is properly placed in front of the tub. (r3_s2)
- R3 checks that the towel is hanging and accessible. (r3_s3)
- R3 makes sure the soap and shampoo are within reach on the sink. (r3_s4)

[0-5 min]
- R4 Pull shower curtain open (r4_s1)
- R4 Place bath mat in front of the tub (r4_s2)
- R4 Ensure soap and shampoo are accessible on the shelf (r4_s3)
```

### LaMMA-P (TF=6 PF=2 OC=2 SC=3 Final=3.35)

```
### Joint Plan

[0-5 min]
- R4 go to bathtub (r4_s1)
- R4 clean bathtub (r4_s2)
- R4 turn on faucet (r4_s3)
- R4 turn off faucet (r4_s4)

[0-5 min]
- R3 go to towel location (r3_s1)
- R3 pick up towel (r3_s2)
- R3 go to soap location (r3_s3)
- R3 pick up soap (r3_s4)
- R3 go to bathtub (r3_s5)
- R3 place towel and soap near bathtub (r3_s6)

[0-5 min]
- R1 go to light switch (r1_s1)
- R1 turn on lights (r1_s2)
- R1 go to candle location (r1_s3)
- R1 light candles (r1_s4)
```

### SMART-LLM (TF=9 PF=2 OC=2 SC=8 Final=5.0)

```
### Joint Plan

[0-5 min]
- R4 go to the bathtub (r4_s1)
- R4 open the faucet (r4_s2)
- R4 switch on the faucet (r4_s3)
- R4 wait for bathtub to fill (r4_s4)
- R4 switch off the faucet (r4_s5)

[0-5 min]
- R3 go to the soap bar (r3_s1)
- R3 pick up the soap bar (r3_s2)
- R3 go to the bathtub (r3_s3)
- R3 place the soap bar near the bathtub (r3_s4)
- R3 go to the towel (r3_s5)
- R3 pick up the towel (r3_s6)
- R3 go to the bathtub (r3_s7)
- R3 place the towel near the bathtub (r3_s8)
```

## Run 2

### Ours (CDA) (TF=1 PF=3 OC=8 SC=2 Final=4.0)

```
### Joint Plan — task2_abstract  (about 15 min / deadline 5 min: MISSED)

[0-5 min]
- R3 [LOCAL] move the Shower curtain aside to expose the bathtub and its controls  (r3_s1)
- R4 [LOCAL] move the Wastebasket away from the route to the bathtub  (r4_s1)
- R3 [LOCAL] move the Pedal waste bin against the wall away from the walking route  (r3_s3)
- R4 [LOCAL] move the first of the Two striped bath mats flat beside the bathtub exit  (r4_s4)
- R3 [LOCAL] move the Black toilet plunger against the wall away from the walking route  (r3_s4)
- R4 [LOCAL] move the second of the Two striped bath mats flat onto the bathtub approach  (r4_s5)
- R3 [LOCAL] move the Toilet brush and holder against the wall away from the walking route  (r3_s5)

[5-10 min]
- R4 [LOCAL] move the White bath towel to a dry position within easy reach of the bathtub  (r4_s8)
- R3 [LOCAL] stage the Brown towel beside the bathtub on a dry surface within reach of the bathtub  (r3_s7)
- R4 [LOCAL] move the Pink bar of soap to the bathtub ledge within reach  (r4_s9)
- R3 [LOCAL] move the Small blue toiletry bottle to a dry position within easy reach of the bather  (r3_s8)
- R4 [LOCAL] move the Brown cylindrical toiletry container to the bathtub ledge within reach  (r4_s10)
- R3 [LOCAL] move the Small beige toiletry bottle to a dry position within easy reach of the bather  (r3_s9)
- R4 [LOCAL] move the Dark pump bottle to the bathtub ledge within reach  (r4_s11)
- R3 [LOCAL] place the Toilet-paper roll at the toilet where it is dry and accessible  (r3_s10)
- R4 [LOCAL] move the Purple toiletry bottle to the bathtub ledge within reach  (r4_s12)

[10-15 min]
- R4 [LOCAL] move the Small green toiletry container to the bathtub ledge within reach  (r4_s13)
- R4 [LOCAL] move the Small brown toiletry container to the bathtub ledge within reach  (r4_s14)
- R4 [LOCAL] move the Additional small light-colored toiletry container to the bathtub ledge within reach  (r4_s15)
```

### Centralized (TF=3 PF=3 OC=2 SC=2 Final=2.5)

```
[0-5 min]
- R1 PickupLightObject (r1_s1): Pick up the mug from the desk.
- R1 PassReceiveObject (r1_s2): Pass the mug to R2 for use in the bathroom.

[0-1 min]
- R2 navigate to the desk area to check for any light objects that might be useful for the bathroom setup. (r2_s1)

[1-2 min]
- R2 pick up any light objects such as a towel or toiletries from the desk area. (r2_s2)

[2-3 min]
- R2 navigate to the bathroom with the collected items. (r2_s3)

[3-4 min]
- R2 place the items in the bathroom for use. (r2_s4)

[4-5 min]
- R2 ensure the bathroom is ready for use by checking for any additional needs. (r2_s5)

[0-1 min]
- R3 can_navigate to the bathtub area (r3_s1).

[1-2 min]
- R3 PickupLightObject: Ensure the towel is within reach by placing it on the towel rack or edge of the bathtub (r3_s2).

[2-3 min]
- R3 can_navigate to the sink area (r3_s3).

[3-4 min]
- R3 PickupLightObject: Place soap or shampoo from the sink area near the bathtub (r3_s4).

[4-5 min]
- R3 can_navigate to the door to ensure it is closed for privacy (r3_s5).

[0-5 min]
- R4 can_navigate to the bathtub area (r4_s1)
- R4 PickupLightObject (shampoo and soap) from the shelf and place them near the bathtub (r4_s2)
- R4 PushFurniture (move the bath mat closer to the bathtub) (r4_s3)
- R4 can_navigate to the sink area and ensure the towel is accessible (r4_s4)
```

### Independent (TF=2 PF=2 OC=2 SC=1 Final=1.85)

```
[0-5 min]
- R1 PickupLightObject (towel) from the chair and prepare it for use. (r1_s1)

[0-5 min]
- R2 PickupLightObject (r2_s1)

[0-5 min]
- R3 Turn on the bathtub faucet to fill the tub with water. (r3_s1)
- R3 Ensure the shower curtain is closed to prevent water splashing. (r3_s2)
- R3 Place the bath mat in front of the tub for safety. (r3_s3)

[0-5 min]
- R4 Pull shower curtain open (r4_s1)
- R4 Place bath mat in front of the tub (r4_s2)
- R4 Ensure soap and shampoo are accessible on the shelf (r4_s3)
```

### LaMMA-P (TF=3 PF=1 OC=2 SC=2 Final=2.1)

```
### Joint Plan

[0-5 min]
- R4 go to mirror (r4_s1)
- R4 clean mirror (r4_s2)
- R4 go to sink (r4_s3)
- R4 clean sink (r4_s4)
- R4 go to floor (r4_s5)
- R4 clean floor (r4_s6)
- R4 go to bathtub (r4_s7)
- R4 clean bathtub (r4_s8)

[0-5 min]
- R1 go to towel (r1_s1)
- R1 pick up towel (r1_s2)
- R1 go to soap bar (r1_s3)
- R1 pick up soap bar (r1_s4)
- R1 go to shampoo (r1_s5)
- R1 pick up shampoo (r1_s6)
- R1 go to conditioner (r1_s7)
- R1 pick up conditioner (r1_s8)

[0-5 min]
- R1 go to faucet (r1_s9)
- R1 switch on faucet (r1_s10)
```

### SMART-LLM (TF=4 PF=2 OC=2 SC=2 Final=2.6)

```
### Joint Plan

[0-5 min]
- R4 go to the bathtub (r4_s1)
- R4 clean the bathtub if necessary (r4_s2)
- R4 go to the faucet (r4_s3)
- R4 turn on the faucet to fill the bathtub (r4_s4)
- R4 wait for the bathtub to fill (r4_s5)
- R4 turn off the faucet (r4_s6)

[0-5 min]
- R3 go to the soap (r3_s1)
- R3 pick up the soap (r3_s2)
- R3 go to the bathtub (r3_s3)
- R3 place the soap near the bathtub (r3_s4)
- R3 go to the shampoo (r3_s5)
- R3 pick up the shampoo (r3_s6)
- R3 go to the bathtub (r3_s7)
- R3 place the shampoo near the bathtub (r3_s8)
- R3 go to the towel (r3_s9)
- R3 pick up the towel (r3_s10)
- R3 go to the bathtub (r3_s11)
- R3 place the towel near the bathtub (r3_s12)

[0-5 min]
- R4 go to the light switch (r4_s7)
- R4 turn on the light if necessary (r4_s8)
```

## Run 3

### Ours (CDA) (TF=1 PF=3 OC=7 SC=1 Final=3.5)

```
### Joint Plan — task2_abstract  (about 15 min / deadline 5 min: MISSED)

[0-5 min]
- R3 [LOCAL] position the Green striped bath mat securely on the floor beside the bathtub  (r3_s5)
- R4 [LOCAL] move the Wastebasket from the bathtub route to an unobstructive position by the wall  (r4_s3)
- R4 [LOCAL] move the Toilet-cleaning tool with holder from the bathtub route to an unobstructive position beside the toilet  (r4_s4)
- R4 [LOCAL] move the first striped bath mat to a secure flat position at the bathtub exit area  (r4_s5)

[5-10 min]
- R4 [LOCAL] move the second striped bath mat to a secure flat position beside the bathtub approach  (r4_s6)
- R4 [LOCAL] move the White hand towel to a dry holder within easy reach of the bathtub  (r4_s7)
- R4 [LOCAL] move the Pink bar of soap to a dry accessible ledge beside the bathtub  (r4_s9)
- R4 [LOCAL] move the Purple toiletry bottle to an accessible ledge beside the bathtub  (r4_s10)

[10-15 min]
- R4 [LOCAL] move the Dark green toiletry bottle to an accessible ledge beside the bathtub  (r4_s11)
- R4 [LOCAL] move the Pump toiletry bottle upright to an accessible ledge beside the bathtub  (r4_s12)
- R4 [LOCAL] move the first small orange toiletry container to an accessible ledge beside the bathtub  (r4_s13)
- R4 [LOCAL] move the second small orange toiletry container to an accessible ledge beside the bathtub  (r4_s14)
```

### Centralized (TF=4 PF=2 OC=3 SC=2 Final=2.95)

```
[0-5 min]
- R1 PickupLightObject (r1_s1): Pick up the mug from the desk.
- R1 PassReceiveObject (r1_s2): Pass the mug to R2 for use in the bathroom.

[0-5 min]
- R2 can_navigate to the desk area (r2_s1)
- R2 PickupLightObject (towel) from the desk chair (r2_s2)
- R2 can_navigate to the bathroom (r2_s3)
- R2 PassReceiveObject (towel) to the bathroom area (r2_s4)

[0-5 min]
- R3 can_navigate to the bathtub and ensure the shower curtain is open. (r3_s1)
- R3 can_navigate to the sink and ensure the soap is accessible. (r3_s2)
- R3 can_navigate to the towel rack and ensure a towel is hanging and accessible. (r3_s3)
- R3 can_navigate to the bath mat and ensure it is properly placed in front of the bathtub. (r3_s4)

[0-5 min]
- R4 can_navigate to the bathtub and ensure the shower curtain is properly closed. (r4_s1)
- R4 PickupLightObject to place soap and shampoo from the shelf onto the edge of the bathtub. (r4_s2)
- R4 can_navigate to the sink and ensure the towel is hanging properly on the towel rack. (r4_s3)
- R4 can_navigate to the bath mat and adjust it if necessary to ensure it is flat and in front of the bathtub. (r4_s4)
```

### Independent (TF=2 PF=2 OC=2 SC=2 Final=2.0)

```
[0-5 min]
- R1 picks up the towel from the chair. (r1_s1)

[0-5 min]
- R2 PickupLightObject (towel from the desk) (r2_s1)

[0-5 min]
- R3 turns on the bathtub faucet to fill the tub with water. (r3_s1)
- R3 ensures the bath mat is properly placed in front of the tub. (r3_s2)
- R3 checks that the towel is hanging and accessible. (r3_s3)
- R3 ensures the soap and shampoo are within reach on the sink. (r3_s4)

[0-5 min]
- R4 Pull shower curtain open to prepare the bathtub for use. (r4_s1)
- R4 Place bath mat in front of the bathtub for safety. (r4_s2)
- R4 Ensure soap and shampoo are accessible on the shelf. (r4_s3)
```

### LaMMA-P (TF=8 PF=2 OC=2 SC=6 Final=4.4)

```
### Joint Plan

[0-5 min]
- R4 goes to the bathtub (r4_s1)
- R4 cleans the bathtub (r4_s2)
- R4 turns on the water faucet (r4_s3)
- R4 turns off the water faucet (r4_s4)

[0-5 min]
- R3 goes to the towel location (r3_s1)
- R3 picks up the towel (r3_s2)
- R3 goes to the soap location (r3_s3)
- R3 picks up the soap (r3_s4)
- R3 goes to the bathtub (r3_s5)
- R3 places the towel near the bathtub (r3_s6)
- R3 places the soap near the bathtub (r3_s7)

[0-5 min]
- R1 goes to the light switch (r1_s1)
- R1 turns on the lights (r1_s2)
- R1 goes to the music player (r1_s3)
- R1 turns on the music player (r1_s4)
```

### SMART-LLM (TF=9 PF=2 OC=2 SC=9 Final=5.15)

```
### Joint Plan

[0-5 min]
- R2 go to the bathtub (r2_s1)
- R2 open the faucet (r2_s2)
- R2 switch on the faucet (r2_s3)
- R2 wait for the bathtub to fill (r2_s4)
- R2 switch off the faucet (r2_s5)

[0-5 min]
- R4 go to the soap bar (r4_s1)
- R4 pick up the soap bar (r4_s2)
- R4 go to the bathtub (r4_s3)
- R4 place the soap bar near the bathtub (r4_s4)
- R4 go to the towel (r4_s5)
- R4 pick up the towel (r4_s6)
- R4 go to the bathtub (r4_s7)
- R4 place the towel near the bathtub (r4_s8)
```

# task3_abstract

> I have a video call in 5 minutes. Get my workspace ready for it.

## Run 1

### Ours (CDA) (TF=2 PF=2 OC=2 SC=2 Final=2.0)

```
### Joint Plan — task3_abstract  (about 25 min / deadline 5 min: MISSED)

[0-5 min]
- R1 [LOCAL] move the Open cardboard box from the visible call area to a nearby reachable off-camera edge  (r1_s1)
- R2 [LOCAL] move the Open laptop from the sofa to a stable, convenient position on the Wooden side table beside the Lit table lamp  (r2_s1)
- R3 [LOCAL] move the Shallow tan bowl or tray to the side of the desk as a stationery organizer  (r3_s4)
- R4 [LOCAL] move the Blue rectangular device on the desk from the active work area to the far return of the L-shaped desk  (r4_s1)
- R2 [LOCAL] pick up the Loose white sheet of paper on the floor and place it neatly on the Dining table away from the call station  (r2_s2)
- R3 [LOCAL] move the Black marker or pen into the Shallow tan bowl or tray  (r3_s5)
- R4 [LOCAL] organize the Small loose desk items in the Desk drawer pedestal, clearing the active work area  (r4_s2)
- R2 [LOCAL] move the Small gray rectangular notebook or pad on the sofa from the sofa to the Dining table  (r2_s3)
- R3 [LOCAL] move the Blue pen or pencil into the Shallow tan bowl or tray  (r3_s6)
- R4 [LOCAL] position the Laptop centrally on the desk with its screen facing the caller  (r4_s3)
- R3 [LOCAL] move the Small blue desk item into the Shallow tan bowl or tray  (r3_s7)
- R3 [LOCAL] move the Notebook or book to a neat stack at the side of the desk  (r3_s8)

[5-10 min]
- R4 [LOCAL] position the Left computer monitor beside the Laptop and angle it toward the caller  (r4_s4)
- R4 [LOCAL] position the Right computer monitor beside the Laptop and angle it toward the caller  (r4_s5)
- R3 [LOCAL] move the Smartphone beside the Laptop within reach but outside the immediate work area  (r3_s9)
- R4 [LOCAL] center the Office chair at the desk directly in front of the Laptop  (r4_s6)
- R3 [LOCAL] move the Blue-and-white cup away from the Laptop and desk edge  (r3_s10)
- R3 [LOCAL] move the Chessboard off the immediate laptop work area and out of the camera view  (r3_s11)

[10-15 min]
- R4 [LOCAL] reposition the Desk lamp to illuminate the caller's face without obstructing the Laptop or monitors  (r4_s7)
- R4 [LOCAL] move the Wastebasket away from the Office chair and outside the camera view  (r4_s8)
- R3 [LOCAL] shift the Potted plant to the side of the desk so it does not obstruct the camera view  (r3_s12)
- R3 [LOCAL] move the Baseball bat or wooden stick against the wall outside the workspace access path and camera view  (r3_s14)
- R3 [LOCAL] straighten the White pillow on the bed for a tidy camera background  (r3_s15)

[15-20 min]
- R4 [LOCAL] move the Broom away from the workspace and outside the camera view  (r4_s9)
- R4 [LOCAL] straighten the White bedding across the Bed  (r4_s10)
- R4 [LOCAL] straighten the Blue blanket across the Bed  (r4_s11)

[20-25 min]
- R4 [LOCAL] straighten the Brown pillow at the head of the Bed  (r4_s12)
```

### Centralized (TF=3 PF=2 OC=2 SC=2 Final=2.3)

```
[0-5 min]
- R1 PickupLightObject (r1_s1): Pick up the box from the table.
- R1 PlaceObject (r1_s2): Place the box out of the camera's view to clear the workspace.
- R1 PickupLightObject (r1_s3): Pick up any small items on the couch that might clutter the view.
- R1 PlaceObject (r1_s4): Place these items out of the camera's view to tidy the area.

[0-1 min]
- R2 navigate to the bedroom to check for any necessary items for the workspace. (r2_s1)

[1-2 min]
- R2 identify and pick up any light objects needed for the workspace, such as a notebook or pen. (r2_s2)

[2-3 min]
- R2 return to the living room with the items. (r2_s3)

[3-4 min]
- R2 place the items on the table next to the laptop. (r2_s4)

[4-5 min]
- R2 adjust the lamp on the side table to ensure proper lighting for the video call. (r2_s5)

[0-5 min]
- R3 PickupLightObject (r3_s1): Pick up the notebook and pen from the desk.
- R3 PlaceObject (r3_s2): Place the notebook and pen neatly on the workspace near the laptop.
- R3 PickupLightObject (r3_s3): Pick up the phone from the desk.
- R3 PlaceObject (r3_s4): Place the phone next to the notebook for easy access during the call.

[0-5 min]
- R4 can_navigate to the desk area (r4_s1)
- R4 PushFurniture to adjust the chair neatly under the desk (r4_s2)
- R4 can_navigate to the bed area (r4_s3)
- R4 PickupHeavyObject to move any visible heavy objects on the bed to the side (r4_s4)
- R4 can_navigate to the window area and adjust the lamp if necessary for better lighting (r4_s5)
```

### Independent (TF=4 PF=3 OC=2 SC=2 Final=2.8)

```
[0-5 min]
- R1 Turn on the lamp for better lighting. (r1_s1)

[0-5 min]
- R2 Turn on the mobile light for better video call lighting. (r2_s1)

[0-5 min]
- R3 Turn on the lamp for better lighting. (r3_s1)
- R3 Tidy up the desk by arranging the notebook and pen neatly. (r3_s2)
- R3 Ensure the laptop is open and ready for the video call. (r3_s3)

[0-5 min]
- R4 Tidy desk area by organizing items and ensuring the laptop is centered for the video call. (r4_s1)
- R4 Adjust chair to face the laptop for optimal video call setup. (r4_s2)
- R4 Ensure the lamp is turned on for proper lighting. (r4_s3)
```

### LaMMA-P (TF=2 PF=1 OC=2 SC=3 Final=1.95)

```
### Joint Plan

[0-5 min]
- R2 Go to workspace (r2_s1)
- R4 Go to light source (r4_s1)

[Step 2]
- R2 Pick up clutter (r2_s2)
- R4 Turn on light (r4_s2)

[Step 3]
- R2 Place clutter in storage (r2_s3)
- R4 Go to computer (r4_s3)

[Step 4]
- R4 Turn on computer (r4_s4)

[Step 5]
- R2 Go to door/window (r2_s4)
- R4 Go to camera/microphone (r4_s5)

[Step 6]
- R2 Close door/window (r2_s5)
- R4 Turn on camera/microphone (r4_s6)
```

### SMART-LLM (TF=2 PF=1 OC=1 SC=2 Final=1.45)

```
### Joint Plan

[0-5 min]
- R4 go to the desk (r4_s1)
- R4 pick up clutter (r4_s2)
- R4 clean the desk (r4_s3)
- R4 put clutter in garbage can (r4_s4)

[0-5 min]
- R3 go to the desk lamp (r3_s1)
- R3 switch on the desk lamp (r3_s2)
- R3 go to the window (r3_s3)
- R3 open the window (r3_s4)

[5-10 min]
- R2 go to the laptop (r2_s1)
- R2 open the laptop (r2_s2)
- R2 switch on the laptop (r2_s3)
```

## Run 2

### Ours (CDA) (TF=2 PF=8 OC=1 SC=4 Final=3.15)

```
### Joint Plan — task3_abstract  (about 25 min / deadline 5 min: MISSED)

[0-5 min]
- R1 [LOCAL] move the Open cardboard box from the nearby surface into the Wastebasket  (r1_s1)
- R2 [LOCAL] carry the Laptop from the sofa to a clear, stable area of the dining table  (r2_s1)
- R3 [LOCAL] move the Blue cup with white lid to a stable part of the desk away from the laptop, monitors, and cables  (r3_s1)
- R4 [LOCAL] position the Laptop centrally on the L-shaped desk for camera use  (r4_s1)
- R2 [LOCAL] pick up the Loose white sheet of paper on the floor and place it neatly with the workspace materials on the dining table  (r2_s2)
- R3 [LOCAL] move the Brown shallow bowl or plate beside the Blue cup with white lid at the far corner of the desk  (r3_s2)
- R4 [LOCAL] position the Left external monitor beside the laptop without blocking the laptop camera  (r4_s2)
- R2 [LOCAL] move the Gray notebook or tablet on the sofa to beside the Laptop on the dining table  (r2_s3)
- R3 [LOCAL] move the Checkerboard from the active laptop area to the far side of the desk  (r3_s3)
- R4 [LOCAL] position the Right external monitor beside the laptop without blocking the laptop camera  (r4_s3)
- R3 [LOCAL] move the Green writing implement from the active laptop area beside the Yellow notebook or book  (r3_s5)
- R3 [LOCAL] move the Orange writing implement from the active laptop area beside the Yellow notebook or book  (r3_s6)

[5-10 min]
- R4 [LOCAL] place the Keyboard directly in front of the laptop and monitors  (r4_s4)
- R4 [LOCAL] place the Computer mouse beside the keyboard within easy reach  (r4_s5)
- R3 [LOCAL] move the Blue pen from the active laptop area beside the Yellow notebook or book  (r3_s7)
- R4 [LOCAL] align the Office chair with the laptop and keyboard at the desk  (r4_s6)
- R3 [LOCAL] move the Small black-and-orange marker or USB-sized object from the active laptop area beside the Yellow notebook or book  (r3_s8)
- R3 [LOCAL] move the Black notebook or tablet from the active laptop area into a neat stack at the far side of the desk  (r3_s9)
- R3 [LOCAL] move the White paper or card from the active laptop area onto the Black notebook or tablet  (r3_s10)
- R3 [LOCAL] move the Small blue card or eraser from the active laptop area beside the Yellow notebook or book  (r3_s11)

[10-15 min]
- R4 [LOCAL] reposition the Desk lamp to illuminate the user's face without blocking the screens  (r4_s7)
- R4 [LOCAL] move the Small blue rectangular device to the far side of the desk outside the active work area  (r4_s9)
- R4 [LOCAL] move the Small black rectangular desk device to the far side of the desk outside the active work area  (r4_s10)
- R4 [LOCAL] move the Small orange desk item to the far side of the desk outside the active work area  (r4_s11)

[15-20 min]
- R4 [LOCAL] move the Broom from the visible call area to beside the dark dresser  (r4_s12)
- R4 [LOCAL] move the Wastebasket from the visible call area to beside the dark dresser  (r4_s13)
- R4 [LOCAL] straighten the White sheet smoothly across the mattress  (r4_s14)

[20-25 min]
- R4 [LOCAL] straighten the Blue blanket neatly over the bed  (r4_s15)
- R4 [LOCAL] place the Patterned pillow neatly at the head of the bed  (r4_s16)
```

### Centralized (TF=3 PF=2 OC=2 SC=3 Final=2.45)

```
[0-5 min]
- R1 PickupLightObject (r1_s1): Pick up the box from the table.
- R1 PlaceObject (r1_s2): Place the box out of the camera's view to clear the workspace.
- R1 PickupLightObject (r1_s3): Pick up any light objects like the vase from the shelf.
- R1 PlaceObject (r1_s4): Arrange the vase neatly on the table for a tidy background.

[0-1 min]
- R2 navigate to the bedroom (r2_s1)

[1-2 min]
- R2 identify and pick up any necessary light objects for the workspace (r2_s2)

[2-3 min]
- R2 return to the living room with the items (r2_s3)

[3-4 min]
- R2 arrange the items on the workspace (r2_s4)

[4-5 min]
- R2 ensure the workspace is tidy and ready for the video call (r2_s5)

[0-5 min]
- R3 PickupLightObject (r3_s1): Pick up the notebook and pen from the desk.
- R3 PlaceObject (r3_s2): Place the notebook and pen neatly on the workspace near the laptop.
- R3 PickupLightObject (r3_s3): Pick up the phone from the desk.
- R3 PlaceObject (r3_s4): Place the phone next to the notebook for easy access during the call.

[0-5 min]
- R4 can_navigate to the desk area (r4_s1)
- R4 PickupHeavyObject to move the chair under the desk (r4_s2)
- R4 can_navigate to the bed area (r4_s3)
- R4 PickupLightObject to straighten the bed cover (r4_s4)
- R4 can_navigate to the trash bin and ensure it's not visible in the camera view (r4_s5)
```

### Independent (TF=3 PF=2 OC=2 SC=2 Final=2.3)

```
[0-5 min]
- R1 Turn on the lamp for better lighting. (r1_s1)

[0-5 min]
- R2 turns on the mobile light for better video call lighting. (r2_s1)

[0-5 min]
- R3 Turn on the lamp for better lighting. (r3_s1)
- R3 Tidy up the desk by organizing the items neatly. (r3_s2)
- R3 Ensure the laptop is open and ready for the video call. (r3_s3)

[0-5 min]
- R4 Tidy desk area by organizing items and ensuring the laptop is centered for the video call. (r4_s1)
- R4 Adjust chair to face the desk properly for the call. (r4_s2)
- R4 Ensure the lamp is turned on for adequate lighting. (r4_s3)
```

### LaMMA-P (TF=7 PF=1 OC=2 SC=2 Final=3.3)

```
### Joint Plan

[0-5 min]
- R2 go to desk (r2_s1)
- R2 pick up clutter (r2_s2)
- R2 place clutter in storage (r2_s3)

[0-5 min]
- R4 go to light switch (r4_s1)
- R4 turn on light (r4_s2)

[0-5 min]
- R3 go to computer (r3_s1)
- R3 turn on computer (r3_s2)

[0-5 min]
- R3 go to door (r3_s3)
- R3 close door (r3_s4)

[0-5 min]
- R3 go to camera and microphone (r3_s5)
- R3 ensure camera and microphone are on (r3_s6)
```

### SMART-LLM (TF=2 PF=2 OC=3 SC=2 Final=2.35)

```
### Joint Plan

[0-5 min]
- R4 clean workspace (r4_s1)
- R2 set up laptop (r2_s1)
- R2 adjust lighting (r2_s2)
- R4 check internet connection (r4_s2)
- R4 prepare necessary materials (r4_s3)
```

## Run 3

### Ours (CDA) (TF=2 PF=3 OC=7 SC=2 Final=3.95)

```
### Joint Plan — task3_abstract  (about 25 min / deadline 5 min: MISSED)

[0-5 min]
- R1 [LOCAL] place one reachable Small decorative bottles or vases into the Open cardboard box  (r1_s1)
- R2 [LOCAL] move the Loose white sheet of paper on the floor from the approach path to the wooden side table  (r2_s1)
- R3 [LOCAL] move Blue cup with white lid from beside the electronics to the far side of the desk away from the laptop and monitors  (r3_s1)
- R4 [LOCAL] position the Laptop on the Desk with its camera facing the call seat and unobstructed  (r4_s1)
- R2 [LOCAL] move the Small white dish from the dining-table laptop and camera area to the wooden side table  (r2_s2)
- R3 [LOCAL] move the Brown shallow bowl or dish to the far side of the desk away from the laptop and monitors  (r3_s2)
- R4 [LOCAL] position the left computer monitor at the back-left of the Desk without obstructing the Laptop camera  (r4_s2)
- R2 [LOCAL] move the Small dark round object from the dining-table laptop and camera area to the wooden side table  (r2_s3)
- R3 [LOCAL] move the Checkered game board with pieces from the laptop work area to an unused section of the desk  (r3_s3)
- R2 [LOCAL] carry the Open laptop on the sofa to the dining table and place it on the cleared, stable section illuminated by the lit table lamp  (r2_s4)
- R3 [LOCAL] move the Yellow-orange notebook or book from the laptop work area to an unused section of the desk  (r3_s4)

[5-10 min]
- R4 [LOCAL] position the right computer monitor at the back-right of the Desk without obstructing the Laptop camera  (r4_s3)
- R4 [LOCAL] move the Office chair into a usable seated position centered at the Desk  (r4_s4)
- R3 [LOCAL] move the Black notebook or tablet with a white sheet from the laptop work area to an unused section of the desk  (r3_s5)
- R4 [LOCAL] move the Keyboard to the front-center of the Desk  (r4_s5)
- R3 [LOCAL] move the Blue writing tool to the stationery group on an unused section of the desk  (r3_s6)
- R4 [LOCAL] move the Mouse or small pointing device beside the Keyboard  (r4_s6)
- R3 [LOCAL] move the Orange or pink writing tool to the stationery group on an unused section of the desk  (r3_s7)
- R3 [LOCAL] move the Small black-and-red bottle away from the electronics to an unused section of the desk  (r3_s8)
- R3 [LOCAL] move the Small blue rectangular item to the grouped small desk items on an unused section of the desk  (r3_s9)

[10-15 min]
- R4 [LOCAL] move the Blue bottle or cup upright from the immediate work area to the Dresser  (r4_s7)
- R4 [LOCAL] move the Small blue rectangular desk item from the immediate work area to the top of the Desk drawer unit  (r4_s8)
- R4 [LOCAL] move the Small black desk items from the immediate work area to the top of the Desk drawer unit  (r4_s9)
- R3 [LOCAL] reposition the Table lamp to illuminate the call seat without obstructing the laptop or monitors  (r3_s10)

[15-20 min]
- R4 [LOCAL] position the Desk lamp to direct available light toward the call seat without obstructing the Laptop camera  (r4_s10)
- R4 [LOCAL] move the Wastebasket beside the Dresser and out of the camera background  (r4_s11)
- R4 [LOCAL] move the Broom beside the Dresser and out of the camera background  (r4_s12)

[20-25 min]
- R4 [LOCAL] straighten the Blue blanket neatly across the Bed  (r4_s13)
- R4 [LOCAL] straighten the White pillow at the head of the Bed  (r4_s14)
- R4 [LOCAL] straighten the Brown patterned pillow at the head of the Bed  (r4_s15)
```

### Centralized (TF=3 PF=3 OC=2 SC=3 Final=2.65)

```
[0-5 min]
- R1 PickupLightObject (r1_s1): Pick up the open box from the table.
- R1 PlaceObject (r1_s2): Place the box out of the camera's view to declutter the workspace.
- R1 PickupLightObject (r1_s3): Pick up the lamp from the table.
- R1 PlaceObject (r1_s4): Position the lamp to ensure good lighting for the video call.

[0-1 min]
- R2 navigate to the bedroom to check for any necessary items. (r2_s1)

[1-2 min]
- R2 identify and pick up any light objects needed for the workspace. (r2_s2)

[2-3 min]
- R2 return to the living room with the items. (r2_s3)

[3-4 min]
- R2 place the items on the table near the laptop. (r2_s4)

[4-5 min]
- R2 adjust the lamp on the side table for optimal lighting. (r2_s5)

[0-5 min]
- R3 PickupLightObject (r3_s1): Pick up the notebook and pen from the desk.
- R3 PlaceObject (r3_s2): Place the notebook and pen neatly on the workspace near the laptop.
- R3 PickupLightObject (r3_s3): Pick up the phone from the desk.
- R3 PlaceObject (r3_s4): Place the phone next to the notebook for easy access during the call.

[0-5 min]
- R4 can_navigate to the desk area (r4_s1).
- R4 PickupHeavyObject to move the chair neatly under the desk (r4_s2).
- R4 can_navigate to the bed area (r4_s3).
- R4 PickupHeavyObject to straighten the bed cover (r4_s4).
- R4 can_navigate to the trash bin and ensure it's not obstructing the workspace (r4_s5).
```

### Independent (TF=3 PF=2 OC=2 SC=2 Final=2.3)

```
[0-5 min]
- R1 Turn on the lamp for better lighting. (r1_s1)

[0-5 min]
- R2 turns on the mobile light for better video call lighting. (r2_s1)

[0-5 min]
- R3 Turn on the lamp for better lighting. (r3_s1)
- R3 Ensure the laptop is open and ready for the video call. (r3_s2)
- R3 Tidy up the desk by organizing the items neatly. (r3_s3)

[0-5 min]
- R4 straighten chair at desk for a tidy appearance (r4_s1)
- R4 adjust desk lamp for better lighting (r4_s2)
- R4 organize items on desk to reduce clutter (r4_s3)
```

### LaMMA-P (TF=4 PF=1 OC=3 SC=4 Final=3.05)

```
### Joint Plan

[0-5 min]
- R4 go to workspace (r4_s1)
- R4 pick up clutter (r4_s2)
- R4 put clutter in drawer (r4_s3)
- R4 go to light (r4_s4)
- R4 switch on light (r4_s5)
- R4 go to computer (r4_s6)
- R4 switch on computer (r4_s7)

[0-5 min]
- R2 go to door (r2_s1)
- R2 close door (r2_s2)

[0-5 min]
- R4 go to camera and microphone (r4_s8)
- R4 switch on camera and microphone (r4_s9)
```

### SMART-LLM (TF=3 PF=1 OC=1 SC=2 Final=1.75)

```
### Joint Plan

[0-5 min]
- R2 go to desk (r2_s1)
- R3 pick up clutter (r3_s1)
- R3 put clutter in garbage can (r3_s2)
- R2 go to laptop (r2_s2)
- R3 pick up laptop (r3_s3)
- R3 put laptop on desk (r3_s4)
- R1 switch on laptop (r1_s1)
- R4 go to desk lamp (r4_s1)
- R1 switch on desk lamp (r1_s2)
- R4 go to window (r4_s2)
- R1 open window blinds (r1_s3)
```

# task4_abstract

> A guest is arriving in 15 minutes. Get the house ready to welcome them.

## Run 1

### Ours (CDA) (TF=7 PF=9 OC=9 SC=5 Final=7.8)

```
### Joint Plan — task4_abstract  (about 10 min / deadline 15 min: OK)

[0-5 min]
- R1 [LOCAL] move the Chef's knife from the loose countertop area to lie flat beside the cutting boards  (r1_s1)
- R2 [LOCAL] move the Open cardboard box from the Coffee table to the wall beside the Television cabinet, outside the entrance-to-seating walking routes  (r2_s1)
- R3 [LOCAL] move the Cardboard box from the doorway area to an unobstructive position against the bedroom wall  (r3_s1)
- R4 [LOCAL] move the Red cylindrical bin from the walkway to the wall, leaving the walkway and toilet access clear  (r4_s1)
- R1 [LOCAL] move the Yellow-handled kitchen utensil from the loose countertop area to a neat position beside the cookware  (r1_s2)
- R2 [LOCAL] move the Remote control from the Coffee table to a neat position on the Round side table  (r2_s2)
- R3 [LOCAL] move the Brown teddy bear from the walking path to a neat position on the bed  (r3_s2)
- R4 [LOCAL] move the Green toiletry bottle from the visible sink area to the rear of the vanity away from the basin  (r4_s2)
- R1 [LOCAL] move the Green sponge from the countertop to the cleaning-supply area  (r1_s3)
- R2 [LOCAL] arrange the Small colorful objects on the coffee table into a compact, orderly display  (r2_s3)
- R3 [LOCAL] move the Small green loose item on the floor into the Small dish or bowl on the dresser  (r3_s3)
- R4 [LOCAL] place the Pink bar of soap neatly beside the sink without blocking the basin  (r4_s3)
- R1 [LOCAL] move the Spray bottle from the countertop to the cleaning-supply area beside the Green sponge  (r1_s4)
- R3 [LOCAL] straighten the Light-colored duvet or bedcover smoothly across the bed  (r3_s4)
- R4 [LOCAL] move the Small white toiletry container from the visible sink area to the rear of the vanity away from the basin  (r4_s4)
- R1 [LOCAL] move the Dark plate to the food-preparation area  (r1_s5)
- R4 [LOCAL] move the Spray bottle from the visible sink area to a rear corner of the vanity  (r4_s5)

[5-10 min]
- R2 [LOCAL] straighten the Light-colored sofa cushion against the back of the Upholstered sofa so the seat remains unobstructed  (r2_s4)
- R3 [LOCAL] straighten the Left bed pillow at the head of the bed  (r3_s5)
- R1 [LOCAL] move the Tomato from the loose countertop area onto the Dark plate  (r1_s6)
- R3 [LOCAL] straighten the Right bed pillow at the head of the bed  (r3_s6)
- R4 [LOCAL] move the Red cloth on the toilet tank from the toilet tank to a dry corner of the vanity away from the sink basin  (r4_s6)
- R1 [LOCAL] move the Lettuce leaf from the loose countertop area onto the Dark plate  (r1_s7)
- R3 [LOCAL] close the Open laptop and align it neatly on the dresser  (r3_s7)
- R1 [LOCAL] move the Patterned plate from the countertop to a neat refreshment-service position  (r1_s10)
- R3 [LOCAL] move the Small loose green item on the dresser into the Small dish or bowl on the dresser  (r3_s8)
```

### Centralized (TF=2 PF=2 OC=2 SC=2 Final=2.0)

```
[0-5 min]
- R1 SliceObject (slice the tomato) (r1_s1)

[5-10 min]
- R1 PourObject (pour coffee into a mug) (r1_s2)

[10-15 min]
- R1 PassReceiveObject (pass the sliced tomato and coffee mug to R2 when it arrives) (r1_s3)

[0-5 min]
- R2 navigate to the kitchen to meet R1 (r2_s1)

[5-10 min]
- R2 receive the snack or drink from R1 (r2_s2)

[10-15 min]
- R2 navigate back to the living room (r2_s3)

[15-20 min]
- R2 place the snack or drink on the table (r2_s4)

[0-5 min]
- R3 can_navigate to the bed and straighten the pillows. (r3_s1)

[5-10 min]
- R3 can_navigate to the dresser and ensure items are neatly arranged. (r3_s2)

[10-15 min]
- R3 can_navigate to the trash bin and ensure it is not overflowing. (r3_s3)

[0-5 min]
- R4 can_navigate to the sink area to check for any clutter. (r4_s1)

[5-10 min]
- R4 PickupLightObject any items on the sink that need to be moved or organized. (r4_s2)

[10-15 min]
- R4 can_navigate to the shower area to ensure it is tidy. (r4_s3)

[15-20 min]
- R4 PushFurniture if any heavy items, like a trash bin, need repositioning for better accessibility. (r4_s4)

[20-25 min]
- R4 can_navigate to the exit to complete the task. (r4_s5)
```

### Independent (TF=3 PF=1 OC=5 SC=2 Final=3.15)

```
[0-5 min]
- R1 SliceObject (slice the tomato) (r1_s1)

[5-10 min]
- R1 PourObject (pour coffee into a mug) (r1_s2)

[10-15 min]
- R1 PickupLightObject (pick up the mug with coffee) (r1_s3)

[0-5 min]
- R2 turns on the mobile light in the living room to create a welcoming atmosphere. (r2_s1)

[5-10 min]
- R2 tidies up the coffee table by arranging the items neatly. (r2_s2)

[10-15 min]
- R2 ensures the curtains are open to let in natural light. (r2_s3)

[0-5 min]
- R3 Turn on the lamp on the bedside table for a welcoming ambiance. (r3_s1)

[5-10 min]
- R3 Tidy the bed by straightening the pillows and smoothing the blanket. (r3_s2)

[10-15 min]
- R3 Close the laptop on the dresser to reduce clutter. (r3_s3)

[0-5 min]
- R4 tidy countertop by organizing items and ensuring the sink area is clean. (r4_s1)

[5-10 min]
- R4 close the shower door to make the bathroom look neat. (r4_s2)

[10-15 min]
- R4 ensure the toilet lid is closed for a tidy appearance. (r4_s3)
```

### LaMMA-P (TF=2 PF=1 OC=2 SC=1 Final=1.65)

```
### Joint Plan

[0-5 min]
- R3 goes to the living room (r3_s1)
- R4 goes to the kitchen (r4_s1)
- R4 goes to the guest room (r4_s1)

[5-10 min]
- R3 picks up clutter in the living room (r3_s2)
- R4 picks up dirty dishes in the kitchen (r4_s2)
- R4 picks up items in the guest room (r4_s2)

[10-15 min]
- R3 places clutter in designated places in the living room (r3_s3)
- R4 places dishes in the dishwasher or sink (r4_s3)
- R4 places items in their correct location in the guest room (r4_s3)

[15-20 min]
- R3 cleans surfaces in the living room (r3_s4)
- R4 wipes down countertops and stove in the kitchen (r4_s4)
- R4 makes the bed and dusts surfaces in the guest room (r4_s4)

[20-25 min]
- R1 goes to the dining area (r1_s1)
- R1 picks up plates, cutlery, and glasses (r1_s2)
- R1 sets the table (r1_s3)

[25-30 min]
- R1 goes to the living room and dining area (r1_s4)
- R1 turns on appropriate lights (r1_s5)
- R1 turns off unnecessary lights (r1_s6)

[30-35 min]
- R1 goes to the entrance (r1_s7)
- R1 opens the door to welcome the guest (r1_s8)
```

### SMART-LLM (TF=2 PF=1 OC=2 SC=1 Final=1.65)

```
### Joint Plan

[0-5 min]
- R4 go to Floor (r4_s1)
- R3 go to LightSwitch (r3_s1)
- R4 go to ArmChair (r4_s2)

[5-10 min]
- R4 clean Floor (r4_s3)
- R3 switch on LightSwitch (r3_s2)
- R4 pull ArmChair to desired position (r4_s4)

[10-15 min]
- R4 go to CoffeeTable (r4_s5)
- R4 go to SideTable (r4_s6)

[15-20 min]
- R4 clean CoffeeTable (r4_s7)
- R4 push SideTable to desired position (r4_s8)

[20-25 min]
- R4 go to Sofa (r4_s9)

[25-30 min]
- R4 clean Sofa (r4_s10)

[30-35 min]
- R4 go to Kitchen (r4_s11)

[35-40 min]
- R4 pick up WateringCan (r4_s12)

[40-45 min]
- R4 go to Fridge (r4_s13)

[45-50 min]
- R4 open Fridge (r4_s14)

[50-55 min]
- R4 pick up Bottle of Water (r4_s15)

[55-60 min]
- R4 close Fridge (r4_s16)

[60-65 min]
- R4 go to DiningTable (r4_s17)

[65-70 min]
- R4 put Bottle of Water on DiningTable (r4_s18)
```

## Run 2

### Ours (CDA) (TF=9 PF=9 OC=10 SC=9 Final=9.35)

```
### Joint Plan — task4_abstract  (about 10 min / deadline 15 min: OK)

[0-5 min]
- R1 [LOCAL] place the Patterned plate in the kitchen serving area for the fresh guest snack  (r1_s1)
- R2 [LOCAL] Straighten the object named Several sofa and armchair cushions on their respective seats so the seating is orderly and usable  (r2_s1)
- R3 [LOCAL] straighten the Top bedding or duvet smoothly across the Bed  (r3_s1)
- R4 [LOCAL] move the Pink bar of soap or small toiletry item to an accessible position beside a sink  (r4_s1)
- R1 [LOCAL] slice the Tomato into snack-sized pieces and place the pieces on the Patterned plate  (r1_s2)
- R2 [LOCAL] move the One lightweight cardboard box from the coffee-table surface to a neat location beside the television cabinet outside the walking route  (r2_s2)
- R3 [LOCAL] arrange the Pillows neatly at the head of the Bed  (r3_s2)
- R4 [LOCAL] move the Green soap or toiletry bottle into a neat position on the vanity  (r4_s2)
- R1 [LOCAL] slice the Lettuce leaf into snack-sized pieces and place the pieces on the Patterned plate  (r1_s3)
- R2 [LOCAL] reposition the One yellow glass vase neatly on the coffee table while leaving clear usable surface space  (r2_s3)
- R4 [LOCAL] move the Spray bottle to the back of the vanity away from the guest soap  (r4_s3)
- R4 [LOCAL] move the Small red item on the toilet tank from the tank to a neat position on the vanity  (r4_s4)
- R4 [LOCAL] move the Red wastebasket to an unobtrusive position beside the vanity  (r4_s5)

[5-10 min]
- R3 [LOCAL] organize the Clothing or fabric in the hamper neatly inside the Laundry hamper  (r3_s3)
- R2 [LOCAL] arrange the Small decorative objects on the coffee table neatly without crowding the usable surface  (r2_s4)
- R3 [LOCAL] place the Teddy bear neatly on the made Bed  (r3_s4)
- R2 [LOCAL] collect and arrange the Remote controls neatly on the round side table  (r2_s5)
- R3 [LOCAL] move the Cardboard box against the wall away from the doorway and walking area  (r3_s5)
- R4 [LOCAL] move the White toilet brush or plunger upright beside the toilet  (r4_s6)
- R4 [LOCAL] push the Toilet lid closed  (r4_s7)
```

### Centralized (TF=2 PF=3 OC=2 SC=1 Final=2.05)

```
[0-5 min]
- R1 SliceObject (Slice the tomato) (r1_s1)

[5-10 min]
- R1 PickupLightObject (Pick up the sliced tomato) (r1_s2)

[10-15 min]
- R1 PourObject (Pour water into the mug) (r1_s3)

[15-20 min]
- R1 PassReceiveObject (Pass the sliced tomato and mug to R2) (r1_s4)

[0-5 min]
- R2 navigate to the kitchen to meet R1 (r2_s1)

[5-10 min]
- R2 receive the snack and drink from R1 (r2_s2)

[10-15 min]
- R2 navigate back to the living room (r2_s3)

[15-20 min]
- R2 place the snack and drink on the table (r2_s4)

[0-5 min]
- R3 can_navigate to the bed and straighten the pillows. (r3_s1)

[5-10 min]
- R3 can_navigate to the dresser and ensure items are neatly arranged. (r3_s2)

[10-15 min]
- R3 can_navigate to the floor area near the trash can and pick up any light objects, placing them in the trash if necessary. (r3_s3)

[0-5 min]
- R4 can_navigate to the sink area to check for any clutter. (r4_s1)

[5-10 min]
- R4 PickupLightObject to remove any small items from the sink area. (r4_s2)

[10-15 min]
- R4 can_navigate to the shower area to ensure it is tidy. (r4_s3)

[15-20 min]
- R4 PushFurniture to adjust the position of the trash bin if necessary. (r4_s4)

[20-25 min]
- R4 can_navigate to the exit of the bathroom, completing the task. (r4_s5)
```

### Independent (TF=3 PF=1 OC=3 SC=3 Final=2.6)

```
[0-5 min]
- R1 SliceObject (lettuce) (r1_s1)

[5-10 min]
- R1 PourObject (coffee into mug) (r1_s2)

[10-15 min]
- R1 PickupLightObject (mug with coffee) (r1_s3)

[0-5 min]
- R2 Turn on the floor lamp for better lighting. (r2_s1)

[5-10 min]
- R2 Tidy up the coffee table by arranging the items neatly. (r2_s2)

[10-15 min]
- R2 Ensure the curtains are open to let in natural light. (r2_s3)

[0-5 min]
- R3 Turn on the lamp for a welcoming ambiance. (r3_s1)

[5-10 min]
- R3 Tidy the bed by arranging the pillows neatly. (r3_s2)

[10-15 min]
- R3 Close the laptop on the dresser to reduce clutter. (r3_s3)

[0-5 min]
- R4 tidy countertop by organizing items and ensuring the sink area is clean (r4_s1)

[5-10 min]
- R4 close the shower door to make the bathroom look neat (r4_s2)

[10-15 min]
- R4 ensure the toilet lid is closed for a tidy appearance (r4_s3)
```

### LaMMA-P (TF=3 PF=1 OC=2 SC=2 Final=2.1)

```
### Joint Plan

[0-5 min]
- R3 goes to the living room (r3_s1)
- R4 goes to the kitchen (r4_s1)
- R1 goes to the fridge (r1_s1)
- R3 goes to the dining area (r3_s2)
- R4 goes to the light switches (r4_s2)

[5-10 min]
- R3 picks up clutter in the living room (r3_s3)
- R4 picks up dirty dishes in the kitchen (r4_s3)
- R1 opens the fridge (r1_s2)
- R3 picks up plates, cutlery, and napkins (r3_s4)
- R4 turns on appropriate lights (r4_s4)

[10-15 min]
- R3 places clutter in designated places (r3_s5)
- R4 places dishes in the dishwasher or sink (r4_s5)
- R1 picks up drinks and snacks (r1_s3)
- R3 sets the dining table (r3_s6)
- R4 turns off unnecessary lights (r4_s6)

[15-20 min]
- R3 cleans surfaces in the living room (r3_s7)
- R4 wipes down countertops and stove (r4_s7)
- R1 places refreshments on the living room table (r1_s4)
- R4 goes to the bathroom (r4_s8)

[20-25 min]
- R1 closes the fridge (r1_s5)
- R4 checks bathroom readiness (r4_s9)

[25-30 min]
- R4 goes to the front door (r4_s10)
- R4 opens the door to welcome the guest (r4_s11)
```

### SMART-LLM (TF=1 PF=1 OC=1 SC=1 Final=1.0)

```
### Joint Plan

[0-5 min]
- R3 Tidy up living room (r3_s1)
- R4 Clean surfaces (r4_s1)
- R1 Prepare refreshments (r1_s1)
- R2 Adjust lighting (r2_s1)
- R3 Check bathroom (r3_s2)

[5-10 min]
- R3 Continue tidying living room (r3_s3)
- R4 Continue cleaning surfaces (r4_s2)
- R1 Continue preparing refreshments (r1_s2)
- R2 Ensure lighting is welcoming (r2_s2)
- R3 Ensure bathroom is stocked (r3_s4)

[10-15 min]
- R3 Finalize tidying living room (r3_s5)
- R4 Finalize cleaning surfaces (r4_s3)
- R1 Finalize refreshments preparation (r1_s3)
- R2 Finalize lighting adjustments (r2_s3)
- R3 Finalize bathroom check (r3_s6)
```

## Run 3

### Ours (CDA) (TF=4 PF=9 OC=8 SC=3 Final=6.25)

```
### Joint Plan — task4_abstract  (about 20 min / deadline 15 min: MISSED)

[0-5 min]
- R1 [LOCAL] move the Green sponge from the countertop to the cleaning-supply corner of the countertop  (r1_s1)
- R2 [LOCAL] move the Open cardboard box from the guest-facing table to an unobtrusive spot beside the media cabinet and outside the walking route  (r2_s1)
- R3 [LOCAL] straighten the Bedcover smoothly over the Mattress  (r3_s1)
- R4 [LOCAL] close the Toilet lid  (r4_s1)
- R1 [LOCAL] move the Spray bottle to the cleaning-supply corner of the countertop  (r1_s2)
- R2 [LOCAL] arrange the Small loose decorative items on the coffee table into a compact neat display, leaving usable table space  (r2_s2)
- R3 [LOCAL] arrange the left pillow neatly at the head of the bed  (r3_s2)
- R4 [LOCAL] move the Small red item on the toilet tank from the toilet tank to a neat position on the vanity  (r4_s2)
- R1 [LOCAL] move the Red-rimmed plate to the food-preparation area  (r1_s3)
- R2 [LOCAL] move the Remote control to a neat position on the Black round side table  (r2_s3)
- R3 [LOCAL] arrange the right pillow neatly beside the left pillow at the head of the bed  (r3_s3)
- R4 [LOCAL] move the Toilet brush or plunger to a neat position beside the toilet and outside the walking path  (r4_s3)
- R1 [LOCAL] move the Tomato onto the Red-rimmed plate  (r1_s4)
- R3 [LOCAL] move the left green slipper from the walking path to beside the bed  (r3_s4)
- R1 [LOCAL] move the Lettuce leaf onto the Red-rimmed plate  (r1_s5)

[5-10 min]
- R2 [LOCAL] straighten the Light-colored sofa cushion neatly on the Large sofa  (r2_s4)
- R4 [LOCAL] move the White lidded waste bin against the wall outside the walking path  (r4_s4)
- R3 [LOCAL] move the right green slipper from the walking path to beside the left green slipper  (r3_s5)
- R4 [LOCAL] move the Red open waste bin or hamper against the wall outside the walking path  (r4_s5)
- R1 [LOCAL] move the Gray plate beside the Red-rimmed plate  (r1_s6)
- R3 [LOCAL] move the Cardboard box from the walking path to a clear position against the wall  (r3_s6)
- R4 [LOCAL] move the Green toiletry or soap bottle to an upright, accessible position beside the sink  (r4_s6)
- R1 [LOCAL] move the Wooden cutting board flat into the food-preparation area  (r1_s7)
- R3 [LOCAL] move the Brown teddy bear from the floor to a neat position on the bed  (r3_s7)
- R4 [LOCAL] move the Pink soap or toiletry item to an upright, orderly position on the vanity  (r4_s7)
- R1 [LOCAL] move the Gray cutting board beside the Wooden cutting board  (r1_s8)
- R1 [LOCAL] move the Kitchen knife safely onto the Gray cutting board  (r1_s9)
- R1 [LOCAL] move the Yellow-handled utensil neatly onto the Wooden cutting board  (r1_s10)

[10-15 min]
- R3 [LOCAL] close the Laptop computer and position it squarely on the Wooden dresser  (r3_s8)
- R4 [LOCAL] move the Amber cleaning spray or pump bottle upright at the back of the vanity  (r4_s8)
- R3 [LOCAL] organize Books and notebooks on the dresser into a neat stack on the Wooden dresser  (r3_s9)
- R3 [LOCAL] position the Small gray container or tray neatly on the Wooden dresser  (r3_s10)
- R1 [LOCAL] move the Black saucepan to the cookware area beside the stove  (r1_s11)
- R3 [LOCAL] place the Small green item on the dresser into the Small gray container or tray on the dresser  (r3_s11)
- R1 [LOCAL] move the Black frying pan beside the Black saucepan  (r1_s12)
- R1 [LOCAL] move the Black cookware lid onto the Black saucepan  (r1_s13)

[15-20 min]
- R3 [LOCAL] align the Table lamp neatly on the Wooden nightstand  (r3_s12)
- R3 [LOCAL] align the Digital alarm clock neatly on the Wooden nightstand  (r3_s13)
```

### Centralized (TF=3 PF=2 OC=2 SC=2 Final=2.3)

```
[0-5 min]
- R1 SliceObject (slice the tomato) (r1_s1)

[5-10 min]
- R1 PickupLightObject (pick up the sliced tomato) (r1_s2)

[10-15 min]
- R1 PassReceiveObject (pass the sliced tomato to R2 when it arrives) (r1_s3)

[0-5 min]
- R2 navigate to the kitchen to meet R1. (r2_s1)

[5-10 min]
- R2 receive the snack from R1. (r2_s2)

[10-15 min]
- R2 navigate back to the living room. (r2_s3)

[15-20 min]
- R2 place the snack on the table in the living room. (r2_s4)

[0-5 min]
- R3 can_navigate to the bed and ensure the pillows are neatly arranged. (r3_s1)

[5-10 min]
- R3 can_navigate to the dresser and ensure any small items are neatly organized. (r3_s2)

[10-15 min]
- R3 can_navigate to the trash bin and ensure it is not overflowing. (r3_s3)

[0-5 min]
- R4 can_navigate to the sink area to check for any clutter or misplaced items. (r4_s1)

[5-10 min]
- R4 PickupLightObject any small items on the sink and organize them neatly. (r4_s2)

[10-15 min]
- R4 can_navigate to the shower area to ensure it is tidy and free of any heavy items. (r4_s3)

[15-20 min]
- R4 PushFurniture if necessary to adjust the position of any heavy items like the trash bin to ensure the bathroom is welcoming. (r4_s4)
```

### Independent (TF=4 PF=2 OC=2 SC=4 Final=2.9)

```
[0-5 min]
- R1 SliceObject (lettuce) (r1_s1)

[5-10 min]
- R1 PourObject (coffee into mug) (r1_s2)

[10-15 min]
- R1 Tidy (countertops) (r1_s3)

[0-5 min]
- R2 Turn on the floor lamp for better lighting. (r2_s1)

[5-10 min]
- R2 Tidy up the coffee table by arranging the items neatly. (r2_s2)

[10-15 min]
- R2 Ensure the curtains are open to let in natural light. (r2_s3)

[0-5 min]
- R3 turns on the lamp for a welcoming ambiance. (r3_s1)

[5-10 min]
- R3 tidies the bed by straightening the pillows and sheets. (r3_s2)

[10-15 min]
- R3 ensures the dresser is neat by arranging any visible items. (r3_s3)

[0-5 min]
- R4 tidy countertop by organizing items and ensuring the sink area is clean. (r4_s1)

[5-10 min]
- R4 close the shower door to make the bathroom look neat. (r4_s2)

[10-15 min]
- R4 ensure the toilet lid is closed for a tidy appearance. (r4_s3)
```

### LaMMA-P (TF=3 PF=1 OC=1 SC=1 Final=1.6)

```
### Joint Plan

[0-5 min]
- R3 goes to the living room (r3_s1)
- R4 goes to the kitchen (r4_s1)
- R4 goes to the guest room (r4_s2)
- R1 goes to the dining area (r1_s1)
- R1 goes to the bathroom (r1_s2)
- R2 goes to light switches and thermostat (r2_s1)
- R2 goes to the kitchen (r2_s2)

[5-10 min]
- R3 picks up clutter in the living room (r3_s2)
- R4 picks up dirty dishes in the kitchen (r4_s3)
- R4 picks up items in the guest room (r4_s4)
- R1 picks up plates, cutlery, and glasses (r1_s3)
- R1 checks bathroom cleanliness (r1_s4)
- R2 adjusts lighting and temperature (r2_s3)
- R2 picks up a glass and beverage (r2_s4)

[10-15 min]
- R3 places clutter in designated places (r3_s3)
- R4 places dishes in dishwasher or sink (r4_s5)
- R4 places items in correct location in guest room (r4_s6)
- R1 sets the dining table (r1_s5)
- R1 stocks bathroom essentials (r1_s6)
- R2 pours beverage into glass and places on tray (r2_s5)

[15-20 min]
- R3 cleans surfaces in the living room (r3_s4)
- R4 wipes down kitchen countertops and stove (r4_s7)
- R4 makes the bed and dusts surfaces in the guest room (r4_s8)
```

### SMART-LLM (TF=2 PF=1 OC=2 SC=2 Final=1.8)

```
### Joint Plan

[0-5 min]
- R3 tidy living room (r3_s1)
- R1 turn on living room lights (r1_s1)
- R2 turn on entrance lights (r2_s1)
- R4 prepare refreshments (r4_s1)
- R5 check bathroom (r5_s1)
- R6 adjust temperature (r6_s1)
```

# task5_abstract

> I'm watching a movie in 30 minutes. Get everything set up for it.

## Run 1

### Ours (CDA) (TF=9 PF=9 OC=7 SC=7 Final=8.0)

```
### Joint Plan — task5_abstract  (about 15 min / deadline 30 min: OK)

[0-5 min]
- R1 [LOCAL] pick up one of the Two mugs and fill it with drinking water  (r1_s1)
- R2 [LOCAL] arrange the Loose gray sofa cushions against the sofa back for comfortable viewing support  (r2_s1)
- R1 [PASS] pass Two mugs to R2 (offered) (hands it over; R2 collects it)  (r1_s2)
- R2 [LOCAL] arrange the Loose blue sofa cushion on the sofa for comfortable viewing support  (r2_s2)
- R1 [LOCAL] pick up one of the Four pears and stage it as a whole ready-to-eat movie snack  (r1_s3)
- R2 [LOCAL] move the Books or magazines on the side table from the Small wooden side table to the Dining table  (r2_s3)

[5-10 min]
- R1 [PASS] pass Four pears to R2 (offered) (hands it over; R2 collects it)  (r1_s4)
- R2 [LOCAL] move the Remote-like small black device on the media cabinet from the media cabinet to the sofa arm within easy reach  (r2_s4)
- R2 [RECEIVE] receive Two mugs (one mug, filled with drinking water) from R1 (collects it from the kitchen)  (r2_s5)
- R2 [LOCAL] place the received mug filled with drinking water on the cleared Small wooden side table  (r2_s6)

[10-15 min]
- R2 [RECEIVE] receive Four pears (one pear, ready to eat) from R1 (collects it from the kitchen)  (r2_s7)
- R2 [LOCAL] place the received ready-to-eat pear on the cleared Small wooden side table  (r2_s8)
```

### Centralized (TF=3 PF=3 OC=2 SC=1 Final=2.35)

```
[0-5 min]
- R1 SliceObject (Slice the tomato) (r1_s1)

[5-10 min]
- R1 PickupLightObject (Pick up the sliced tomato) (r1_s2)

[10-15 min]
- R1 PourObject (Pour a drink using the coffee machine) (r1_s3)

[15-20 min]
- R1 PickupLightObject (Pick up the drink) (r1_s4)

[20-25 min]
- R1 PassReceiveObject (Pass the sliced tomato and drink to R2) (r1_s5)

[0-5 min]
- R2 navigate to the kitchen to meet R1 (r2_s1)

[5-10 min]
- R2 receive snacks and drinks from R1 (r2_s2)

[10-15 min]
- R2 navigate back to the living room (r2_s3)

[15-20 min]
- R2 place snacks and drinks on the table in the living room (r2_s4)

[0-5 min]
- R3 navigate to the living room (r3_s1)

[5-10 min]
- R3 pick up any light objects (e.g., small items on the floor or coffee table) and place them in their appropriate locations to tidy up the living room (r3_s2)

[10-15 min]
- R3 ensure that the seating area is clear of any light objects and ready for use (r3_s3)

[15-20 min]
- R3 check that the lighting in the living room is appropriate for watching a movie, adjusting any light objects if necessary (r3_s4)

[20-25 min]
- R3 return to the bedroom (r3_s5)

[25-30 min]
- R3 standby in the bedroom, ready to assist if needed (r3_s6)

I can't see the living room from the images provided, but here's a general plan based on my capabilities:

[0-5 min]
- R4 exit the bathroom and navigate to the living room. (r4_s1)

[5-10 min]
- R4 assess the living room for any heavy furniture that might need moving to optimize the viewing experience. (r4_s2)

[10-20 min]
- R4 move any heavy furniture as needed to improve the viewing setup. (r4_s3)

[20-25 min]
- R4 ensure the seating is comfortable and the view of the screen is unobstructed. (r4_s4)

[25-30 min]
- R4 return to standby mode after confirming the setup is complete. (r4_s5)
```

### Independent (TF=2 PF=1 OC=1 SC=1 Final=1.3)

```
[0-5 min]
- R1 turns on the coffee machine to prepare coffee for the movie. (r1_s1)

[5-10 min]
- R1 slices the lemon on the counter for potential use as a garnish or in drinks. (r1_s2)

[10-15 min]
- R1 cleans the sink area using the dish sponge to ensure the kitchen is tidy. (r1_s3)

[15-20 min]
- R1 pours water into a glass for hydration during the movie. (r1_s4)

[20-25 min]
- R1 tidies up the counter by organizing the utensils and objects. (r1_s5)

[25-30 min]
- R1 checks the stove to ensure it is turned off for safety. (r1_s6)

[0-5 min]
- R2 Turn on the TV for the movie. (r2_s1)

[5-10 min]
- R2 Adjust the curtains to reduce glare on the TV. (r2_s2)

[10-15 min]
- R2 Arrange the seating area for optimal viewing. (r2_s3)

[15-20 min]
- R2 Ensure the lighting is dimmed for a better movie experience. (r2_s4)

[20-25 min]
- R2 Check that the remote control is accessible on the table. (r2_s5)

[25-30 min]
- R2 Tidy up any clutter around the seating area. (r2_s6)

I'm sorry, but I cannot see the image of your room. However, based on the information provided, I will assume that the bedroom might need some preparation for watching a movie. Here is what I can do:

[0-5 min]
- R3 PickupLightObject (r3_s1)

[5-10 min]
- R3 can_navigate to the light switch (r3_s2)

[10-15 min]
- R3 Turn off Mobile_Light to create a better movie-watching ambiance (r3_s3)

If there are any other specific actions you would like me to consider, please let me know!

[0-5 min]
- R4 turns off the bathroom light to save energy for the movie. (r4_s1)
```

### LaMMA-P (TF=6 PF=1 OC=1 SC=2 Final=2.65)

```
### Joint Plan

[0-5 min]
- R3 goes to the light switch (r3_s1)
- R4 goes to the curtains (r4_s1)
- R3 goes to the television (r3_s2)
- R4 goes to the media player (r4_s2)
- R1 goes to the kitchen (r1_s1)

[5-10 min]
- R3 turns off the main lights (r3_s3)
- R4 opens the curtains (r4_s3)
- R3 turns on the television (r3_s4)
- R4 turns on the media player (r4_s4)
- R1 picks up snacks (r1_s2)

[10-15 min]
- R3 goes to the floor lamp (r3_s5)
- R1 goes to the living room (r1_s3)

[15-20 min]
- R3 turns on the ambient lighting (r3_s6)
- R1 places snacks on the coffee table (r1_s4)

[20-25 min]
- R4 goes to the fridge (r4_s5)

[25-30 min]
- R4 opens the fridge (r4_s6)
- R4 picks up drinks (r4_s7)
- R4 goes to the living room (r4_s8)
- R4 places drinks on the coffee table (r4_s9)
```

### SMART-LLM (TF=4 PF=2 OC=2 SC=5 Final=3.05)

```
### Joint Plan

[0-5 min]
- R4 go to the Television (r4_s1)
- R4 switch on the Television (r4_s2)
- R4 go to the Sofa (r4_s3)

[0-5 min]
- R2 go to the Popcorn (r2_s1)
- R2 pick up the Popcorn (r2_s2)
- R2 go to the Microwave (r2_s3)

[5-10 min]
- R2 open the Microwave (r2_s4)
- R2 put Popcorn in the Microwave (r2_s5)
- R2 close the Microwave (r2_s6)
- R2 switch on the Microwave (r2_s7)

[10-15 min]
- R2 wait for popcorn to pop (r2_s8)

[15-20 min]
- R2 switch off the Microwave (r2_s9)
- R2 open the Microwave (r2_s10)
- R2 pick up the Popcorn (r2_s11)
- R2 go to the CounterTop (r2_s12)
- R2 put the Popcorn on the CounterTop (r2_s13)

[20-25 min]
- R2 go to the Drinks (r2_s14)
- R2 pick up the Drinks (r2_s15)
- R2 put the Drinks on the CounterTop (r2_s16)

[25-30 min]
- R4 go to the RemoteControl (r4_s4)
- R4 pick up the RemoteControl (r4_s5)
- R4 go to the LightSwitch (r4_s6)
- R4 switch off the LightSwitch (r4_s7)
```

## Run 2

### Ours (CDA) (TF=8 PF=7 OC=4 SC=5 Final=5.95)

```
### Joint Plan — task5_abstract  (about 10 min / deadline 30 min: OK)

[0-5 min]
- R1 [LOCAL] slice the Bread with the Knife into ready-to-eat snack portions  (r1_s1)
- R2 [LOCAL] move the Books or papers on the small table from the Small wooden desk or side table to the Small dark cabinet or stand  (r2_s1)
- R1 [PASS] pass Bread to R2 (offered) (hands it over; R2 collects it)  (r1_s2)
- R2 [LOCAL] arrange the Sofa cushions and pillows on the Large sofa for comfortable movie seating  (r2_s2)

[5-10 min]
- R2 [LOCAL] fold the Blue throw blanket and place it within reach on the Large sofa  (r2_s3)
- R2 [RECEIVE] receive Bread (one lightweight serving, sliced and ready to eat) from R1 (collects it from the kitchen)  (r2_s4)
- R2 [LOCAL] move the Bread from the handoff to the cleared Small wooden desk or side table  (r2_s5)
```

### Centralized (TF=4 PF=2 OC=3 SC=2 Final=2.95)

```
[0-5 min]
- R1 SliceObject (Slice the tomato) (r1_s1)

[5-10 min]
- R1 PickupLightObject (Pick up the sliced tomato) (r1_s2)

[10-15 min]
- R1 PourObject (Pour drinks from the coffee machine into a cup) (r1_s3)

[15-20 min]
- R1 PassReceiveObject (Pass the sliced tomato and drink to R2) (r1_s4)

[0-5 min]
- R2 navigate to the kitchen to meet R1 (r2_s1)

[5-10 min]
- R2 receive snacks and drinks from R1 (r2_s2)

[10-15 min]
- R2 navigate back to the living room with snacks and drinks (r2_s3)

[15-20 min]
- R2 place snacks and drinks on the table in the living room (r2_s4)

[0-5 min]
- R3 can_navigate to the bed and straighten the blankets. (r3_s1)

[5-10 min]
- R3 can_navigate to the desk and organize any light objects, such as papers or small items. (r3_s2)

[10-15 min]
- R3 can_navigate to the trash bin and ensure it is not overflowing. (r3_s3)

[15-20 min]
- R3 can_navigate to the door and proceed to the living room to assist further if needed. (r3_s4)

I can't see the living room from here, but I can outline a general plan based on my capabilities:

[0-5 min]
- R4 can_navigate to the living room. (r4_s1)

[5-10 min]
- R4 assess the living room layout to identify heavy furniture that can be moved to optimize the viewing experience. (r4_s2)

[10-20 min]
- R4 PushFurniture to rearrange heavy furniture for optimal viewing. (r4_s3)

[20-25 min]
- R4 ensure all furniture is stable and the viewing area is clear. (r4_s4)

[25-30 min]
- R4 return to the bathroom or standby mode. (r4_s5)
```

### Independent (TF=3 PF=1 OC=2 SC=2 Final=2.1)

```
[0-5 min]
- R1 turns on the coffee maker to prepare coffee for the movie. (r1_s1)

[5-10 min]
- R1 slices the lemon on the counter for potential use as a garnish or in drinks. (r1_s2)

[10-15 min]
- R1 cleans the sink area using the dish sponge to ensure the kitchen is tidy. (r1_s3)

[15-20 min]
- R1 pours water into a glass for hydration during the movie. (r1_s4)

[20-25 min]
- R1 places the prepared coffee and sliced lemon on the counter for easy access. (r1_s5)

[25-30 min]
- R1 ensures all appliances are turned off and the kitchen is tidy. (r1_s6)

[0-5 min]
- R2 Turn on the TV for the movie. (r2_s1)

[5-10 min]
- R2 Adjust the curtains to reduce glare on the TV. (r2_s2)

[10-15 min]
- R2 Arrange the seating area for optimal viewing. (r2_s3)

[15-20 min]
- R2 Ensure the lighting is dimmed for a better movie experience. (r2_s4)

[20-25 min]
- R2 Check that the remote control is accessible on the coffee table. (r2_s5)

[25-30 min]
- R2 Tidy up any clutter around the seating area. (r2_s6)

[0-5 min]
- R3 Turn on the mobile light for better ambiance. (r3_s1)

[5-10 min]
- R3 Adjust the bed covers to tidy up the room. (r3_s2)

[10-15 min]
- R3 Ensure the window is closed for a quiet environment. (r3_s3)

[15-20 min]
- R3 Turn off the computer to minimize distractions. (r3_s4)

[20-25 min]
- R3 Arrange the chairs neatly. (r3_s5)

[25-30 min]
- R3 Ensure the trash bin is not overflowing. (r3_s6)

[0-5 min]
- R4 turns off the bathroom light to save energy for the movie. (r4_s1)
```

### LaMMA-P (TF=5 PF=1 OC=1 SC=4 Final=2.65)

```
### Joint Plan

[0-5 min]
- R4 goes to the living room (r4_s1)
- R3 goes to the television (r3_s1)
- R1 goes to the kitchen (r1_s1)

[5-10 min]
- R4 cleans the viewing area (r4_s2)
- R3 turns on the television (r3_s2)
- R1 picks up snacks (r1_s2)

[10-15 min]
- R4 arranges the seating (r4_s3)
- R3 goes to the remote control (r3_s3)
- R1 goes to the living room (r1_s3)

[15-20 min]
- R3 turns on the sound system (r3_s4)
- R1 places snacks on the table (r1_s4)

[20-25 min]
- R3 goes to the light switch (r3_s5)

[25-30 min]
- R3 dims or turns off the lights (r3_s6)
- R4 goes to the living room for final check (r4_s4)
- R4 verifies everything is ready (r4_s5)
```

### SMART-LLM (TF=3 PF=1 OC=2 SC=2 Final=2.1)

```
### Joint Plan

[0-5 min]
- R4 go to Television (r4_s1)
- R4 switch on Television (r4_s2)
- R4 go to Sofa (r4_s3)

[5-10 min]
- R3 go to RemoteControl (r3_s1)
- R3 pick up RemoteControl (r3_s2)
- R3 navigate to movie (r3_s3)
- R3 put RemoteControl on SideTable (r3_s4)

[10-15 min]
- R1 go to Kitchen (r1_s1)
- R1 go to Popcorn (r1_s2)
- R1 pick up Popcorn (r1_s3)
- R1 go to Microwave (r1_s4)
- R1 open Microwave (r1_s5)
- R1 put Popcorn in Microwave (r1_s6)
- R1 close Microwave (r1_s7)
- R1 switch on Microwave (r1_s8)

[15-20 min]
- R1 wait for popcorn to pop (r1_s9)
- R1 switch off Microwave (r1_s10)
- R1 open Microwave (r1_s11)
- R1 take out Popcorn (r1_s12)
- R1 close Microwave (r1_s13)

[20-25 min]
- R1 go to CounterTop (r1_s14)
- R1 put Popcorn on CounterTop (r1_s15)
- R1 go to Drinks (r1_s16)
- R1 pick up Drinks (r1_s17)

[25-30 min]
- R1 go to CounterTop (r1_s18)
- R1 put Drinks on CounterTop (r1_s19)
```

## Run 3

### Ours (CDA) (TF=4 PF=5 OC=7 SC=3 Final=5.1)

```
### Joint Plan — task5_abstract  (about 5 min / deadline 30 min: OK)

[0-5 min]
- R2 [LOCAL] arrange the Sofa cushions against the back of the Sofa for comfortable viewing  (r2_s1)
- R2 [LOCAL] fold the Blue throw blanket and place it over an arm of the Sofa within easy reach  (r2_s2)
- R2 [LOCAL] move the Television remote control on the media console from the Wooden media console to the Side table beside the Sofa  (r2_s3)
```

### Centralized (TF=2 PF=2 OC=2 SC=2 Final=2.0)

```
[0-5 min]
- R1 PickupLightObject (lettuce) from the sink. (r1_s1)

[5-10 min]
- R1 SliceObject (lettuce) using the knife. (r1_s2)

[10-15 min]
- R1 PourObject (water) into a cup from the sink. (r1_s3)

[15-20 min]
- R1 PassReceiveObject (sliced lettuce and water) to R2. (r1_s4)

[0-5 min]
- R2 navigate to the kitchen to meet R1 (r2_s1)

[5-10 min]
- R2 receive snacks and drinks from R1 (r2_s2)

[10-15 min]
- R2 navigate back to the living room (r2_s3)

[15-20 min]
- R2 place snacks and drinks on the table in the living room (r2_s4)

[0-5 min]
- R3 can_navigate to the door and exit the bedroom. (r3_s1)

[5-10 min]
- R3 can_navigate to the living room. (r3_s2)

[10-15 min]
- R3 PickupLightObject any small items on the floor in the living room and place them in their appropriate locations. (r3_s3)

[15-20 min]
- R3 can_navigate to the coffee table and ensure it is clear of clutter. (r3_s4)

[20-25 min]
- R3 can_navigate to the seating area and arrange any cushions or blankets neatly. (r3_s5)

[25-30 min]
- R3 can_navigate to the light switch and adjust the lighting for a comfortable movie-watching environment. (r3_s6)

I'm unable to see the living room from the images provided, but I can outline a general plan based on my capabilities and the task requirements.

[0-5 min]
- R4 navigate from the bathroom to the living room. (r4_s1)

[5-10 min]
- R4 assess the living room for any heavy furniture that might need moving to optimize the viewing experience. (r4_s2)

[10-20 min]
- R4 push or reposition any heavy furniture as needed to ensure a clear view of the screen and comfortable seating arrangement. (r4_s3)

[20-25 min]
- R4 ensure all pathways are clear and the living room is tidy for the movie viewing. (r4_s4)

[25-30 min]
- R4 return to the bathroom or standby mode as needed. (r4_s5)
```

### Independent (TF=2 PF=1 OC=5 SC=2 Final=2.85)

```
[0-5 min]
- R1 turns on the coffee maker to prepare coffee for the movie. (r1_s1)

[5-10 min]
- R1 slices the lemon on the counter for potential use as a garnish or in drinks. (r1_s2)

[10-15 min]
- R1 cleans the sink area using the dish sponge to ensure the kitchen is tidy. (r1_s3)

[15-20 min]
- R1 pours water into a glass for hydration during the movie. (r1_s4)

[20-25 min]
- R1 places the prepared coffee and sliced lemon on the counter for easy access. (r1_s5)

[25-30 min]
- R1 ensures all appliances are turned off and the kitchen is tidy before the movie starts. (r1_s6)

[0-5 min]
- R2 Turn on the TV for the movie. (r2_s1)

[5-10 min]
- R2 Adjust the curtains to reduce glare on the TV. (r2_s2)

[10-15 min]
- R2 Arrange the seating area for optimal viewing. (r2_s3)

[15-20 min]
- R2 Ensure the remote control is accessible on the coffee table. (r2_s4)

[20-25 min]
- R2 Dim the lights for a better movie-watching experience. (r2_s5)

[25-30 min]
- R2 Check that the sound system is on and set to the correct input. (r2_s6)

[0-5 min]
- R3 Turn on the mobile light for better ambiance. (r3_s1)

[5-10 min]
- R3 Tidy up the bed to make the room more comfortable. (r3_s2)

[10-15 min]
- R3 Ensure the window is closed to minimize outside noise. (r3_s3)

[15-20 min]
- R3 Adjust the chair near the desk for potential use. (r3_s4)

[20-25 min]
- R3 Check that the TV is ready for viewing. (r3_s5)

[25-30 min]
- R3 Turn off any unnecessary lights to focus on the screen. (r3_s6)

[0-5 min]
- R4 turns off the bathroom light to save energy during the movie. (r4_s1)
```

### LaMMA-P (TF=3 PF=1 OC=2 SC=3 Final=2.25)

```
### Joint Plan

[0-5 min]
- R4 move to living room (r4_s1)
- R3 move to remote control location (r3_s1)
- R1 move to kitchen for snacks (r1_s1)

[5-10 min]
- R4 clean viewing area (r4_s2)
- R3 pick up remote control (r3_s2)
- R1 gather snacks (r1_s2)

[10-15 min]
- R4 turn on TV and devices (r4_s3)
- R3 turn on streaming device (r3_s3)
- R1 prepare snacks in microwave (r1_s3)

[15-20 min]
- R3 navigate to movie selection and select movie (r3_s4)
- R4 move to fridge for drinks (r4_s4)
- R1 move back to viewing area with snacks (r1_s4)

[20-25 min]
- R4 gather drinks and return to viewing area (r4_s5)
- R3 adjust lighting for optimal viewing (r3_s5)
- R1 arrange pillows and blankets (r1_s5)

[25-30 min]
- R3 perform final check around viewing area (r3_s6)
- R4 adjust temperature for comfort (r4_s6)
- R1 ensure comfort settings are optimal (r1_s6)
```

### SMART-LLM (TF=7 PF=1 OC=2 SC=4 Final=3.6)

```
### Joint Plan

[0-5 min]
- R4 go to the television (r4_s1)
- R4 switch on the television (r4_s2)
- R4 adjust pillows on the sofa (r4_s3)

[5-10 min]
- R4 go to the television or streaming device (r4_s4)
- R4 select the movie to watch (r4_s5)

[0-5 min]
- R1 go to the kitchen (r1_s1)
- R1 pick up popcorn (r1_s2)
- R1 go to the microwave (r1_s3)
- R1 open the microwave (r1_s4)
- R1 put popcorn in the microwave (r1_s5)
- R1 close the microwave (r1_s6)
- R1 switch on the microwave (r1_s7)

[5-10 min]
- R1 wait for popcorn to pop (r1_s8)
- R1 switch off the microwave (r1_s9)
- R1 open the microwave (r1_s10)
- R1 pick up popcorn (r1_s11)

[10-15 min]
- R1 pick up soda (r1_s12)
- R1 go to the coffee table (r1_s13)
- R1 put popcorn on the coffee table (r1_s14)
- R1 put soda on the coffee table (r1_s15)

[25-30 min]
- R4 go to the light switch (r4_s6)
- R4 switch off the lights (r4_s7)
```

# task6_abstract

> I need to prepare the living room for a home workout in 20 minutes. Clear the space and make sure everything else is ready too.

## Run 1

### Ours (CDA) (TF=3 PF=4 OC=4 SC=2 Final=3.4)

```
### Joint Plan — task6_abstract  (about 25 min / deadline 20 min: MISSED)

[0-5 min]
- R2 [LOCAL] move the White paper shopping bag from the Glass coffee table to the Black desk outside the workout zone  (r2_s1)
- R4 [LOCAL] pick up and fold the Brown bath towel in the bathroom so it is ready for use as the workout sweat towel  (r4_s1)
- R2 [LOCAL] move the left Yellow bottle or container from the Glass coffee table to the Black desk outside the workout zone  (r2_s2)
- R4 [PASS] pass Brown bath towel to R2 (offered) (brings it to the living room)  (r4_s2)
- R2 [LOCAL] move the right Yellow bottle or container from the Glass coffee table to the Black desk outside the workout zone  (r2_s3)

[5-10 min]
- R4 [HELP] roll up and move the Living-room area rug from the central workout floor to the room perimeter (help R2 in the living room)  (r4_s6)

[10-15 min]
- R4 [HELP] move the right reddish accent chair from the central workout area to the room perimeter (help R2 in the living room)  (r4_s5)

[15-20 min]
- R2 [ASK_HELP] wait for R4 to: push the cleared Glass coffee table away from the central workout floor to the room perimeter  (r2_s4)
- R4 [HELP] move the left reddish accent chair from the central workout area to the room perimeter (help R2 in the living room)  (r4_s4)
- R4 [HELP] move the cleared Glass coffee table from the central workout floor to the room perimeter (help R2 in the living room) [after r2_s1, r2_s2, r2_s3]  (r4_s3)
- R2 [ASK_HELP] wait for R4 to: push the left reddish accent chair from the central workout area to the room perimeter  (r2_s5)
- R2 [ASK_HELP] wait for R4 to: push the right reddish accent chair from the central workout area to the room perimeter  (r2_s6)
- R2 [ASK_HELP] wait for R4 to: roll up the Living-room area rug and clear it from the central workout floor  (r2_s7)

[20-25 min]
- R2 [LOCAL] relocate any light loose workout hazard exposed on the central floor to the Black desk outside the workout zone  (r2_s10)
- R2 [RECEIVE] receive Brown bath towel (one clean towel suitable for use as a workout sweat towel) from R4  (r2_s8)
- R2 [LOCAL] place the Brown bath towel at the perimeter of the cleared workout area  (r2_s11)
```

### Centralized (TF=2 PF=3 OC=2 SC=2 Final=2.2)

```
[0-5 min]
- R1 PickupLightObject: Cup from the shelf (r1_s1)

[5-10 min]
- R1 PickupLightObject: Plate from the shelf (r1_s2)

[10-15 min]
- R1 PickupLightObject: Knife from the counter (r1_s3)

[15-20 min]
- R1 PassReceiveObject: Pass Cup, Plate, and Knife to R2 when it arrives (r1_s4)

[0-5 min]
- R2 navigate to the coffee table area (r2_s1)

[5-10 min]
- R2 PickupLightObject (e.g., bottles, magazines) from the coffee table (r2_s2)

[10-15 min]
- R2 move light objects to a designated storage area (r2_s3)

[15-20 min]
- R2 receive any necessary items from R1 (r2_s4)

[0-5 min]
- R3 can_navigate to the bedroom door (r3_s1)

[5-10 min]
- R3 can_navigate to any light objects in the bedroom (r3_s2)

[10-15 min]
- R3 PickupLightObject and carry it to the living room (r3_s3)

[15-20 min]
- R3 can_navigate back to the bedroom to check for more light objects (r3_s4)

[0-5 min]
- R4 navigate to the living room (r4_s1)

[5-10 min]
- R4 push any heavy furniture out of the way to clear space (r4_s2)

[10-15 min]
- R4 pick up any light objects on the floor and place them aside (r4_s3)

[15-20 min]
- R4 ensure the space is clear and ready for the workout (r4_s4)
```

### Independent (TF=2 PF=1 OC=2 SC=1 Final=1.65)

```
[0-5 min]
- R1 SliceObject (lettuce) for a healthy post-workout snack. (r1_s1)

[5-10 min]
- R1 PourObject (water into a cup) for hydration. (r1_s2)

[10-15 min]
- R1 PickupLightObject (cup) and place it on the counter for easy access. (r1_s3)

[15-20 min]
- R1 Ensure all appliances are turned off for safety. (r1_s4)

[0-5 min]
- R2 PickupLightObject (remove items from the coffee table) (r2_s1)

[5-10 min]
- R2 can_navigate (move small items to a corner) (r2_s2)

[10-15 min]
- R2 can_navigate (ensure the floor is clear for workout space) (r2_s3)

[15-20 min]
- R2 can_navigate (turn off the lamp for safety) (r2_s4)

I'm unable to view images, but based on the description of your capabilities and the task at hand, I will proceed with the assumption that I need to ensure the bedroom is in a state that supports the preparation of the living room for a workout. Since I can only interact with light objects and navigate, I will focus on ensuring the bedroom is tidy and any portable items that might be needed in the living room are ready.

[0-5 min]
- R3 PickupLightObject (e.g., any small items like clothes or books on the floor) and place them neatly on a surface to ensure the bedroom is tidy. (r3_s1)

[5-10 min]
- R3 Ensure the Mobile_Light is turned off if not needed, to conserve energy for the workout session. (r3_s2)

[10-15 min]
- R3 Check for any portable workout-related items (e.g., yoga mat, resistance bands) that might be in the bedroom and place them near the door for easy access to the living room. (r3_s3)

[15-20 min]
- R3 Final check to ensure the bedroom is tidy and nothing is obstructing the path to the living room. (r3_s4)

[0-5 min]
- R4 Close shower curtain to tidy the bathroom. (r4_s1)

[5-10 min]
- R4 Ensure all toiletries are neatly arranged on the shelf. (r4_s2)

[10-15 min]
- R4 Empty trash can if full to maintain cleanliness. (r4_s3)

[15-20 min]
- R4 Turn off bathroom lights to save energy. (r4_s4)
```

### LaMMA-P (TF=3 PF=2 OC=2 SC=3 Final=2.45)

```
### Joint Plan

[0-5 min]
- R4 move vases and pillows to storage (r4_s1)
- R1 gather lighter workout equipment (r1_s1)

[5-10 min]
- R4 move small electronics to storage (r4_s2)
- R1 place workout equipment in designated area (r1_s2)

[10-15 min]
- R4 continue clearing space if needed (r4_s3)
- R1 assist with any remaining equipment setup (r1_s3)

[15-20 min]
- R3 adjust lighting (r3_s1)
- R3 set up music or timer (r3_s2)
```

### SMART-LLM (TF=4 PF=1 OC=2 SC=4 Final=2.7)

```
### Joint Plan

[0-5 min]
- R1 move chair to corner (r1_s1)
- R1 move coffee table to corner (r1_s2)

[5-10 min]
- R3 bring yoga mat to center of room (r3_s1)
- R3 bring dumbbells to center of room (r3_s2)

[10-15 min]
- R1 switch on light (r1_s3)

[15-20 min]
- R1 switch on speaker (r1_s4)
```

## Run 2

### Ours (CDA) (TF=5 PF=9 OC=8 SC=8 Final=7.3)

```
### Joint Plan — task6_abstract  (about 10 min / deadline 20 min: OK)

[0-5 min]
- R1 [PASS] fill one Drinking glasses with drinking water at the sink and pass it to R2 -> R2 (hands it over; R2 collects it)  (r1_s3)
- R2 [LOCAL] move the White vase or pitcher from the Glass coffee table to the Dining table  (r2_s1)
- R4 [LOCAL] pick up the Brown towel in the bathroom and prepare it for use as the workout sweat towel  (r4_s1)
- R2 [LOCAL] move the Loose papers or napkins on the coffee table from the Glass coffee table to the Desk  (r2_s2)
- R4 [PASS] pass Brown towel to R2 (offered) (brings it to the living room)  (r4_s2)
- R2 [LOCAL] move the first Yellow bottles on the coffee table bottle from the Glass coffee table to the Dining table  (r2_s3)
- R2 [LOCAL] move the second Yellow bottles on the coffee table bottle from the Glass coffee table to the Dining table  (r2_s4)
- R2 [RECEIVE] receive Brown towel (one clean, dry towel) from R4  (r2_s5)

[5-10 min]
- R2 [LOCAL] place the Brown towel at the edge of the cleared workout area  (r2_s7)
- R2 [RECEIVE] receive Drinking glasses (one glass filled with drinking water) from R1 (collects it from the kitchen)  (r2_s6)
- R2 [LOCAL] place the filled Drinking glasses at the edge of the cleared workout area  (r2_s8)
```

### Centralized (TF=2 PF=3 OC=2 SC=2 Final=2.2)

```
[0-5 min]
- R1 PickupLightObject: Cup from the shelf (r1_s1)

[5-10 min]
- R1 PickupLightObject: Plate from the shelf (r1_s2)

[10-15 min]
- R1 PickupLightObject: Knife from the counter (r1_s3)

[15-20 min]
- R1 PassReceiveObject: Pass Cup, Plate, and Knife to R2 when it arrives (r1_s4)

[0-5 min]
- R2 navigate to the coffee table and pickup light objects like the bottle and any small items. (r2_s1)

[5-10 min]
- R2 place the picked-up items in a designated storage area or corner. (r2_s2)

[10-15 min]
- R2 navigate to the desk area and pickup light objects like the notebook and keys. (r2_s3)

[15-20 min]
- R2 place these items in the designated storage area or corner. (r2_s4)

- R2 ready to receive any necessary items from R1. (r2_s5)

[0-5 min]
- R3 navigate to the desk and pick up the teddy bear. (r3_s1)

[5-10 min]
- R3 move the teddy bear to the living room. (r3_s2)

[10-15 min]
- R3 return to the bedroom and pick up the book from the desk. (r3_s3)

[15-20 min]
- R3 move the book to the living room. (r3_s4)

[0-5 min]
- R4 can_navigate to the living room (r4_s1)

[5-10 min]
- R4 push any heavy furniture out of the way (r4_s2)

[10-15 min]
- R4 pickup light objects and move them to clear the space (r4_s3)

[15-20 min]
- R4 assist with any additional clearing or organizing as needed (r4_s4)
```

### Independent (TF=2 PF=1 OC=4 SC=2 Final=2.5)

```
[0-5 min]
- R1 SliceObject (lettuce) for a healthy post-workout snack. (r1_s1)

[5-10 min]
- R1 PourObject (water into a cup) for hydration during the workout. (r1_s2)

[10-15 min]
- R1 PickupLightObject (cup with water) and place it on the counter for easy access. (r1_s3)

[15-20 min]
- R1 Ensure all appliances are turned off for safety. (r1_s4)

[0-5 min]
- R2 PickupLightObject (remove items from the coffee table)  (r2_s1)

[5-10 min]
- R2 can_navigate (move small items to a corner)  (r2_s2)

[10-15 min]
- R2 can_navigate (ensure the floor is clear for workout space)  (r2_s3)

[15-20 min]
- R2 can_navigate (turn off the TV to avoid distractions)  (r2_s4)

[0-5 min]
- R3 PickupLightObject (dumbbell) from the desk and place it on the bed. (r3_s1)

[5-10 min]
- R3 PickupLightObject (tennis racket) from the floor and place it on the bed. (r3_s2)

[10-15 min]
- R3 PickupLightObject (book) from the desk and place it on the bed. (r3_s3)

[15-20 min]
- R3 PickupLightObject (lamp) and turn it off. (r3_s4)

[0-5 min]
- R4 Close shower curtain to tidy the bathroom. (r4_s1)

[5-10 min]
- R4 Ensure all items on the sink are organized. (r4_s2)

[10-15 min]
- R4 Empty trash can if full to maintain cleanliness. (r4_s3)

[15-20 min]
- R4 Turn off bathroom lights to save energy. (r4_s4)
```

### LaMMA-P (TF=2 PF=3 OC=2 SC=2 Final=2.2)

```
### Joint Plan

[0-5 min]
- R3 Move objects to storage (r3_s1)
- R4 Move heavier objects to storage (r4_s1)
- R3 Start cleaning the floor (r3_s2)

[5-10 min]
- R3 Continue cleaning the floor (r3_s3)
- R4 Continue moving objects to storage (r4_s2)

[10-15 min]
- R4 Finish moving objects to storage (r4_s3)
- R3 Finish cleaning the floor (r3_s4)

[15-20 min]
- R3 Set up workout equipment (r3_s5)
- R4 Assist with setting up workout equipment (r4_s4)
```

### SMART-LLM (TF=2 PF=1 OC=1 SC=2 Final=1.45)

```
### Joint Plan

[0-5 min]
- R1 move Sofa to StorageRoom (r1_s1)
- R4 move CoffeeTable to StorageRoom (r4_s1)

[5-10 min]
- R1 move DiningTable to StorageRoom (r1_s2)
- R4 move Chair to StorageRoom (r4_s2)

[10-15 min]
- R1 move ArmChair to StorageRoom (r1_s3)
- R4 move Vase to StorageRoom (r4_s3)

[15-20 min]
- R1 move Statue to StorageRoom (r1_s4)
- R4 move YogaMat to WorkoutArea (r4_s4)

[20-25 min]
- R4 move Dumbbells to WorkoutArea (r4_s5)
- R4 move ResistanceBands to WorkoutArea (r4_s6)

[25-30 min]
- R4 adjust lighting (r4_s7)
```

## Run 3

### Ours (CDA) (TF=3 PF=9 OC=9 SC=3 Final=6.3)

```
### Joint Plan — task6_abstract  (about 10 min / deadline 20 min: OK)

[0-5 min]
- R2 [LOCAL] move the White decorative vase or container from the Glass coffee table or workout area to a safe living-room perimeter surface  (r2_s1)
- R4 [LOCAL] take the Brown hanging towel down from its bathroom hook and prepare it for the workout handoff  (r4_s1)
- R2 [LOCAL] move the first of the Two yellow bottles from the Glass coffee table or workout area to the living-room perimeter  (r2_s2)
- R4 [PASS] pass Brown hanging towel to R2 (offered) (brings it to the living room)  (r4_s2)
- R2 [LOCAL] move the second of the Two yellow bottles from the Glass coffee table or workout area to the living-room perimeter  (r2_s3)
- R2 [LOCAL] move the Small gray cup or container from the Glass coffee table or workout area to a safe living-room perimeter surface  (r2_s4)
- R2 [LOCAL] move the Red throw pillow off the intended workout floor and place it on the Sectional sofa  (r2_s5)

[5-10 min]
- R2 [LOCAL] move the Light-colored throw pillow off the intended workout floor and place it on the Sectional sofa  (r2_s6)
- R2 [RECEIVE] receive Brown hanging towel (one clean, dry Brown hanging towel) from R4  (r2_s14)
- R2 [LOCAL] place the Brown hanging towel beside the cleared workout area  (r2_s15)
```

### Centralized (TF=2 PF=3 OC=2 SC=2 Final=2.2)

```
[0-5 min]
- R1 PickupLightObject: Cup from the shelf (r1_s1)

[5-10 min]
- R1 PickupLightObject: Plate from the shelf (r1_s2)

[10-15 min]
- R1 PickupLightObject: Knife from the counter (r1_s3)

[15-20 min]
- R1 PassReceiveObject: Pass Cup, Plate, and Knife to R2 when it arrives (r1_s4)

[0-5 min]
- R2 navigate to the coffee table and pick up any light objects (e.g., bottles, magazines). (r2_s1)

[5-10 min]
- R2 place the picked-up objects in a designated storage area or another room. (r2_s2)

[10-15 min]
- R2 navigate to the desk area and pick up any light objects (e.g., keys, small electronics). (r2_s3)

[15-20 min]
- R2 place these objects in a designated storage area or another room. (r2_s4)
- R2 receive any workout items from R1. (r2_s5)

[0-5 min]
- R3 navigate to the desk and pick up the teddy bear (r3_s1).

[5-10 min]
- R3 move the teddy bear to the living room and place it in a designated area (r3_s2).

[10-15 min]
- R3 navigate to the table and pick up the badminton racket (r3_s3).

[15-20 min]
- R3 move the badminton racket to the living room and place it in a designated area (r3_s4).

[0-5 min]
- R4 navigate to the living room (r4_s1)

[5-10 min]
- R4 push any heavy furniture out of the way to clear space (r4_s2)

[10-15 min]
- R4 pick up any light objects on the floor and place them aside (r4_s3)

[15-20 min]
- R4 ensure the living room is clear and ready for the workout (r4_s4)
```

### Independent (TF=2 PF=1 OC=7 SC=2 Final=3.55)

```
[0-5 min]
- R1 SliceObject (lettuce) for a healthy post-workout snack. (r1_s1)

[5-10 min]
- R1 PourObject (water into a cup) for hydration. (r1_s2)

[10-15 min]
- R1 PickupLightObject (cup) and place it on the counter for easy access. (r1_s3)

[15-20 min]
- R1 Ensure all kitchen appliances are turned off for safety. (r1_s4)

[0-5 min]
- R2 PickupLightObject (remove items from the coffee table) (r2_s1)

[5-10 min]
- R2 can_navigate (move small items to a corner to clear space) (r2_s2)

[10-15 min]
- R2 can_navigate (ensure the floor is clear for workout space) (r2_s3)

[15-20 min]
- R2 can_navigate (turn off the lamp to create a focused workout environment) (r2_s4)

[0-5 min]
- R3 PickupLightObject (dumbbell) from the desk and place it on the bed. (r3_s1)

[5-10 min]
- R3 PickupLightObject (tennis racket) from the floor and place it on the bed. (r3_s2)

[10-15 min]
- R3 PickupLightObject (notebook) from the desk and place it on the bed. (r3_s3)

[15-20 min]
- R3 PickupLightObject (lamp) and turn it off. (r3_s4)

[0-5 min]
- R4 Close shower curtain to tidy the bathroom. (r4_s1)

[5-10 min]
- R4 Ensure all items on the sink are organized. (r4_s2)

[10-15 min]
- R4 Empty trash can if full to maintain cleanliness. (r4_s3)

[15-20 min]
- R4 Turn off bathroom lights to save energy. (r4_s4)
```

### LaMMA-P (TF=2 PF=1 OC=1 SC=2 Final=1.45)

```
### Joint Plan

[0-5 min]
- R4 move small items to storage (r4_s1)
- R1 move chairs to storage (r1_s1)
- R3 prepare workout equipment (r3_s1)

[5-10 min]
- R4 move vases to storage (r4_s2)
- R1 move coffee table to storage (r1_s2)
- R3 arrange equipment in workout area (r3_s2)

[10-15 min]
- R4 assist with remaining small items (r4_s3)
- R1 ensure all large items are cleared (r1_s3)
- R3 check for hazards (r3_s3)

[15-20 min]
- R4 switch off unnecessary devices (r4_s4)
- R1 finalize space clearing (r1_s4)
- R3 clean any spills or slippery surfaces (r3_s4)
```

### SMART-LLM (TF=2 PF=1 OC=5 SC=3 Final=3.0)

```
### Joint Plan

[0-5 min]
- R1 move chair to side (r1_s1)
- R1 move coffee table to side (r1_s2)
- R1 move armchair to side (r1_s3)

[5-10 min]
- R3 place yoga mat on floor (r3_s1)

[10-15 min]
- R2 clean floor (r2_s1)

[15-20 min]
- R4 turn on lights (r4_s1)
```

# task7_abstract

> A typhoon is coming in 10 minutes. Seal up the house completely.

## Run 1

### Ours (CDA) (TF=1 PF=5 OC=7 SC=1 Final=3.9)

```
### Joint Plan — task7_abstract  (about 5 min / deadline 10 min: OK)

[0-5 min]
- R5 [LOCAL] push the bedroom window fully shut and secure its reachable latch or lock  (r5_s1)
- R6 [LOCAL] move the Metal rolling storage cart away from the approach to the bathroom exterior window  (r6_s1)
- R5 [LOCAL] lower the Window blind over the secured bedroom window  (r5_s2)
```

### Centralized (TF=1 PF=3 OC=2 SC=2 Final=1.9)

```
[0-5 min]
- R1 PickupLightObject (r1_s1): Pick up the apple from the counter.

[5-10 min]
- R1 PassReceiveObject (r1_s2): Pass the apple to R2 for sealing.

[0-5 min]
- R2 navigate to R1 to collect light objects. (r2_s1)

[5-10 min]
- R2 receive light objects from R1. (r2_s2)

[10-15 min]
- R2 navigate to windows and doors in the kitchen. (r2_s3)

[15-20 min]
- R2 assist in sealing windows and doors using collected light objects. (r2_s4)

[0-5 min]
- R3 PickupLightObject (r3_s1): Pick up the laptop from the table.

[5-10 min]
- R3 PassReceiveObject (r3_s2): Pass the laptop to R4 for sealing.

[0-2 min]
- R4 navigate to R3 to collect light objects (r4_s1)

[2-5 min]
- R4 PickupLightObject from R3 (r4_s2)

[5-8 min]
- R4 navigate to windows and doors in the living room (r4_s3)

[8-10 min]
- R4 use collected light objects to assist in sealing windows and doors (r4_s4)

[0-5 min]
- R5 navigate to the dresser near the window (r5_s1).

[5-10 min]
- R5 push the dresser against the window to secure it (r5_s2).

[0-5 min]
- R6 navigate to the towel rack and pick up the towel. (r6_s1)

[5-10 min]
- R6 push the towel rack against the window to secure it. (r6_s2)
```

### Independent (TF=1 PF=1 OC=1 SC=2 Final=1.15)

```
[0-5 min]
- R1 Close the window (r1_s1)

[0-5 min]
- R2 Close all windows in the kitchen (r2_s1)

[5-10 min]
- R2 Close all cabinet doors in the kitchen (r2_s2)

[0-5 min]
- R3 Close curtains (r3_s1)

[0-5 min]
- R4 closes all windows and curtains in the living room to seal the room against the typhoon. (r4_s1)

[0-5 min]
- R5 close window blinds to seal the room (r5_s1)

[0-5 min]
- R6 close both windows to seal the bathroom. (r6_s1)
```

### LaMMA-P (TF=2 PF=1 OC=2 SC=2 Final=1.8)

```
### Joint Plan

[0-5 min]
- R4 Go to each window (r4_s1)
- R6 Go to each door (r6_s1)
- R3 Go to each loose object (r3_s1)

[5-10 min]
- R4 Close each window (r4_s2)
- R6 Close each door (r6_s2)
- R3 Pick up and secure each loose object (r3_s2)

[10-15 min]
- R4 Go to each electrical appliance (r4_s3)
- R6 Go to each electrical appliance (r6_s3)

[15-20 min]
- R4 Switch off each appliance (r4_s4)
- R6 Switch off each appliance (r6_s4)
```

### SMART-LLM (TF=5 PF=2 OC=1 SC=3 Final=2.7)

```
### Joint Plan

[0-5 min]
- R4 close Window1 (r4_s1)
- R4 close Window2 (r4_s2)
- R4 close Window3 (r4_s3)

[0-5 min]
- R6 close FrontDoor (r6_s1)
- R6 close BackDoor (r6_s2)
- R6 close SideDoor (r6_s3)

[5-10 min]
- R4 secure Vent1 (r4_s4)
- R4 secure Skylight1 (r4_s5)
```

## Run 2

### Ours (CDA) (TF=1 PF=3 OC=7 SC=2 Final=3.65)

```
### Joint Plan — task7_abstract  (about 15 min / deadline 10 min: MISSED)

[0-5 min]
- R1 [LOCAL] move the Knife from the counter into the reachable cutting workspace  (r1_s2)
- R2 [LOCAL] move the Potted plant from the kitchen window area to a safe interior counter location  (r2_s1)
- R5 [LOCAL] close and latch the Bedroom window securely  (r5_s1)
- R6 [LOCAL] operate the Bathroom window to fully close and latch it  (r6_s1)
- R5 [LOCAL] move the Gray folded blanket or throw from its storage position and pack it tightly around the closed bedroom window frame to block gaps  (r5_s2)
- R6 [LOCAL] pack the Beige hand towel into visible gaps around the Bathroom window frame  (r6_s2)
- R5 [LOCAL] lower the Bedroom window blind over the secured and draft-blocked window  (r5_s3)

[5-10 min]
- R6 [LOCAL] pack the Cloth into residual visible gaps around the Bathroom window frame  (r6_s3)
- R6 [LOCAL] move the Green toiletry bottle on the cart from the cart to the sink-side area away from the window  (r6_s4)
- R6 [LOCAL] move the Small light-colored toiletry item on the cart from the cart to the sink-side area away from the window  (r6_s5)
- R6 [LOCAL] move the Blue bottle on the cart from the cart to the sink-side area away from the window  (r6_s6)
- R6 [LOCAL] move the Brown bottle on the cart from the cart to the sink-side area away from the window  (r6_s7)

[10-15 min]
- R6 [LOCAL] push the Rolling metal bathroom cart away from the window to an interior wall without blocking the exit  (r6_s8)
```

### Centralized (TF=2 PF=2 OC=3 SC=2 Final=2.35)

```
[0-5 min]
- R1 PickupLightObject (r1_s1): Pick up the cup from the counter.

[5-10 min]
- R1 PassReceiveObject (r1_s2): Pass the cup to R2 for sealing.

[0-5 min]
- R2 navigate to the window in the kitchen to check for any light objects that can be used to seal it. (r2_s1)

[5-10 min]
- R2 pick up the dish sponge and any other light objects available to help seal the window. (r2_s2)

[10-15 min]
- R2 navigate to the door in the kitchen and check for any gaps that can be sealed with light objects. (r2_s3)

[15-20 min]
- R2 use the dish sponge and other light objects to seal any gaps around the door. (r2_s4)

[20-25 min]
- R2 navigate to the next room to assist in sealing windows and doors. (r2_s5)

[0-5 min]
- R3 picks up the laptop from the table. (r3_s1)

[5-10 min]
- R3 passes the laptop to R4 for sealing. (r3_s2)

[0-2 min]
- R4 can_navigate to the windows in the living room (r4_s1).

[2-4 min]
- R4 PickupLightObject to gather any light objects like cushions or small items to use for sealing gaps (r4_s2).

[4-6 min]
- R4 can_navigate to the doors in the living room (r4_s3).

[6-8 min]
- R4 PassReceiveObject to assist in sealing the doors with light objects (r4_s4).

[8-10 min]
- R4 can_navigate to the next room to assist further (r4_s5).

[0-5 min]
- R5 navigate to the dresser near the window (r5_s1)

[5-7 min]
- R5 push the dresser against the window to block it (r5_s2)

[7-10 min]
- R5 navigate to the bed (r5_s3)

[10-12 min]
- R5 push the bed against the door to block it (r5_s4)

[0-5 min]
- R6 navigate to the window. (r6_s1)

[5-10 min]
- R6 push the towel rack against the window to seal it. (r6_s2)
```

### Independent (TF=2 PF=1 OC=2 SC=2 Final=1.8)

```
[0-5 min]
- R1 Close window (r1_s1)

[0-5 min]
- R2 Close all windows in the kitchen to seal the room. (r2_s1)

[5-10 min]
- R2 Turn off all lights to conserve energy during the typhoon. (r2_s2)

[0-5 min]
- R3 Close curtains (r3_s1)

[0-5 min]
- R4 Close all windows and curtains in the living room to seal the room. (r4_s1)

[0-5 min]
- R5 close window blinds to seal the room (r5_s1)

[0-5 min]
- R6 Close both windows to seal the bathroom. (r6_s1)
```

### LaMMA-P (TF=2 PF=1 OC=2 SC=1 Final=1.65)

```
### Joint Plan

[0-5 min]
- R4 goes to a window (r4_s1)
- R6 goes to a window (r6_s1)
- R3 goes to a loose object (r3_s1)
- R3 goes to another loose object (r3_s2)
- R4 goes to a door (r4_s2)
- R6 goes to a door (r6_s2)

[5-10 min]
- R4 closes the window (r4_s3)
- R6 closes the window (r6_s3)
- R3 picks up the loose object (r3_s3)
- R3 picks up another loose object (r3_s4)
- R4 closes the door (r4_s4)
- R6 closes the door (r6_s4)
- R3 places the object in a secure location (r3_s5)
- R3 places another object in a secure location (r3_s6)

[10-15 min]
- R4 goes to an appliance (r4_s5)
- R6 goes to an appliance (r6_s5)
- R3 goes to another appliance (r3_s7)

[15-20 min]
- R4 turns off the appliance (r4_s6)
- R6 turns off the appliance (r6_s6)
- R3 turns off the appliance (r3_s8)
```

### SMART-LLM (TF=5 PF=1 OC=2 SC=3 Final=2.85)

```
### Joint Plan

[0-5 min]
- R6 go to Window1 (r6_s1)
- R6 close Window1 (r6_s2)
- R6 lock Window1 (r6_s3)
- R6 go to Window2 (r6_s4)
- R6 close Window2 (r6_s5)
- R6 lock Window2 (r6_s6)
- R6 go to Window3 (r6_s7)
- R6 close Window3 (r6_s8)
- R6 lock Window3 (r6_s9)

[0-5 min]
- R4 go to FrontDoor (r4_s1)
- R4 close FrontDoor (r4_s2)
- R4 lock FrontDoor (r4_s3)
- R4 go to BackDoor (r4_s4)
- R4 close BackDoor (r4_s5)
- R4 lock BackDoor (r4_s6)
- R4 go to SideDoor (r4_s7)
- R4 close SideDoor (r4_s8)
- R4 lock SideDoor (r4_s9)

[0-5 min]
- R3 go to Vent (r3_s1)
- R3 close Vent (r3_s2)
- R3 lock Vent (r3_s3)
- R3 go to Skylight (r3_s4)
- R3 close Skylight (r3_s5)
- R3 lock Skylight (r3_s6)
```

## Run 3

### Ours (CDA) (TF=1 PF=4 OC=9 SC=2 Final=4.55)

```
### Joint Plan — task7_abstract  (about 10 min / deadline 10 min: OK)

[0-5 min]
- R5 [LOCAL] move the Brown-orange ball from the bedroom window area to the interior side of the room  (r5_s1)
- R6 [LOCAL] push the Bathroom window fully closed and engage its reachable latch  (r6_s1)
- R5 [LOCAL] move the Gray-blue beanbag chair away from the bedroom window and out of the access route  (r5_s2)
- R6 [LOCAL] move the Wall-hung towel beneath the window from its hanger and press it firmly into residual gaps around the closed Bathroom window  (r6_s2)
- R5 [LOCAL] move the Black chair cushion from the window-side chair to the bed away from the glass  (r5_s3)

[5-10 min]
- R5 [LOCAL] move the Black metal chair away from the bedroom window and out of the access route  (r5_s4)
- R5 [LOCAL] move the Black wastebasket away from the bedroom window and access route  (r5_s5)
- R5 [LOCAL] move the Open laptop to the Small white bedside cabinet or shelving unit away from the bedroom window  (r5_s6)
- R5 [LOCAL] move the Small black rectangular object on the bed to the Small white bedside cabinet or shelving unit away from the bedroom window  (r5_s7)
```

### Centralized (TF=2 PF=2 OC=2 SC=2 Final=2.0)

```
[0-5 min]
- R1 PickupLightObject (r1_s1): Pick up the apple from the counter.

[5-10 min]
- R1 PassReceiveObject (r1_s2): Pass the apple to R2 for sealing.

[0-5 min]
- R2 navigate to R1 to collect light objects (r2_s1)

[5-10 min]
- R2 receive light objects from R1 (r2_s2)

[10-15 min]
- R2 navigate to windows and doors in the kitchen (r2_s3)

[15-20 min]
- R2 use collected light objects to assist in sealing windows and doors (r2_s4)

[0-5 min]
- R3 PickupLightObject (r3_s1): Pick up the laptop from the table.

[5-10 min]
- R3 PassReceiveObject (r3_s2): Pass the laptop to R4 for sealing.

[0-2 min]
- R4 navigate to R3 to collect light objects (r4_s1)

[2-5 min]
- R4 PickupLightObject from R3 (r4_s2)

[5-8 min]
- R4 navigate to windows and doors in the living room (r4_s3)

[8-10 min]
- R4 use collected light objects to assist in sealing windows and doors (r4_s4)

[0-5 min]
- R5 navigate to the dresser near the window (r5_s1)
- R5 push the dresser against the window to secure it (r5_s2)

[5-10 min]
- R5 navigate to the bed (r5_s3)
- R5 push the bed against the door to secure it (r5_s4)

[0-5 min]
- R6 navigate to the towel rack and remove the towel. (r6_s1)

[5-10 min]
- R6 push the towel rack against the window to secure it. (r6_s2)
```

### Independent (TF=2 PF=1 OC=2 SC=2 Final=1.8)

```
[0-5 min]
- R1 Close window (r1_s1)

[0-5 min]
- R2 close all cabinets and drawers (r2_s1)

[5-10 min]
- R2 close the window blinds (r2_s2)

[0-5 min]
- R3 Close curtains (r3_s1)
- R3 Turn off lamp (r3_s2)

[0-5 min]
- R4 closes all windows in the living room to seal the house. (r4_s1)

[0-5 min]
- R5 close window blinds to seal the room (r5_s1)

[0-5 min]
- R6 close window (r6_s1)
```

### LaMMA-P (TF=2 PF=2 OC=2 SC=2 Final=2.0)

```
### Joint Plan

[0-5 min]
- R4 close all windows (R4_s1)
- R6 close all doors (R6_s1)
- R3 secure loose objects (R3_s1)
- R4 switch off electrical appliances (R4_s2)

[5-10 min]
- R6 close the fridge (R6_s2)
```

### SMART-LLM (TF=3 PF=1 OC=2 SC=4 Final=2.4)

```
### Joint Plan

[0-5 min]
- R4 Go to Window1 (r4_s1)
- R4 Close Window1 (r4_s2)
- R4 Lock Window1 (r4_s3)
- R4 Go to Window2 (r4_s4)
- R4 Close Window2 (r4_s5)
- R4 Lock Window2 (r4_s6)
- R4 Go to Window3 (r4_s7)
- R4 Close Window3 (r4_s8)
- R4 Lock Window3 (r4_s9)

[0-5 min]
- R6 Go to FrontDoor (r6_s1)
- R6 Close FrontDoor (r6_s2)
- R6 Lock FrontDoor (r6_s3)
- R6 Go to BackDoor (r6_s4)
- R6 Close BackDoor (r6_s5)
- R6 Lock BackDoor (r6_s6)

[0-5 min]
- R3 Go to Vent (r3_s1)
- R3 Close Vent (r3_s2)
- R3 Lock Vent (r3_s3)
- R3 Go to Skylight (r3_s4)
- R3 Close Skylight (r3_s5)
- R3 Lock Skylight (r3_s6)
```

# task8_abstract

> I need an isolation room ready in 20 minutes for people with the flu.

## Run 1

### Ours (CDA) (TF=3 PF=9 OC=9 SC=3 Final=6.3)

```
### Joint Plan — task8_abstract  (about 35 min / deadline 20 min: MISSED)

[0-5 min]
- R3 [PASS] pass Throw blanket to R4 (hands it over; R4 collects it)  (r3_s2)
- R4 [LOCAL] move the One open laptop from the wooden coffee-table chest to the far end of the dining table  (r4_s1)
- R5 [LOCAL] move the Pair of dumbbells from the doorway-to-bed route to the far wall  (r5_s1)
- R6 [LOCAL] move the White pump soap dispenser to an accessible position beside the bathroom sink  (r6_s1)
- R4 [LOCAL] move one small remote control from the wooden chest beside the sofas to the far end of the dining table  (r4_s2)
- R5 [LOCAL] move the Guitar from the patient zone to the wall beside the Tall shelving cabinet  (r5_s2)
- R6 [LOCAL] move the Toilet paper roll to the toilet-paper holder within easy reach of the toilet  (r6_s2)
- R4 [LOCAL] reposition the One green throw pillow at the head end of the first purple sofa  (r4_s3)
- R6 [LOCAL] move the Toilet plunger from the walking area to the storage corner beside the toilet  (r6_s3)
- R4 [LOCAL] place the One red throw pillow or folded throw on the second purple sofa as its dedicated support or cover  (r4_s4)
- R6 [LOCAL] move the Toilet brush from the walking area to the storage corner beside the toilet  (r6_s4)
- R6 [LOCAL] move the Toothbrush/toiletry item beside the sinks away from the shared sink area into bathroom toiletry storage  (r6_s5)

[5-10 min]
- R5 [LOCAL] move Cardboard box and loose cardboard pieces from the patient zone to beside the Tall shelving cabinet  (r5_s3)
- R5 [LOCAL] move the Small turquoise floor item from the walking route into the Desk drawer unit  (r5_s4)
- R4 [RECEIVE] receive Throw blanket (one dry throw blanket) from R3 (collects it from the living room)  (r4_s5)
- R5 [LOCAL] move the Orange rod-like item from the walking route to the far wall  (r5_s5)
- R4 [LOCAL] place the Throw blanket on the first purple sofa as its dedicated blanket  (r4_s6)
- R6 [PASS] pass Green waste bin to R5 (offered) (brings it to the bedroom)  (r6_s7)
- R6 [PASS] pass Tan bath towel to R5 (offered) (brings it to the bedroom)  (r6_s9)

[10-15 min]
- R5 [LOCAL] move the Large black bag or soft bundle from the patient zone to the wall beside the Wooden dresser  (r5_s6)
- R5 [LOCAL] move Green fabric item beside the black bundle from the floor onto the Wooden dresser  (r5_s7)
- R5 [LOCAL] move the Long black rod or bar beside the desk to the far wall  (r5_s8)
- R5 [LOCAL] move the Green fabric item on the bed from the sleeping surface to the Wooden dresser  (r5_s9)

[15-20 min]
- R5 [LOCAL] spread the Black-and-white blanket or duvet neatly over the mattress  (r5_s10)
- R5 [LOCAL] fold the Green patterned blanket and place it at the foot of the bed  (r5_s11)
- R5 [LOCAL] position the White pillow at the head of the bed  (r5_s12)

[20-25 min]
- R5 [LOCAL] move the Laptop computer with cable from the Wooden desk to the Wooden dresser  (r5_s13)
- R5 [LOCAL] move the Alarm clock from the Wooden desk to the Wooden dresser  (r5_s14)
- R5 [LOCAL] move the Small red desk item from the Wooden desk into the Desk drawer unit  (r5_s15)
- R5 [LOCAL] move the Small yellow writing utensil from the Wooden desk into the Desk drawer unit  (r5_s16)

[25-30 min]
- R5 [LOCAL] move the Small gray desk item from the Wooden desk into the Desk drawer unit  (r5_s17)
- R5 [LOCAL] push the Wooden chair beside the Wooden desk without obstructing the doorway-to-bed route  (r5_s18)
- R5 [RECEIVE] receive Green waste bin from R6  (r5_s21)
- R5 [LOCAL] place the received Green waste bin beside the bed as the dedicated patient waste station and contaminated-tissue container  (r5_s22)

[30-35 min]
- R5 [RECEIVE] receive Tan bath towel from R6  (r5_s23)
- R5 [LOCAL] place the received Tan bath towel folded on the Wooden dresser as a dedicated flu-patient towel  (r5_s24)
```

### Centralized (TF=3 PF=2 OC=2 SC=1 Final=2.15)

```
[0-5 min]
- R1 PickupLightObject: Mug (r1_s1)

[5-10 min]
- R1 PickupLightObject: Tomato (r1_s2)

[10-15 min]
- R1 PassReceiveObject: Pass Mug to R2 (r1_s3)

[15-20 min]
- R1 PassReceiveObject: Pass Tomato to R2 (r1_s4)

[0-5 min]
- R2 navigate to the green mug on the counter (r2_s1)

[5-10 min]
- R2 pick up the green mug (r2_s2)

[10-15 min]
- R2 navigate to the isolation room (r2_s3)

[15-20 min]
- R2 place the green mug in the isolation room (r2_s4)

[0-5 min]
- R3 scans the living room for light objects that might be useful for an isolation room, such as blankets, pillows, or small medical supplies. (r3_s1)

[5-10 min]
- R3 uses its gripper to pick up a light blanket from the living room. (r3_s2)

[10-15 min]
- R3 picks up a small pillow using its gripper. (r3_s3)

[15-20 min]
- R3 waits for R4 to arrive in the living room to pass the collected items. Once R4 arrives, R3 passes the blanket and pillow to R4. (r3_s4)

[0-5 min]
- R4 navigate to the coffee table (r4_s1)

[5-10 min]
- R4 pickup light objects from the coffee table (e.g., laptop, remote) (r4_s2)

[10-15 min]
- R4 transport light objects to the isolation room (r4_s3)

[15-20 min]
- R4 return to the living room for additional objects if needed (r4_s4)

[0-5 min]
- R5 can_navigate to the desk area. (r5_s1)

[5-10 min]
- R5 PickupHeavyObject: Move the chair from the desk to the isolation room. (r5_s2)

[10-15 min]
- R5 can_navigate to the bed area. (r5_s3)

[15-20 min]
- R5 PickupHeavyObject: Move the bed to the isolation room. (r5_s4)

[0-5 min]
- R6 can_navigate to the bathroom and identify heavy objects such as the trash bin and plunger. (r6_s1)

[5-10 min]
- R6 PickupHeavyObject the trash bin and move it to the isolation room. (r6_s2)

[10-15 min]
- R6 PickupHeavyObject the plunger and move it to the isolation room. (r6_s3)

[15-20 min]
- R6 can_navigate back to the bathroom to ensure no other heavy objects remain. (r6_s4)
```

### Independent (TF=1 PF=1 OC=1 SC=1 Final=1.0)

```
[0-5 min]
- R1 Boil water in the kettle for potential hot drinks. (r1_s1)

[5-10 min]
- R1 Slice the tomato for potential use in meals. (r1_s2)

[10-15 min]
- R1 Pour water into mugs for serving. (r1_s3)

[15-20 min]
- R1 Prepare tea or coffee using the machine for comfort drinks. (r1_s4)

[0-5 min]
- R2 Pick up the green mug and place it in a cupboard to tidy the kitchen. (r2_s1)

[5-10 min]
- R2 Ensure all visible lights are turned off to conserve energy for the isolation room. (r2_s2)

[10-15 min]
- R2 Check the sink area and ensure it is clean and free of any dishes. (r2_s3)

[15-20 min]
- R2 Close any open cupboards or drawers to maintain a tidy environment. (r2_s4)

I'm sorry, but I cannot see any images. However, I can help you with the task based on the description provided. Since I am located in the living room and can only interact with objects within this room, I will perform actions based on the typical setup of a living room and the capabilities I have.

Given the task of preparing an isolation room for people with the flu, I will focus on ensuring the living room is clean and free of any unnecessary items that could contribute to the spread of germs. Here are the actions I will take:

[0-5 min]
- R3 PickupLightObject (e.g., magazines, remote controls) and place them in a designated area to declutter the living room. (r3_s1)

[5-10 min]
- R3 SliceObject (e.g., open any sealed packages of tissues or cleaning wipes) to ensure they are ready for use. (r3_s2)

[10-15 min]
- R3 PourObject (e.g., pour cleaning solution onto a cloth) to clean surfaces such as tables and remote controls. (r3_s3)

[15-20 min]
- R3 PassReceiveObject (e.g., pass a box of tissues or cleaning wipes to another robot if they come to the living room) to ensure these items are available in the isolation room. (r3_s4)

These actions will help ensure the living room is tidy and ready to support the isolation room setup.

[0-5 min]
- R4 Turn off the lights to create a calming environment. (r4_s1)

[5-10 min]
- R4 Close the curtains to ensure privacy and reduce light. (r4_s2)

[10-15 min]
- R4 Turn on the lamp for soft lighting. (r4_s3)

[15-20 min]
- R4 Ensure the room is tidy by arranging cushions on the sofa. (r4_s4)

[0-5 min]
- R5 Make the bed neatly to ensure a clean and comfortable resting area. (r5_s1)

[5-10 min]
- R5 Turn on the lamp for adequate lighting. (r5_s2)

[10-15 min]
- R5 Clear the desk by organizing or removing unnecessary items to create a tidy environment. (r5_s3)

[15-20 min]
- R5 Close the window to maintain a stable room temperature. (r5_s4)

[0-5 min]
- R6 Pick up the paper towel roll and place it on the counter for easy access. (r6_s1)

[5-10 min]
- R6 Ensure the sink area is clean and tidy by wiping down the counter with a paper towel. (r6_s2)

[10-15 min]
- R6 Check that the trash bin is empty and ready for use. (r6_s3)

[15-20 min]
- R6 Ensure the toilet area is clean and the toilet paper is stocked. (r6_s4)
```

### LaMMA-P (TF=4 PF=2 OC=2 SC=3 Final=2.75)

```
### Joint Plan

[0-5 min]
- R6 goes to the room (r6_s1)
- R6 goes to surfaces (r6_s2)
- R4 goes to the storage area (r4_s1)
- R3 goes to the windows (r3_s1)

[5-10 min]
- R6 cleans the room (r6_s3)
- R6 disinfects surfaces (r6_s4)
- R4 picks up isolation equipment (r4_s2)
- R3 opens the windows (r3_s2)

[10-15 min]
- R4 goes to the room (r4_s3)

[15-20 min]
- R4 places the equipment in the room (r4_s4)
```

### SMART-LLM (TF=2 PF=2 OC=2 SC=1 Final=1.85)

```
### Joint Plan

[0-5 min]
- R6 go to the room (r6_s1)
- R4 go to the supply closet (r4_s1)
- R6 go to the ventilation system (r6_s2)
- R4 go to the PPE storage (r4_s2)
- R6 go to the sign storage (r6_s3)

[5-10 min]
- R6 clean the room (r6_s4)
- R4 pick up supplies (r4_s3)
- R6 switch on the ventilation (r6_s5)
- R4 pick up PPE (r4_s4)
- R6 pick up restriction signs (r6_s6)

[10-15 min]
- R4 go to the room (r4_s5)
- R6 go to the room entrance (r6_s7)

[15-20 min]
- R4 set up supplies in the room (r4_s6)
- R4 place PPE in the room (r4_s7)
- R6 place signs to restrict access (r6_s8)
```

## Run 2

### Ours (CDA) (TF=2 PF=7 OC=8 SC=3 Final=5.25)

```
### Joint Plan — task8_abstract  (about 30 min / deadline 20 min: MISSED)

[0-5 min]
- R4 [PASS] pass Green throw pillow to R5 (offered) (brings it to the bedroom)  (r4_s2)
- R5 [LOCAL] move the first dumbbell from the walking path to the wall  (r5_s6)
- R6 [PASS] pass Paper towel roll to R5 (offered) (brings it to the bedroom)  (r6_s1)
- R5 [LOCAL] move the second dumbbell from the walking path to the wall  (r5_s7)
- R5 [LOCAL] move the Long metal exercise bar from the walking path and place it securely along the wall  (r5_s8)
- R5 [LOCAL] move the Tennis racket from the floor to the wall beside the exercise equipment  (r5_s9)

[5-10 min]
- R5 [LOCAL] move the Small turquoise floor item from the walking path to the Wooden dresser  (r5_s10)
- R5 [LOCAL] move the Green fabric item near the black bag from the floor to the Wooden dresser  (r5_s11)
- R5 [LOCAL] move the Open cardboard box from the floor to a reachable position beside the bed  (r5_s12)
- R5 [LOCAL] fit the Black bag or bundled fabric into the Open cardboard box as a waste-container liner  (r5_s13)

[10-15 min]
- R5 [LOCAL] straighten the White bed sheet over the Mattress  (r5_s14)
- R5 [LOCAL] arrange the Black-and-white patterned blanket neatly on the patient bed  (r5_s15)
- R5 [LOCAL] place the Green folded fabric or blanket on the bed neatly at the foot of the patient bed  (r5_s16)

[15-20 min]
- R5 [RECEIVE] receive Green throw pillow (one pillow) from R4  (r5_s1)
- R5 [LOCAL] place the received Green throw pillow at the head of the patient bed  (r5_s17)

[20-25 min]
- R5 [LOCAL] move the Wooden drawer unit or nightstand beside the bed as an accessible supply surface  (r5_s18)
- R5 [LOCAL] move the Chair near the bed while keeping it outside the walking path  (r5_s19)

[25-30 min]
- R5 [RECEIVE] receive Paper towel roll (one roll) from R6  (r5_s3)
- R5 [LOCAL] place the received Paper towel roll on the Wooden drawer unit or nightstand within patient reach  (r5_s21)
```

### Centralized (TF=2 PF=2 OC=2 SC=2 Final=2.0)

```
[0-5 min]
- R1 PickupLightObject: Mug (r1_s1)

[5-10 min]
- R1 PickupLightObject: Tomato (r1_s2)

[10-15 min]
- R1 PassReceiveObject: Pass Mug to R2 (r1_s3)

[15-20 min]
- R1 PassReceiveObject: Pass Tomato to R2 (r1_s4)

[0-5 min]
- R2 navigate to R1 to collect items (r2_s1)

[5-10 min]
- R2 receive items from R1 (r2_s2)

[10-15 min]
- R2 navigate to the isolation room (r2_s3)

[15-20 min]
- R2 deliver items to the isolation room (r2_s4)

[0-5 min]
- R3 PickupLightObject: Gather any light objects in the living room that might be useful for setting up an isolation room, such as blankets, pillows, or small medical supplies. (r3_s1)

[5-10 min]
- R3 SliceObject: If there are any objects that need to be divided or prepared, such as cutting a roll of tape or slicing a piece of cloth, perform this action. (r3_s2)

[10-15 min]
- R3 PourObject: If there are any liquid supplies that need to be transferred into smaller containers for easier handling, perform this action. (r3_s3)

[15-20 min]
- R3 PassReceiveObject: Pass all prepared and gathered light objects to R4 when it arrives in the living room to take them to the isolation room. (r3_s4)

[0-5 min]
- R4 navigate to R3 to collect items (r4_s1)

[5-10 min]
- R4 receive items from R3 (r4_s2)

[10-15 min]
- R4 navigate to the isolation room (r4_s3)

[15-20 min]
- R4 deliver items to the isolation room (r4_s4)

[0-5 min]
- R5 can_navigate to the isolation room (r5_s1).

[5-10 min]
- R5 can_navigate back to the bedroom to assess which heavy objects or furniture need moving (r5_s2).

[10-15 min]
- R5 PickupHeavyObject: Move the bed to create more space in the isolation room (r5_s3).

[15-20 min]
- R5 PushFurniture: Rearrange the desk and chair to ensure clear pathways and accessibility (r5_s4).

[0-5 min]
- R6 navigate to the isolation room. (r6_s1)

[5-10 min]
- R6 assess the room for any heavy objects or furniture that need moving. (r6_s2)

[10-15 min]
- R6 move any heavy objects or furniture as needed to prepare the room. (r6_s3)

[15-20 min]
- R6 ensure the room is clear and ready for use. (r6_s4)
```

### Independent (TF=2 PF=2 OC=2 SC=2 Final=2.0)

```
[0-5 min]
- R1 Boil water in the kettle for potential hot drinks. (r1_s1)

[5-10 min]
- R1 Slice the tomato for potential use in meals. (r1_s2)

[10-15 min]
- R1 Prepare mugs by placing them on the counter for easy access. (r1_s3)

[15-20 min]
- R1 Pour hot water into the mugs for tea or other hot beverages. (r1_s4)

[0-5 min]
- R2 Pick up the green mug and place it in a designated area for use in the isolation room. (r2_s1)

[5-10 min]
- R2 Ensure the kitchen counters are clear of unnecessary items to maintain cleanliness. (r2_s2)

[10-15 min]
- R2 Check that the sink area is tidy and free of clutter to ensure it can be used for washing hands or dishes. (r2_s3)

[15-20 min]
- R2 Turn off any unnecessary lights to conserve energy, ensuring the kitchen is ready for any further tasks. (r2_s4)

I'm sorry, but I can't see the attached image of your room. Could you please describe the objects and their arrangement in the living room?

[0-5 min]
- R4 Turn off the TV to reduce noise and distractions. (r4_s1)

[5-10 min]
- R4 Turn on the lamp for better lighting. (r4_s2)

[10-15 min]
- R4 Ensure the curtains are closed for privacy. (r4_s3)

[15-20 min]
- R4 Tidy up the living room by arranging cushions neatly. (r4_s4)

[0-5 min]
- R5 tidy the room by picking up any visible clutter and placing it in the open box. (r5_s1)

[5-10 min]
- R5 make the bed to ensure it is clean and ready for use. (r5_s2)

[10-15 min]
- R5 turn on the lamp to ensure the room is well-lit. (r5_s3)

[15-20 min]
- R5 close the window to maintain a stable room temperature. (r5_s4)

[0-5 min]
- R6 Pick up the paper towel roll and place it on the counter for easy access. (r6_s1)

[5-10 min]
- R6 Ensure the sink area is clean and tidy by wiping down the counter with a paper towel. (r6_s2)

[10-15 min]
- R6 Check that the trash bin is empty and ready for use. (r6_s3)

[15-20 min]
- R6 Ensure the toilet area is clean and the toilet paper is stocked. (r6_s4)
```

### LaMMA-P (TF=2 PF=1 OC=2 SC=2 Final=1.8)

```
### Joint Plan

[0-5 min]
- R6 go to cleaning supplies (r6_s1)
- R6 (second instance) go to furniture (r6_s1)
  
[5-10 min]
- R6 pick up cleaning supplies (r6_s2)
- R6 (second instance) pick up furniture (r6_s2)

[10-15 min]
- R6 go to room (r6_s3)
- R6 (second instance) go to desired location in room (r6_s3)

[15-20 min]
- R6 clean the room (r6_s4)
- R6 (second instance) place furniture in desired location (r6_s4)

[20-25 min]
- R6 put back cleaning supplies (r6_s5)

[25-30 min]
- R4 go to supply storage (r4_s1)

[30-35 min]
- R4 pick up necessary supplies (r4_s2)

[35-40 min]
- R4 go to room (r4_s3)

[40-45 min]
- R4 place supplies in room (r4_s4)
```

### SMART-LLM (TF=4 PF=1 OC=2 SC=1 Final=2.25)

```
### Joint Plan

[0-5 min]
- R4 Go to the room (r4_s1)
- R4 Clean the room (r4_s2)

[5-10 min]
- R4 Go to the storage area (r4_s3)
- R4 Pick up masks, gloves, hand sanitizer, tissues, waste bags (r4_s4)

[10-15 min]
- R4 Go to the room (r4_s5)
- R4 Place masks, gloves, hand sanitizer, tissues, waste bags in the room (r4_s6)

[0-5 min]
- R3 Go to the bed (r3_s1)
- R3 Pick up clean linens (r3_s2)

[5-10 min]
- R3 Make the bed with clean linens (r3_s3)

[0-5 min]
- R3 Go to the ventilation system (r3_s4)
- R3 Switch on the ventilation (r3_s5)

[0-5 min]
- R3 Go to the communication device (r3_s6)
- R3 Switch on the communication device (r3_s7)
```

## Run 3

### Ours (CDA) (TF=2 PF=9 OC=8 SC=3 Final=5.65)

```
### Joint Plan — task8_abstract  (about 35 min / deadline 20 min: MISSED)

[0-5 min]
- R5 [LOCAL] move the first dumbbell from Two dumbbells from the door-to-bed route to the wall beside the shelving cabinet  (r5_s1)
- R6 [PASS] pass Paper towel roll to R5 (offered) (brings it to the bedroom)  (r6_s1)
- R5 [LOCAL] move the second dumbbell from Two dumbbells from the door-to-bed route to the wall beside the shelving cabinet  (r5_s2)
- R6 [PASS] bring White pump bottle with red pump to R5 in the bedroom and pass it -> R5 (brings it to the bedroom)  (r6_s2)

[5-10 min]
- R5 [LOCAL] move the Guitar out of the access route and place it securely against the wall  (r5_s3)
- R5 [LOCAL] move the Small turquoise floor item from the floor into the Open cardboard box  (r5_s4)
- R5 [LOCAL] move the Green fabric item near the waste bin from the floor into the Open cardboard box  (r5_s5)
- R5 [LOCAL] move the Open cardboard box out of the door-to-bed route to beside the Wooden shelving cabinet  (r5_s6)

[10-15 min]
- R5 [LOCAL] push the Wooden chair under the Wooden desk and away from the access space around the bed  (r5_s7)
- R5 [LOCAL] move the Laptop computer from the exposed desk surface to the Wooden shelving cabinet  (r5_s8)
- R5 [LOCAL] move the Small red desk item from the desk into the Wooden drawer pedestal  (r5_s9)
- R5 [LOCAL] move the Small orange desk item from the desk into the Wooden drawer pedestal  (r5_s10)

[15-20 min]
- R5 [LOCAL] move the Small black item on the dresser from the dresser into the Wooden drawer pedestal  (r5_s11)
- R5 [LOCAL] straighten the White mattress and sheet smoothly over the mattress  (r5_s12)
- R5 [LOCAL] straighten the White pillow and position it at the head of the bed  (r5_s13)

[20-25 min]
- R5 [LOCAL] straighten the Black-and-white patterned blanket over the bed  (r5_s14)
- R5 [LOCAL] fold the Green blanket or garment on the bed and move it to the Wooden shelving cabinet  (r5_s15)
- R5 [LOCAL] move the Striped tissue box on the dresser to the Wooden drawer pedestal within reach of the bed  (r5_s16)

[25-30 min]
- R5 [LOCAL] move the Black waste bin with green liner beside the bed without blocking the access route  (r5_s17)
- R5 [LOCAL] move the Desk lamp to the Wooden drawer pedestal within reach of the bed  (r5_s18)
- R5 [RECEIVE] receive White pump bottle with red pump (the pump bottle containing liquid soap) from R6  (r5_s21)
- R5 [LOCAL] place the White pump bottle with red pump near the bedroom entrance for hand hygiene  (r5_s22)
- R5 [RECEIVE] receive Paper towel roll (one dry paper towel roll) from R6  (r5_s23)

[30-35 min]
- R5 [LOCAL] place the Paper towel roll near the liquid-soap pump bottle for disposable hand drying and cleanup  (r5_s24)
```

### Centralized (TF=2 PF=3 OC=2 SC=2 Final=2.2)

```
[0-5 min]
- R1 PickupLightObject (Mug) (r1_s1)

[5-10 min]
- R1 PickupLightObject (Pan) (r1_s2)

[10-15 min]
- R1 PickupLightObject (Tomato) (r1_s3)

[15-20 min]
- R1 PassReceiveObject (Mug, Pan, Tomato) to R2 (r1_s4)

[0-5 min]
- R2 navigate to the green mug on the counter (r2_s1)

[5-10 min]
- R2 pick up the green mug (r2_s2)

[10-15 min]
- R2 transport the green mug to the isolation room (r2_s3)

[15-20 min]
- R2 place the green mug in the isolation room (r2_s4)

[0-5 min]
- R3 PickupLightObject: Gather any light objects in the living room that might be useful for setting up an isolation room, such as blankets, pillows, or small medical supplies. (r3_s1)

[5-10 min]
- R3 SliceObject: If there are any objects that need to be divided or prepared, such as cutting a roll of tape or slicing a piece of cloth, do so now. (r3_s2)

[10-15 min]
- R3 PourObject: If there are any liquid supplies that need to be transferred into smaller containers for easier handling, pour them now. (r3_s3)

[15-20 min]
- R3 PassReceiveObject: Pass all gathered and prepared light objects to R4 when it arrives in the living room to take them to the isolation room. (r3_s4)

[0-5 min]
- R4 navigate to the coffee table (r4_s1)

[5-10 min]
- R4 pickup the laptop from the coffee table (r4_s2)

[10-15 min]
- R4 transport the laptop to the isolation room (r4_s3)

[15-20 min]
- R4 return to the living room and navigate to the dining table (r4_s4)

[20-25 min]
- R4 pickup the vase from the dining table (r4_s5)

[25-30 min]
- R4 transport the vase to the isolation room (r4_s6)

[0-5 min]
- R5 can_navigate to the bed area. (r5_s1)

[5-10 min]
- R5 PickupHeavyObject to move the bed against the wall to create more space. (r5_s2)

[10-15 min]
- R5 can_navigate to the desk area. (r5_s3)

[15-20 min]
- R5 PushFurniture to move the desk to the corner, maximizing open space for isolation. (r5_s4)

[0-5 min]
- R6 navigate to the sink area to check for any light objects that can be moved. (r6_s1)

[5-10 min]
- R6 pick up the paper towel roll from the sink area. (r6_s2)

[10-15 min]
- R6 navigate to the trash bin and ensure it is empty or remove any trash if necessary. (r6_s3)

[15-20 min]
- R6 assist R5 in moving any heavy objects or furniture to the isolation room as needed. (r6_s4)
```

### Independent (TF=1 PF=1 OC=1 SC=1 Final=1.0)

```
[0-5 min]
- R1 Boil water in the kettle for potential hot drinks or sanitization. (r1_s1)

[5-10 min]
- R1 Slice the tomato for potential use in meals or snacks. (r1_s2)

[10-15 min]
- R1 Pour water into mugs for hydration. (r1_s3)

[15-20 min]
- R1 Prepare tea or coffee using the machine for comfort. (r1_s4)

[0-5 min]
- R2 Pick up the green mug and place it in a convenient location for use. (r2_s1)

[5-10 min]
- R2 Ensure the kitchen counter is tidy by organizing visible items like the bread and bowl. (r2_s2)

[10-15 min]
- R2 Check that the sink area is clear and clean for any necessary use. (r2_s3)

[15-20 min]
- R2 Turn off any unnecessary lights to conserve energy. (r2_s4)

I'm sorry, but I cannot see the attached image of the living room. However, I can help you with general actions that might be relevant for preparing a living room as part of setting up an isolation room for people with the flu. Here are some potential actions based on common living room items:

[0-5 min]
- R3 Turn off any fans or air conditioning to prevent the spread of germs. (r3_s1)

[5-10 min]
- R3 Pickup any light objects like magazines or remote controls and place them in a drawer or on a shelf to tidy the area. (r3_s2)

[10-15 min]
- R3 Slice any fruits or prepare any light snacks that might be available in the living room for the comfort of the person in isolation. (r3_s3)

[15-20 min]
- R3 Pour water into a glass or bottle to ensure hydration for the person in isolation. (r3_s4)

If you can provide more specific details or describe the image, I can tailor the actions more precisely to the living room's setup.

[0-5 min]
- R4 Turn off the TV to reduce noise and create a calm environment. (r4_s1)

[5-10 min]
- R4 Turn on the lamp for better lighting, ensuring the room is well-lit for any necessary activities. (r4_s2)

[10-15 min]
- R4 Close the curtains to maintain privacy and control lighting. (r4_s3)

[15-20 min]
- R4 Tidy up the coffee table by organizing any loose items to ensure the room is neat and ready for use. (r4_s4)

[0-5 min]
- R5 Push bed against the wall to create more space. (r5_s1)

[5-10 min]
- R5 Pickup and tidy scattered items on the floor. (r5_s2)

[10-15 min]
- R5 Turn on the lamp for better lighting. (r5_s3)

[15-20 min]
- R5 Close the window to maintain room temperature. (r5_s4)

[0-5 min]
- R6 Pick up the paper towel roll and place it on the counter for easy access. (r6_s1)

[5-10 min]
- R6 Ensure the sink area is clean and tidy by wiping down the counter with a paper towel. (r6_s2)

[10-15 min]
- R6 Check that the trash bin is empty and ready for use. (r6_s3)

[15-20 min]
- R6 Ensure the toilet area is clean and the toilet paper is stocked. (r6_s4)
```

### LaMMA-P (TF=2 PF=1 OC=3 SC=3 Final=2.3)

```
### Joint Plan

[0-5 min]
- R4 Go to cleaning supplies (r4_s1)
- R3 Go to medical supplies storage (r3_s1)

[5-10 min]
- R4 Pick up cleaning supplies (r4_s2)
- R3 Pick up medical supplies (r3_s2)

[10-15 min]
- R4 Go to the room (r4_s3)
- R3 Go to the room (r3_s3)

[15-20 min]
- R4 Clean the room (r4_s4)
- R3 Place medical supplies in the room (r3_s4)

[20-25 min]
- R4 Go to air purifier (r4_s5)

[25-30 min]
- R4 Turn on air purifier (r4_s6)

[30-35 min]
- R4 Go to room door (r4_s7)

[35-40 min]
- R4 Open room door for ventilation (r4_s8)

[40-45 min]
- R4 Close room door (r4_s9)
```

### SMART-LLM (TF=4 PF=2 OC=3 SC=2 Final=2.95)

```
### Joint Plan

[0-5 min]
- R6 go to the room (r6_s1)
- R4 go to the ventilation system (r4_s1)

[5-10 min]
- R6 clean the room (r6_s2)
- R4 switch on the ventilation (r4_s2)

[10-15 min]
- R6 go to supply storage (r6_s3)
- R6 pick up medical supplies (r6_s4)

[15-20 min]
- R6 go to the room (r6_s5)
- R6 place medical supplies in the room (r6_s6)
- R6 go to linen storage (r6_s7)
- R6 pick up clean linens (r6_s8)
- R6 go to the room (r6_s9)
- R6 make the bed (r6_s10)
- R6 go to device storage (r6_s11)
- R6 pick up communication devices (r6_s12)
- R6 go to the room (r6_s13)
- R6 place communication devices in the room (r6_s14)
```

# task9_abstract

> Get the house ready for bedtime in 15 minutes.

## Run 1

### Ours (CDA) (TF=3 PF=3 OC=2 SC=2 Final=2.5)

```
### Joint Plan — task9_abstract  (about 15 min / deadline 15 min: OK)

[0-5 min]
- R1 [LOCAL] place the Kitchen knife flat in the Brown baking pan or tray with its cutting edge away from the counter edge  (r1_s1)
- R3 [LOCAL] move the First small remote-like device on the glass side table away from the glass side-table edge  (r3_s5)
- R4 [LOCAL] move the Striped throw cushion to a burgundy sofa, leaving it out of the walking route  (r4_s1)
- R5 [LOCAL] spread and smooth the White checked sheet over the Mattress  (r5_s1)
- R6 [LOCAL] move the Pink pump bottle to an upright, orderly position on the bathroom shelf  (r6_s1)
- R1 [LOCAL] move the Dark plate or saucer under the tomato into the Brown baking pan or tray  (r1_s4)
- R3 [LOCAL] move the Second small remote-like device on the glass side table away from the glass side-table edge  (r3_s6)
- R4 [LOCAL] move the White ceramic vase to the center of the Narrow console table  (r4_s2)
- R5 [LOCAL] spread the Dark blue blanket neatly over the White checked sheet  (r5_s2)
- R6 [LOCAL] move the Green pump bottle to an upright, orderly position on the bathroom shelf  (r6_s2)
- R1 [LOCAL] move the Small plate or saucer under the bread into the Brown baking pan or tray  (r1_s7)
- R4 [LOCAL] move the Small orange media device to a secure position on the Media cabinet  (r4_s3)
- R5 [LOCAL] arrange the White pillow at the head of the bed  (r5_s3)
- R6 [LOCAL] move the Pink bar of soap to a neat position with the washing supplies by the sink  (r6_s3)
- R4 [LOCAL] move the Small black tabletop device away from the edge of the Dining table  (r4_s4)
- R6 [LOCAL] move the Toothbrush cup to an upright, accessible position on the bathroom counter  (r6_s4)

[5-10 min]
- R5 [LOCAL] arrange the Dark blue pillow at the head of the bed  (r5_s4)
- R5 [LOCAL] move the Cardboard box from the walking path to a safe position beside the Wooden desk with hutch  (r5_s5)
- R6 [LOCAL] place the Toothbrushes together in the Toothbrush cup  (r6_s5)
- R5 [LOCAL] pick up the Basketball from the floor and place it into the Cardboard box  (r5_s6)
- R6 [LOCAL] hang and straighten the Green towel  (r6_s6)
- R6 [LOCAL] hang and straighten the Blue-and-white towel  (r6_s7)

[10-15 min]
- R5 [LOCAL] move the Baseball bat from the walking path to the wall beside the Wooden desk with hutch  (r5_s7)
- R5 [LOCAL] pick up the Loose white cord from the floor and place it securely on the Wooden desk with hutch  (r5_s8)
- R6 [LOCAL] move the Loose red item in the bathtub from the bathtub to a safe place with the bathroom supplies  (r6_s8)
- R5 [LOCAL] push the Wooden chair neatly under the Wooden desk with hutch  (r5_s9)
- R6 [LOCAL] straighten the Shower curtain along its rail while leaving the bathtub entry accessible  (r6_s9)
```

### Centralized (TF=1 PF=2 OC=1 SC=1 Final=1.2)

```
[0-5 min]
- R1 SliceObject (Apple) (r1_s1)

[5-10 min]
- R1 SliceObject (Lettuce) (r1_s2)

[10-15 min]
- R1 PourObject (Water into Cup) (r1_s3)

[0-5 min]
- R2 pick up the apple from the shelf. (r2_s1)

[5-10 min]
- R2 transport the apple to the living room. (r2_s2)

[10-15 min]
- R2 return to the kitchen and pick up the cup from the shelf. (r2_s3)

[15-20 min]
- R2 transport the cup to the dining room. (r2_s4)

Based on the images, there are no visible light food items in the living room that need slicing or pouring. Therefore, no actions related to slicing or pouring can be performed.

If there were any light food items, the plan would involve:

[0-5 min]
- R3 Identify any light food items that need slicing or pouring. (r3_s1)

[5-10 min]
- R3 Slice any identified food items. (r3_s2)

[10-15 min]
- R3 Pour any identified liquid items. (r3_s3)

Since no such items are visible, no further actions are needed.

[0-5 min]
- R4 navigate to the table and pick up any light objects (e.g., books, small decorations) (r4_s1).

[5-10 min]
- R4 transport the light objects to the bedroom (r4_s2).

[10-15 min]
- R4 return to the living room and ensure all light objects are cleared from surfaces (r4_s3).

[0-5 min]
- R5 can_navigate to the trash can and move it closer to the wall. (r5_s1)

[5-10 min]
- R5 can_navigate to the desk chair and push it under the desk. (r5_s2)

[10-15 min]
- R5 can_navigate to the cardboard box and move it to a corner of the room. (r5_s3)

[0-5 min]
- R6 PickupLightObject: Collect any visible small items like the toothbrush and toothpaste from the countertop. (r6_s1)

[5-10 min]
- R6 PickupHeavyObject: Move any heavy objects or furniture, such as the laundry basket or hamper, to a designated area if needed. (r6_s2)

[10-15 min]
- R6 can_navigate: Ensure the bathroom is tidy by arranging towels and ensuring the shower curtain is closed. (r6_s3)
```

### Independent (TF=3 PF=1 OC=2 SC=3 Final=2.25)

```
[0-5 min]
- R1 Turn off the coffee maker (r1_s1)

[5-10 min]
- R1 Turn off the stove (r1_s2)

[10-15 min]
- R1 Close the microwave door (r1_s3)

[0-5 min]
- R2 turns off the kitchen lights. (r2_s1)

[5-10 min]
- R2 closes any open cabinets. (r2_s2)

[10-15 min]
- R2 ensures all appliances are turned off. (r2_s3)

[0-5 min]
- R3 Turn off the ceiling light (r3_s1)

[5-10 min]
- R3 Turn off the floor lamp (r3_s2)

[10-15 min]
- R3 Close the laptop on the table (r3_s3)

[0-5 min]
- R4 Turn off the TV (r4_s1)

[5-10 min]
- R4 Turn off the table lamp (r4_s2)

[10-15 min]
- R4 Close the curtains (r4_s3)

[0-5 min]
- R5 Turn off the lamp on the dresser (r5_s1)

[5-10 min]
- R5 Close the window blinds (r5_s2)

[10-15 min]
- R5 Tidy the desk by organizing items (r5_s3)

[0-5 min]
- R6 Turn off bathroom light (r6_s1)

[5-10 min]
- R6 Close shower curtain (r6_s2)

[10-15 min]
- R6 Ensure towel is neatly hung (r6_s3)
```

### LaMMA-P (TF=2 PF=2 OC=2 SC=1 Final=1.85)

```
### Joint Plan

[0-5 min]
- R4 go to light switch (r4_s1)
- R6 go to light switch (r6_s1)
- R4 switch off light (r4_s2)
- R6 switch off light (r6_s2)

[5-10 min]
- R4 go to window (r4_s3)
- R6 go to curtain (r6_s3)
- R4 close window (r4_s4)
- R6 close curtain (r6_s4)

[10-15 min]
- R4 go to door (r4_s5)
- R6 go to door (r6_s5)
- R4 lock door (r4_s6)
- R6 lock door (r6_s6)

[0-5 min]
- R3 go to item (r3_s1)
- R4 go to item (r4_s1)
- R6 go to item (r6_s1)

[5-10 min]
- R3 pick up item (r3_s2)
- R4 pick up item (r4_s2)
- R6 pick up item (r6_s2)

[10-15 min]
- R3 put item in place (r3_s3)
- R4 put item in place (r4_s3)
- R6 put item in place (r6_s3)

[0-5 min]
- R4 go to bed (r4_s7)
- R6 go to bed (r6_s7)

[5-10 min]
- R4 open bed (r4_s8)
- R6 open bed (r6_s8)

[10-15 min]
- R4 switch off bedroom light (r4_s9)
- R6 switch off bedroom light (r6_s9)
```

### SMART-LLM (TF=3 PF=1 OC=1 SC=3 Final=1.9)

```
### Joint Plan

[0-5 min]
- R4 go to LivingRoomLight (r4_s1)
- R4 switch off LivingRoomLight (r4_s2)
- R6 go to KitchenLight (r6_s1)
- R6 switch off KitchenLight (r6_s2)
- R4 go to BathroomLight (r4_s3)
- R4 switch off BathroomLight (r4_s4)
- R6 go to LivingRoomWindow (r6_s3)
- R6 close LivingRoomWindow (r6_s4)
- R4 go to BedroomWindow (r4_s5)
- R4 close BedroomWindow (r4_s6)
- R6 go to LivingRoomCurtains (r6_s5)
- R6 close LivingRoomCurtains (r6_s6)
- R4 go to BedroomCurtains (r4_s7)
- R4 close BedroomCurtains (r4_s8)
- R6 go to FrontDoor (r6_s7)
- R6 lock FrontDoor (r6_s8)
- R4 go to BackDoor (r4_s9)
- R4 lock BackDoor (r4_s10)
- R6 go to Bed (r6_s9)
- R6 clean Bed (r6_s10)
- R4 go to Bedroom (r4_s11)
- R4 arrange Bedroom (r4_s12)
- R6 go to AlarmClock (r6_s11)
- R6 set AlarmClock (r6_s12)
```

## Run 2

### Ours (CDA) (TF=4 PF=7 OC=2 SC=3 Final=3.75)

```
### Joint Plan — task9_abstract  (about 20 min / deadline 15 min: MISSED)

[0-5 min]
- R1 [LOCAL] pick up the Cup (reported outside camera view) and position it for filling  (r1_s1)
- R2 [LOCAL] move the White cup or mug into the Brown tray or basket on the shelving unit  (r2_s1)
- R3 [LOCAL] close the lid of the Open laptop and leave it safely on the Glass dining table  (r3_s1)
- R4 [LOCAL] arrange Red sofa cushions neatly against the backrests of Two red sofas  (r4_s1)
- R5 [LOCAL] move the Open cardboard box from the bedside or doorway path to a stable location beside the Desk with hutch  (r5_s1)
- R6 [LOCAL] move the Small red toiletry item in the bathtub from the bathtub to a stable accessible place on the counter  (r6_s1)
- R2 [LOCAL] move the Small white dish or bowl into the Brown tray or basket on the shelving unit  (r2_s2)
- R4 [LOCAL] move the Striped sofa cushion to a stable position against the backrest of one red sofa  (r4_s2)
- R5 [LOCAL] move the Basketball from the floor into the Open cardboard box  (r5_s2)
- R6 [LOCAL] move the Pink spray bottle or pump dispenser away from the counter edge to a stable rear area of the counter  (r6_s2)
- R2 [LOCAL] move the Small brown bowl into the Brown tray or basket on the shelving unit  (r2_s3)
- R4 [LOCAL] move Small dining-table items to a stable location near the center of the Dining table  (r4_s3)
- R5 [LOCAL] move the Baseball bat from the floor into the Open cardboard box in a secure position  (r5_s3)
- R6 [LOCAL] place the Pink bar of soap accessibly beside the sink for bedtime washing  (r6_s3)
- R6 [LOCAL] place the Toothbrush holder cup upright in a stable accessible area beside the sink  (r6_s4)

[5-10 min]
- R5 [LOCAL] move the Blue wastebasket away from the bedside and doorway paths to beside the Desk with hutch  (r5_s4)
- R5 [LOCAL] push the Desk chair into a neat position at the Desk with hutch, clear of the walking path  (r5_s5)
- R6 [LOCAL] place the Toothbrushes upright in the Toothbrush holder cup  (r6_s5)
- R5 [LOCAL] move the Small brown item on the bed from the sleeping surface into the Blue desk organizer  (r5_s6)
- R6 [LOCAL] hang the Green towel neatly on the bathroom towel rack for bedtime use  (r6_s6)
- R6 [LOCAL] hang the Blue-gray towel neatly on the bathroom towel rack for bedtime use  (r6_s7)

[10-15 min]
- R5 [LOCAL] smooth and tuck the Checkered bed sheet across the Bed  (r5_s7)

[15-20 min]
- R5 [LOCAL] spread the Blue blanket neatly over the Checkered bed sheet  (r5_s8)
- R5 [LOCAL] arrange the Bed pillows at the head of the Bed for sleep  (r5_s9)
```

### Centralized (TF=2 PF=2 OC=2 SC=2 Final=2.0)

```
[0-5 min]
- R1 SliceObject (apple) (r1_s1)

[5-10 min]
- R1 PourObject (water into cup) (r1_s2)

[10-15 min]
- R1 SliceObject (lettuce) (r1_s3)

[0-5 min]
- R2 navigate to the living room (r2_s1)

[5-10 min]
- R2 assist with passing or receiving light objects in the living room (r2_s2)

[10-15 min]
- R2 ensure all light objects are in their designated places for bedtime (r2_s3)

[0-5 min]
- R3 PickupLightObject (r3_s1): Pick up the laptop from the table.

[5-10 min]
- R3 PassReceiveObject (r3_s2): Pass the laptop to another robot for safekeeping.

[10-15 min]
- R3 PourObject (r3_s3): Pour water from the pitcher into a glass to prepare for bedtime hydration.

[0-5 min]
- R4 navigate to the kitchen (r4_s1)

[5-10 min]
- R4 assist with passing or receiving light objects in the kitchen (r4_s2)

[10-15 min]
- R4 continue assisting as needed until the task is complete (r4_s3)

[0-5 min]
- R5 can_navigate to the bed and adjust the blanket to ensure it is neatly spread. (r5_s1)

[5-10 min]
- R5 can_navigate to the desk and push the chair under the desk to tidy up the area. (r5_s2)

[10-15 min]
- R5 can_navigate to the trash can and ensure it is positioned against the wall to clear the floor space. (r5_s3)

[0-5 min]
- R6 can_navigate to the bathtub area and PickupHeavyObject (bathtub plug) to ensure it is in place for bedtime. (r6_s1)

[5-10 min]
- R6 can_navigate to the countertop and PickupLightObject (toothbrush) to place it in its holder. (r6_s2)

[10-15 min]
- R6 can_navigate to the towel rack and ensure the towel is neatly hung for easy access. (r6_s3)
```

### Independent (TF=4 PF=2 OC=2 SC=3 Final=2.75)

```
[0-5 min]
- R1 Turn off the coffee maker (r1_s1)

[5-10 min]
- R1 Turn off the stove (r1_s2)

[10-15 min]
- R1 Close the microwave door (r1_s3)

[0-5 min]
- R2 Turn off kitchen lights to prepare for bedtime (r2_s1)

[5-10 min]
- R2 Close any open cabinets to tidy the kitchen (r2_s2)

[10-15 min]
- R2 Ensure all appliances are turned off (e.g., toaster, coffee maker) (r2_s3)

[0-5 min]
- R3 Turn off the ceiling light (r3_s1)

[5-10 min]
- R3 Turn off the floor lamp (r3_s2)

[10-15 min]
- R3 Close the laptop (r3_s3)

[0-5 min]
- R4 Turn off the lamp on the side table to prepare for bedtime. (r4_s1)

[5-10 min]
- R4 Close the curtains to block out light from outside. (r4_s2)

[10-15 min]
- R4 Turn off the overhead light to ensure the room is dark for bedtime. (r4_s3)

[0-5 min]
- R5 turn off the desk lamp (r5_s1)

[5-10 min]
- R5 close the window blinds (r5_s2)

[10-15 min]
- R5 tidy the bed (r5_s3)

[0-5 min]
- R6 Turn off bathroom light (r6_s1)

[5-10 min]
- R6 Close shower curtain (r6_s2)

[10-15 min]
- R6 Ensure towel is neatly hung (r6_s3)
```

### LaMMA-P (TF=3 PF=1 OC=2 SC=2 Final=2.1)

```
### Joint Plan

[0-5 min]
- R6 go to LightSwitch (r6_s1)
- R4 go to Door (r4_s1)
- R4 go to Window (r4_s1)
- R6 go to Television (r6_s1)

[5-10 min]
- R6 switch off LightSwitch (r6_s2)
- R4 lock Door (r4_s2)
- R4 close Window (r4_s2)
- R6 switch off Television (r6_s2)

[10-15 min]
- R6 go to FloorLamp (r6_s3)
- R6 go to DeskLamp (r6_s4)
- R6 go to Laptop (r6_s3)

[15-20 min]
- R6 switch off FloorLamp (r6_s5)
- R6 switch off DeskLamp (r6_s6)
- R6 switch off Laptop (r6_s4)
```

### SMART-LLM (TF=4 PF=1 OC=1 SC=3 Final=2.2)

```
### Joint Plan

[0-5 min]
- R1 turn off living room light (r1_s1)
- R2 close living room curtains (r2_s1)
- R3 lock front door (r3_s1)
- R4 turn off television (r4_s1)

[5-10 min]
- R1 turn off bedroom light (r1_s2)
- R2 close bedroom curtains (r2_s2)
- R3 lock back door (r3_s2)
- R4 turn off laptop (r4_s2)

[10-15 min]
- R1 turn off kitchen light (r1_s3)
- R5 set house alarm (r5_s1)
```

## Run 3

### Ours (CDA) (TF=3 PF=5 OC=9 SC=3 Final=5.5)

```
### Joint Plan — task9_abstract  (about 20 min / deadline 15 min: MISSED)

[0-5 min]
- R1 [LOCAL] move the Loaf of bread to the stable food-storage area of the counter away from the red appliance  (r1_s5)
- R3 [LOCAL] move the Laptop computer to a stable position away from the edge of the Glass dining table  (r3_s1)
- R4 [LOCAL] move the White dish-like object on the floor from the living-room walking route to the dining table with the dishware  (r4_s1)
- R5 [LOCAL] straighten the Checkered sheet or bedspread smoothly over the Mattress  (r5_s1)
- R6 [LOCAL] move the Blue cloth or towel beside the toilet to an accessible towel location, clearing the bathroom walking route  (r6_s1)
- R1 [LOCAL] move the Coffee-maker carafe to a stable position beside the Black coffee maker  (r1_s6)
- R4 [LOCAL] move the Black laptop or tabletop electronic device from the dining table to a stable position on the side table  (r4_s2)
- R5 [LOCAL] spread the Blue blanket neatly on the bed  (r5_s2)
- R6 [LOCAL] move the Spray bottle to safe storage away from towels, toothbrushes, and soap  (r6_s2)
- R1 [LOCAL] move the Dark plate or shallow bowl to the organized dish area  (r1_s7)
- R4 [LOCAL] straighten the striped cushion on one sofa  (r4_s3)
- R5 [LOCAL] arrange the White pillow neatly at the head of the bed  (r5_s3)
- R6 [LOCAL] if the Candle is unlit, move it to a stable safe storage location away from towels and the counter edge  (r6_s3)
- R1 [LOCAL] move the Blue bowl to the organized dish area  (r1_s8)
- R6 [LOCAL] arrange the Green towel in an accessible towel location for nighttime hygiene  (r6_s4)
- R1 [LOCAL] move the Apple to the nonperishable food-storage area  (r1_s9)
- R6 [LOCAL] arrange the Light-colored towel in an accessible towel location for nighttime hygiene  (r6_s5)

[5-10 min]
- R5 [LOCAL] arrange the Brown pillow neatly at the head of the bed  (r5_s4)
- R5 [LOCAL] move the Baseball bat from the walking route to a safe position beside the Wooden nightstand or dresser  (r5_s5)
- R1 [LOCAL] move the Paper towel roll to an upright position in the cleanup-supplies area  (r1_s11)
- R5 [LOCAL] move the Basketball from the walking route to a stable position beside the Tan laundry hamper  (r5_s6)
- R6 [LOCAL] arrange the Dark-colored towel in an accessible towel location for nighttime hygiene  (r6_s6)
- R1 [LOCAL] move the Yellow-and-green sponge to the cleanup-supplies area beside the sink  (r1_s12)
- R6 [LOCAL] place the Soap dispenser upright in an accessible, orderly position on the counter  (r6_s7)
- R6 [LOCAL] place the Pink bar of soap in an accessible dry position on the counter  (r6_s8)
- R6 [LOCAL] place the Toothbrush holder upright in an accessible position on the counter  (r6_s9)

[10-15 min]
- R5 [LOCAL] move the Cardboard box from the walking route to the wall beside the Wooden desk with hutch  (r5_s7)
- R5 [LOCAL] move the Laptop to a neat position on the Wooden desk with hutch  (r5_s8)
- R5 [LOCAL] move the Small stack of books to a neat position on the Wooden desk with hutch  (r5_s9)
- R6 [LOCAL] arrange the Toothbrushes upright in the Toothbrush holder  (r6_s10)
- R6 [LOCAL] move the Small red toiletry item in the bathtub to an orderly accessible position on the counter  (r6_s11)

[15-20 min]
- R5 [LOCAL] align the Blue books or binders neatly on the Wooden desk with hutch  (r5_s10)
- R5 [LOCAL] move the Clear cup or bowl to a secure back corner of the Wooden desk with hutch  (r5_s11)
- R5 [LOCAL] position the Round black clock upright and neatly on the Wooden desk with hutch  (r5_s12)
- R5 [LOCAL] position the Green bedside lamp securely on the Wooden nightstand or dresser  (r5_s13)
- R5 [LOCAL] position the Small bedside alarm clock upright and accessibly on the Wooden nightstand or dresser  (r5_s14)
```

### Centralized (TF=2 PF=4 OC=2 SC=2 Final=2.4)

```
[0-5 min]
- R1 SliceObject (apple) (r1_s1)

[5-10 min]
- R1 PourObject (water into cup) (r1_s2)

[10-15 min]
- R1 PassReceiveObject (sliced apple and cup of water to R2) (r1_s3)

[0-5 min]
- R2 navigate to the living room to assist R3 with any light objects (r2_s1)

[5-10 min]
- R2 assist R3 by picking up and passing any light objects (r2_s2)

[10-15 min]
- R2 return to the kitchen to help R1 if necessary (r2_s3)

[0-5 min]
- R3 picks up the laptop from the table. (r3_s1)

[5-10 min]
- R3 closes the laptop to prepare it for bedtime. (r3_s2)

[10-15 min]
- R3 places the closed laptop back on the table. (r3_s3)

[0-5 min]
- R4 navigate to the kitchen to assist R1 (r4_s1)

[5-10 min]
- R4 assist R1 with any light objects (r4_s2)

[10-15 min]
- R4 return to the living room to help R3 if necessary (r4_s3)

[0-5 min]
- R5 can_navigate to the trash can and PickupHeavyObject to move it to a corner of the room. (r5_s1)

[5-10 min]
- R5 can_navigate to the desk and PickupLightObject to organize any loose items on the desk. (r5_s2)

[10-15 min]
- R5 can_navigate to the bed and PushFurniture to ensure it is aligned against the wall. (r5_s3)

[0-5 min]
- R6 can_navigate to the bathtub area to check for any heavy objects. (r6_s1)

[5-10 min]
- R6 PickupHeavyObject if any heavy items are found in or around the bathtub and move them to a safe location. (r6_s2)

[10-15 min]
- R6 can_navigate to the countertop to ensure it is clear of heavy objects, moving any found to a safe location. (r6_s3)
```

### Independent (TF=5 PF=1 OC=5 SC=3 Final=3.9)

```
[0-5 min]
- R1 Turn off the stove (r1_s1)

[5-10 min]
- R1 Put away the bread (r1_s2)

[10-15 min]
- R1 Turn off the coffee maker (r1_s3)

[0-5 min]
- R2 turns off the kitchen lights to prepare for bedtime. (r2_s1)

[5-10 min]
- R2 closes any open cabinets to tidy the kitchen. (r2_s2)

[10-15 min]
- R2 ensures the kitchen counter is clear by organizing visible items like the vase and bowl. (r2_s3)

[0-5 min]
- R3 Turn off the ceiling light (r3_s1)

[5-10 min]
- R3 Turn off the floor lamp (r3_s2)

[10-15 min]
- R3 Close the laptop (r3_s3)

[0-5 min]
- R4 Turn off the lamp on the side table to prepare for bedtime. (r4_s1)

[5-10 min]
- R4 Close the curtains to block out light from outside. (r4_s2)

[10-15 min]
- R4 Turn off the overhead light above the dining table. (r4_s3)

[0-5 min]
- R5 turn off the desk lamp (r5_s1)

[5-10 min]
- R5 close the window blinds (r5_s2)

[10-15 min]
- R5 tidy the desk by organizing items (r5_s3)

[0-5 min]
- R6 Turn off the bathroom light to prepare for bedtime. (r6_s1)
```

### LaMMA-P (TF=2 PF=1 OC=1 SC=2 Final=1.45)

```
### Joint Plan

[0-5 min]
- R4 go to LightSwitch (r4_s1)
- R4 turn off LightSwitch (r4_s2)
- R6 go to FloorLamp (r6_s1)
- R6 turn off FloorLamp (r6_s2)
- R4 go to DeskLamp (r4_s3)
- R4 turn off DeskLamp (r4_s4)
- R6 go to Window (r6_s3)
- R6 close Window (r6_s4)
- R4 go to Curtains (r4_s5)
- R4 close Curtains (r4_s6)
- R6 go to Television (r6_s5)
- R6 turn off Television (r6_s6)
- R4 go to Laptop (r4_s7)
- R4 turn off Laptop (r4_s8)

[5-10 min]
- R6 go to Door (r6_s7)
- R6 lock Door (r6_s8)

[10-15 min]
- R4 go to AlarmSystem (r4_s9)
- R4 set Alarm (r4_s10)
```

### SMART-LLM (TF=2 PF=1 OC=1 SC=2 Final=1.45)

```
### Joint Plan

[0-5 min]
- R4 turn off LivingRoomLight (r4_s1)
- R4 turn off KitchenLight (r4_s2)
- R4 turn off HallwayLight (r4_s3)
- R6 close LivingRoomCurtains (r6_s1)
- R6 close BedroomCurtains (r6_s2)
- R6 close LivingRoomWindow (r6_s3)
- R6 close BedroomWindow (r6_s4)
- R6 lock FrontDoor (r6_s5)
- R6 lock BackDoor (r6_s6)
- R3 clean Bedroom (r3_s1)
- R3 arrange Bedroom (r3_s2)
- R4 set AlarmClock (r4_s4)

[5-10 min]
- R3 continue arranging Bedroom (r3_s3)

[10-15 min]
- R3 finalize Bedroom preparation (r3_s4)
```

# task10_abstract

> I need to do the dishes in 15 minutes. Clean up the kitchen and bring back anything that belongs there.

## Run 1

### Ours (CDA) (TF=3 PF=9 OC=9 SC=3 Final=6.3)

```
### Joint Plan — task10_abstract  (about 20 min / deadline 15 min: MISSED)

[0-5 min]
- R1 [LOCAL] move the Dish-soap bottle to the counter beside the sink  (r1_s1)
- R2 [LOCAL] move the White bowl from its visible location to the sink  (r2_s1)
- R4 [LOCAL] pick up the Green recycling bin in the living room for return to the kitchen  (r4_s1)
- R5 [LOCAL] pick up the Bowl from the bedroom desk  (r5_s1)
- R6 [LOCAL] pick up the Gray bowl from the bedroom desk for immediate delivery to the kitchen  (r6_s1)
- R1 [LOCAL] move the White mug on the stove from the stove to the sink  (r1_s2)
- R2 [LOCAL] move the White plate from its visible location to the sink  (r2_s2)
- R4 [PASS] pass Green recycling bin to R2 (offered) (brings it to the kitchen)  (r4_s2)
- R5 [PASS] pass Bowl to R6 (offered) (hands it over; R6 collects it)  (r5_s2)
- R6 [PASS] pass Gray bowl to R1 (offered) (brings it to the kitchen)  (r6_s2)
- R1 [LOCAL] move the Frying pan on the stove from the stove to the sink  (r1_s5)
- R2 [LOCAL] move the Visible eating utensils from the dining area to the sink  (r2_s3)
- R6 [RECEIVE] receive Bowl from R5 (collects it from the bedroom)  (r6_s3)
- R2 [LOCAL] move the Orange mug from its visible location to the sink  (r2_s4)

[5-10 min]
- R1 [LOCAL] move the Black cooking pot to the sink  (r1_s6)
- R6 [LOCAL] move the Bowl from the bedroom to the kitchen and place it with the dishes for washing  (r6_s4)
- R1 [LOCAL] move the White cup to the sink  (r1_s7)
- R2 [LOCAL] move the Cutting board from the counter to the sink  (r2_s5)
- R1 [LOCAL] move the White saucer to the sink  (r1_s8)
- R2 [LOCAL] move the washed White bowl from the washing area to dish storage  (r2_s8)
- R1 [LOCAL] move the Small white dish to the sink  (r1_s9)
- R2 [LOCAL] move the washed White plate from the washing area to dish storage  (r2_s9)
- R1 [LOCAL] move the Knife to the sink  (r1_s10)
- R2 [LOCAL] move the washed Visible eating utensils from the washing area to utensil storage  (r2_s10)

[10-15 min]
- R1 [LOCAL] move the Onion from the counter to reachable food storage  (r1_s12)
- R2 [LOCAL] move the washed Orange mug from the washing area to mug storage  (r2_s11)
- R1 [LOCAL] move the Lime from the counter to reachable food storage  (r1_s14)
- R2 [LOCAL] move the washed Cutting board from the washing area to cutting-board storage  (r2_s12)
- R1 [LOCAL] move the Pear from the counter to reachable food storage  (r1_s15)
- R2 [LOCAL] move the washed Gray bowl from the washing area to bowl storage  (r2_s13)
- R1 [LOCAL] move the Cardboard box from the counter to the kitchen recycling area  (r1_s17)
- R2 [LOCAL] put the Red apple on shelving rack into kitchen food storage  (r2_s14)
- R2 [LOCAL] move the Loaf of bread from the counter to bread storage  (r2_s15)

[15-20 min]
- R1 [RECEIVE] receive Gray bowl (one gray bowl returned to the kitchen) from R6  (r1_s18)
- R1 [LOCAL] place the returned Gray bowl at the kitchen sink for washing  (r1_s19)
- R2 [LOCAL] move the Green apple from the counter to refrigerated food storage  (r2_s16)
- R2 [LOCAL] move the Green bottle or container from the counter to its kitchen storage location  (r2_s17)
- R2 [RECEIVE] receive Green recycling bin (one green recycling bin delivered to the kitchen) from R4  (r2_s18)
- R2 [LOCAL] move the returned Green recycling bin to the kitchen recycling station  (r2_s19)
```

### Centralized (TF=2 PF=2 OC=2 SC=1 Final=1.85)

```
[0-5 min]
- R1 PickupLightObject (Fork) (r1_s1)

[5-10 min]
- R1 PassReceiveObject to R2 (Fork) (r1_s2)

[10-15 min]
- R1 PickupLightObject (Spoon) (r1_s3)

[15-20 min]
- R1 PassReceiveObject to R2 (Spoon) (r1_s4)

[20-25 min]
- R1 PickupLightObject (Tomato) (r1_s5)

[25-30 min]
- R1 PassReceiveObject to R2 (Tomato) (r1_s6)

[0-5 min]
- R2 navigate to the counter and pick up the potato. (r2_s1)

[5-10 min]
- R2 navigate to the table and place the potato there. (r2_s2)

[10-15 min]
- R2 navigate to the counter and pick up the tomato. (r2_s3)

[15-20 min]
- R2 navigate to the table and place the tomato there. (r2_s4)

[20-25 min]
- R2 check for any other light objects on the counter and move them to the table if necessary. (r2_s5)

[0-5 min]
- R3 PickupLightObject (papers on the table) (r3_s1)

[5-10 min]
- R3 PassReceiveObject (papers to R4) (r3_s2)

[10-15 min]
- R3 PickupLightObject (box on the table) (r3_s3)

[15-20 min]
- R3 PassReceiveObject (box to R4) (r3_s4)

[0-5 min]
- R4 navigate to the coffee table (r4_s1)

[5-10 min]
- R4 PickupLightObject (magazines) from the coffee table (r4_s2)

[10-15 min]
- R4 navigate to the kitchen and PassReceiveObject (magazines) (r4_s3)

[0-5 min]
- R5 PickupLightObject (bowl) (r5_s1)

[5-10 min]
- R5 PassReceiveObject (bowl to R6) (r5_s2)

[10-15 min]
- R5 PickupLightObject (remote) (r5_s3)

[15-20 min]
- R5 PassReceiveObject (remote to R6) (r5_s4)

[0-5 min]
- R6 navigate to the desk area and identify any kitchen-related items. (r6_s1)

[5-10 min]
- R6 pickup any light or heavy kitchen-related objects from the desk. (r6_s2)

[10-15 min]
- R6 navigate to the door to pass the collected items to the kitchen. (r6_s3)

[0-5 min]
- R7 PickupLightObject (soap) from the sink area (r7_s1)

[5-10 min]
- R7 PickupLightObject (spray bottle) from the bathroom (r7_s2)

[10-15 min]
- R7 PassReceiveObject (soap and spray bottle) to R8 when it arrives (r7_s3)

[0-5 min]
- R8 can_navigate to the sink area to check for any kitchen items. (r8_s1)

[5-10 min]
- R8 PickupLightObject any kitchen items found near the sink. (r8_s2)

[10-15 min]
- R8 can_navigate to the bathroom door and pass the collected items to the kitchen. (r8_s3)
```

### Independent (TF=2 PF=2 OC=2 SC=2 Final=2.0)

```
[0-5 min]
- R1 Pick up the dirty dishes from the counter and place them in the sink. (r1_s1)

[5-10 min]
- R1 Use dish soap and water to wash the dishes in the sink. (r1_s2)

[10-15 min]
- R1 Dry the dishes and place them back on the counter. (r1_s3)

[0-5 min]
- R2 picks up the dishes from the counter and places them in the sink for washing. (r2_s1)

[5-10 min]
- R2 tidies up the counter by organizing any loose items. (r2_s2)

[10-15 min]
- R2 checks the trash can and ensures it is not overflowing, ready for any waste from dishwashing. (r2_s3)

[0-5 min]
- R3 PickupLightObject (papers on the table) and organize them. (r3_s1)

[5-10 min]
- R3 PickupLightObject (empty box on the table) and place it neatly on the shelf. (r3_s2)

[10-15 min]
- R3 PickupLightObject (any small items on the floor) and place them on the table. (r3_s3)

[0-5 min]
- R4 PickupLightObject (r4_s1)

[5-10 min]
- R4 Navigate to kitchen (r4_s2)

[10-15 min]
- R4 Place object in kitchen (r4_s3)

[0-5 min]
- R5 PickupLightObject (bowl) (r5_s1)

[5-10 min]
- R5 PassReceiveObject (bowl) to another robot if they come to the bedroom (r5_s2)

[10-15 min]
- No action needed (r5_s3)

[0-5 min]
- R6 PickupLightObject (pick up the green plate from the floor) (r6_s1)

[5-10 min]
- R6 can_navigate (navigate to the kitchen) (r6_s2)

[10-15 min]
- R6 PassReceiveObject (place the green plate in the kitchen) (r6_s3)

[0-5 min]
- R7 PickupLightObject (spray bottle) and prepare to pass it to another agent for cleaning tasks. (r7_s1)

I'm unable to view the image, but based on the description, here's what I can do:

[0-5 min]
- R8 PickupLightObject: SprayBottle from the bathroom (r8_s1)

[5-10 min]
- R8 can_navigate: Move to the kitchen with the SprayBottle (r8_s2)

[10-15 min]
- R8 PassReceiveObject: Place SprayBottle in the kitchen for cleaning purposes (r8_s3)
```

### LaMMA-P (TF=2 PF=1 OC=2 SC=2 Final=1.8)

```
### Joint Plan

[0-5 min]
- R4 Identify items to be returned (r4_s1)
- R6 Identify items to be returned (r6_s1)

[5-10 min]
- R4 Gather items (r4_s2)
- R6 Gather items (r6_s2)
- R3 Clean kitchen surfaces (r3_s1)

[10-15 min]
- R4 Return items to kitchen (r4_s3)
- R6 Do the dishes (r6_s3)
- R3 Clean kitchen appliances (r3_s2)
```

### SMART-LLM (TF=4 PF=2 OC=2 SC=2 Final=2.6)

```
### Joint Plan

[0-5 min]
- R3 Collect dirty plates and place in sink (r3_s1)
- R4 Collect dirty cups and place in sink (r4_s1)
- R6 Collect dirty bowls and place in sink (r6_s1)

[5-10 min]
- R6 Wash dishes in sink (r6_s2)

[10-15 min]
- R3 Dry and store plates in cabinet (r3_s2)
- R4 Dry and store cups in cabinet (r4_s2)
- R6 Dry and store bowls in cabinet (r6_s3)

[10-15 min]
- R3 Return forks to drawer (r3_s3)
- R4 Return knives to drawer (r4_s3)
- R6 Return spoons to drawer (r6_s4)
```

## Run 2

### Ours (CDA) (TF=3 PF=2 OC=2 SC=3 Final=2.45)

```
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
```

### Centralized (TF=2 PF=2 OC=2 SC=1 Final=1.85)

```
[0-5 min]
- R1 PickupLightObject (Fork) (r1_s1)
- R1 PassReceiveObject to R2 (r1_s2)

[5-10 min]
- R1 PickupLightObject (Spoon) (r1_s3)
- R1 PassReceiveObject to R2 (r1_s4)

[10-15 min]
- R1 PickupLightObject (Tomato) (r1_s5)
- R1 PassReceiveObject to R2 (r1_s6)

[0-5 min]
- R2 navigate to the counter and pick up the potato. (r2_s1)

[5-10 min]
- R2 navigate to the table and place the potato there. (r2_s2)

[10-15 min]
- R2 navigate to the counter and pick up the tomato. (r2_s3)
- R2 navigate to the table and place the tomato there. (r2_s4)

[0-5 min]
- R3 PickupLightObject (papers on the table) (r3_s1)

[5-10 min]
- R3 PassReceiveObject (papers to R4) (r3_s2)

[10-15 min]
- R3 PickupLightObject (box on the table) (r3_s3)

[15-20 min]
- R3 PassReceiveObject (box to R4) (r3_s4)

[0-5 min]
- R4 navigate to the coffee table (r4_s1)

[5-10 min]
- R4 pickup light objects (e.g., papers, small items) from the coffee table (r4_s2)

[10-15 min]
- R4 navigate to the kitchen and pass the collected items (r4_s3)

[0-5 min]
- R5 PickupLightObject (bowl) from the desk (r5_s1)

[5-10 min]
- R5 PassReceiveObject (bowl) to R6 when it arrives (r5_s2)

[0-5 min]
- R6 navigate to the desk area and identify any kitchen-related items. (r6_s1)

[5-10 min]
- R6 pick up any light objects that belong in the kitchen, such as cups or utensils. (r6_s2)

[10-15 min]
- R6 navigate to the door and pass the collected items to the kitchen. (r6_s3)

[0-5 min]
- R7 PickupLightObject (soap) from the sink area (r7_s1)

[5-10 min]
- R7 PickupLightObject (spray bottle) from the bathroom (r7_s2)

[10-15 min]
- R7 PassReceiveObject (soap and spray bottle) to R8 when it arrives (r7_s3)

[0-5 min]
- R8 can_navigate to the sink area to check for any kitchen items. (r8_s1)

[5-10 min]
- R8 PickupLightObject any kitchen items found near the sink. (r8_s2)

[10-15 min]
- R8 can_navigate to the kitchen to deliver the collected items. (r8_s3)
```

### Independent (TF=2 PF=1 OC=1 SC=1 Final=1.3)

```
[0-5 min]
- R1 Pick up the apple from the counter and place it in the fruit bowl. (r1_s1)

[5-10 min]
- R1 Pick up the cup from the counter and place it in the sink. (r1_s2)

[10-15 min]
- R1 Use the dish soap to clean the cup in the sink. (r1_s3)

[0-5 min]
- R2 picks up the dishes from the counter and places them in the sink for washing. (r2_s1)

[5-10 min]
- R2 tidies up the counter by organizing any loose items. (r2_s2)

[10-15 min]
- R2 checks the trash can and ensures it is not overflowing, ready for any waste from dishwashing. (r2_s3)

[0-5 min]
- R3 PickupLightObject (papers on the table) (r3_s1)

[5-10 min]
- R3 PickupLightObject (box on the table) (r3_s2)

[10-15 min]
- R3 PassReceiveObject (papers and box to another robot) (r3_s3)

[0-5 min]
- R4 PickupLightObject (magazines from the coffee table) (r4_s1)

[5-10 min]
- R4 can_navigate (to the kitchen) (r4_s2)

[10-15 min]
- R4 PassReceiveObject (magazines to the kitchen) (r4_s3)

[0-5 min]
- R5 PickupLightObject (bowl) from the desk (r5_s1)

[5-10 min]
- R5 Wait for another robot to come and receive the bowl (r5_s2)

[10-15 min]
- R5 PassReceiveObject (bowl) to another robot for transport to the kitchen (r5_s3)

[0-5 min]
- R6 PickupLightObject (green item on the floor) (r6_s1)

[5-10 min]
- R6 PickupLightObject (white item on the floor) (r6_s2)

[10-15 min]
- R6 Navigate to kitchen and place items in appropriate location (r6_s3)

[0-5 min]
- R7 PickupLightObject (soap) from the sink area and prepare to pass it to another robot for kitchen cleaning. (r7_s1)

[0-5 min]
- R8 PickupLightObject (spray bottle) from the bathroom counter (r8_s1)

[5-10 min]
- R8 can_navigate to the kitchen with the spray bottle (r8_s2)

[10-15 min]
- R8 PassReceiveObject (spray bottle) to the kitchen area (r8_s3)
```

### LaMMA-P (TF=3 PF=2 OC=3 SC=2 Final=2.65)

```
### Joint Plan

[0-5 min]
- R3 Identify items to return to the kitchen (r3_s1)
- R4 Identify items to return to the kitchen (r4_s1)
- R6 Identify items to return to the kitchen (r6_s1)

[5-10 min]
- R3 Go to item location and pick up light items (r3_s2)
- R4 Go to item location and pick up small items (r4_s2)
- R6 Go to item location and pick up heavy items (r6_s2)

[10-15 min]
- R3 Return to kitchen and place light items (r3_s3)
- R4 Return to kitchen and place small items (r4_s3)
- R6 Return to kitchen and place heavy items (r6_s3)
- R3 Clean kitchen areas (r3_s4)
- R4 Clean kitchen areas (r4_s4)
- R6 Clean kitchen areas (r6_s4)
```

### SMART-LLM (TF=3 PF=1 OC=2 SC=2 Final=2.1)

```
### Joint Plan

[0-5 min]
- R4 go to dining table (r4_s1)
- R4 identify dirty dishes (r4_s2)
- R4 collect dirty dishes (r4_s3)
- R4 go to countertop (r4_s4)
- R4 identify dirty dishes (r4_s5)
- R4 collect dirty dishes (r4_s6)
- R4 go to sink (r4_s7)
- R4 identify dirty dishes (r4_s8)
- R4 collect dirty dishes (r4_s9)

[5-10 min]
- R3 go to sink (r3_s1)
- R3 put dishes in sink (r3_s2)
- R3 switch on faucet (r3_s3)
- R3 wait for dishes to clean (r3_s4)
- R3 switch off faucet (r3_s5)
- R3 pick up clean dishes (r3_s6)

[10-15 min]
- R3 go to cabinet (r3_s7)
- R3 put clean dishes in cabinet (r3_s8)
- R4 go to dining table (r4_s10)
- R4 clean dining table (r4_s11)
- R4 go to countertop (r4_s12)
- R4 clean countertop (r4_s13)
- R4 identify misplaced items (r4_s14)
- R4 pick up misplaced items (r4_s15)
- R4 go to kitchen (r4_s16)
- R4 put items in kitchen (r4_s17)
```

## Run 3

### Ours (CDA) (TF=2 PF=4 OC=8 SC=2 Final=4.5)

```
### Joint Plan — task10_abstract  (about 25 min / deadline 15 min: MISSED)

[0-5 min]
- R1 [LOCAL] move the White mug near the stove to the sink  (r1_s1)
- R2 [LOCAL] move the White plates from the kitchen surface to the sink  (r2_s1)
- R4 [LOCAL] pick up the Small white dish or bowl on the coffee table for return to the kitchen  (r4_s1)
- R5 [LOCAL] pick up the Gray translucent bowl from the bedroom desk  (r5_s1)
- R1 [LOCAL] move the Red mug to the sink  (r1_s2)
- R2 [LOCAL] move the White bowls from the kitchen surface to the sink  (r2_s2)
- R4 [PASS] pass Small white dish or bowl on the coffee table to R2 (offered) (brings it to the kitchen)  (r4_s2)
- R5 [PASS] pass Gray translucent bowl to R6 (offered) (hands it over; R6 collects it)  (r5_s2)
- R1 [LOCAL] move the White cup to the sink  (r1_s3)
- R6 [RECEIVE] receive Gray translucent bowl (one empty bowl for return to the kitchen and washing) from R5 (collects it from the bedroom)  (r6_s1)
- R1 [LOCAL] move the White saucer to the sink  (r1_s4)
- R6 [LOCAL] place the received Gray translucent bowl inside the Beige bowl on the bedroom desk for transport  (r6_s2)

[5-10 min]
- R2 [LOCAL] move the Silver utensils from the kitchen surface to the sink  (r2_s3)
- R2 [LOCAL] move the Orange mug to the sink  (r2_s4)
- R1 [LOCAL] move the Stacked white dishes on the island to the sink  (r1_s5)
- R2 [LOCAL] move the Black cooking pot from the work area to the sink  (r2_s6)
- R6 [PASS] pass Beige bowl to R2 (offered) (brings it to the kitchen)  (r6_s3)
- R1 [LOCAL] use the Green dish-soap bottle to dispense dish soap into the sink for washing  (r1_s10)
- R1 [LOCAL] place the cleaned Dark utensil in the sink with the clean utensils  (r1_s13)
- R1 [LOCAL] place the cleaned White mug near the stove with the clean cups  (r1_s14)
- R1 [LOCAL] place the cleaned Red mug with the clean cups  (r1_s15)

[10-15 min]
- R2 [LOCAL] move Frying pan and cookware on the stove from the stove to the sink for washing  (r2_s7)
- R2 [LOCAL] move the Loaf of bread from the work surface to the metal shelving rack  (r2_s8)
- R2 [LOCAL] move the Cutting board from the work surface to the metal shelving rack  (r2_s9)
- R2 [LOCAL] move the Green fruit from the work surface into the refrigerator  (r2_s10)
- R1 [LOCAL] place the cleaned White cup with the clean cups  (r1_s16)
- R1 [LOCAL] place the cleaned White saucer with the clean plates  (r1_s17)
- R1 [LOCAL] place the cleaned Stacked white dishes on the island into an organized clean-dish stack  (r1_s18)
- R1 [LOCAL] place the cleaned Small white dish or bowl on the coffee table with the clean dishes  (r1_s19)

[15-20 min]
- R2 [LOCAL] move the White cloth or napkin from the work surface to the sink-side cleaning-supply area  (r2_s11)
- R2 [LOCAL] move the Potted plant from the round dining table to the metal shelving rack  (r2_s12)
- R2 [RECEIVE] receive Small white dish or bowl on the coffee table (one dish or bowl returned to the kitchen) from R4  (r2_s13)
- R2 [LOCAL] place the returned Small white dish or bowl at the sink for washing  (r2_s14)
- R1 [LOCAL] place the cleaned Beige bowl with the clean bowls  (r1_s20)
- R1 [LOCAL] move the Potted plant on the dining table from the dining table to a reachable clear counter section before wiping  (r1_s21)
- R1 [LOCAL] move the Brown food bag or wrapped food item near the sink from the counter to the island  (r1_s24)
- R1 [LOCAL] move the First seasoning shaker from the stove area to a reachable clear counter section  (r1_s27)

[20-25 min]
- R2 [RECEIVE] receive Beige bowl (one bowl returned to the kitchen) from R6  (r2_s17)
- R2 [LOCAL] place the returned Beige bowl at the sink for washing  (r2_s18)
- R2 [LOCAL] move the washed and dried White plates from the drying area to the metal shelving rack  (r2_s19)
- R1 [LOCAL] move the Second seasoning shaker from the stove area to a reachable clear counter section  (r1_s28)
- R1 [LOCAL] move the Second seasoning shaker from the clear counter section back to the cleaned stove area  (r1_s31)
```

### Centralized (TF=2 PF=2 OC=2 SC=2 Final=2.0)

```
[0-5 min]
- R1 PickupLightObject (r1_s1): Pick up the apple from the counter.

[5-10 min]
- R1 SliceObject (r1_s2): Slice the apple and place it on a plate.

[10-15 min]
- R1 PassReceiveObject (r1_s3): Pass the sliced apple to another robot or person for serving.

[0-5 min]
- R2 navigate to the counter to collect the bowl and spoon. (r2_s1)

[5-10 min]
- R2 pass the bowl and spoon to R1 for dishwashing. (r2_s2)

[10-15 min]
- R2 navigate to the shelf to collect the tomato. (r2_s3)
- R2 pass the tomato to R1 for dishwashing. (r2_s4)

[0-5 min]
- R3 PickupLightObject (papers on the table) (r3_s1)

[5-10 min]
- R3 PassReceiveObject (papers to R4) (r3_s2)

[10-15 min]
- R3 PickupLightObject (box on the table) (r3_s3)

[15-20 min]
- R3 PassReceiveObject (box to R4) (r3_s4)

[0-5 min]
- R4 navigate to the coffee table (r4_s1)

[5-10 min]
- R4 pickup any light objects that belong in the kitchen, such as cups or small dishes (r4_s2)

[10-15 min]
- R4 navigate to the kitchen and place the items in their appropriate location (r4_s3)

[0-5 min]
- R5 PickupLightObject (bowl) from the desk. (r5_s1)

[5-10 min]
- R5 Prepare to pass the bowl to R6 when it arrives. (r5_s2)

[10-15 min]
- R5 Wait for R6 to arrive to pass the bowl. (r5_s3)

[0-5 min]
- R6 can_navigate to the desk area to check for any kitchen items. (r6_s1)

[5-10 min]
- R6 PickupLightObject any kitchen-related items found on the desk. (r6_s2)

[10-15 min]
- R6 can_navigate to the kitchen to deliver the items. (r6_s3)

[0-5 min]
- R7 PickupLightObject: Pick up the spray bottle from the counter. (r7_s1)

[5-10 min]
- R7 PrepareObject: Ensure the spray bottle is ready for use by R8. (r7_s2)

[10-15 min]
- R7 PassReceiveObject: Pass the spray bottle to R8 when R8 arrives. (r7_s3)

[0-5 min]
- R8 can_navigate to the sink area to check for any kitchen items. (r8_s1)

[5-10 min]
- R8 PickupLightObject any kitchen items found near the sink. (r8_s2)

[10-15 min]
- R8 can_navigate to the kitchen to deliver the items. (r8_s3)
```

### Independent (TF=3 PF=2 OC=2 SC=2 Final=2.3)

```
[0-5 min]
- R1 Pick up the dirty dishes from the counter and place them in the sink. (r1_s1)

[5-10 min]
- R1 Use dish soap and water to wash the dishes in the sink. (r1_s2)

[10-15 min]
- R1 Dry the dishes and place them back on the counter. (r1_s3)

[0-5 min]
- R2 picks up the dishes from the counter and places them in the sink for washing. (r2_s1)

[5-10 min]
- R2 tidies up the counter by organizing any loose items. (r2_s2)

[10-15 min]
- R2 checks the trash can and ensures it is not overflowing. (r2_s3)

[0-5 min]
- R3 Pick up papers from the coffee table (r3_s1)

[5-10 min]
- R3 Place papers in the recycling bin (r3_s2)

[10-15 min]
- R3 Pick up any cups or dishes on the coffee table (r3_s3)

[0-5 min]
- R4 PickupLightObject (r4_s1)

[5-10 min]
- R4 Navigate to kitchen (r4_s2)

[10-15 min]
- R4 Place object in kitchen (r4_s3)

[0-5 min]
- R5 PickupLightObject (bowl) from the desk to prepare for passing to another agent for kitchen use. (r5_s1)

[0-5 min]
- R6 PickupLightObject (green recycling bin) and bring it to the kitchen (r6_s1)

[5-10 min]
- R6 PickupLightObject (trash can) and bring it to the kitchen (r6_s2)

[10-15 min]
- R6 Return to bedroom (r6_s3)

[0-5 min]
- R7 PickupLightObject (spray bottle) (r7_s1)

[5-10 min]
- R7 PassReceiveObject (spray bottle) to another robot if they come to the bathroom (r7_s2)

[0-5 min]
- R8 PickupLightObject (toothbrush) from the sink area and place it in the holder. (r8_s1)

[5-10 min]
- R8 PickupLightObject (soap dispenser) and ensure it is filled and placed neatly. (r8_s2)

[10-15 min]
- R8 Check for any towels or cloths that need to be tidied or hung properly. (r8_s3)
```

### LaMMA-P (TF=2 PF=2 OC=2 SC=2 Final=2.0)

```
### Joint Plan

[0-5 min]
- R4 gather items (r4_s1)
- R6 gather items (r6_s1)
- R5 clean countertops (r5_s1)

[5-10 min]
- R4 return items to kitchen (r4_s2)
- R6 return items to kitchen (r6_s2)
- R5 clean appliances (r5_s2)

[10-15 min]
- R4 do the dishes (r4_s3)
- R5 clean the floor (r5_s3)
```

### SMART-LLM (TF=2 PF=1 OC=2 SC=2 Final=1.8)

```
### Joint Plan

[0-5 min]
- R6 go to DiningTable (r6_s1)
- R6 collect dirty dishes (r6_s2)
- R6 go to CounterTop (r6_s3)
- R6 collect dirty dishes (r6_s4)
- R6 go to Sink (r6_s5)
- R6 collect dirty dishes (r6_s6)

[5-10 min]
- R3 go to Sink (r3_s1)
- R3 wash dishes (r3_s2)

[10-15 min]
- R6 return clean dishes to designated places (r6_s7)
- R6 organize misplaced items (r6_s8)
- R6 clean CounterTop (r6_s9)
- R6 clean DiningTable (r6_s10)
- R6 clean Sink (r6_s11)
```
