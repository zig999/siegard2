---
title: Loan renewal
summary: A loan's due date at borrowing, a member renewing it once for fourteen more days, and the reservation that refuses a renewal.
rationale: The scope names one capability, renewal, and the due date it moves and the reservation that refuses it are the facts that capability reads, so one epic holds all of it.
covers:
- domain/lending/loan
- domain/lending/member
- domain/lending/copy
- domain/lending/reservation
- rules/lending/loan-due-fourteen-days-after-borrowing
- rules/lending/loan-renewed-at-most-once
- rules/lending/renewal-extends-due-date-fourteen-days
- rules/lending/reserved-copy-blocks-renewal
sources:
- intake/scope.md
---

## What it is
The epic groups the due date a loan is made with, the renewal that moves it, and the reservation that refuses a renewal.

## Notes
None.
