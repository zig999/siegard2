---
type: aggregate-root
attributes:
  - name: name
    type: string
    required: true
relationships:
  - target: loan
    type: composition
    cardinality: 0..*
operations:
  - borrow
  - renew
  - return
---

## Description

A member ("sócio") is a person registered with the library who may borrow its copies.

## Responsibility

It holds every loan the member has taken, so the limits on what one member may hold are checked in one place.
