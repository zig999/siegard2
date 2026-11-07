---
target: app
implementation: sha256:afe5f2ecd47aacdf5c59681d80b7b7d3390bfd4f8ff7ba641369b4a66a1ab23b
standard:
  at: standard.yaml
  pin: sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6
run: run/fees-compute-late-fee-suite
title: Proof for computing the late fee of a returned loan
summary: Tests that hold the late fee of a returned loan to 0 cents on or before its
  due date and to 100 cents per calendar day after it.
tests:
- file: tests/test_fees.py
  name: test_a_loan_returned_on_its_due_date_carries_no_late_fee
  proves: A loan returned on or before its due date carries a late fee of 0 cents
    — at the boundary, a return on the due date itself.
  fails_when: a return on the due date is counted as a day late, or the fee for it
    is anything but 0
- file: tests/test_fees.py
  name: test_a_loan_returned_before_its_due_date_carries_no_late_fee
  proves: A loan returned on or before its due date carries a late fee of 0 cents
    — for a return days before the due date.
  fails_when: an early return answers a negative fee, a credit, or any value other
    than 0
- file: tests/test_fees.py
  name: test_a_loan_returned_one_day_after_its_due_date_carries_100_cents
  proves: A loan returned after its due date carries 100 cents for each calendar day
    between its due date and its return — at the boundary, one day late.
  fails_when: the first day after the due date is not charged, is charged twice, or
    is charged at a rate other than 100 cents
- file: tests/test_fees.py
  name: test_a_loan_returned_ten_days_after_its_due_date_carries_100_cents_per_day
  proves: A loan returned after its due date carries 100 cents for each calendar day
    between its due date and its return — over several days.
  fails_when: the fee stops scaling with the number of calendar days late, as a flat
    late fee or a capped one would
not_applicable:
- edge_case: an empty collection of loans
  why: the obligation is stated over one returned loan, and the function takes exactly
    one
- edge_case: a dependency that fails or answers slowly
  why: the computation reads only the loan's two dates and calls nothing outside itself
- edge_case: two computations over one loan at once
  why: the computation is a pure function of a frozen record and changes no state
untested:
- 'rules/lending/late-fee-per-overdue-day: its fact holds for every count of overdue
  calendar days, a set nothing enumerates, so no finite test decides it whole; the
  tests prove one day and ten days only.'
- 'The implementation''s inference that a loan not yet returned is refused with a
  ValueError: no node states the fee of a loan still out, so the choice is recorded
  as unproven and not pinned by a test.'
---
## What it is
Tests that hold the late fee of a returned loan to 0 cents on or before its due date and to 100 cents per calendar day after it.

## Notes
None.
