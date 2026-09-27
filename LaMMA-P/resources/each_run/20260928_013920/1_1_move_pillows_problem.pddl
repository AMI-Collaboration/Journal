(define (problem move_pillows_problem)
  (:domain robot2)
  (:objects
    robot2 - robot
    pillow - object
    sofa - object
    storage - object
  )
  (:init
    (at robot2 sofa)
    (at-location pillow sofa)
    (inaction robot2)
  )
  (:goal
    (and
      (at-location pillow storage)
    )
  )
)