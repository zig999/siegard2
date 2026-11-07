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
  name: test_a_loan_returned_before_its_due_date_carries_no_late_fee
  proves: A loan returned on or before its due date carries a late fee of 0 cents
    — the class of returns strictly before the due date.
  fails_when: a return before the due date is answered anything but 0, such as a negative
    fee from an unclamped day count
- file: tests/test_fees.py
  name: test_a_loan_returned_on_its_due_date_carries_no_late_fee
  proves: A loan returned on or before its due date carries a late fee of 0 cents
    — the boundary of a return on the due date itself.
  fails_when: a return on the due date is charged, such as a fee counted inclusively
    of the due date or a minimum charge once the due date is reached
- file: tests/test_fees.py
  name: test_a_loan_returned_one_day_after_its_due_date_carries_100_cents
  proves: A loan returned after its due date carries 100 cents for each calendar day
    between its due date and its return — the boundary of the first overdue day.
  fails_when: the first day past the due date is charged anything but 100 cents, such
    as a grace day that charges nothing
- file: tests/test_fees.py
  name: test_a_loan_returned_days_after_its_due_date_carries_100_cents_per_calendar_day
  proves: A loan returned after its due date carries 100 cents for each calendar day
    between its due date and its return — several overdue days, counted across a month
    boundary.
  fails_when: the fee stops scaling with the number of overdue days, the rate per
    day is not 100 cents, or days are counted other than as calendar days across a
    month boundary
not_applicable:
- edge_case: a return dated before the loan was borrowed
  why: no criterion or node states what such a loan carries, and the Loan the task
    reads holds its dates as given
- edge_case: an absent loan
  why: the task's objective is a given returned loan; no obligation states an answer
    over no loan
- edge_case: fractional amounts or rounding
  why: the fee is a whole number of days at a whole number of cents, so no obligation
    raises a rounding case
- edge_case: a dependency that fails or answers slowly, and two computations at once
  why: the computation reads one loan and no dependency, and no obligation states
    concurrent behavior
untested:
- 'rules/lending/late-fee-per-overdue-day: its fact holds for every overdue day count,
  an unbounded set the node does not enumerate, so no finite test decides it whole;
  the criterion tests exercise the first overdue day and several days across a month
  boundary without claiming the node.'
- 'the refusal of a loan not yet returned with a ValueError: an inference the implementation
  recorded about behavior that no node decides, so it is left unproven rather than
  pinned.'
---
## What it is
What proves task/fees/compute-late-fee, written against its implementation record.

## Notes
None.
