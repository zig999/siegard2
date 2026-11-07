---
type: invariant
statement: A loan MUST NOT be renewed more than once.
constrains:
  - domain/lending/loan
---

## Description

This rule refuses a second renewal of the same loan.
