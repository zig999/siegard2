---
type: invariant
statement: A member holding an unreturned loan whose due date has passed MUST NOT borrow another copy until that loan is returned.
constrains:
  - domain/lending/member
  - domain/lending/loan
---

## Description

This rule refuses borrowing to a member with an overdue loan, and lifts once every overdue loan is returned.
