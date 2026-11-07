---
target: app
implementation: sha256:afe5f2ecd47aacdf5c59681d80b7b7d3390bfd4f8ff7ba641369b4a66a1ab23b
standard:
  at: standard.yaml
  pin: sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6
run: run/fees-compute-late-fee-suite
title: Proof for computing the late fee of a returned loan
summary: Four tests holding late_fee_cents() to the task's two criteria at each class
  and boundary where the fee changes.
tests:
- file: tests/test_fees.py
  name: test_a_loan_returned_before_its_due_date_carries_no_late_fee
  proves: A loan returned on or before its due date carries a late fee of 0 cents
    — the class of returns strictly before the due date.
  fails_when: an early return is answered anything but 0, such as a negative fee from
    the day difference left unclamped
- file: tests/test_fees.py
  name: test_a_loan_returned_on_its_due_date_carries_no_late_fee
  proves: A loan returned on or before its due date carries a late fee of 0 cents
    — the boundary at the due date itself.
  fails_when: the due date itself is counted as an overdue day, or the comparison
    is off by one
- file: tests/test_fees.py
  name: test_a_loan_returned_one_day_after_its_due_date_carries_100_cents
  proves: A loan returned after its due date carries 100 cents for each calendar day
    between its due date and its return — the boundary one day past the due date.
  fails_when: the first overdue day is not charged, is charged other than 100 cents,
    or the fee starts a day late
- file: tests/test_fees.py
  name: test_a_loan_returned_several_days_late_carries_100_cents_per_day
  proves: A loan returned after its due date carries 100 cents for each calendar day
    between its due date and its return — the class of returns more than one day late.
  fails_when: the fee stops scaling with the overdue days, as a flat charge or a rate
    other than 100 cents per day would
not_applicable:
- edge_case: a loan returned before it was borrowed
  why: no criterion and no node states a fee for that date order, and the loan's own
    construction is not this task's
- edge_case: two fee computations over one loan at once
  why: the computation reads one immutable loan and writes nothing, and no node states
    concurrent behavior
- edge_case: a dependency that fails or answers slowly
  why: the computation calls nothing outside the loan it is handed
untested:
- rules/lending/late-fee-per-overdue-day states the fee for every loan returned after
  its due date, a totality over every overdue day count that no finite set of inputs
  enumerates; the criterion tests above sample it at the boundary and one class, and
  no test claims the node whole.
- The implementation's inference that a loan not yet returned is refused with a ValueError
  is a behavior no node decides, so it is left unpinned for the specification to give
  it a home.
---
## What it is
Four tests holding late_fee_cents() to the task's two criteria at each class and boundary where the fee changes.

## Notes
None.
