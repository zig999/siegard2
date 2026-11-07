---
title: Renew a loan
summary: A member renews a loan once, moving its due date, unless its copy is reserved.
sources:
  - intake/scope.md
objective: A member renews a loan as the specification allows and is refused where it forbids.
criteria:
  - Renewing a loan moves its due date fourteen calendar days later.
  - Renewing a loan that was already renewed is refused.
  - Renewing a loan whose copy holds a reservation is refused.
depends_on:
  - task/renewals/compute-due-date
implements:
  - rules/lending/loan-renewed-at-most-once
  - rules/lending/renewal-extends-due-date-fourteen-days
  - rules/lending/reserved-copy-blocks-renewal
---

## What it is

The one renewal a loan may take.

## Notes

None.
