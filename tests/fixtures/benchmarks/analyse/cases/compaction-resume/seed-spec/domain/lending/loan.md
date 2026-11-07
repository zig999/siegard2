---
type: entity
aggregate: member
attributes:
  - name: borrowed_on
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
  - name: late_fee
    type: decimal
relationships:
  - target: copy
    type: reference
    cardinality: "1"
---

## Description

A loan ("empréstimo") is one copy lent to one member, from the day it is borrowed until the day it is returned.
A loan is overdue while it is unreturned after its due date.

## Responsibility

Record when a copy was borrowed, when it is due, whether it was renewed and when it came back.
