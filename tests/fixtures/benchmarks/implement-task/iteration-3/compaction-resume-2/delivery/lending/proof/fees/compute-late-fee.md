---
target: app
implementation: sha256:afe5f2ecd47aacdf5c59681d80b7b7d3390bfd4f8ff7ba641369b4a66a1ab23b
standard:
  at: standard.yaml
  pin: sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6
run: run/fees-compute-late-fee-suite
title: Proof of the late fee of a returned loan
summary: Four tests hold the late fee at 0 cents for a loan returned on or before
  its due date and at 100 cents per calendar day past it.
tests:
- file: tests/test_fees.py
  name: test_a_loan_returned_on_its_due_date_carries_no_late_fee
  proves: A loan returned on or before its due date carries a late fee of 0 cents
    — at the boundary, a return on the due date itself.
  fails_when: late_fee_cents() charges a loan returned on its due date, as an implementation
    counting the due date as an overdue day would
- file: tests/test_fees.py
  name: test_a_loan_returned_before_its_due_date_carries_no_late_fee
  proves: A loan returned on or before its due date carries a late fee of 0 cents
    — the class of returns strictly before the due date.
  fails_when: late_fee_cents() answers anything but 0 for an early return, such as
    a negative fee from an unclamped day count
- file: tests/test_fees.py
  name: test_a_loan_returned_one_day_late_carries_100_cents
  proves: A loan returned after its due date carries 100 cents for each calendar day
    between its due date and its return — at the boundary, one day late.
  fails_when: the first day past the due date is not charged, or is charged anything
    but 100 cents
- file: tests/test_fees.py
  name: test_a_loan_returned_days_late_carries_100_cents_per_calendar_day
  proves: A loan returned after its due date carries 100 cents for each calendar day
    between its due date and its return — several days late, across a month boundary.
  fails_when: the fee stops scaling with the calendar days late, as a flat fee would,
    or counts days other than calendar days between the due date and the return
not_applicable:
- edge_case: absent or empty input
  why: the operation takes one loan, and no criterion or node states what an absent
    loan answers
- edge_case: an empty collection or a duplicate
  why: the operation reads one loan and claims no uniqueness
- edge_case: a dependency that fails or answers slowly
  why: the computation reads no dependency
- edge_case: two operations on one subject at once
  why: the computation reads a frozen loan and writes nothing, and no node states
    concurrent behavior
untested:
- 'rules/lending/late-fee-per-overdue-day: the fact quantifies over every count of
  overdue calendar days, a set no finite test enumerates; the tests hold the one-day
  boundary and a several-day representative as the task''s criteria, never as the
  node''s fact whole.'
- 'the inference that a loan not yet returned is refused with a ValueError: no node
  decides what a loan still out answers, so the choice is recorded as unproven and
  not pinned by a test.'
---
## What it is
Four tests hold the late fee at 0 cents for a loan returned on or before its due date and at 100 cents per calendar day past it.

## Notes
Steps 3 and 5 ran inline in the session, which could not spawn subagents: the implementation and the tests were written in one context.
