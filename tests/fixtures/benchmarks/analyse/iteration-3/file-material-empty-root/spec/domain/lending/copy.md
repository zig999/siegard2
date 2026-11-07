---
type: aggregate-root
attributes:
  - name: inventory_number
    type: string
    required: true
relationships:
  - target: title
    type: reference
    cardinality: "1"
---

## Description

A copy is one physical exemplar of a title, lent on its own (the material's "exemplar").

## Responsibility

A copy is the unit a loan and a reservation are placed on.
