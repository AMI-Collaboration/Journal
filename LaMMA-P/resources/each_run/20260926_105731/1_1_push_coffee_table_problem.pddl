(define (problem push_coffee_table_problem)
  (:domain robot1)
  (:objects
    robot1 - robot
    CoffeeTable - object
    initialLocation - object
    corner - object
  )
  (:init
    (at robot1 initialLocation)
    (at-location CoffeeTable initialLocation)
    (inaction robot1)
  )
  (:goal
    (and
      (at-location CoffeeTable corner)
    )
  )
)