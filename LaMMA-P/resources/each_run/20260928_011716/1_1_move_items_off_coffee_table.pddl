(define (problem move_items_off_coffee_table)
  (:domain robot2)
  (:objects
    robot2 - robot
    Box - object
    CellPhone - object
    CreditCard - object
    RemoteControl - object
    coffeeTable - object
    shelf - object
  )
  (:init
    (at robot2 coffeeTable)
    (at-location Box coffeeTable)
    (at-location CellPhone coffeeTable)
    (at-location CreditCard coffeeTable)
    (at-location RemoteControl coffeeTable)
  )
  (:goal
    (and 
      (at-location Box shelf)
      (at-location CellPhone shelf)
      (at-location CreditCard shelf)
      (at-location RemoteControl shelf)
    )
  )
)