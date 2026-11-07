---
target: app
task: sha256:97b0fea7bc6d3f382702037fbab9c70bc20656ac9a810ef8f8907d6d1b097846
standard:
  at: standard.yaml
  pin: sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6
run: run/fees-compute-late-fee-build
title: Compute the late fee of a returned loan
summary: A function that answers, in cents, the late fee a returned loan carries.
files:
- path: lending/fees.py
  effect: answers the late fee of a returned loan as 100 cents per calendar day past
    its due date, and 0 when it was returned on time
criteria:
- criterion: A loan returned on or before its due date carries a late fee of 0 cents.
  met: true
  how: late_fee_cents() clamps a non-positive day count to 0 before multiplying
- criterion: A loan returned after its due date carries 100 cents for each calendar
    day between its due date and its return.
  met: true
  how: late_fee_cents() multiplies the calendar days between due_on and returned_on
    by CENTS_PER_OVERDUE_DAY, which is 100
nodes:
- node: rules/lending/late-fee-per-overdue-day
  encoded_at:
  - lending/fees.py
  how: the fee is the rule's BRL 1.00 per calendar day, held as 100 integer cents
    per day
inferences:
- inferred: a loan not yet returned is refused with a ValueError rather than answered
    a fee.
  from: the rule states the fee of a loan returned after its due date and states nothing
    of a loan still out
---
## What it is
A function that answers, in cents, the late fee a returned loan carries.

## Notes
None.
