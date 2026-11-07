---
title: Renew a loan once
summary: A member renews an unrenewed loan, moving its due date fourteen calendar days later, and a second renewal is refused.
rationale: The scope states renewing once and the fourteen-day move together as one act, cut apart from the reservation refusal because that answers to a different rule and lands as a further refusal on this act.
objective: A member renews an unrenewed loan, moving its due date fourteen calendar days later, once.
criteria:
- Renewing an unrenewed loan due on 2026-01-15 moves its due date to 2026-01-29.
- Renewing an unrenewed loan records the loan as renewed.
- Renewing a loan already renewed is refused.
- A refused renewal of a loan already renewed leaves its due date unchanged.
implements:
- rules/lending/renewal-extends-due-date-fourteen-days
- rules/lending/loan-renewed-at-most-once
- rules/lending/loan-due-fourteen-days-after-borrowing
- domain/lending/loan
- domain/lending/member
sources:
- intake/scope.md
---

## What it is
The task delivers the renew operation domain/lending/member declares, over a loan it holds.

## Notes
UNDERDETERMINED, from the specification — rules/lending/reserved-copy-blocks-renewal refuses a renewal while the loan's copy holds a reservation, and no criterion here excludes it.
Implementation that passes: a renewal that moves the due date of an unrenewed loan whose copy holds a reservation.
ADVISORY, from the specification — no candidate states whether a loan already returned may be renewed, and no criterion of this task rests on it.
