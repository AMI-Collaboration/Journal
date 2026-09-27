(define (problem move_items_off_coffee_table)
  (:domain robot3)
  (:objects
    robot3 - robot
    robot4 - robot
    Box - object
    CellPhone - object
    CreditCard - object
    RemoteControl - object
    CoffeeTable - object
    Storage - object
  )
  (:init
    (at robot3 CoffeeTable)
    (at robot4 CoffeeTable)
    (at-location Box CoffeeTable)
    (at-location CellPhone CoffeeTable)
    (at-location CreditCard CoffeeTable)
    (at-location RemoteControl CoffeeTable)
  )
  (:goal
    (and 
      (at-location Box Storage)
      (at-location CellPhone Storage)
      (at-location CreditCard Storage)
      (at-location RemoteControl Storage)
    )
  )
)