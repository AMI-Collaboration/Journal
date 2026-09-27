(define (problem setup_workout_equipment_problem)
  (:domain robot2)
  (:objects
    robot2 - robot
    YogaMat - object
    Dumbbells - object
    ResistanceBands - object
    Floor - object
    WorkoutArea - object
  )
  (:init
    (at robot2 Floor)
    (at-location YogaMat Floor)
    (at-location Dumbbells Floor)
    (at-location ResistanceBands Floor)
    (inaction robot2)
  )
  (:goal
    (and
      (at-location YogaMat WorkoutArea)
      (at-location Dumbbells WorkoutArea)
      (at-location ResistanceBands WorkoutArea)
    )
  )
)