---
target: app
implementation: sha256:96a44463d9fad457adecca1f00e17cbce34f7216c9f4c67595d16b7dceb89b2c
standard:
  at: standard.yaml
  pin: sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6
run: run/fees-compute-late-fee-suite
title: Proof of the late fee of a returned loan
summary: Four tests over late_fee_cents, one per class and boundary the task's criteria
  and the late-fee rule turn on.
tests:
- file: tests/test_fees.py
  name: test_a_loan_returned_before_its_due_date_carries_no_fee
  proves: A loan returned on or before its due date carries a late fee of 0 cents.
  fails_when: a loan returned before its due date is answered with anything but 0,
    such as a negative fee from a day count that is not clamped at zero
- file: tests/test_fees.py
  name: test_a_loan_returned_on_its_due_date_carries_no_fee
  proves: A loan returned on or before its due date carries a late fee of 0 cents,
    at the boundary where the return date equals the due date
  fails_when: a loan returned on its due date is charged, as an off-by-one in the
    day count would
- file: tests/test_fees.py
  name: test_a_loan_returned_one_day_after_its_due_date_carries_100_cents
  proves: A loan returned after its due date carries 100 cents for each calendar day
    between its due date and its return, at the boundary of the first late day
  fails_when: the first day past the due date is not charged, or is charged anything
    but 100 cents
- file: tests/test_fees.py
  name: test_a_late_loan_carries_100_cents_for_each_calendar_day_across_a_month_end
  proves: A loan returned after its due date carries 100 cents for each calendar day
    between its due date and its return
  fails_when: the fee stops growing by 100 cents per calendar day, is a fixed amount,
    or counts days other than calendar days across a month end
  demonstrates: rules/lending/late-fee-per-overdue-day
not_applicable:
- edge_case: two fee computations over one loan at once
  why: the computation reads one immutable record and writes nothing, and no node
    states concurrent behavior
- edge_case: a dependency that fails or answers slowly
  why: the computation calls no dependency
- edge_case: a return date far in the past or a very long delay
  why: no node states an upper bound or a cap on the fee, so no boundary exists past
    the first late day
untested:
- 'the refusal of a loan with no returned_on, which the implementation recorded as
  an inference: no node states what the fee of an unreturned loan is, so the behavior
  is left unpinned'
---
## What it is
Four tests over late_fee_cents, one per class and boundary the task's criteria and the late-fee rule turn on.

## Notes
The prove step ran inline in the session that wrote the source, which could not spawn subagents, applying agents/test-author.md.
