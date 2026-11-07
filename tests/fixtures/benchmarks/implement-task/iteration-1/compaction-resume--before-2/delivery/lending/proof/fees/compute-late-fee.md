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
  fails_when: an early return answers anything but 0, such as a negative fee for the
    days it came back early
- file: tests/test_fees.py
  name: test_a_loan_returned_on_its_due_date_carries_no_late_fee
  proves: A loan returned on or before its due date carries a late fee of 0 cents
    — the boundary where the return falls on the due date itself.
  fails_when: the due date itself is counted as an overdue day, answering 100 instead
    of 0
- file: tests/test_fees.py
  name: test_a_loan_returned_one_day_after_its_due_date_carries_100_cents
  proves: A loan returned after its due date carries 100 cents for each calendar day
    between its due date and its return — the boundary at the first overdue day.
  fails_when: the first day past the due date is not charged, is charged other than
    100 cents, or the day count is off by one
- file: tests/test_fees.py
  name: test_a_loan_returned_days_after_its_due_date_across_a_month_carries_100_cents_per_calendar_day
  proves: A loan returned after its due date carries 100 cents for each calendar day
    between its due date and its return — the class of several overdue days, counted
    in calendar days across a month end.
  fails_when: the fee stops scaling with the number of calendar days late, is a fixed
    amount, or miscounts days across a month boundary
not_applicable:
- edge_case: absent or empty input (no loan)
  why: every obligation is stated over a returned loan; none states what answers when
    no loan is given
- edge_case: an empty collection where one comes back
  why: the computation answers one integer for one loan, never a collection
- edge_case: a duplicate where uniqueness is claimed
  why: no obligation claims uniqueness of anything
- edge_case: a dependency that fails or answers slowly
  why: the computation reads only the loan it is handed and calls no dependency
- edge_case: two operations against one subject at once
  why: the computation is a pure function of an immutable loan and changes no state
untested:
- rules/lending/late-fee-per-overdue-day — its fact holds over every loan returned
  after its due date, a set no node enumerates, so no finite test decides it whole;
  the criterion tests exercise representatives of its classes and boundaries and are
  not offered as its proof.
- A loan not yet returned is refused with a ValueError — the implementation's recorded
  inference; no node decides what a loan still out answers, so it is left unproven
  rather than pinned.
---
## What it is
What proves task/fees/compute-late-fee, written against its implementation record.

## Notes
None.
