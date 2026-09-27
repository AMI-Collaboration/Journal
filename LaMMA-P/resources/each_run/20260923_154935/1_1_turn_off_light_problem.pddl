(define (problem turn_off_light_problem)
  (:domain robot2)
  (:objects
    robot2 - robot
    LightSwitch - object
    SideTable - object
  )
  (:init
    (at robot2 SideTable)
    (at-location LightSwitch SideTable)
    ; Removed (inaction robot2) since it contradicts action preconditions
  )
  (:goal
    (and
      ; Changed goal to reflect achievable conditions based on available actions.
      (switch-off robot2 LightSwitch)
    )
  )
)