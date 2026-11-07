---
title: Renew a loan
summary: The renewal that moves a loan's due date fourteen calendar days later and
  records that the loan was renewed.
rationale: Renewal's effect on the due date is cut apart from the limits that refuse
  a renewal, since each limit changes for a reason of its own.
sources:
- intake/scope.md
objective: Renewing a loan moves its due date fourteen calendar days later and leaves
  the loan recorded as renewed.
criteria:
- Renewing a loan due on 2026-01-15 leaves it due on 2026-01-29.
- Renewing a loan due on 2026-01-25 leaves it due on 2026-02-08.
- A loan that was renewed reads as renewed.
- Renewing a loan leaves the day its copy was borrowed unchanged.
implements:
- domain/lending/loan
- domain/lending/member
- rules/lending/renewal-extends-due-date-fourteen-days
---
## What it is
The renewal that moves a loan's due date fourteen calendar days later and records that the loan was renewed.

## Notes
ADVISORY, from the specification — no candidate states whether a loan already returned may be renewed, and no criterion of this task rests on it.
