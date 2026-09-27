(define (problem slice_and_store_lettuce_problem)
  (:domain robot1)
  (:objects
    robot1 - robot
    robot3 - robot
    lettuce - object
    knife - object
    fridge - object
    counterTop - object
    floor - object
  )
  (:init
    (at robot1 counterTop)
    (at-location lettuce counterTop)
    (at-location knife counterTop)
    (at-location fridge floor)
    (inaction robot1)
    (inaction robot3)
  )
  (:goal
    (and
      (sliced lettuce)
      (at-location lettuce fridge)
    )
  )
)