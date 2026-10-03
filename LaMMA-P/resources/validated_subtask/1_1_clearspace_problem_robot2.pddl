(define (problem clearspace_problem_robot2)
   (:domain robot2)
   (:objects
     robot2- robot
     chair1- object
     chair2- object
     coffeetable- object
     storageArea- object
   )
   (:init
     ;; Initial conditions go here. Example:
     (at-location chair1- storageArea-)
     (at-location chair2- storageArea-)
     (at-location coffeetable- storageArea-)
     (inaction robot2-) ;; Assuming robot starts in an inactive state.
   )
   (:goal
     ;; Goal conditions go here. Example:
     (and 
       (cleaned robot2- chair1-) 
       (cleaned robot2- chair2-) 
       (cleaned robot2- coffeetable-) 
       ;; Add more goals as needed.
     )
   )
)