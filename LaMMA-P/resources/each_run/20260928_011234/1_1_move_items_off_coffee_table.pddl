(define (problem move_items_off_coffee_table)
  (:domain robot3)
  (:objects
    robot3 - robot
    coffeeTable - object
    shelf - object
    box - object
    cellphone - object
    creditcard - object
  )
  (:init
    (at robot3 coffeeTable)
    (at-location box coffeeTable)
    (at-location cellphone coffeeTable)
    (at-location creditcard coffeeTable)
  )
  (:goal
    (and
      (at-location box shelf)
      (at-location cellphone shelf)
      (at-location creditcard shelf)
    )
  )
)