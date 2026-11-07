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
  name: test_a_loan_returned_before_its_due_date_carries_no_fee
  proves: A loan returned on or before its due date carries a late fee of 0 cents
    (the class of returns strictly before the due date).
  fails_when: an early return answers anything but 0, such as a fee over the absolute
    number of days between due date and return
- file: tests/test_fees.py
  name: test_a_loan_returned_on_its_due_date_carries_no_fee
  proves: A loan returned on or before its due date carries a late fee of 0 cents
    (the boundary, a return on the due date itself).
  fails_when: the due date itself is counted as an overdue day, so a return on it
    answers 100 cents instead of 0
- file: tests/test_fees.py
  name: test_a_loan_returned_one_day_after_its_due_date_carries_100_cents
  proves: A loan returned after its due date carries 100 cents for each calendar day
    between its due date and its return (the boundary, the first overdue day).
  fails_when: the first day past the due date is not charged, is charged other than
    100 cents, or an off-by-one counts it as two days
- file: tests/test_fees.py
  name: test_a_loan_returned_ten_calendar_days_late_across_a_month_carries_1000_cents
  proves: A loan returned after its due date carries 100 cents for each calendar day
    between its due date and its return (the class of returns several days late, counted
    in calendar days across a month end).
  fails_when: the fee stops scaling with the number of overdue days, or the days are
    counted other than as calendar days across a month end
not_applicable:
- edge_case: an absent loan passed in place of one
  why: no criterion and no node states what is answered for no loan, and the function's
    input is a loan
- edge_case: a return dated before the borrowing date
  why: no criterion and no node states a loan whose dates are out of order, so no
    obligation reaches it
- edge_case: two fee computations over one loan at once
  why: the computation reads one immutable loan and writes nothing, and no node states
    concurrent behavior
- edge_case: the fee's rendering as BRL rather than cents
  why: the task's criteria state the fee in cents, and no node states how an amount
    is displayed
untested:
- rules/lending/late-fee-per-overdue-day — its fact quantifies over every loan returned
  after its due date, an unbounded set of date pairs no finite test enumerates; the
  tests above exercise one representative per class and the boundary, which is part
  of the fact and is never offered as the whole of it.
- the inference that a loan not yet returned is refused with a ValueError rather than
  answered a fee — a behavior the implementation chose that no node decides, recorded
  as unproven and never pinned by a test.
---
## What it is
What proves task/fees/compute-late-fee, written against its implementation record.

## Notes
None.
