---
target: app
task: sha256:97b0fea7bc6d3f382702037fbab9c70bc20656ac9a810ef8f8907d6d1b097846
standard:
  at: standard.yaml
  pin: sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6
run: run/fees-compute-late-fee-build
title: Late fee of a returned loan
summary: A function that answers, in integer cents, the late fee a returned loan carries
  under the per-overdue-day rule.
files:
- path: lending/fees.py
  effect: answers late_fee_cents(loan), 0 for a loan returned on or before its due
    date and 100 cents per calendar day between the due date and the return otherwise
criteria:
- criterion: A loan returned on or before its due date carries a late fee of 0 cents.
  met: true
  how: late_fee_cents in lending/fees.py floors the day count between due_on and returned_on
    at 0, so a return on or before the due date answers 0
- criterion: A loan returned after its due date carries 100 cents for each calendar
    day between its due date and its return.
  met: true
  how: late_fee_cents in lending/fees.py multiplies the calendar days from due_on
    to returned_on by LATE_FEE_CENTS_PER_DAY, which is 100
nodes:
- node: rules/lending/late-fee-per-overdue-day
  encoded_at:
  - lending/fees.py
  how: the fee of BRL 1.00 per calendar day between the due date and the return is
    LATE_FEE_CENTS_PER_DAY times the date difference in days, computed in integer
    cents
inferences:
- inferred: BRL 1.00 is held as 100 integer cents, and the function answers cents
    rather than a decimal amount.
  from: the task's objective, which answers the fee in cents, and rule PY-01 of standard.yaml,
    which computes money in integer cents
- inferred: The function reads the loan's due_on and returned_on from the existing
    Loan record rather than taking dates of its own.
  from: the inventory's must_not_duplicate entry for the Loan record and its dates
    at lending/loans.py
deferred:
- what: The domain node domain/lending/loan lists a late_fee attribute that the Loan
    record in lending/loans.py does not carry.
  why: the task asks for a function that answers the fee, not for the fee stored on
    the record, and changing Loan reaches past it
- what: What late_fee_cents answers for a loan that has not been returned is stated
    nowhere.
  why: the task and the rule speak only of a returned loan, so the function is written
    for that input alone
---
## What it is
A function that answers, in integer cents, the late fee a returned loan carries under the per-overdue-day rule.

## Notes
None.
