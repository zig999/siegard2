---
type: entity
aggregate: copy
attributes:
  - name: reserved_on
    type: date
    required: true
  - name: pickup_deadline
    type: date
relationships:
  - target: member
    type: reference
    cardinality: "1"
---

## Description

A reservation ("reserva") is a member's claim on a copy, to borrow it once it is returned.

## Responsibility

Hold a copy for the member who reserved it.
