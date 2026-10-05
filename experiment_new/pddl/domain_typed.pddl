(define (domain household-multiagent)
  (:requirements :strips :typing :negative-preconditions)
  (:types
    agent - object
    gripper mobile - agent
    mobile_light mobile_heavy - mobile
    room - object
    item - object
  )
  (:predicates
    (agent-at ?a - agent ?r - room)
    (agent-at-door ?a - agent ?r - room)
    (object-at ?o - item ?r - room)
    (object-at-door ?o - item ?r - room)
    (holding ?a - agent ?o - item)
    (agent-free ?a - agent)
    (can-access ?a - agent ?r - room)
    (inside ?o - item ?container - item)
    (is-on ?o - item)
    (is-off ?o - item)
    (is-open ?o - item)
    (is-closed ?o - item)
    (is-sliced ?o - item)
    (is-filled ?o - item)
    (is-cooked ?o - item)
    (is-clean ?o - item)
    (is-ready ?o - item)
    (passed ?o - item ?r_from - room ?r_to - room)
    (received ?o - item ?a - agent)
    (fast-mover ?a - mobile_light)
    (is_gripper ?a - agent)
    (is_mobile ?a - agent)
    (is_mobile_heavy ?a - agent)
  )
  (:action move
    :parameters (?a - mobile ?r_from - room ?r_to - room)
    :precondition (and (agent-at ?a ?r_from) (can-access ?a ?r_to))
    :effect (and (agent-at ?a ?r_to) (not (agent-at ?a ?r_from))))
  (:action move-to-door
    :parameters (?a - mobile ?r - room)
    :precondition (agent-at ?a ?r)
    :effect (and (agent-at-door ?a ?r) (not (agent-at ?a ?r))))
  (:action move-from-door
    :parameters (?a - mobile ?r - room)
    :precondition (agent-at-door ?a ?r)
    :effect (and (agent-at ?a ?r) (not (agent-at-door ?a ?r))))
  (:action pick-up
    :parameters (?a - agent ?o - item ?r - room)
    :precondition (and (agent-at ?a ?r) (object-at ?o ?r) (agent-free ?a))
    :effect (and (holding ?a ?o) (not (object-at ?o ?r)) (not (agent-free ?a))))
  (:action put-down
    :parameters (?a - agent ?o - item ?r - room)
    :precondition (and (agent-at ?a ?r) (holding ?a ?o))
    :effect (and (object-at ?o ?r) (not (holding ?a ?o)) (agent-free ?a)))
  (:action put-down-at-door
    :parameters (?a - agent ?o - item ?r - room)
    :precondition (and (agent-at-door ?a ?r) (holding ?a ?o))
    :effect (and (object-at-door ?o ?r) (not (holding ?a ?o)) (agent-free ?a)))
  (:action pick-up-at-door
    :parameters (?a - agent ?o - item ?r - room)
    :precondition (and (agent-at-door ?a ?r) (object-at-door ?o ?r) (agent-free ?a))
    :effect (and (holding ?a ?o) (not (object-at-door ?o ?r)) (not (agent-free ?a))))
  (:action pass-object
    :parameters (?a1 - agent ?a2 - agent ?o - item ?r_from - room ?r_to - room)
    :precondition (and (holding ?a1 ?o) (agent-at ?a1 ?r_from) (agent-at ?a2 ?r_to))
    :effect (and (holding ?a2 ?o) (not (holding ?a1 ?o)) (passed ?o ?r_from ?r_to) (received ?o ?a2) (agent-free ?a1)))
  (:action toggle-on
    :parameters (?a - agent ?o - item ?r - room)
    :precondition (and (agent-at ?a ?r) (object-at ?o ?r) (is-off ?o))
    :effect (and (is-on ?o) (not (is-off ?o))))
  (:action toggle-off
    :parameters (?a - agent ?o - item ?r - room)
    :precondition (and (agent-at ?a ?r) (object-at ?o ?r) (is-on ?o))
    :effect (and (is-off ?o) (not (is-on ?o))))
  (:action open-object
    :parameters (?a - agent ?o - item ?r - room)
    :precondition (and (agent-at ?a ?r) (object-at ?o ?r) (is-closed ?o))
    :effect (and (is-open ?o) (not (is-closed ?o))))
  (:action close-object
    :parameters (?a - agent ?o - item ?r - room)
    :precondition (and (agent-at ?a ?r) (object-at ?o ?r) (is-open ?o))
    :effect (and (is-closed ?o) (not (is-open ?o))))
  (:action put-inside
    :parameters (?a - agent ?o - item ?container - item ?r - room)
    :precondition (and (agent-at ?a ?r) (holding ?a ?o) (object-at ?container ?r))
    :effect (and (inside ?o ?container) (not (holding ?a ?o)) (agent-free ?a)))
  (:action slice-object
    :parameters (?a - agent ?o - item ?r - room)
    :precondition (and (agent-at ?a ?r) (object-at ?o ?r))
    :effect (is-sliced ?o))
  (:action fill-object
    :parameters (?a - agent ?o - item ?r - room)
    :precondition (and (agent-at ?a ?r) (object-at ?o ?r))
    :effect (is-filled ?o))
  (:action cook-object
    :parameters (?a - agent ?o - item ?r - room)
    :precondition (and (agent-at ?a ?r) (object-at ?o ?r))
    :effect (is-cooked ?o))
  (:action clean-object
    :parameters (?a - agent ?o - item ?r - room)
    :precondition (and (agent-at ?a ?r) (object-at ?o ?r))
    :effect (is-clean ?o))
  (:action push-furniture
    :parameters (?a - mobile_heavy ?o - item ?r - room)
    :precondition (and (agent-at ?a ?r) (object-at ?o ?r))
    :effect (is-clean ?o))
)
