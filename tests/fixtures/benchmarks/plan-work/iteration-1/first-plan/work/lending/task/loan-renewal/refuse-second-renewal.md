---
title: Refuse a second renewal
summary: The once-only limit on renewing a loan.
rationale: The once-only limit is cut apart from the renewal it refuses, so it changes
  and is demonstrated on its own over a renewal that already exists.
sources:
- intake/scope.md
depends_on:
- task/loan-renewal/renew-loan
objective: A loan already renewed once is refused a second renewal.
criteria:
- Renewing a loan that was already renewed is refused.
- A refused second renewal leaves the loan's due date unchanged.
- Renewing a loan not yet renewed is not refused by this limit.
implements:
- domain/lending/loan
- domain/lending/member
- rules/lending/loan-renewed-at-most-once
---
## What it is
The once-only limit on renewing a loan.

## Notes
None.
