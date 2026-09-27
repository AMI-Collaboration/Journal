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
    (inaction robot2)
  )
  (:goal
    (and
      (switch-off robot2 LightSwitch)
    )
  )
)