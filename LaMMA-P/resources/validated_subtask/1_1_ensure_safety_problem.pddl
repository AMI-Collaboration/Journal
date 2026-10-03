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
    ; Removed (inaction robot2) to allow actions to be executed.
  )
  (:goal
    (and
      ; Adjusted goal conditions to use existing predicates.
      (cleaned robot2 ArmChair)
      (cleaned robot2 Desk)
      (cleaned robot2 Sofa)
    )
  )
)