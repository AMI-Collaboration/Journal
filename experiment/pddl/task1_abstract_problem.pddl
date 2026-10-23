(define (problem task1_abstract)
  (:domain household-multiagent)
  (:objects
    r1 - gripper
    r2 - mobile_light
    r3 - gripper
    r4 - mobile_heavy
    kitchen - room
    living_room - room
    cup - item
    plate - item
    keys - item
    wallet - item
  )
  (:init
    (agent-at r1 kitchen)
    (agent-at r2 kitchen)
    (agent-at r3 living_room)
    (agent-at r4 living_room)
    (agent-free r1)
    (agent-free r2)
    (agent-free r3)
    (agent-free r4)
    (can-access r2 kitchen)
    (can-access r2 living_room)
    (can-access r4 kitchen)
    (can-access r4 living_room)
    (object-at cup kitchen)
    (object-at plate kitchen)
    (object-at keys living_room)
    (object-at wallet living_room)
  )
  (:goal
    (and
      (object-at cup r1)
      (object-at plate r1)
      (object-at keys r4)
      (object-at wallet r4)
    )
  )
)