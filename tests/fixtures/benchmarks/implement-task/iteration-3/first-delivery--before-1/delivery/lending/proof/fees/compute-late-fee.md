---
target: app
implementation: sha256:64715d1a5999ec2b5ccad9f932bd7ddd8e9cd72ef4ff7c6a5ad4f5edb38507ac
standard:
  at: standard.yaml
  pin: sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6
run: run/fees-compute-late-fee-suite
title: Proof of the late fee of a returned loan
summary: Four tests over late_fee_cents covering the on-time class, the due-date boundary,
  the first overdue day and a multi-day return across a month end.
tests:
- file: tests/test_fees.py
  name: test_a_loan_returned_on_its_due_date_carries_no_fee
  proves: A loan returned on or before its due date carries a late fee of 0 cents
    — at the due date itself, the boundary of the criterion.
  fails_when: a loan returned on its due date is charged for a day, as an off-by-one
    count of the days between due date and return would do
- file: tests/test_fees.py
  name: test_a_loan_returned_before_its_due_date_carries_no_fee
  proves: A loan returned on or before its due date carries a late fee of 0 cents
    — for a return strictly before the due date.
  fails_when: an early return answers anything but 0, such as a negative fee from
    the unfloored day difference
- file: tests/test_fees.py
  name: test_a_loan_returned_one_day_late_carries_100_cents
  proves: A loan returned after its due date carries 100 cents for each calendar day
    between its due date and its return — at the first overdue day, the boundary where
    a fee begins.
  fails_when: the first day after the due date is charged anything but 100 cents
- file: tests/test_fees.py
  name: test_a_loan_returned_across_a_month_end_carries_100_cents_per_calendar_day
  proves: A loan returned after its due date carries 100 cents for each calendar day
    between its due date and its return — over several days spanning a month end.
  fails_when: the fee stops being 100 cents per calendar day between the due date
    and the return, whether by another rate, a fixed amount, or a day count that is
    not calendar days
  demonstrates: rules/lending/late-fee-per-overdue-day
not_applicable:
- edge_case: a loan that has not been returned
  why: the task and the rule state the fee of a returned loan only, and the implementation
    record defers the unreturned case as stated nowhere
- edge_case: absent input in place of a loan
  why: no obligation states what an absent loan answers
- edge_case: two computations over one loan at once
  why: the computation reads one immutable record and no obligation states concurrent
    behavior
- edge_case: a dependency that fails or answers slowly
  why: the computation calls no dependency
untested:
- The amount BRL 1.00 is held as 100 integer cents; the rule is stated in BRL and
  the cents form follows the task's objective and PY-01, which is an inference of
  the implementation and not pinned here beyond the criteria's own 100 cents.
---
## What it is
Four tests over late_fee_cents covering the on-time class, the due-date boundary, the first overdue day and a multi-day return across a month end.

## Notes
None.
