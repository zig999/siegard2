---
type: aggregate-root
attributes:
  - name: code
    type: string
    required: true
relationships:
  - target: book
    type: reference
    cardinality: "1"
  - target: reservation
    type: composition
    cardinality: 0..1
operations:
  - reserve
---

## Description

A copy ("exemplar") is one physical item of a book, lent on its own.

## Responsibility

Be the thing a loan lends and a reservation reserves.
