(define (problem wash_knife_problem)
  (:domain robot3)
  (:objects
    robot3 - robot
    knife - object
    bowl - object
    sink - object
    counterTop - object
  )
  (:init
    (at robot3 counterTop)
    (at-location knife counterTop)
    (at-location bowl counterTop)
    (inaction robot3)
  )
  (:goal
    (and
      (cleaned robot3 knife)
    )
  )
)