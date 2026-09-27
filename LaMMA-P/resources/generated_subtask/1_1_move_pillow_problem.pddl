(define (problem move_pillow_problem)
  (:domain robot2)
  (:objects
    robot2 - robot
    pillow - object
    sofa - object
    storage_area - object
  )
  (:init
    (at robot2 sofa)
    (at-location pillow sofa)
    (inaction robot2)
  )
  (:goal
    (and
      (at-location pillow storage_area)
    )
  )
)