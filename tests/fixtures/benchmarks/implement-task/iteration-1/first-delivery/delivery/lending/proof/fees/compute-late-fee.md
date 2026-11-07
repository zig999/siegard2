---
target: app
implementation: sha256:a14ffddc9e7212182107b45dfc299997791824e08164890aa412902396e0d8ac
standard:
  at: standard.yaml
  pin: sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6
run: run/fees-compute-late-fee-suite
title: Proof of the late fee of a returned loan
summary: Four tests in tests/test_fees.py holding late_fee_cents to both criteria
  and to the per-overdue-day rule.
tests:
- file: tests/test_fees.py
  name: test_a_loan_returned_on_its_due_date_carries_no_fee
  proves: A loan returned on or before its due date carries a late fee of 0 cents
    — at the boundary, a return on the due date itself.
  fails_when: A return on the due date is charged, for instance by counting the due
    date itself as an overdue day.
- file: tests/test_fees.py
  name: test_a_loan_returned_before_its_due_date_carries_no_fee
  proves: A loan returned on or before its due date carries a late fee of 0 cents
    — the early-return class, apart from the boundary.
  fails_when: An early return answers anything but 0, such as a negative fee from
    multiplying a negative day count by the rate.
- file: tests/test_fees.py
  name: test_a_loan_returned_one_day_late_carries_100_cents
  proves: A loan returned after its due date carries 100 cents for each calendar day
    between its due date and its return — at the boundary, one day after the due date.
  fails_when: The first overdue day is not charged or is charged twice, or the rate
    per day is not 100 cents.
- file: tests/test_fees.py
  name: test_a_loan_returned_across_a_month_end_carries_100_cents_per_calendar_day
  proves: A loan returned after its due date carries 100 cents for each calendar day
    between its due date and its return — several calendar days spanning a month end.
  fails_when: The fee stops scaling with the number of overdue days, days are counted
    other than by the calendar across a month boundary, or the rate stops being 100
    cents per day.
  demonstrates: rules/lending/late-fee-per-overdue-day
not_applicable:
- edge_case: A loan not yet returned.
  why: The task's objective is stated over a returned loan, and no criterion or node
    states what an unreturned loan carries; the implementation records that domain
    as an inference.
- edge_case: Absent or empty input.
  why: The function takes one Loan record, and no obligation states an answer for
    no loan.
- edge_case: Two computations over one loan at once.
  why: The computation reads a frozen record and writes nothing, and no obligation
    states concurrent behavior.
- edge_case: A dependency that fails or answers slowly.
  why: The computation calls no dependency.
untested:
- The implementation's inference that an unreturned loan is outside late_fee_cents's
  domain and gets no answer of its own is behavior no node decides, so it is left
  unproven rather than pinned by a test.
---
## What it is
Four tests in tests/test_fees.py holding late_fee_cents to both criteria and to the per-overdue-day rule.

## Notes
Step 5 ran inline in the session that wrote the source, which could not spawn subagents: the test-author's file was applied in place.
