---
target: app
task: sha256:97b0fea7bc6d3f382702037fbab9c70bc20656ac9a810ef8f8907d6d1b097846
standard:
  at: standard.yaml
  pin: sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6
run: run/fees-compute-late-fee-build
title: Late fee of a returned loan
summary: The function that answers, in integer cents, the late fee a returned loan
  carries, written for task/fees/compute-late-fee.
files:
- path: lending/fees.py
  effect: late_fee_cents(loan) answers 0 cents for a loan returned on or before its
    due date and 100 cents per calendar day between the due date and the return for
    one returned after it, and refuses a loan with no return date
criteria:
- criterion: A loan returned on or before its due date carries a late fee of 0 cents.
  met: true
  how: late_fee_cents() takes the day difference between returned_on and due_on, and
    max(overdue_days, 0) makes a return on or before the due date answer 0 in lending/fees.py
- criterion: A loan returned after its due date carries 100 cents for each calendar
    day between its due date and its return.
  met: true
  how: late_fee_cents() multiplies the calendar days (returned_on - due_on).days by
    LATE_FEE_CENTS_PER_OVERDUE_DAY, which is 100, in lending/fees.py
nodes:
- node: rules/lending/late-fee-per-overdue-day
  encoded_at:
  - lending/fees.py
  how: the invariant's BRL 1.00 per calendar day between the due date and the return
    is LATE_FEE_CENTS_PER_OVERDUE_DAY (100 cents) times the date difference, computed
    in integer cents as PY-01 requires
inferences:
- inferred: A loan with no returned_on is refused with ValueError rather than answered
    with a fee.
  from: the task's objective names a returned loan as the input, and no node states
    what the fee of an unreturned loan is
- inferred: The fee is answered as an int of cents rather than the decimal the Loan
    entity's late_fee attribute declares.
  from: the task's objective and criteria state the fee in cents, and the standard's
    PY-01 requires money in integer cents
- inferred: The function takes the existing Loan record rather than a pair of dates.
  from: the inventory's must_not_duplicate names the Loan record and its dates at
    lending/loans.py
preserved:
- lending/loans.py's Loan record keeps its fields and their defaults, and tests/test_loans.py
  keeps passing over it
deferred:
- what: The Loan record at lending/loans.py carries no late_fee attribute, though
    domain/lending/loan declares one.
  why: the task's objective is a function answering the fee, and storing it on the
    record reaches past that objective and into a node the task does not implement
---
## What it is
The function that answers, in integer cents, the late fee a returned loan carries, written for task/fees/compute-late-fee.

## Notes
The source was written inline, applying agents/task-implementer.md in place, because this session cannot spawn subagents.
