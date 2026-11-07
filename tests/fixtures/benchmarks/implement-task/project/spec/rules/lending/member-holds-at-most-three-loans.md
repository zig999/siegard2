---
type: invariant
statement: A member MUST NOT hold more than three unreturned loans at the same time.
constrains:
  - domain/lending/member
  - domain/lending/loan
---

## Description

A borrowing that would give the member a fourth unreturned loan is refused.
