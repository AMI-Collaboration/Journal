(define (problem move_pillows_problem)
  (:domain robot2)
  (:objects
    robot2 - robot
    pillow1 - object
    pillow2 - object
    storageLocation - object
    sofa - object
  )
  (:init
    (at robot2 sofa)
    (at-location pillow1 sofa)
    (at-location pillow2 sofa)
    (inaction robot2)
  )
  (:goal
    (and
      (at-location pillow1 storageLocation)
      (at-location pillow2 storageLocation)
    )
  )
)