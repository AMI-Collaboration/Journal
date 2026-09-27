(define (problem move_items_off_coffee_table)
  (:domain robot2)
  (:objects
    robot2 - robot
    Box - object
    CellPhone - object
    CreditCard - object
    KeyChain - object
    RemoteControl - object
    CoffeeTable - object
    Shelf - object ; Assuming Shelf is the storage location.
  )
  (:init
    (at robot2 CoffeeTable)
    (at-location Box CoffeeTable)
    (at-location CellPhone CoffeeTable)
    (at-location CreditCard CoffeeTable)
    (at-location KeyChain CoffeeTable)
    (at-location RemoteControl CoffeeTable)
  )
  (:goal
    (and 
      (at-location Box Shelf)
      (at-location CellPhone Shelf)
      (at-location CreditCard Shelf)
      (at-location KeyChain Shelf)
      (at-location RemoteControl Shelf)
    )
  )
)