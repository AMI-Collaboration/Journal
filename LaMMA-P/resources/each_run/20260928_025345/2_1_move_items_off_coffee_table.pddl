(define (problem move_items_off_coffee_table)
  (:domain robot3)
  (:objects
    robot3 - robot
    Box - object
    CellPhone - object
    CreditCard - object
    RemoteControl - object
    CoffeeTable - object
    StorageArea - object
  )
  (:init
    (at robot3 CoffeeTable)
    (at-location Box CoffeeTable)
    (at-location CellPhone CoffeeTable)
    (at-location CreditCard CoffeeTable)
    (at-location RemoteControl CoffeeTable)
    (inaction robot3)
  )
  (:goal
    (and
      (at-location Box StorageArea)
      (at-location CellPhone StorageArea)
      (at-location CreditCard StorageArea)
      (at-location RemoteControl StorageArea)
    )
  )
)