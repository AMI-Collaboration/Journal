(define (problem mat_compound)
  (:domain household-multiagent)
  (:objects
    r1 - gripper
    r2 - mobile_light
    r3 - mobile_heavy
    r4 - gripper
    bathroom - room
    toilet_paper - item
    blue_trash_bin - item
    bathroom_light - item
    sink_faucet - item
  )
  (:init
    (agent-at r1 bathroom)
    (agent-at r2 bathroom)
    (agent-at r3 bathroom)
    (agent-at r4 bathroom)
    (agent-free r1)
    (agent-free r2)
    (agent-free r3)
    (agent-free r4)
    (can-access r2 bathroom)
    (can-access r3 bathroom)
    (object-at toilet_paper bathroom)
    (object-at blue_trash_bin bathroom)
    (object-at bathroom_light bathroom)
    (object-at sink_faucet bathroom)
    (is-off bathroom_light)
    (is-off sink_faucet)
  )
  (:goal
    (and
      (is-on sink_faucet)
      (inside toilet_paper blue_trash_bin)
    )
  )
)