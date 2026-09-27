(define (problem move_items_off_coffee_table)
  (:domain robot3)
  (:objects
    robot3 - robot
    RemoteControl - object
    CellPhone - object
    Vase - object
    CoffeeTable - object
    Storage - object
  )
  (:init
    (at robot3 CoffeeTable)
    (at-location RemoteControl CoffeeTable)
    (at-location CellPhone CoffeeTable)
    (at-location Vase CoffeeTable)
  )
  (:goal
    (and
      (at-location RemoteControl Storage)
      (at-location CellPhone Storage)
      (at-location Vase Storage)
    )
  )
)