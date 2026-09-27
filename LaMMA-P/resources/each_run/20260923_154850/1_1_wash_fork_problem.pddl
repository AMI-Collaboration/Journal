(define (problem wash_fork_problem)
  (:domain robot3)
  (:objects
    robot3 - robot
    fork - object
    sink - object
    counterTop - object
  )
  (:init
    (at robot3 counterTop)
    (at-location fork counterTop)
    (at-location sink counterTop)
    (inaction robot3)
  )
  (:goal
    (and
      (cleaned fork)
    )
  )
)