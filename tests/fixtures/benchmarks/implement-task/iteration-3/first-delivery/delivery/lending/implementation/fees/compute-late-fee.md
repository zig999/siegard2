---
target: app
task: sha256:97b0fea7bc6d3f382702037fbab9c70bc20656ac9a810ef8f8907d6d1b097846
standard:
  at: standard.yaml
  pin: sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6
run: run/fees-compute-late-fee-build
title: Late fee of a returned loan
summary: A function that answers, in integer cents, the late fee one returned loan
  carries.
files:
- path: lending/fees.py
  effect: late_fee_cents(loan) answers 0 for a loan returned on or before its due
    date, and 100 cents for each calendar day between its due date and its return
    otherwise
criteria:
- criterion: A loan returned on or before its due date carries a late fee of 0 cents.
  met: true
  how: late_fee_cents counts the days from due_on to returned_on and answers 0 where
    that count is zero or negative
- criterion: A loan returned after its due date carries 100 cents for each calendar
    day between its due date and its return.
  met: true
  how: late_fee_cents multiplies the calendar days from due_on to returned_on by LATE_FEE_CENTS_PER_DAY,
    which is 100
nodes:
- node: rules/lending/late-fee-per-overdue-day
  encoded_at:
  - lending/fees.py
  how: the fee of BRL 1.00 per calendar day overdue is LATE_FEE_CENTS_PER_DAY (100
    cents) times the date difference returned_on - due_on, charged only where that
    difference is positive
inferences:
- inferred: the function takes the Loan record and reads its due_on and returned_on,
    rather than taking the two dates as separate arguments
  from: the inventory's must_not_duplicate entry for the Loan record and its dates
    at lending/loans.py, and the task's objective "Given a returned loan"
- inferred: the fee lives in a new module lending/fees.py rather than in lending/loans.py
  from: the inventory names lending/loans.py as a module this area depends on, and
    the epic fees is a concern of its own
deferred:
- what: A Loan whose returned_on is None is not handled; late_fee_cents over it raises
    the TypeError date subtraction raises.
  why: the task's objective is a returned loan, and no node states what an unreturned
    loan's fee is
---
## What it is
A function that answers, in integer cents, the late fee one returned loan carries.

## Notes
Steps 3 and 5 ran inline in the session, which could not spawn subagents: the source and the tests were written in one context.
