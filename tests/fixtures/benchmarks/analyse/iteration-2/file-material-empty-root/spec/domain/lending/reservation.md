---
type: aggregate-root
attributes:
  - name: reserved_on
    type: date
    required: true
  - name: collect_by
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

A reservation ("reserva") is a member's claim on a copy that is currently lent to someone else.
Its collection deadline is set when the copy is returned.

## Responsibility

It holds a returned copy for the member who reserved it.
