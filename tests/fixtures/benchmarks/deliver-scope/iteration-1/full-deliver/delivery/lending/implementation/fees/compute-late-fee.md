---
target: app
task: sha256:97b0fea7bc6d3f382702037fbab9c70bc20656ac9a810ef8f8907d6d1b097846
standard:
  at: standard.yaml
  pin: sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6
run: run/fees-compute-late-fee-build
title: Late fee of a returned loan
summary: A function that answers, in integer cents, the late fee a returned loan carries
  for each calendar day past its due date.
files:
- path: lending/fees.py
  effect: late_fee_cents(loan) answers 0 for a loan returned on or before its due
    date, and 100 cents per calendar day between the due date and the return otherwise.
criteria:
- criterion: A loan returned on or before its due date carries a late fee of 0 cents.
  met: true
  how: late_fee_cents subtracts due_on from returned_on and answers 0 where the day
    count is zero or negative.
- criterion: A loan returned after its due date carries 100 cents for each calendar
    day between its due date and its return.
  met: true
  how: late_fee_cents multiplies the calendar days between due_on and returned_on
    by LATE_FEE_CENTS_PER_DAY, which is 100.
nodes:
- node: rules/lending/late-fee-per-overdue-day
  encoded_at:
  - lending/fees.py
  how: BRL 1.00 per calendar day between the due date and the return is LATE_FEE_CENTS_PER_DAY
    = 100 times the date difference in days, answered in integer cents.
inferences:
- inferred: The fee is answered in integer cents, BRL 1.00 being 100 cents.
  from: The task's objective and criteria state the fee in cents, and standard rule
    PY-01 requires money in integer cents.
- inferred: The computation lives in a new module lending/fees.py that reads the existing
    Loan record rather than redefining it.
  from: The inventory's must_not_duplicate entry for the Loan record at lending/loans.py
    and its area lending/.
deferred:
- what: The fee of a loan with no returned_on is not computed; the function is stated
    over returned loans only.
  why: The task's objective is a returned loan, and no node states what an unreturned
    loan's fee answers.
---
## What it is
A function that answers, in integer cents, the late fee a returned loan carries for each calendar day past its due date.

## Notes
The task-implementer step ran inline in the session, because no agent of this plugin is registered in it.
