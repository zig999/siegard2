---
type: aggregate-root
attributes:
  - name: notified_on
    type: date
relationships:
  - target: member
    type: reference
    cardinality: "1"
  - target: copy
    type: reference
    cardinality: "1"
---

## Description

A reservation is a member's claim on a copy that is currently lent to someone else (the material's "reserva").

## Responsibility

A reservation decides who is told when the copy comes back and who may pick it up first.
