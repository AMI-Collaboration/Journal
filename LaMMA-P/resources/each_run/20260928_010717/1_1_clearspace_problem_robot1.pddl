(define (problem clearspace_problem_robot1)
   (:domain robot1)
   (:objects
     robot1 - robot
     chair1 chair2 chair3 chair4 chair5 chair6 chair7 armChair coffeeTable storageArea - object 
   )
   (:init 
     ;; Example initial states (you need to fill these based on your scenario)
     (at-location chair1 storageArea)
     (at-location chair2 storageArea)
     (at-location coffeeTable storageArea)
     (inaction robot1)
     ;; Add more initial conditions as needed
   )
   (:goal 
     ;; Example goal states (you need to fill these based on your scenario)
     (and
       (at-location chair1 armChair)
       (at-location coffeeTable armChair)
       ;; Add more goal conditions as needed
     )
   )
)