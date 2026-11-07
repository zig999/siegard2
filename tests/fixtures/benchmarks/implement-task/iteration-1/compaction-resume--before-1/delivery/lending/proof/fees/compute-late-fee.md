---
target: app
implementation: sha256:afe5f2ecd47aacdf5c59681d80b7b7d3390bfd4f8ff7ba641369b4a66a1ab23b
standard:
  at: standard.yaml
  pin: sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6
run: run/fees-compute-late-fee-suite
title: Proof of the late fee of a returned loan
summary: Four tests holding the zero fee up to and on the due date and the 100 cents
  per overdue calendar day after it.
tests:
- file: tests/test_fees.py
  name: test_a_loan_returned_before_its_due_date_carries_no_late_fee
  proves: A loan returned on or before its due date carries a late fee of 0 cents.
    (the before class)
  fails_when: a loan returned before its due date is answered any fee other than 0,
    such as a negative fee from an unclamped day count
- file: tests/test_fees.py
  name: test_a_loan_returned_on_its_due_date_carries_no_late_fee
  proves: A loan returned on or before its due date carries a late fee of 0 cents.
    (the boundary at the due date itself)
  fails_when: the due date itself is counted as an overdue day, so a loan returned
    on it is answered a fee other than 0
- file: tests/test_fees.py
  name: test_a_loan_returned_one_day_after_its_due_date_carries_100_cents
  proves: A loan returned after its due date carries 100 cents for each calendar day
    between its due date and its return. (the boundary at the first overdue day)
  fails_when: the first day after the due date is not charged, is charged other than
    100 cents, or the day count is off by one
- file: tests/test_fees.py
  name: test_a_loan_returned_several_days_after_its_due_date_carries_100_cents_per_day
  proves: A loan returned after its due date carries 100 cents for each calendar day
    between its due date and its return. (the per-day multiplication over several
    days)
  fails_when: the fee is not 100 cents multiplied by each calendar day past the due
    date, such as a flat fee for any lateness
not_applicable:
- edge_case: a return date across a month or year boundary
  why: the obligation counts calendar days whatever months they fall in; the dimension
    does not change what it requires
- edge_case: absent or empty input, collections, duplicates, concurrent operations,
    a failing dependency
  why: the computation is a pure function of one loan's two dates; no obligation reaches
    these
untested:
- 'rules/lending/late-fee-per-overdue-day: the fact holds for every count of overdue
  calendar days, a totality over a set nothing enumerates, so no finite test decides
  it whole; the tests above prove criterion instances and claim no node'
- 'the implementation''s inference that a loan not yet returned is refused with a
  ValueError: a behavior no node and no criterion states, so it is recorded as unproven
  and never pinned by a test'
---
## What it is
Four tests holding the zero fee up to and on the due date and the 100 cents per overdue calendar day after it.

## Notes
None.
