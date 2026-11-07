---
type: policy
statement: A loan MUST NOT be renewed while a reservation is held on its copy.
constrains:
  - domain/lending/loan
  - domain/lending/reservation
consistency: eventual
---

## Description

This rule refuses a renewal of a loan whose copy someone has reserved.
