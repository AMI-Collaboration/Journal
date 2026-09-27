(define (problem move_pillow_problem)
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
  )
  (:goal
    (and
      (at-location pillow storage)
    )
  )
)