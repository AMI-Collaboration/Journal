(define (problem turn_on_floorlamp_problem)
  (:domain robot2)
  (:objects
    robot2 - robot
    FloorLamp - object
    LivingRoom - object
  )
  (:init
    (at robot2 LivingRoom)
    (at-location FloorLamp LivingRoom)
  )
  (:goal
    (and
      (switch-on robot2 FloorLamp)
    )
  )
)