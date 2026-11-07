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
    date, and 100 cents per calendar day between the due date and the return otherwise.
criteria:
- criterion: A loan returned on or before its due date carries a late fee of 0 cents.
  met: true
  how: late_fee_cents counts the days from due_on to returned_on and returns 0 where
    that count is zero or negative.
- criterion: A loan returned after its due date carries 100 cents for each calendar
    day between its due date and its return.
  met: true
  how: late_fee_cents multiplies the positive day count between due_on and returned_on
    by LATE_FEE_CENTS_PER_DAY, which is 100.
nodes:
- node: rules/lending/late-fee-per-overdue-day
  encoded_at:
  - lending/fees.py
  how: The rule's BRL 1.00 per calendar day after the due date is LATE_FEE_CENTS_PER_DAY
    = 100 times the calendar days returned_on minus due_on, computed in integer cents.
inferences:
- inferred: The fee is answered by a function over the existing Loan record rather
    than stored as a new late_fee field on Loan.
  from: The task's objective names a service that answers the fee given a returned
    loan, and the inventory names the Loan record in lending/loans.py as what must
    not be duplicated.
- inferred: A loan with no returned_on is outside the function's domain and raises
    ValueError rather than answering a fee.
  from: The task's objective states the function is given a returned loan; no node
    states a fee for an unreturned loan.
divergences:
- from: domain/lending/loan
  departure: The fee is answered in integer cents rather than as the decimal type
    the loan's late_fee attribute declares.
  why: The task's objective states the fee in cents and the standard's PY-01 requires
    money in integer cents.
deferred:
- what: The loan entity declares a late_fee attribute that the Loan dataclass in lending/loans.py
    does not hold.
  why: The task asks for the computation only; adding the attribute to the record
    reaches past its objective.
---
## What it is
A function that answers, in integer cents, the late fee a returned loan carries.

## Notes
None.
