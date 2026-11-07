---
target: app
implementation: sha256:f2660d13092d48a557784e87064d3925e163e51a6990cbb4945db12fef52c132
standard:
  at: standard.yaml
  pin: sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6
run: run/fees-compute-late-fee-suite
title: Proof of the late fee of a returned loan
summary: Four tests holding the zero fee up to the due date and the 100 cents per
  calendar day after it.
tests:
- file: tests/test_fees.py
  name: test_a_loan_returned_on_its_due_date_carries_no_fee
  proves: A loan returned on or before its due date carries a late fee of 0 cents.
  fails_when: a loan returned on its due date is charged anything, as where the day
    of the due date itself is counted as overdue
- file: tests/test_fees.py
  name: test_a_loan_returned_before_its_due_date_carries_no_fee
  proves: A loan returned on or before its due date carries a late fee of 0 cents.
  fails_when: a loan returned before its due date is charged anything, as where the
    days between return and due date are counted regardless of their sign
- file: tests/test_fees.py
  name: test_a_loan_returned_one_day_late_carries_100_cents
  proves: A loan returned after its due date carries 100 cents for each calendar day
    between its due date and its return.
  fails_when: the first day after the due date is not charged 100 cents, as where
    charging starts from a later day or the count is off by one
- file: tests/test_fees.py
  name: test_a_loan_returned_days_late_across_a_month_end_carries_100_cents_per_calendar_day
  proves: A loan returned after its due date carries 100 cents for each calendar day
    between its due date and its return.
  fails_when: the fee stops being 100 cents times the calendar days between due date
    and return, as where the per-day amount changes, the fee is flat, or days are
    counted within a month rather than across the calendar
  demonstrates: rules/lending/late-fee-per-overdue-day
not_applicable:
- edge_case: a loan not yet returned, whose returned_on is absent
  why: the task's objective is a returned loan, no node states an unreturned loan's
    fee, and the implementation recorded it as deferred
- edge_case: a renewed loan
  why: renewal moves due_on, and the fee is stated over the due date the loan carries,
    so a renewed loan is the same class as any other
- edge_case: two computations over one loan at once, or a dependency that fails or
    answers slowly
  why: the computation is a pure function over one record with no dependency and no
    state
---
## What it is
Four tests holding the zero fee up to the due date and the 100 cents per calendar day after it.

## Notes
Step 5 ran inline in the session that wrote the source, which could not spawn subagents.
