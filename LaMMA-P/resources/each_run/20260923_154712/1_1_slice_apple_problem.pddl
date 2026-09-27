(define (problem slice_apple_problem)
  (:domain robot1)
  (:objects
    robot1 - robot
    apple - object
    knife - object
    counterTop - object
  )
  (:init
    (at robot1 counterTop)
    (at-location apple counterTop)
    (at-location knife counterTop)
    (inaction robot1)
  )
  (:goal
    (and
      (sliced apple)
    )
  )
)