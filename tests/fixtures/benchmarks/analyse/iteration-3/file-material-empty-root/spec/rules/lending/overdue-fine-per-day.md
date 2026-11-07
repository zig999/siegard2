---
type: invariant
statement: An overdue loan MUST accrue a fine of 1.00 BRL for each calendar day past its due date until it is returned.
constrains:
  - domain/lending/loan
---

## Description

This rule fixes what a member owes for returning a copy late.
It does not decide how or when the fine is paid.
