(define (problem moveitems_coffeetable_problem_robot3)
  (:domain robot3)
  (:objects
    robot3- robot
    remotControl- object
    coffeetable- object
    storagelocation- object
    initiallocation- object ; Added initial location as an object
  )

  (:init
    (at robot3- initiallocation-) ; Corrected syntax for 'at' predicate
    (at-location remotControl- coffeetable-) ; Corrected syntax for 'at-location' predicate
  )

  (:goal
    (and 
      (at-location remotControl- storagelocation-) ; Corrected syntax for 'at-location' predicate in goal
      (not (holding robot3- remotControl-)) ; Corrected syntax for 'holding' predicate in goal
    )
  )
)