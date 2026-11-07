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
    — the class of returns before the due date.
  fails_when: a return before the due date answers anything but 0, such as a negative
    fee from an unclamped day count
- file: tests/test_fees.py
  name: test_a_loan_returned_on_its_due_date_carries_no_late_fee
  proves: A loan returned on or before its due date carries a late fee of 0 cents
    — the boundary at the due date itself.
  fails_when: the due date itself is counted as an overdue day
- file: tests/test_fees.py
  name: test_a_loan_returned_one_day_after_its_due_date_carries_100_cents
  proves: A loan returned after its due date carries 100 cents for each calendar day
    between its due date and its return — the boundary where the fee starts.
  fails_when: the first day past the due date is not charged, or is charged anything
    but 100 cents
- file: tests/test_fees.py
  name: test_a_loan_returned_late_carries_100_cents_for_each_calendar_day_past_its_due_date
  proves: A loan returned after its due date carries 100 cents for each calendar day
    between its due date and its return — a return 19 calendar days late, across a
    month boundary.
  fails_when: the fee stops scaling by calendar day at BRL 1.00 per day — a flat fee,
    another rate, or a day count other than calendar days between due date and return
  demonstrates: rules/lending/late-fee-per-overdue-day
not_applicable:
- edge_case: absent or empty input
  why: the function takes one loan, and no obligation states behavior for a missing
    loan
- edge_case: an empty collection or a duplicate
  why: the computation reads one loan, and no obligation is over a collection or claims
    uniqueness
- edge_case: a dependency that fails or answers slowly
  why: the computation reads no dependency
- edge_case: two operations on one loan at once
  why: the computation is a pure function of one immutable loan, and no node states
    concurrent behavior
untested:
- 'A loan not yet returned is refused with a ValueError: an inference the implementation
  recorded about behavior, which no node decides, so it is not pinned by a test.'
---
## What it is
What proves task/fees/compute-late-fee, written against its implementation record.

## Notes
Prove ran inline, in the context that wrote the source: this session cannot spawn subagents, so the test-author's discipline was applied in place.
