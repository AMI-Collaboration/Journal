(define (problem clearspace_sofas_problem)
  (:domain robot1)
  (:objects
    robot1 - robot
    sofa1 - object
    livingRoom - object
    storageArea - object
    startingLocation - object
  )
  
  (:init
    (at robot1 startingLocation)
    (at-location sofa1 livingRoom)
    (inaction robot1)
  )
  
  (:goal
  	(and 
  	 	(not(holding robot1 sofa1))
  		(at-location sofa1 storageArea)
  	)
  )
)