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
    ;; Remove inaction predicate since actions require not being inaction.
  )
  (:goal
    (and
      (sliced apple)
    )
  )
)