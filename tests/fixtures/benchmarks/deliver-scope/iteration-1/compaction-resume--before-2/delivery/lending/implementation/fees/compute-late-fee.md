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
    otherwise
criteria:
- criterion: A loan returned on or before its due date carries a late fee of 0 cents.
  met: true
  how: late_fee_cents in lending/fees.py returns 0 whenever the days from due_on to
    returned_on are zero or negative
- criterion: A loan returned after its due date carries 100 cents for each calendar
    day between its due date and its return.
  met: true
  how: late_fee_cents in lending/fees.py multiplies the calendar days from due_on
    to returned_on by LATE_FEE_CENTS_PER_DAY, which is 100
nodes:
- node: rules/lending/late-fee-per-overdue-day
  encoded_at:
  - lending/fees.py
  how: the rule's BRL 1.00 per calendar day is LATE_FEE_CENTS_PER_DAY = 100 in integer
    cents, applied to each calendar day between due_on and returned_on, and no fee
    is charged when the loan is returned on or before its due date
inferences:
- inferred: The number of calendar days between the due date and the return is returned_on
    minus due_on in days, so a loan returned the day after its due date carries one
    day's fee.
  from: the rule's statement "each calendar day between its due date and its return"
    and the date fields of the Loan record in lending/loans.py
- inferred: The function takes the existing Loan record and reads its due_on and returned_on,
    rather than receiving the two dates separately.
  from: the task's objective "Given a returned loan" and the inventory's must_not_duplicate
    entry for the Loan record and its dates at lending/loans.py
- inferred: The fee is an int of cents, the rule's BRL 1.00 being 100 cents.
  from: the task's criteria stated in cents and the standard's rule PY-01
deferred:
- what: A loan whose returned_on is None is outside the function's domain, and no
    refusal is written for it.
  why: The task states the fee of a returned loan only, and no node catalogues what
    answering the fee of an unreturned loan should do.
- what: The Loan entity's late_fee attribute (decimal) is not added to the Loan record
    in lending/loans.py.
  why: The task's objective is the computation; storing the fee on the record reaches
    past it.
---
## What it is
A function that answers, in integer cents, the late fee a returned loan carries.

## Notes
None.
