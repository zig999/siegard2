---
type: entity
aggregate: member
attributes:
  - name: checked_out_on
    type: date
    required: true
  - name: due_on
    type: date
    required: true
  - name: renewed
    type: boolean
    required: true
  - name: returned_on
    type: date
relationships:
  - target: copy
    type: reference
    cardinality: "1"
---

## Description

A loan records one copy checked out by one member, from its checkout until its return (the material's "empréstimo").
A loan whose due date has passed while it is unreturned is overdue.

## Responsibility

A loan carries the dates that decide when its copy is due back and whether it may still be renewed.
