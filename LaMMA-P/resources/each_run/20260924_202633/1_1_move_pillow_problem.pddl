(define (problem move_pillow_problem)
  (:domain robot1)
  (:objects
    robot1 - robot
    pillow - object
    sofa - object
    storage - object
  )
  (:init
    (at robot1 sofa)
    (at-location pillow sofa)
    ;; Removed (inaction robot1) to allow actions to be performed.
  )
  (:goal
    (and
      (at-location pillow storage)
    )
  )
)