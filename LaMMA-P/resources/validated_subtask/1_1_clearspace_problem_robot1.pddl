(define (problem clearspace_problem_robot1)
   (:domain robot1)
   (:objects
     robot1 - robot
     chair3 - object
     chair4 - object
     coffeetable2 - object
     storageArea2 - object 
   )
   (:init 
      (at-location chair3 storageArea2)
      (at-location chair4 storageArea2)
      (at-location coffeetable2 storageArea2)
      (inaction robot1)
   ) 
   (:goal 
      (and 
        (cleaned robot1 chair3)
        (cleaned robot1 chair4)
        (cleaned robot1 coffeetable2)
      )
   ) 
)