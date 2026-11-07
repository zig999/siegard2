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
  - check-out
  - renew-loan
  - return-copy
---

## Description

A member is a person registered with the library who may borrow its copies (the material's "sócio").

## Responsibility

A member holds the loans whose limits decide whether it may check out another copy.
