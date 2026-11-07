---
target: app
task: sha256:97b0fea7bc6d3f382702037fbab9c70bc20656ac9a810ef8f8907d6d1b097846
standard:
  at: standard.yaml
  pin: sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6
run: run/fees-compute-late-fee-build
title: Late fee of a returned loan
summary: A function in lending/fees.py that answers the late fee a returned loan carries,
  in integer cents.
files:
- path: lending/fees.py
  effect: late_fee_cents(loan) answers 0 for a loan returned on or before its due
    date, and 100 cents for each calendar day between its due date and its return
    otherwise.
criteria:
- criterion: A loan returned on or before its due date carries a late fee of 0 cents.
  met: true
  how: late_fee_cents takes the day difference between returned_on and due_on and
    floors it at 0, so a return on or before the due date answers 0.
- criterion: A loan returned after its due date carries 100 cents for each calendar
    day between its due date and its return.
  met: true
  how: late_fee_cents multiplies the calendar days between due_on and returned_on
    by LATE_FEE_CENTS_PER_DAY, which is 100.
nodes:
- node: rules/lending/late-fee-per-overdue-day
  encoded_at:
  - lending/fees.py
  how: BRL 1.00 per calendar day between the due date and the return is held as LATE_FEE_CENTS_PER_DAY
    = 100, multiplied by the overdue day count in late_fee_cents.
inferences:
- inferred: The fee is answered as an int of cents, so BRL 1.00 per day is the constant
    100.
  from: The task's objective and criteria state the fee in cents, and the standard's
    PY-01 requires money in integer cents.
- inferred: The function takes the existing Loan record and reads due_on and returned_on
    from it rather than taking two dates.
  from: The inventory's must_not_duplicate entry names the Loan record and its dates
    at lending/loans.py, and the task's objective is given a returned loan.
- inferred: A loan without returned_on is outside the function's domain and is not
    answered; no guard or error was added for it.
  from: The task's objective states the function answers over a returned loan, and
    no node catalogues an error for an unreturned one.
deferred:
- what: The Loan record in lending/loans.py carries no late_fee attribute, though
    domain/lending/loan declares one typed decimal.
  why: The task asks for a function that answers the fee, not for the fee to be stored
    on the loan, and domain/lending/loan is not a node this task implements.
---
## What it is
A function in lending/fees.py that answers the late fee a returned loan carries, in integer cents.

## Notes
Steps 3 and 5 ran inline in one session, because this session cannot spawn subagents: the source and the tests were written in the same context.
