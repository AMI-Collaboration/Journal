(define (problem clearspace_robot2_problem)
  (:domain robot2)
  (:objects
    robot2 - robot
    chair3 - object
    chair4 - object
    floor - object
    storageArea - object
  )
  (:init
    (at robot2 startinglocation)
    (at-location chair3 floor)
    (at-location chair4 floor)
    (inaction robot2)
  )
  (:goal
    (and 
      (at-location chair3 storageArea)
      (at-location chair4 storageArea)
      (not(holding robot2 chair3))
      (not(holding robot2 chair4))
     )
   )
)