---
type: invariant
statement: A member MUST hold at most three unreturned loans at the same time.
constrains:
  - domain/lending/member
  - domain/lending/loan
---

## Description

This rule limits how many copies one member may have out at once.
It does not decide whether an overdue loan blocks a checkout; rules/lending/overdue-loan-blocks-checkout does.
