---
target: app
implementation: sha256:afe5f2ecd47aacdf5c59681d80b7b7d3390bfd4f8ff7ba641369b4a66a1ab23b
standard:
  at: standard.yaml
  pin: sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6
run: run/fees-compute-late-fee-suite
title: Proof for computing the late fee of a returned loan
summary: Tests that hold late_fee_cents() to a zero fee for a loan returned on or
  before its due date and to 100 cents per calendar day for one returned after it.
tests:
- file: tests/test_fees.py
  name: test_a_loan_returned_on_its_due_date_carries_no_late_fee
  proves: 'A loan returned on or before its due date carries a late fee of 0 cents,
    at its boundary: a return on the due date itself.'
  fails_when: a loan returned on its due date is charged anything but 0 cents, as
    when the due date itself is counted as an overdue day
- file: tests/test_fees.py
  name: test_a_loan_returned_before_its_due_date_carries_no_late_fee
  proves: A loan returned on or before its due date carries a late fee of 0 cents,
    for a return strictly before the due date.
  fails_when: a loan returned early is answered a non-zero fee, as when the days before
    the due date come back as a negative fee or a credit
- file: tests/test_fees.py
  name: test_a_loan_returned_one_day_after_its_due_date_carries_100_cents
  proves: 'A loan returned after its due date carries 100 cents for each calendar
    day between its due date and its return, at its boundary: one day past the due
    date.'
  fails_when: the first day past the due date is not charged, or is charged anything
    but 100 cents
- file: tests/test_fees.py
  name: test_a_loan_returned_days_after_its_due_date_carries_100_cents_per_calendar_day
  proves: A loan returned after its due date carries 100 cents for each calendar day
    between its due date and its return, over several days across a month boundary.
  fails_when: the fee stops scaling with the calendar days between the due date and
    the return, is charged at any rate but 100 cents a day, or miscounts days across
    a month boundary
  demonstrates: rules/lending/late-fee-per-overdue-day
not_applicable:
- edge_case: a loan with no return date
  why: no criterion and no node states the fee of a loan still out; the implementation's
    refusal is an inference, recorded under untested
- edge_case: two fee computations over one loan at once
  why: the computation is a pure function over one immutable loan, and no obligation
    states concurrent behavior
- edge_case: a dependency that fails or answers slowly
  why: the computation reads no dependency; it is arithmetic over the loan's two dates
- edge_case: a duplicate where uniqueness is claimed, or an empty collection
  why: the obligations take one loan and answer one amount; no collection and no uniqueness
    claim is involved
untested:
- The implementation refuses a loan with no return date by raising ValueError; that
  is an inference the implementation recorded, no node decides the fee of a loan still
  out, and it is not pinned by a test.
---
## What it is
Tests that hold late_fee_cents() to a zero fee for a loan returned on or before its due date and to 100 cents per calendar day for one returned after it.

## Notes
None.
