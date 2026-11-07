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
  name: test_a_loan_returned_on_its_due_date_carries_no_late_fee
  proves: A loan returned on or before its due date carries a late fee of 0 cents,
    at the boundary where the return falls on the due date itself.
  fails_when: a return on the due date is counted as one overdue day, or answers anything
    but 0
- file: tests/test_fees.py
  name: test_a_loan_returned_before_its_due_date_carries_no_late_fee
  proves: A loan returned on or before its due date carries a late fee of 0 cents,
    for a return strictly before the due date.
  fails_when: the days before the due date are charged or credited, so an early return
    answers a non-zero fee
- file: tests/test_fees.py
  name: test_a_loan_returned_one_day_after_its_due_date_carries_100_cents
  proves: A loan returned after its due date carries 100 cents for each calendar day
    between its due date and its return, at the boundary of one day past the due date.
  fails_when: the first overdue day is not charged, or is charged at anything but
    100 cents
- file: tests/test_fees.py
  name: test_a_loan_returned_days_after_its_due_date_carries_100_cents_per_calendar_day
  proves: A loan returned after its due date carries 100 cents for each calendar day
    between its due date and its return, over ten calendar days that cross a month
    end.
  fails_when: the fee stops being BRL 1.00 per calendar day between the due date and
    the return — a different rate, a count that skips or adds days across the month
    end, or a flat fee
  demonstrates: rules/lending/late-fee-per-overdue-day
not_applicable:
- edge_case: absent or empty input
  why: the function takes one Loan whose dates the dataclass requires; no obligation
    states a loan without a due date
- edge_case: an empty collection or a duplicate
  why: the computation is over one loan; no obligation names a collection or a uniqueness
- edge_case: a dependency that fails or answers slowly
  why: the computation reads no dependency; it is arithmetic over two dates
- edge_case: two operations on one subject at once
  why: the computation is pure over an immutable loan; no obligation states concurrent
    behavior
untested:
- 'A loan not yet returned is refused with a ValueError: an inference the implementation
  recorded about behavior, which no node decides and no test pins.'
---
## What it is
What proves task/fees/compute-late-fee, written against its implementation record.

## Notes
None.
