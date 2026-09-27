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
    (at robot2 floor) ; Assuming 'floor' as starting location for validity.
    (at-location chair3 floor)
    (at-location chair4 floor)
    ; Removed (inaction robot2) to allow actions.
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