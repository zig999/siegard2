---
target: app
implementation: sha256:bda5756edd429a0464359e80ad3eec79554b37e091bcd3e35993911991d028a4
standard:
  at: standard.yaml
  pin: sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6
run: run/fees-compute-late-fee-suite
title: Proof of the late fee of a returned loan
summary: Four tests in tests/test_fees.py that hold late_fee_cents to the two criteria
  of task/fees/compute-late-fee at their boundaries.
tests:
- file: tests/test_fees.py
  name: test_a_loan_returned_before_its_due_date_carries_no_fee
  proves: A loan returned on or before its due date carries a late fee of 0 cents.
  fails_when: A loan returned before its due date answers any fee but 0, such as a
    negative fee for the days it came back early.
- file: tests/test_fees.py
  name: test_a_loan_returned_on_its_due_date_carries_no_fee
  proves: A loan returned on or before its due date carries a late fee of 0 cents
    — at the boundary of the due date itself.
  fails_when: The due date itself is counted as an overdue day, so a return on it
    answers a fee above 0.
- file: tests/test_fees.py
  name: test_a_loan_returned_one_day_late_carries_100_cents
  proves: A loan returned after its due date carries 100 cents for each calendar day
    between its due date and its return — at the first day past the due date.
  fails_when: The first overdue day is not charged, is charged other than 100 cents,
    or the count is off by one.
- file: tests/test_fees.py
  name: test_a_loan_returned_days_late_across_a_month_end_carries_100_cents_per_calendar_day
  proves: A loan returned after its due date carries 100 cents for each calendar day
    between its due date and its return — over several days spanning a month end.
  fails_when: The fee stops scaling by the calendar day count, or days are counted
    other than as calendar days across a month boundary.
untested:
- The fact of rules/lending/late-fee-per-overdue-day — BRL 1.00 for each calendar
  day between the due date and the return — holds over an unbounded number of overdue
  days, so no finite test decides it whole; the criterion tests hold it at the first
  overdue day and at one multi-day return across a month end.
- 'What late_fee_cents answers for a loan with no returned_on: the implementation
  recorded as an inference that such a loan is outside its domain, and no node decides
  it.'
not_applicable:
- edge_case: two computations over one loan at once
  why: late_fee_cents reads a frozen record and holds no state, and no obligation
    states concurrent behavior.
- edge_case: a dependency that fails or answers slowly
  why: the computation calls no dependency.
- edge_case: an empty collection or a duplicate where uniqueness is claimed
  why: the function takes one loan and no obligation claims uniqueness.
- edge_case: a return date earlier than the borrow date
  why: no obligation states what such a loan answers, and the criteria reach only
    the due date against the return.
---
## What it is
Four tests in tests/test_fees.py that hold late_fee_cents to the two criteria of task/fees/compute-late-fee at their boundaries.

## Notes
Steps 3 and 5 ran inline in one session, because this session cannot spawn subagents: the tests were written in the context that wrote the source.
