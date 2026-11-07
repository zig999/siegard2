---
type: aggregate-root
attributes:
  - name: code
    type: string
    required: true
relationships:
  - target: title
    type: reference
    cardinality: "1"
---

## Description

A copy ("exemplar") is one physical item of a title, and it is the unit that is lent.

## Responsibility

It is what a loan and a reservation point at, so two copies of one title are lent and reserved separately.
