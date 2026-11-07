---
title: Compute the late fee of a returned loan
summary: A function that answers the late fee a returned loan carries.
objective: Given a returned loan, the service answers the late fee it carries, in cents.
criteria:
  - A loan returned on or before its due date carries a late fee of 0 cents.
  - A loan returned after its due date carries 100 cents for each calendar day between its due date and its return.
implements:
  - rules/lending/late-fee-per-overdue-day
---

## What it is

The late-fee computation over one returned loan.

## Notes

None.
