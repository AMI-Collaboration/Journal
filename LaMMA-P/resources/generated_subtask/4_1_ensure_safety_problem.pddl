(define (problem ensure_safety_problem)
  (:domain robot2)
  (:objects
    robot2 - robot
    ArmChair - object
    Desk - object
    Sofa - object
    Floor - object
  )
  (:init
    (at robot2 Floor)
    (at-location ArmChair Floor)
    (at-location Desk Floor)
    (at-location Sofa Floor)
    (inaction robot2)
  )
  (:goal
    (and
      (adjusted-stability ArmChair)
      (adjusted-stability Desk)
      (adjusted-stability Sofa)
    )
  )
)