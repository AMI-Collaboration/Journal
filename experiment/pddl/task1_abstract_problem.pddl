(define (problem task1_abstract)
  (:domain household-multiagent)
  (:objects
    r1 - gripper
    r2 - mobile_light
    r3 - gripper
    r4 - mobile_heavy
    kitchen - room
    living_room - room
    brown_bread - item
    green_apple - item
    red_apple - item
    white_magazine - item
    purple_pillow - item
    red_flowers - item
    black_laptop - item
    black_mug - item
    floor_lamp - item
    bowl - item
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
    (object-at brown_bread kitchen)
    (object-at green_apple kitchen)
    (object-at red_apple kitchen)
    (object-at white_magazine living_room)
    (object-at purple_pillow living_room)
    (object-at red_flowers living_room)
    (object-at black_laptop living_room)
    (object-at black_mug kitchen)
    (object-at floor_lamp living_room)
    (object-at bowl kitchen)
    (is-on floor_lamp)
  )
  (:goal
    (and
      (is-sliced brown_bread)
      (object-at bowl living_room)
      (is-off floor_lamp)
    )
  )
)