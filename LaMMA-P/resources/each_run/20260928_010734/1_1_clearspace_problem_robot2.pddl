(define (problem clearspace_problem_robot2)
  (:domain robot2)
  (:objects
    robot2 - robot
    chair1 chair2 chair3 chair4 chair5 chair6 chair7 armChair coffeeTable storageArea - object
  )
  (:init
    ;; Example initial states, replace with actual conditions
    (at-location chair1 storageArea)
    (at-location chair2 storageArea)
    (at-location coffeeTable armChair)
    (inaction robot2)
    ;; Add more initial conditions as needed
  )
  (:goal
    ;; Example goal states, replace with actual goals
    (and 
      (at-location coffeeTable storageArea)
      (cleaned robot2 armChair)
      ;; Add more goal conditions as needed
    )
  )
)