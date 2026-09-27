(define (problem put_fork_in_bowl_problem)
  (:domain robot3)
  (:objects
    robot3 - robot
    fork - object
    bowl - object
    counterTop - object
  )
  (:init
    (at robot3 counterTop)
    (at-location fork counterTop)
    (at-location bowl counterTop)
    (holding robot3 fork)
  )
  (:goal
    (and
      (at-location fork bowl)
    )
  )
)