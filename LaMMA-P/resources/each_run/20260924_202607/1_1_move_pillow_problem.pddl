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
    (inaction robot1)
  )
  (:goal
    (and
      (at-location pillow storage)
    )
  )
)