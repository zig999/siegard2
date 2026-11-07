---
target: app
task: sha256:97b0fea7bc6d3f382702037fbab9c70bc20656ac9a810ef8f8907d6d1b097846
standard:
  at: standard.yaml
  pin: sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6
run: run/fees-compute-late-fee-build
title: Late fee of a returned loan
summary: A function that answers, in integer cents, the late fee a returned loan carries.
files:
- path: lending/fees.py
  effect: late_fee_cents(loan) answers 0 for a loan returned on or before its due
    date, and 100 cents for each calendar day between its due date and its return
    otherwise; it refuses a loan with no return date
criteria:
- criterion: A loan returned on or before its due date carries a late fee of 0 cents.
  met: true
  how: late_fee_cents counts the days from due_on to returned_on and returns 0 where
    that count is zero or negative, in lending/fees.py
- criterion: A loan returned after its due date carries 100 cents for each calendar
    day between its due date and its return.
  met: true
  how: late_fee_cents multiplies the positive day count (returned_on - due_on).days
    by LATE_FEE_CENTS_PER_DAY, which is 100, in lending/fees.py
nodes:
- node: rules/lending/late-fee-per-overdue-day
  encoded_at:
  - lending/fees.py
  how: the rule's BRL 1.00 per calendar day between the due date and the return is
    LATE_FEE_CENTS_PER_DAY = 100 applied to the day count, held in integer cents as
    PY-01 states
inferences:
- inferred: a loan carrying no returned_on is refused with a ValueError rather than
    answered with a fee
  from: the task's objective is stated over a returned loan, and no node states what
    the fee of an unreturned loan is
- inferred: the fee is answered by a module-level function over the existing Loan
    record rather than a method on it
  from: the inventory's convention that a domain record is a frozen dataclass with
    typed fields, seen at lending/loans.py, and its must_not_duplicate entry for the
    Loan record
deferred:
- what: domain/lending/loan declares a late_fee attribute that the Loan record in
    lending/loans.py does not carry
  why: the task's objective is the computation of the fee, and storing it on the loan
    reaches past it
---
## What it is
A function that answers, in integer cents, the late fee a returned loan carries.

## Notes
The implement and prove steps ran inline in one session, which could not spawn subagents, applying agents/task-implementer.md and agents/test-author.md in turn.
