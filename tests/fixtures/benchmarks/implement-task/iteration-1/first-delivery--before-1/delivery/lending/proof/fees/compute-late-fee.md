---
target: app
implementation: sha256:9fd898ce6460f6ca63d7a9b075f82333fa44022962010552f74b048492b35b1c
standard:
  at: standard.yaml
  pin: sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6
run: run/fees-compute-late-fee-suite
title: Proof of the late fee of a returned loan
summary: The tests that hold up task/fees/compute-late-fee, one per class and boundary
  of its two criteria and one demonstrating the per-day fee rule.
tests:
- file: tests/test_fees.py
  name: test_a_loan_returned_on_its_due_date_carries_no_late_fee
  proves: A loan returned on or before its due date carries a late fee of 0 cents.
    (the boundary, a return on the due date itself)
  fails_when: a return on the due date is counted as a day late, or any fee but 0
    is answered for it
- file: tests/test_fees.py
  name: test_a_loan_returned_before_its_due_date_carries_no_late_fee
  proves: A loan returned on or before its due date carries a late fee of 0 cents.
    (the class of returns strictly before the due date)
  fails_when: an early return answers a negative fee or any fee other than 0
- file: tests/test_fees.py
  name: test_a_loan_returned_one_day_late_carries_100_cents
  proves: A loan returned after its due date carries 100 cents for each calendar day
    between its due date and its return. (the boundary, the first day past the due
    date)
  fails_when: the first overdue day is not charged, is charged twice, or is charged
    at any amount but 100 cents
- file: tests/test_fees.py
  name: test_a_loan_returned_late_carries_100_cents_per_calendar_day_across_a_month_end
  proves: A loan returned after its due date carries 100 cents for each calendar day
    between its due date and its return. (several overdue days counted as calendar
    days across a month end)
  fails_when: the fee stops being 100 cents times the calendar days between the due
    date and the return, such as a flat fee, a different rate, or a day count that
    does not follow the calendar
  demonstrates: rules/lending/late-fee-per-overdue-day
not_applicable:
- edge_case: a loan with no return date
  why: the task's objective and criteria answer for a returned loan only, and no node
    states what an unreturned loan's fee is
- edge_case: two computations over one loan at once
  why: the computation is a pure function of the loan's dates, and no node states
    concurrent behavior
- edge_case: fee amounts large enough to overflow
  why: Python integers do not overflow, and no node bounds the number of overdue days
untested:
- The refusal of a loan with no returned_on by ValueError is a behavior the implementation
  inferred and no node decides, so it is recorded as unproven rather than pinned by
  a test.
---
## What it is
The tests that hold up task/fees/compute-late-fee, one per class and boundary of its two criteria and one demonstrating the per-day fee rule.

## Notes
The tests were written inline, applying agents/test-author.md in place, because this session cannot spawn subagents.
