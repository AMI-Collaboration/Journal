(define (problem clearspace_robot1_problem)
  (:domain robot1)
  (:objects
    robot1 - robot
    chair1 - object
    chair2 - object
    chair3 - object
    chair4 - object
    floor - object
    storageArea - object
  )
  (:init
    (at robot1 floor) ; Assuming 'floor' is where the robot starts.
    (at-location chair1 floor)
    (at-location chair2 floor)
  )
  (:goal
    (and
      (at-location chair1 storageArea)
      (at-location chair2 storageArea)
      (not(holding robot1 chair1))
      (not(holding robot1 chair2))
    )
  )
)