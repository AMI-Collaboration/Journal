# 새 1~5점 프롬프트: TF/GF 점수와 심사 이유 (CDA-1116 현재=run11, LaMMA-P, SMART-LLM)

점수는 반복 2회([rep0, rep1]), 이유는 rep0 원문(영어).

## 2대 task2
- **CDA-1116 TF [1, 1]**: At most one required goal is achieved. R2 places the towel in the bathtub (r2_s2), but the goal to fill the bathtub with warm water is completely missing.
- **CDA-1116 GF [4, 4]**: Exactly one minor violation: R2 picks up the towel from the 'bathroom rack' (r2_s1), which is a hallucinated object not in the list.
- **LaMMA-P TF [3, 3]**: Both core goals (filling the bathtub and placing the towel) are achieved using concrete actions on real objects, but they are completed in the 5-10 min block (r1_s4, r2_s4), which is one block after the 5-minute deadline.
- **LaMMA-P GF [5, 3]**: Zero violations. All actions are physically executable and use listed objects (Faucet, Towel).
- **SMART-LLM TF [3, 3]**: The goals are to fill the bathtub and place a towel nearby. The towel is placed in the 0-5 min block (r2_s4), but the faucet is turned off in the 5-10 min block (r1_s5, r1_s6), finishing one 5-minute block after the deadline.
- **SMART-LLM GF [4, 2]**: Exactly one minor violation: 'Towel Holder' (r2_s3, r2_s4) is hallucinated as it is not in the listed objects.

## 2대 task3
- **CDA-1116 TF [1, 2]**: The goals are to make the desk presentable, see clearly, and hear clearly. Only 'see clearly' is partially achieved by turning on the desk lamp (r2_s1). Moving the garbage can (r2_s2) does not make the desk presentable, and 'hear clearly' is missing. At most one goal is achieved.
- **CDA-1116 GF [3, 5]**: There are two violations: r1_s1 and r2_s1 use 'turn on', which is an action outside the robots' CAN list. Additionally, r1_s1 has weird phrasing ('to the living room floor'). The plan is still mostly executable.
- **LaMMA-P TF [1, 1]**: The goals are to make the desk presentable, see clearly, and hear clearly. All actions addressing these goals (r2_s2, r1_s2, r1_s4) occur in the 5-10 minute block, missing the 5-minute deadline. Zero goals are achieved on time.
- **LaMMA-P GF [2, 1]**: There are four or more violations: r1_s1 (light switch is hallucinated), r2_s2 (clutter is vague/hallucinated), r2_s3 (designated place is vague), r2_s4 (clean desk surface is vague), and r1_s3 (audio device is hallucinated).
- **SMART-LLM TF [1, 1]**: The goals are to make the desk presentable, see clearly, and hear clearly. Only 'see clearly' is achieved (r2_s2). 'Desk presentable' uses hallucinated objects (r1_s2 Newspaper, r1_s4 TissueBox), and 'hear clearly' is vague (r2_s4). At most one goal is achieved.
- **SMART-LLM GF [2, 1]**: There are four or more violations: r2_s1 (LightSwitch is hallucinated), r1_s2 (Newspaper is hallucinated), r1_s4 (TissueBox is hallucinated), r2_s4 (Check Laptop functionality is vague), and r1_s6 (Clean Desk surface is vague).

## 2대 task9
- **CDA-1116 TF [2, 3]**: Goals achieved: Quiet (r1_s1 turns off Television). Goals incomplete: Lights down (bedroom DeskLamp is left on) and Things put away (only Mug and Laptop are moved, leaving many loose objects). Bedroom ready is missed due to a vague step (r2_s6). At least two goals are achieved (or partially achieved) but half or fewer.
- **CDA-1116 GF [4, 4]**: Exactly one minor violation: r2_s6 is a vague step ('ensure the bed') that does not specify a concrete action.
- **LaMMA-P TF [1, 2]**: At most one required goal is achieved. Lights down is incomplete (r1_s2 is vague, only DeskLamp is turned off in r2_s10). Things put away is not achieved because objects are moved to vague 'storage locations'. Bedroom ready and Quiet are completely missed.
- **LaMMA-P GF [1, 1]**: Violations dominate (13 out of 28 steps): r1_s1 (hallucinated 'light switch'), r1_s2 (vague 'Turn off/dim lights'), r2_s3/r1_s5/r2_s7/r1_s9/r1_s13 (vague 'storage location'), r2_s4/r1_s6/r2_s8/r1_s10/r1_s14 (vague 'Put away'), and r2_s12 (hallucinated 'windows/doors').
- **SMART-LLM TF [2, 2]**: Goals achieved: Quiet (r1_s5 turns off Television) and Bedroom ready (r2_s5). Things put away is incomplete (only RemoteControl is moved). Lights down is not achieved because it relies entirely on hallucinated objects. Two goals achieved is half or fewer.
- **SMART-LLM GF [1, 1]**: Violations dominate (7 out of 11 steps): r1_s1 (LivingRoomLight), r1_s2 (KitchenLight), r1_s3/r1_s4 (BedroomLight), r2_s3 (Magazine), r2_s4 (MagazineRack), and r1_s6 (Radio) all use hallucinated objects that do not exist in the rooms.

## 4대 task2
- **CDA-1116 TF [1, 1]**: Only one required goal is achieved (towel nearby). As explicitly stated in the rules, the action 'pour the faucet' does not fit its object and therefore does not produce the state of a filled bathtub.
- **CDA-1116 GF [3, 3]**: Two violations: 'bathroom towel rack' and 'bathroom shelf' are hallucinated places not matching listed objects.
- **LaMMA-P TF [2, 2]**: The goals are achieved, but the plan finishes in the [15-20 min] block, exceeding the deadline by more than one 5-minute block.
- **LaMMA-P GF [3, 3]**: Two independent violations: R3 navigates (r3_s1, r3_s3) despite lacking the capability; R4 operates the faucet (r4_s2, r4_s4) despite lacking manipulation/pour capabilities.
- **SMART-LLM TF [3, 3]**: The goals (bathtub filled, towel nearby) are achieved, but the plan finishes in the [5-10 min] block, exceeding the 5-minute deadline by one block.
- **SMART-LLM GF [2, 2]**: Four violations: R3 navigates (r3_s1) but CANNOT navigate; 'Heater' is hallucinated; R2 operates the faucet (r2_s2) but lacks manipulation capabilities; 'TowelHolder' is hallucinated.

## 4대 task3
- **CDA-1116 TF [1, 1]**: At most one required goal is achieved. The 'turn on' actions (r1_s1, r3_s1) are invalid as they are outside the robots' capabilities, so the lighting goals are not achieved. Moving the garbage can and plant does not make the desk presentable.
- **CDA-1116 GF [2, 5]**: Four or more violations: 'turn on' is not in the CAN list for R1 (r1_s1) and R3 (r3_s1), and 'bedroom corner' is a vague location (r4_s3, r4_s4). This makes the core lighting actions impossible.
- **LaMMA-P TF [1, 1]**: At most one required goal is achieved. The 'Turn on' actions (r3_s2, r4_s5) are outside the robots' capabilities, so the lighting and laptop goals are not achieved. Other goals rely on hallucinated objects.
- **LaMMA-P GF [1, 1]**: Violations dominate: R3 cannot navigate (r3_s1), 'Turn on' is not in the CAN list (r3_s2, r4_s5), and multiple hallucinated objects/places are used such as desk, light switch, clutter, and storage.
- **SMART-LLM TF [1, 1]**: At most one required goal is achieved. The 'Switch on' actions (r2_s2, r3_s2, r3_s4) are outside the robots' capabilities, meaning the lighting and laptop goals are not achieved.
- **SMART-LLM GF [1, 1]**: Violations dominate: R3 cannot navigate (r3_s1, r3_s3), 'Switch on' and 'Clean' are not in the CAN list, and multiple hallucinated objects are used like Desk, LightSwitch, and Newspaper.

## 4대 task9
- **CDA-1116 TF [1, 3]**: Only the 'things put away' goal is achieved. The 'lights down' and 'bedroom ready' goals are not achieved because lights are left on in the bedroom, kitchen, and bathroom. At most one required goal is achieved.
- **CDA-1116 GF [3, 3]**: There are three isolated violations: hallucinated 'living room desk' (r2_s2), 'living room cabinet' (r2_s3), and 'bathroom shelf' (r4_s4). The rest of the plan is executable.
- **LaMMA-P TF [1, 1]**: No required goals are achieved by concrete actions on real objects, as the plan consists almost entirely of vague actions ('item', 'storage location') and hallucinated objects.
- **LaMMA-P GF [1, 1]**: Violations dominate: hallucinated 'light switch' in multiple rooms, hallucinated 'hallway', hallucinated 'curtains in bedroom', invalid action 'Open bed', and vague references to 'item' and 'storage location'.
- **SMART-LLM TF [2, 2]**: Goals are achieved only through hallucinated objects, such as hallucinated light switches in the living room, kitchen, and bedroom, and a hallucinated sink in the kitchen.
- **SMART-LLM GF [1, 2]**: Violations dominate: hallucinated 'living room light switch' (r4_s1), 'kitchen light switch' (r4_s3), 'bedroom light switch' (r4_s5), 'sink' in kitchen (r3_s6), 'bedroom window' (r4_s7), 'bedroom curtains' (r4_s9), and vague 'dishes' (r3_s5).

## 6대 task2
- **CDA-1116 TF [2, 1]**: Only one goal is achieved (towel placed by r4_s3 and r5_s2). The bathtub goal is incomplete because the faucet is turned on (r4_s1) but never turned off.
- **CDA-1116 GF [1, 1]**: Violations dominate: R1 puts down a pillow in the bathroom (r1_s3) but cannot navigate; hallucinated towel rack (r5_s1) and wall (r4_s2); and R1, R2, and R3 all pick up the same pillow.
- **LaMMA-P TF [3, 3]**: The towel is placed near the bathtub within the 5-minute deadline (r5_s4), but the bathtub filling finishes in the 5-10 minute block (r6_s5), exceeding the deadline by one block.
- **LaMMA-P GF [5, 3]**: Zero violations. All actions are physically executable, use real objects (Towel, Faucet, Bathtub), and are within the robots' capabilities.
- **SMART-LLM TF [3, 3]**: The towel is placed nearby within the 5-minute deadline (r6_s4), but the bathtub filling finishes in the 5-10 minute block (r5_s5), exceeding the deadline by one block.
- **SMART-LLM GF [4, 3]**: There is exactly one minor violation: R6 places the towel on a 'TowelHolder' (r6_s4), which is a hallucinated object not in the bathroom list.

## 6대 task3
- **CDA-1116 TF [1, 1]**: At most one required goal is achieved (turning on the desk lamp in r4_s1). The bedroom light is not turned on, and clearing the desk relies on hallucinated locations ('desk', 'drawer').
- **CDA-1116 GF [1, 3]**: Violations dominate: R1 and R4 cannot navigate but interact with multiple furniture pieces across their rooms (r1_s1, r1_s2, r1_s3, r4_s1, r4_s3). Hallucinated objects/locations include 'Watch_1', 'desk' in the bedroom, and 'drawer' in the bedroom.
- **LaMMA-P TF [1, 1]**: All actions intended to achieve the goals occur in the [5-10 min] block, which is past the 5-minute deadline. Additionally, goals are addressed through vague actions and hallucinated objects.
- **LaMMA-P GF [1, 1]**: Violations dominate: R4 cannot navigate but is instructed to go to the light switch (r4_s1). The plan relies heavily on vague steps ('Pick up items', 'Clean the desk surface') and hallucinated objects ('light switch', 'camera and microphone').
- **SMART-LLM TF [1, 1]**: No required goals are validly achieved. The plan relies on hallucinated objects ('LightSwitch') and vague actions ('Clean Desk'), and objects are placed without being picked up.
- **SMART-LLM GF [1, 1]**: Violations dominate: The plan uses vague steps ('Clean Desk' in r6_s2, 'Check Audio Equipment setup' in r6_s9) and hallucinated objects ('LightSwitch', 'Audio Equipment').

## 6대 task9
- **CDA-1116 TF [3, 3]**: More than half of the required goals are achieved (things put away, bedroom ready, some appliances/lights off), but core goals like turning off lights in the bedroom, bathroom, and kitchen are missing. Score is 3.
- **CDA-1116 GF [3, 3]**: Three isolated violations: R3 puts laptop and statue on a 'shelf' (living room has no shelf), and R3 puts remote on a 'coffee table' (living room has no coffee table). Score is 3.
- **LaMMA-P TF [2, 2]**: Goals are achieved only through hallucinated objects ('LightSwitch', 'Bedroom LightSwitch') and vague actions ('storage for RemoteControl', 'Put away'). Score is 2.
- **LaMMA-P GF [2, 2]**: Four or more violations: hallucinated 'LightSwitch' and 'Bedroom LightSwitch', and vague actions/locations like 'storage for RemoteControl', 'Put away RemoteControl', 'storage for Laptop', 'Put away Laptop'. Score is 2.
- **SMART-LLM TF [2, 2]**: Goals are achieved only through hallucinated objects ('LivingRoomLight', 'KitchenLight', 'BedroomLight', 'Bookshelf'). Score is 2.
- **SMART-LLM GF [1, 2]**: Violations dominate: hallucinated objects ('LivingRoomLight', 'KitchenLight', 'BedroomLight', 'Bookshelf'), vague actions ('Final check to ensure...'), and multiple physical actions combined into single steps (r6_s4, r6_s5, r6_s6). Score is 1.

## 평균 (9개 조합 × 반복 2회)

| 방법 | TF | GF |
|---|---|---|
| CDA-1116 | 1.61 | 3.06 |
| LaMMA-P | 1.72 | 2.06 |
| SMART-LLM | 2.00 | 1.78 |
