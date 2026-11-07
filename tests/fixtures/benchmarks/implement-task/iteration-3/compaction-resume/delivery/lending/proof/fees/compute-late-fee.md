---
target: app
implementation: sha256:afe5f2ecd47aacdf5c59681d80b7b7d3390bfd4f8ff7ba641369b4a66a1ab23b
standard:
  at: standard.yaml
  pin: sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6
run: run/fees-compute-late-fee-suite
title: Proof for computing the late fee of a returned loan
summary: Four tests that hold late_fee_cents() to the on-time and late boundaries
  of the task's two criteria.
tests:
- file: tests/test_fees.py
  name: test_a_loan_returned_on_its_due_date_carries_no_late_fee
  proves: A loan returned on or before its due date carries a late fee of 0 cents
    — at the boundary, a return on the due date itself.
  fails_when: a return on the due date is charged anything, such as a day counted
    inclusively of the due date
- file: tests/test_fees.py
  name: test_a_loan_returned_before_its_due_date_carries_no_late_fee
  proves: A loan returned on or before its due date carries a late fee of 0 cents
    — the class of returns strictly before the due date.
  fails_when: an early return is charged, such as a fee computed from the absolute
    number of days between the two dates, or a negative fee is answered
- file: tests/test_fees.py
  name: test_a_loan_returned_one_day_after_its_due_date_carries_100_cents
  proves: A loan returned after its due date carries 100 cents for each calendar day
    between its due date and its return — at the boundary, the first late day.
  fails_when: the first late day is not charged, as under a grace day, or is charged
    anything but 100 cents
- file: tests/test_fees.py
  name: test_a_loan_returned_late_across_a_month_end_carries_100_cents_per_calendar_day
  proves: A loan returned after its due date carries 100 cents for each calendar day
    between its due date and its return — several days, counted across a month end.
  fails_when: the fee stops scaling at 100 cents per day, or the days are counted
    other than as calendar days, such as by day-of-month difference across the month
    end
not_applicable:
- edge_case: a loan with no due date, or a missing loan
  why: the Loan the task computes over always carries a due date, and no obligation
    states behavior over an absent loan
- edge_case: two fee computations over one loan at once
  why: the computation reads one immutable loan and writes nothing, and no obligation
    states concurrent behavior
- edge_case: a dependency that fails or answers slowly
  why: the computation calls no dependency
- edge_case: an empty collection or a duplicate
  why: the computation takes one loan, and no obligation states uniqueness or a collection
untested:
- 'rules/lending/late-fee-per-overdue-day: its fact holds over every pairing of a
  due date and a later return, a set nothing enumerates, so no finite test decides
  it whole; the tests above prove the task''s criteria at their boundaries and one
  representative of each class, and claim no node.'
- 'The implementation''s inference that a loan not yet returned is refused with a
  ValueError: no node decides the behavior over a loan still out, so it is recorded
  as unproven and not pinned by a test.'
---
## What it is
Four tests that hold late_fee_cents() to the on-time and late boundaries of the task's two criteria.

## Notes
The test-author's step ran inline in the session that wrote the source, because this session cannot spawn subagents.
