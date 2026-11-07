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

A member ("sócio") is a person registered with the community library who may borrow its copies.
A member holds the loans currently and previously made to them.

## Responsibility

Decide whether a member may borrow or renew, against the loans the member already holds.
