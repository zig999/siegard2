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
relationships:
  - target: copy
    type: reference
    cardinality: "1"
---

## Description

A loan ("empréstimo") is one copy in a member's hands, from the day it is borrowed until the day it is returned.
A loan whose due date has passed and that has not been returned is overdue.

## Responsibility

It records when a copy left, when it is due back, and whether it has been renewed.
