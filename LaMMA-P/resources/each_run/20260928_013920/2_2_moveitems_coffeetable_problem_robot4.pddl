(define (problem moveitems_coffeetable_problem_robot4)
(:domain robot4)
(:objects
   robot4- robot
   remotControl- object
   coffeetable- object
   storagelocation-object 
)

(:init 
   at(robot4 initiallocation) 
   at-location(remotControl coffeetable) 
   inaction(robot4) 
)

(:goal 
     and(
        at-location(remotControl storagelocation),
        not(holding(robot4 remotControl))
     )   
)

)