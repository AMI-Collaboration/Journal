(define (problem clearspace_chairs_problem)
  (:domain robot2)
  (:objects
    robot2 - robot
    chair1 - object
    chair2 - object
    chair3 - object
    chair4 - object
    chair5 - object
    room - object
    storageArea - object
    startingLocation - object
  )
  
  (:init
    (at robot2 startingLocation)
    (at-location chair1 room)
    (at-location chair2 room)
    (at-location chair3 room)
    (at-location chair4 room)
    (at-location chair5 room)
    (inaction robot2)
  )
  
  (:goal
    (and
      (not(holding robot2 chair1))
      (not(holding robot2 chair2))
      (not(holding robot2 chair3))
      (not(holding robot2 chair4))
      (not(holding robot2 chair5))
      (forall (?chair - object) 
        (implies 
          (or 
            (= ?chair chair1) 
            (= ?chair chair2) 
            (= ?chair chair3) 
            (= ?chair chair4) 
            (= ?chair chair5)) 
          (at-location ?chair storageArea)))
     )
   )
 )