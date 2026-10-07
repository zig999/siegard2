---
entries:
- field: type
  unstated: The material names two states a customer can be in and names no rule governing how a customer moves between them.
  decided: state-machine
  why: Two states on one aggregate with no transition stated leave every status change undecided, and a state machine is the one class that decides them totally.
- field: initial
  unstated: The material does not say which state a customer is in when registered.
  decided: active
  why: A customer registered is a customer the business is trading with, and nothing in the material registers one already inactive.
- field: transitions
  unstated: The material names no trigger that moves a customer between active and inactive.
  decided: active moves to inactive on deactivate, and inactive moves to active on activate
  why: Neither state is named final, so each state leaves by one trigger into the other and no third trigger is needed.
- field: rejections
  unstated: The material does not say what happens when a customer is activated while active or deactivated while inactive.
  decided: both are rejected
  why: A trigger that would leave the customer in the state it already holds changes nothing, and rejecting it keeps every pairing decided.
---
