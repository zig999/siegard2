---
title: Due date at borrowing
summary: A loan is made due fourteen calendar days after the day its copy was borrowed.
rationale: The scope states the due date as a fact renewal moves, and fixing how a loan gets it changes for a different reason than renewing, so it is a task of its own.
objective: A loan records a due date fourteen calendar days after the day its copy was borrowed.
criteria:
- A loan whose copy was borrowed on 2026-01-01 is due on 2026-01-15.
- A loan whose copy was borrowed on 2026-12-25 is due on 2027-01-08, weekends and holidays counted.
implements:
- rules/lending/loan-due-fourteen-days-after-borrowing
- domain/lending/loan
sources:
- intake/scope.md
---

## What it is
The task makes the loan's due date a consequence of its borrowing day rather than a value the caller supplies.

## Notes
REMAINDER, from the specification — the clause 'until the loan is renewed' of rules/lending/loan-due-fourteen-days-after-borrowing reaches no criterion of this task; it belongs to the renewal act, task/loan-renewal/renew-loan.
ADVISORY, from the specification — this task fixes the due date a loan is made with and does not deliver the borrow operation domain/lending/member declares.
