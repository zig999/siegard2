---
type: policy
statement: A loan MUST NOT be renewed while a reservation is held on its copy.
constrains:
  - domain/lending/loan
  - domain/lending/reservation
consistency: eventual
---

## Description

This rule gives a member waiting on a copy precedence over the member who holds it.
