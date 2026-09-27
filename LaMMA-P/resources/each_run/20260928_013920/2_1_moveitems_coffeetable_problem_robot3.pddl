(define (problem moveitems_coffeetable_problem_robot3)
(:domain robot3)
(:objects
   robot3- robot
   remotControl- object
   coffeetable- object
   storagelocation- object
)

(:init
   at(robot3 initiallocation)
   at-location(remotControl coffeetable)
   inaction(robot3)
)

(:goal
   and(
      at-location(remotControl storagelocation),
      not(holding(robot3 remotControl))
   )
)

)