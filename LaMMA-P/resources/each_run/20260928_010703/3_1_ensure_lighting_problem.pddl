(define (problem ensure_lighting_problem)
  (:domain robot2)
  (:objects
    robot2 - robot
    lightSwitch - object
    wall - object
  )
  (:init
    (at robot2 wall)
    (at-location lightSwitch wall)
    (inaction robot2)
  )
  (:goal
    (and
      (switch-on robot2 lightSwitch)
    )
  )
)