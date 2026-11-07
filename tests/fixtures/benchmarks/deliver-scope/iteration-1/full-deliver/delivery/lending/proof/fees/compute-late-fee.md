---
target: app
implementation: sha256:5f0412ab696de565143d90445342c6d1467095f5132154f6e172f38b92db91b4
standard:
  at: standard.yaml
  pin: sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6
run: run/fees-compute-late-fee-suite
title: Proof of the late fee of a returned loan
summary: Four tests holding late_fee_cents to a zero fee on or before the due date
  and 100 cents per calendar day after it.
tests:
- file: tests/test_fees.py
  name: test_a_loan_returned_on_its_due_date_carries_no_fee
  proves: A loan returned on or before its due date carries a late fee of 0 cents
    — the boundary at the due date itself.
  fails_when: A return on the due date is charged any fee, for instance where the
    day count is taken inclusively.
- file: tests/test_fees.py
  name: test_a_loan_returned_before_its_due_date_carries_no_fee
  proves: A loan returned on or before its due date carries a late fee of 0 cents
    — the class of early returns.
  fails_when: An early return answers a negative or non-zero fee instead of 0.
- file: tests/test_fees.py
  name: test_a_loan_returned_one_day_late_carries_one_hundred_cents
  proves: A loan returned after its due date carries 100 cents for each calendar day
    between its due date and its return — the boundary at one day late.
  fails_when: The first overdue day is not charged, or is charged anything other than
    100 cents.
- file: tests/test_fees.py
  name: test_a_loan_returned_days_late_across_a_month_end_carries_one_hundred_cents_per_calendar_day
  proves: A loan returned after its due date carries 100 cents for each calendar day
    between its due date and its return — several days, counted as calendar days across
    a month end.
  fails_when: The fee stops scaling at 100 cents per calendar day, or the day count
    breaks across a month boundary.
not_applicable:
- edge_case: A loan with no return date.
  why: The task's obligations are stated over a returned loan, and no node states
    what an unreturned loan's fee answers.
- edge_case: Two computations over one loan at once.
  why: The computation is a pure function of one loan's dates, and no node states
    concurrent behavior.
untested:
- 'rules/lending/late-fee-per-overdue-day: its fact quantifies over every overdue
  day count, which no finite test decides whole; the criteria''s tests hold its boundary
  and a representative instead.'
---
## What it is
Four tests holding late_fee_cents to a zero fee on or before the due date and 100 cents per calendar day after it.

## Notes
The test-author step ran inline in the session, because no agent of this plugin is registered in it.
