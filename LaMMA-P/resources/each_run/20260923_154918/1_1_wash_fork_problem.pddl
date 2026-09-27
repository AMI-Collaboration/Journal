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
    ;; Removed (inaction robot3) since actions require not being inaction.
  )
  (:goal
    (and
      (cleaned robot3 fork) ;; Corrected to match domain predicate definition.
    )
  )
)