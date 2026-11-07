---
title: Reserved copy blocks renewal
summary: The refusal of a renewal while the loan's copy holds a reservation.
rationale: The reservation block is cut apart from the renewal it refuses because
  it reads another aggregate, the copy and its reservation, and changes with the reservation
  rules.
sources:
- intake/scope.md
depends_on:
- task/loan-renewal/renew-loan
objective: Renewing a loan whose copy holds a reservation is refused.
criteria:
- Renewing a loan whose copy holds a reservation is refused.
- A renewal refused over a reserved copy leaves the loan's due date unchanged.
- A renewal refused over a reserved copy leaves the loan not renewed.
- Renewing a loan whose copy holds no reservation is not refused by this rule.
implements:
- domain/lending/copy
- domain/lending/loan
- domain/lending/member
- domain/lending/reservation
- rules/lending/reserved-copy-blocks-renewal
---
## What it is
The refusal of a renewal while the loan's copy holds a reservation.

## Notes
ADVISORY, from the specification — rules/lending/reserved-copy-blocks-renewal is eventual: the renewal reads the reservation as domain/lending/copy last recorded it, and no criterion tests how promptly a new reservation takes effect.
