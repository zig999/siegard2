---
title: Reservation refuses renewal
summary: A renewal is refused while the loan's copy holds a reservation.
rationale: The reservation refusal answers to its own rule and adds a refusal to the renewal act, so it is cut as a second task over that act.
objective: A renewal of a loan is refused while the loan's copy holds a reservation.
criteria:
- Renewing an unrenewed loan whose copy holds a reservation is refused.
- A renewal refused because the copy holds a reservation leaves the loan's due date unchanged.
- A renewal refused because the copy holds a reservation leaves the loan recorded as not renewed.
- Renewing an unrenewed loan whose copy holds no reservation is not refused by the reservation rule.
depends_on:
- task/loan-renewal/renew-loan
implements:
- rules/lending/reserved-copy-blocks-renewal
- domain/lending/copy
- domain/lending/reservation
- domain/lending/loan
- domain/lending/member
sources:
- intake/scope.md
---

## What it is
The task brings the copy and the reservation it holds into the renewal decision, read as the copy last recorded it.

## Notes
ADVISORY, from the specification — rules/lending/reserved-copy-blocks-renewal is eventual, so the renewal reads the reservation as the copy last recorded it, not under one transaction with the loan.
ADVISORY, from the specification — this task reads a copy's reservation and does not deliver the reserve operation domain/lending/copy declares.
