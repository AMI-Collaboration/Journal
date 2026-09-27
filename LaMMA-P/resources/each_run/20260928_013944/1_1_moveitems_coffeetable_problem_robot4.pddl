(define (problem moveitems_coffeetable_problem_robot4)
  (:domain robot4)
  (:objects
    robot4 - robot
    remotControl - object
    coffeetable - object
    storagelocation - object 
    initiallocation - object
  )

  (:init 
    (at robot4 initiallocation) 
    (at-location remotControl coffeetable) 
  )

  (:goal 
    (and
      (at-location remotControl storagelocation)
      (not (holding robot4 remotControl))
    )   
  )
)