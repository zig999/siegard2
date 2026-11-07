---
type: invariant
statement: A member MUST NOT hold more than three unreturned loans at the same time.
constrains:
  - domain/lending/member
  - domain/lending/loan
---

## Description

This rule refuses the borrowing that would give a member a fourth copy at once.
