---
title: Due date set at borrowing
summary: The due date a loan starts with, counted from the day its copy was borrowed.
rationale: The due date a loan starts with is cut apart from renewal because it changes
  with the borrowing period, not with the renewal rules.
sources:
- intake/scope.md
objective: A loan made for a copy borrowed on a given day is due fourteen calendar
  days after that day.
criteria:
- A loan whose copy was borrowed on 2026-01-01 is due on 2026-01-15.
- A loan whose copy was borrowed on 2026-01-25 is due on 2026-02-08, counting across
  the end of the month.
- A loan whose copy was borrowed on 2026-12-25 is due on 2027-01-08, counting weekends
  and holidays as days.
implements:
- domain/lending/loan
- rules/lending/loan-due-fourteen-days-after-borrowing
---
## What it is
The due date a loan starts with, counted from the day its copy was borrowed.

## Notes
REMAINDER, from the specification — the clause "until the loan is renewed" of rules/lending/loan-due-fourteen-days-after-borrowing reaches no criterion here; it belongs to task/loan-renewal/renew-loan, which moves the due date.
