# FINAL PROMPT v19 — TF / PF / OC / SC (reference-aligned)

## MANDATORY POSSESSION OVERRIDE — HIGHEST PRIORITY (SC ONLY)

These rules override any conflicting interpretation elsewhere in this evaluation prompt.

1. PUT DOWN FROM GRIPPER: If an action says an object is put down "from the gripper", the acting robot's possession immediately before that action is already established. A missing earlier PICKUP action MUST NOT be treated as "never acquired" or as a missing prerequisite. Do not count this as an SC error.
2. PASS: A PASS action itself establishes that the sender possesses or controls the object immediately before transfer. A missing earlier PICKUP action MUST NOT be treated as "never acquired". Do not count this as an SC error.
3. RECEIVE: RECEIVE or explicit collection establishes the receiver's possession. Check whether dependent actions occur before receipt. A delay between PASS and RECEIVE is not automatically an error.
4. MANDATORY CONTRADICTION CHECK: Before assigning any SC score, compare every alleged possession violation against the original action text. If explicit gripper or PASS evidence exists, remove the unsupported "never acquired" violation from the error count and reassess the score.
5. PROHIBITED REASONING: Do not write that a robot "never picked up", "never acquired", or "never possessed" an object when the same plan explicitly establishes its possession through gripper wording or PASS.

These rules apply equally to all supplied methods.

## Task
{task_text}

## Agent Configuration
{AGENT_CONFIG}

## Ground-Truth Object Inventory
The following inventory is loaded from the task scene database. Use it only to verify whether a named object exists in the task rooms. Room presence does not automatically mean an individual robot observed it; apply OC separately. Hidden objects are explicitly marked.
{ROOM_OBJECTS_TEXT}

## Natural Language Plans
Evaluate each plan below independently using exactly the same criteria. The labels PLAN_A, PLAN_B, etc. are anonymous identifiers; do not infer or guess the method behind a label. Do not rank plans against one another. Score each plan on its own evidence.

{plans_block}

## Scoring Instructions

Score each criterion from 0 to 5 (5 is the maximum; 0 is the minimum). Evaluate the actual plan evidence, not the writing style, confidence, length, or formatting. Use the full integer scale 0, 1, 2, 3, 4, 5. Do NOT use decimal scores or scores above 5.

### Scoring procedure

For each plan and each criterion, assign the highest 0-to-5 score whose anchor is supported by concrete evidence. Use the full integer scale; never use decimals or scores outside 0-5. Apply the same definitions to every plan. Do not infer a score from a method name, expected ranking, or comparison with another plan.

Reasons must identify the evidence that supports the selected score and the material issue(s) that prevent the next higher score. Do not manufacture a list of hypothetical faults merely to justify lower scores. If evidence is missing or ambiguous, state exactly what cannot be established and distinguish uncertainty from a confirmed violation.

Evaluate TF, PF, OC, and SC independently. A single underlying issue may affect more than one criterion only when it has a distinct consequence under each criterion. Do not double-penalize one issue merely by renaming it. Do not add or subtract points to achieve a preferred ranking.

### TF: Task Fulfillment

Evaluate Task Fulfillment (TF) according to the reference rubric's criterion A1: Required Goal Fulfillment. TF measures how completely the combined plan supports all required task outcomes.

#### 1. Establish the required goals before scoring
- Use the task's ground-truth goals as the authoritative reference when available. Otherwise derive required outcomes from the task description without inventing requirements.
- Identify each required outcome, destination, condition, required quantity, and explicit deadline.
- Follow the task's stated goal granularity. Do not split one open-ended or collective outcome into extra required goals merely because several candidate objects or sub-actions appear in the plan.
- Separate required goals from optional, supportive, redundant, or alternative actions. Do not promote optional details into requirements.
- Apply the same required goals and interpretation to every method.

#### 2. Search the complete joint plan
- Review every robot's relevant actions and explicit communications over the complete plan.
- A goal may be achieved by one robot or by complementary actions from multiple robots.
- Before marking a goal unachieved, search every robot and every relevant time interval for a complete qualifying path.
- Recognize semantically equivalent objects and actions. Do not demand a literal action token when the action's meaning clearly supports the required outcome.
- Do not assume unreported actions, movements, handoffs, object-state changes, or successful completion.
- Count each required goal once, even when several robots contribute.

#### 3. Determine each goal's achievement status
For every required goal, assign one status:
- **Achieved (1.0):** A sufficiently complete and feasible action path supports the required outcome under the explicit task constraints.
- **Partially achieved (0.5):** Meaningful progress is documented, but an essential action, dependency, destination, quantity, or condition remains incomplete or unsupported.
- **Not achieved (0.0):** The goal is omitted, unsupported, or infeasible under the documented constraints.
- Mere mention, intention, assignment, or a claim of success is not an action path.
- When only a plan is provided, judge whether the proposed actions support the expected outcome; do not require proof of physical execution.
- Do not require a surface, container, intermediate step, or exact object unless the task or ground truth requires it.

#### 4. Interpret open-ended outcomes and ground objects
- Use the Ground-Truth Object Inventory to verify object existence and any explicitly stated room or hidden/invisible status.
- For an open-ended singular request (for example, "a snack" or "something quick to eat"), one suitable existing object is enough when the plan documents its handling and arrival at the required destination.
- For a collective goal, require multiple objects only when the task or ground truth explicitly specifies multiple items or categories. Do not turn examples or possible alternatives into additional mandatory goals.
- For a specific-object goal, verify the named object against the inventory and accept unambiguous synonyms.
- A generic category phrase alone does not prove completion. It may support partial progress only when the plan documents meaningful actions toward the outcome.
- If the inventory is unavailable or not known to be exhaustive, state that grounding is uncertain. Do not invent an object match or automatically declare an object nonexistent.
- Scene existence does not establish what a particular robot observed; assess information access under OC.

#### 5. Evaluate deadlines per required goal
- Determine the earliest time at which the complete essential action path for EACH required goal is supported.
- Compare that goal-completion time with the task's explicit deadline.
- Do not use the final timestamp or makespan of the entire plan as a substitute for an individual goal's completion time.
- Later optional, redundant, or unrelated actions do not invalidate a required goal already completed within the deadline.
- If an essential action for a required goal occurs after the deadline, that goal is not fully achieved within the deadline.
- Use explicit plan times and scheduling metadata as evidence, cross-checking metadata against the actions. Do not invent durations or use API/runtime wall-clock time.

#### 6. Keep TF separate from PF, OC, and SC
- Reduce TF for a capability, information, ordering, or dependency issue only when it actually prevents or undermines a required outcome.
- Redundant work, inefficient allocation, repeated actions, or an invalid optional branch do not automatically reduce or cap TF when a complete valid path still achieves the required outcome.
- A duplicate or conflicting action affects TF only when it invalidates the successful path, blocks the outcome, or pushes an essential action beyond the deadline. Explain that consequence.
- Do not reward extra agents, longer plans, extra object mentions, or coordination language unless they contribute to a required outcome.

#### 7. Calculate the TF score consistently
- Use explicit ground-truth goal weights when supplied; otherwise use equal weights.
- Assign each goal its achievement value: Achieved = 1.0, Partially achieved = 0.5, Not achieved = 0.0.
- Calculate Coverage = sum(goal_weight * achievement_value) / sum(goal_weights).
- Calculate TF_10 = round(1 + 9 * Coverage).
- Convert to the required 0-to-5 output using TF = round(5 * (TF_10 - 1) / 9). Use conventional half-up rounding.
- Do not add a subjective adjustment, duplicate-work cap, whole-plan-makespan cap, or method-specific adjustment after this calculation.
- The reported TF must match the calculation exactly.

#### 8. Required TF reasoning
For every goal, report the required outcome, weight, qualifying object or alternative, responsible robot(s), action path, destination/condition, earliest completion time, deadline status, achievement value, and any essential unmet requirement or uncertainty.
Then show the Coverage calculation, TF_10 calculation, and final 0-to-5 TF conversion. Explain why the selected status is supported by the plan. Apply the same standard to every method and do not target a preferred ranking.

### PF: Plan Feasibility — is it executable given each agent's capabilities?

Evaluate whether the plan's actions are executable given each agent's capabilities.

Check the following score descriptions from 5 down to 0, one point at a time, and select the highest supported score:
- 5: All or nearly all actions are executable given the assigned agents' specified capabilities. No material capability violations remain.
- 4: Most actions are executable by the assigned agents; any remaining capability concerns are minor or limited and do not undermine the main task path.
- 3: The main task path is still feasible, but meaningful capability or assignment concerns remain and require attention.
- 2: Several actions exceed or conflict with known capabilities, and important steps are substantially undermined.
- 1: Most essential actions are infeasible given the assigned agents' known capabilities. Major capability violations prevent reliable execution.
- 0: No meaningful executable action path is supported by the plan, or the plan is absent/entirely incompatible with the specified capabilities.

Base PF on the actions and the capabilities specified in the evaluation input. Do not assume unsupported capabilities or penalize actions based on capabilities that are not specified.

Criterion boundary: PF evaluates intrinsic robot capabilities using the explicit CAN/CANNOT list. Map pickup to PickupLightObject/PickupHeavyObject, slicing to SliceObject, pouring to PourObject, passing/receiving to PassReceiveObject, and inter-room movement to can_navigate. Do not penalize an action when the assigned robot explicitly has the required capability in CAN. A robot putting down an object it never picked up or received is an object-possession/prerequisite problem under SC, not by itself an intrinsic PF capability violation. Keep the existing PF deductions for vague object and location references.

### Additional PF Deductions — Vague Object and Location References
Penalize any of the following vague expressions, as they indicate the plan does not specify concrete, executable actions:
- "any ..." (e.g., "any items", "any small objects", "any clutter")
- "one of the ..." without naming the specific object
- "something" / "anything" / "some items" / "some objects"
- Generic terms without specific object names: "clutter", "mess", "stuff", "things", "items", "misplaced items"
- Vague food/snack references: "quick snack item", "snack", "food item" without naming the object
- Vague location references: "somewhere", "appropriate place", "within reach", "nearby", "reachable position", "close to", "near", "somewhere accessible"
- Object names that change throughout the plan (e.g., "bread" → "sandwich" → "food") — inconsistent object naming indicates ambiguity

In PF_reason, cite concrete actions and specified capabilities, identify any vague references and capability conflicts, and explain the descending 5-to-0 check. Do not deduct for a valid synonym or a location that is clear from the task context.

### OC: Observability Consistency

Evaluate whether the plan respects a TRUE DISTRIBUTED setting.

Each agent initially knows its own room and cannot see or automatically know the contents of other rooms unless the relevant information is explicitly provided through task instructions or communicated by another agent. Information available to the overall planner or evaluator must not automatically be treated as information available to every individual agent.

OC evaluates INFORMATION ACCESS, not plan organization, object existence, physical capability, or action ordering.

1. Establish each agent's information boundary.

For each agent, determine what it could know before performing each relevant action.

- The agent may use information explicitly provided to it by the current task instructions or its configuration.
- The agent may use information obtained from its own room and observations.
- The agent may use information explicitly communicated to it by another agent, provided the message was received before the dependent action.
- An agent must not automatically know the objects, locations, or hidden states of another room merely because those facts appear in the combined plan or scene inventory.
- A centralized or combined plan does not itself prove that every agent has received the information contained in it.

2. Check cross-room information.

For every action involving information about another room, ask:

- Was the relevant fact explicitly provided to the acting agent?
- Did the agent obtain the information through its own observation or presence in the relevant room?
- Did another agent communicate the information before the action?
- Does the communication actually contain the specific information being used?

If none of these sources supports the information, treat the action as an unsupported cross-room information assumption.

Do not assume that an agent knows another room's objects or their locations simply because another agent can access that room.

3. Check hidden and invisible objects.

- Do not assume an agent knows the location or state of an explicitly hidden or invisible object without a valid discovery or communication event.
- A general statement that an object exists does not establish its room or exact position.
- Knowing an object's room does not establish its exact position or hidden state.
- A discovery or observation action can establish information only to the extent supported by the task input and action description.
- Do not invent a hidden-object restriction when the task input does not establish that the object is hidden or invisible.

4. Check communication evidence.

Explicit ASK_HELP / HELP / PASS / RECEIVE-style interaction is positive evidence of distributed coordination only when the information or transfer is actually established.

- A request alone does not mean that a response was received.
- A response counts only for the agent that receives it.
- Use only the information actually conveyed by the message.
- The message must be available before the action that relies on it.
- A message to one agent does not automatically inform other agents.
- Do not award a high OC score merely because communication keywords appear in the plan.

5. Distinguish OC from other criteria.

- An object missing from the environment inventory is not, by itself, an OC violation. Evaluate object grounding under the relevant criterion.
- An action exceeding an agent's physical capabilities is primarily a PF issue.
- An incorrect possession assumption or action dependency is primarily an SC issue.
- Penalize OC when an agent relies on information that it could not have obtained under the distributed information constraints.
- A plan written centrally is not automatically a violation. A material violation occurs when the plan assigns actions based on global or cross-room knowledge that was never made available to the acting agent.

6. Evaluate the scope and severity.

Consider:
- How many independent cross-room or hidden-information assumptions occur.
- Whether the assumptions affect essential actions or only minor details.
- Whether the information was actually communicated or observed.
- Whether the violation is isolated or repeated across agents and task paths.

Count the same underlying unsupported information assumption once. Do not repeatedly penalize every later action that depends on the same root cause. Count separate violations when they involve independent unsupported facts or separate information-boundary failures.

7. Score OC from 1 to 10.

- 1-2: Severe violation of distributed information constraints. Agents repeatedly act on unjustified global, cross-room, or hidden-object information. Essential actions depend on information never made available to the acting agents.
- 3-4: Significant information-boundary violations. Multiple material actions rely on unsupported cross-room knowledge, hidden information, or unjustified assumptions. Some valid local information use may still remain.
- 5-6: Mixed compliance. The plan includes valid local observations or communication, but meaningful information-transfer gaps or unsupported assumptions remain.
- 7-8: Mostly compliant. Agents generally act on their own room information or information actually received from others. Only limited unsupported assumptions remain.
- 9-10: Strong compliance. Each agent consistently acts on its own available information or information explicitly communicated before use. No material cross-room or hidden-information violation remains.

Do not assign OC=1 or OC=2 for one isolated unclear detail. These scores require severe and repeated violations that materially undermine the distributed information constraint.

8. Explain OC.

In OC_reason, identify the relevant agent, action, information being relied upon, and whether that information was available through local knowledge, task instructions, or communication. Explain the number and impact of independent violations. Do not describe an object-existence, capability, possession, or sequencing issue as an OC violation unless it separately demonstrates an information-boundary failure.



### OC clarification — Direct possession and handling evidence

Apply this clarification when evaluating whether an agent has information about an object it physically handles.

- If an action explicitly states that an agent is holding, carrying, grasping, or putting an object down from its gripper, this is direct evidence that the agent has physical access to that same object and knows the identity of the object being handled.
- Do NOT classify the agent's action of handling, carrying, or placing that explicitly possessed object as unsupported cross-room knowledge merely because a separate observation action or message is not listed.
- A stated pickup, collection, PASS/RECEIVE, or equivalent explicit handoff may also establish the relevant object's availability or transfer to the participating agent. Use only what the action actually establishes.
- This evidence is limited to the specific object being handled. It does NOT automatically establish knowledge of the object's original room, exact previous location, hidden state, or other objects.
- If the plan separately relies on an unsupported fact about the object's previous location or another hidden object, evaluate that distinct information assumption on its own evidence.
- Do not count the same physical-possession evidence as both a valid SC possession override and an OC information violation.
- In OC_reason, distinguish direct evidence that an agent possesses or handles an object from unsupported assumptions about information the agent never received.

### SC: Sequential Coherence

Evaluate whether each agent's action sequence respects its prerequisites and dependencies and whether the combined plan can logically lead to the required outcomes.

SC MUST use an integer score from 0 to 5. Apply the same scoring standard to every evaluated method.

## MANDATORY POSSESSION OVERRIDE — HIGHEST PRIORITY

These rules override any conflicting interpretation in the SC evaluation.

1. PUT DOWN FROM GRIPPER:
   If an action says an object is put down "from the gripper", the acting agent's possession immediately before that action is established.
   A missing earlier PICKUP action MUST NOT be treated as "never acquired" or as a missing prerequisite.
   Do not count this as an SC error.

2. PASS:
   A PASS action establishes that the sending agent possesses or controls the object immediately before transfer.
   A missing earlier PICKUP action MUST NOT be treated as "never acquired".
   Do not count this as an SC error.

3. RECEIVE:
   RECEIVE or explicit collection establishes the receiving agent's possession from that point onward.
   Check whether dependent actions occur before receipt.
   A time gap between PASS and RECEIVE is not automatically an error.

4. CONTRADICTION CHECK:
   Before assigning an SC score, compare every alleged possession violation against the original action text. Remove any unsupported claim that an agent never acquired or possessed an object when explicit gripper, holding, carrying, or PASS evidence exists.

5. PROHIBITED REASONING:
   Do not claim that an agent "never picked up", "never acquired", or "never possessed" an object when the plan explicitly establishes possession through these rules.

## 1. Track each agent's own sequence

- Track each agent's actions and movement separately.
- Preserve the stated order within each agent's own plan.
- Agents may act in parallel. The printed order of different agents' plans does NOT establish a shared global timeline.
- For cross-agent dependencies, use explicit timestamps, schedules, messages, handoffs, or other evidence to determine whether a prerequisite occurred in time.
- Do not invent missing actions or unsupported state transitions.
- A compound action may establish its necessary intermediate steps when its wording clearly includes them.

## 2. Check prerequisites and dependencies

For each material action, check whether its required prerequisites were available beforehand:

- The required object is available.
- The object has not already been moved or taken in a way that prevents the action.
- The acting agent possesses the object when possession is required.
- Required preparation or placement has occurred.
- Required assistance, handoff, or information transfer has been completed.
- The agent's established location supports the action.

Penalize a dependency only when the plan provides evidence that the prerequisite was missing, contradicted, or unresolved.

An omitted intermediate action is not automatically proof that a prerequisite was unsatisfied. Check whether the action wording or a compound action establishes it.

## 3. Track agent movement separately from object movement

- Use the initial locations in the current task's agent configuration.
- Track each agent's own room transitions independently.
- Distinguish movement of an agent from movement of an object.
- When an action explicitly transports or carries an object from a source location to a destination, treat the acting agent as having traveled to that destination as part of the transport.
- Do not assume the agent automatically returns to a previous location.
- If the same agent subsequently performs an action requiring the source location, check whether a return transition is stated or clearly included in a compound action.
- A compound action that clearly includes travel and an activity may establish the necessary movement without a separate navigation command.
- If location evidence is incomplete or ambiguous, state the uncertainty rather than asserting a definite contradiction.

A missing transition is a genuine defect only when the agent's current location is established, the next action requires a different location, and no stated or clearly implied movement resolves the conflict.

## 4. Track object state and possession

Track object availability, pickup, carrying, placement, passing, and receiving.

- "From the gripper", "holding", and "carrying" establish possession.
- PASS establishes sender possession immediately before transfer.
- RECEIVE or explicit collection establishes receiver possession.
- A receiver must not perform an action requiring possession before receiving or collecting the object.
- A time gap between PASS and RECEIVE is not automatically a sequencing violation.
- Do not infer possession merely because an object is mentioned, assigned, requested, or nearby.
- Do not assume similarly named objects are identical without supporting evidence.
- A completed placement or transfer updates the object's state according to the stated result.

## 5. Check assistance and communication dependencies

- A request alone does not establish that assistance was provided.
- Check whether a response, assistance action, handoff, or information transfer occurred before a dependent action.
- Check whether the intended agent actually received the required assistance or information.
- A delayed response is not an error when no dependent action occurs before the response.
- Do not penalize an unanswered request when no subsequent action relies on its completion.

## 6. Build a root-cause ledger BEFORE scoring

Do not score by counting every suspicious action independently.

First group affected actions by their underlying cause. For each distinct root cause, record:

- The first action where the dependency fails.
- The missing, contradicted, or unresolved prerequisite.
- All downstream actions affected by that same cause.
- Whether those downstream actions introduce a new independent failure.
- Whether the issue blocks an essential path or is recoverable.
- Whether another explicitly provided valid path remains.

MANDATORY ROOT-CAUSE RULES:

- One missing room transition that affects several consecutive actions is ONE defect, not one defect per affected action.
- One unavailable object or unresolved handoff that causes multiple downstream actions to fail is ONE root cause unless a separate new dependency fails independently.
- Do not convert the number of affected actions into the number of independent errors.
- Count a second defect only when it has a distinct prerequisite failure that would remain even if the first root cause were corrected.
- Do not count uncertain or merely undocumented events as confirmed defects.
- Do not count a valid gripper, PASS, or RECEIVE possession event as a defect.

## 7. Assess impact on the complete plan

For each root cause, determine whether it affects:

- A single localized action.
- A limited sub-path that can be corrected.
- An important execution path.
- An essential task outcome with no valid alternative.

A valid alternative path can reduce the impact of a defect but does not erase a real error in another path.

Do not automatically invalidate every later action because one earlier dependency is uncertain. Independent actions and paths remain valid unless they depend on the same unresolved condition.

Do not invent unreported recovery actions or alternative paths.

An object absent from the inventory is not, by itself, a sequencing error. A capability limitation is primarily a PF issue unless a distinct sequencing dependency is also violated.

Do not evaluate task allocation, workload distribution, or the number of actions assigned to each agent.

## 8. SC score anchors (0-5)

5 — All material prerequisites and dependencies are satisfied. No material sequencing issue remains.

4 — The sequence is mostly coherent. There is at most a small number of localized, recoverable root-cause defects. Essential execution paths remain valid. One missing transition affecting several consecutive actions normally belongs here when it is one correctable underlying defect.

3 — Multiple independent, noticeable sequencing defects remain, OR one significant unresolved dependency materially disrupts an important path. Meaningful execution remains possible, but correction or replanning is needed.

2 — Several independent major prerequisite or dependency failures block essential paths. The plan has no supported recovery for those blocked outcomes. This score requires multiple distinct root causes, not merely multiple downstream actions caused by one omission.

1 — Critical, widespread sequencing failures prevent most essential actions or make task completion largely infeasible.

0 — No meaningful executable action sequence exists.

## 9. Mandatory score-selection checks

Before returning SC, apply these checks in order:

- First test whether score 5 is justified. If any material sequencing defect remains, do not assign 5.
- Then test score 4. If the plan has only localized, recoverable defects and its essential paths remain valid, assign 4.
- Use score 3 when multiple independent noticeable defects exist or one significant unresolved dependency disrupts an important path.
- Assign score 2 only if you can explicitly identify at least TWO independent major root causes AND explain how they block essential paths without a supported recovery.
- If you cannot identify two independent major root causes, do NOT assign score 2.
- Assign score 1 only when most essential paths are critically infeasible.
- Assign score 0 only when no meaningful executable sequence exists.

A single defect must not be escalated to score 2 merely because it affects several downstream actions.

Do not award 4 or 5 when several independent major dependencies remain unresolved.

## 10. Required SC reasoning

Before scoring, perform the mandatory possession contradiction check and build the root-cause ledger.

In SC_reason:
- Identify each independent root cause separately.
- Identify the affected action or actions and their prerequisite.
- State whether the prerequisite is satisfied, unresolved, contradicted, or uncertain.
- Explain the actual consequence for execution.
- Distinguish independent defects from downstream effects of the same defect.
- Explain whether the problem affects a localized action, a path, or an essential outcome.
- Identify explicitly provided valid alternatives when relevant.
- Explain why the selected score is supported by the evidence.
- If assigning score 2, explicitly identify at least two independent major root causes and the essential paths each blocks.

Apply exactly the same criteria to every evaluated method. Do not adjust scores to obtain a preferred ranking.

The SC output value MUST be an integer from 0 through 5.

### Cross-criterion consistency

Apply the same criteria to every evaluated method.

- Evaluate the actual plan rather than the method name or presumed strengths of the approach.
- Do not award points solely for fluent narration, detailed formatting, or coordination keywords.
- Avoid double-penalizing the same problem without considering its distinct consequences for each criterion. For example, an unsupported object claim may affect OC, while its effect on task achievement or execution may separately affect TF or PF.
- When evidence is insufficient, explain what cannot be verified rather than assuming successful execution.
- Provide concise, plan-specific reasons for every score.
- Apply the score anchors consistently. Comparable evidence should receive comparable scores across methods.
- Do not adjust scores to favor a particular method or obtain a preferred ranking.

Output JSON only. Return one entry for every supplied plan label, using this exact structure:
{{
  "PLAN_A": {{"TF": 0, "TF_reason": "...", "PF": 0, "PF_reason": "...", "OC": 0, "OC_reason": "...", "SC": 0, "SC_reason": "..."}},
  "PLAN_B": {{"TF": 0, "TF_reason": "...", "PF": 0, "PF_reason": "...", "OC": 0, "OC_reason": "...", "SC": 0, "SC_reason": "..."}}
}}
Only include labels that were supplied. Scores must be integers from 0 to 5, with 5 as the maximum. Reasons must identify the evidence supporting the selected score and the material issue that prevents the next higher score.
