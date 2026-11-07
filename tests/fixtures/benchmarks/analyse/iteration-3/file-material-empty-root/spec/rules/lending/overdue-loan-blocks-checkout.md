---
type: invariant
statement: A member holding an unreturned loan whose due date has passed MUST NOT check out another copy until that loan is returned.
constrains:
  - domain/lending/member
  - domain/lending/loan
---

## Description

This rule stops a member with an overdue loan from borrowing more.
