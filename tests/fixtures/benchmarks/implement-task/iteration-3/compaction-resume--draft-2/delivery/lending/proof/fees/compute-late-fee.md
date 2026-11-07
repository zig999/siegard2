---
target: app
implementation: sha256:afe5f2ecd47aacdf5c59681d80b7b7d3390bfd4f8ff7ba641369b4a66a1ab23b
standard:
  at: standard.yaml
  pin: sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6
run: run/fees-compute-late-fee-suite
title: Proof for computing the late fee of a returned loan
summary: What proves task/fees/compute-late-fee, written against its implementation
  record.
tests:
- file: tests/test_fees.py
  name: test_a_loan_returned_on_its_due_date_carries_no_late_fee
  proves: A loan returned on or before its due date carries a late fee of 0 cents,
    at the boundary where the return falls on the due date itself.
  fails_when: a return on the due date is counted as a day late, or answers anything
    but 0
- file: tests/test_fees.py
  name: test_a_loan_returned_before_its_due_date_carries_no_late_fee
  proves: A loan returned on or before its due date carries a late fee of 0 cents,
    for the class of returns before the due date.
  fails_when: an early return answers a negative fee, or anything but 0
- file: tests/test_fees.py
  name: test_a_loan_returned_one_day_late_carries_100_cents
  proves: A loan returned after its due date carries 100 cents for each calendar day
    between its due date and its return, at the boundary of one day late.
  fails_when: the first overdue day is not charged, is charged twice, or is charged
    other than 100 cents
- file: tests/test_fees.py
  name: test_a_loan_returned_days_late_across_a_month_end_carries_100_cents_per_calendar_day
  proves: A loan returned after its due date carries 100 cents for each calendar day
    between its due date and its return, for a delay of several days spanning a month
    end.
  fails_when: the fee stops scaling per calendar day, is a fixed amount, or miscounts
    days across a month boundary
not_applicable:
- edge_case: a return dated before the loan was borrowed
  why: no criterion or node states what such a loan carries, and the Loan the task
    receives is built by another task
- edge_case: a fraction of a day late
  why: loans carry dates without times, so the delay is always a whole count of calendar
    days
- edge_case: two fee computations over one loan at once
  why: the computation reads a frozen loan and writes nothing, so nothing concurrent
    can interfere
untested:
- 'rules/lending/late-fee-per-overdue-day: its fact is BRL 1.00 for every count of
  overdue days, a totality over a set the node does not enumerate, so no finite test
  decides it whole; the criterion tests sample its boundary and one representative.'
- a loan not yet returned is refused with a ValueError, a behavior the implementation
  inferred and no node decides.
---
## What it is
What proves task/fees/compute-late-fee, written against its implementation record.

## Notes
None.
