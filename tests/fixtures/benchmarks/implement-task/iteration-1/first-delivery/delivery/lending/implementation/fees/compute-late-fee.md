---
target: app
task: sha256:97b0fea7bc6d3f382702037fbab9c70bc20656ac9a810ef8f8907d6d1b097846
standard:
  at: standard.yaml
  pin: sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6
run: run/fees-compute-late-fee-build
title: Late fee of a returned loan
summary: A function in lending/fees.py that answers, in integer cents, the late fee
  a returned loan carries.
files:
- path: lending/fees.py
  effect: late_fee_cents(loan) answers 0 for a loan returned on or before its due
    date, and 100 cents for each calendar day between its due date and its return
    otherwise.
criteria:
- criterion: A loan returned on or before its due date carries a late fee of 0 cents.
  met: true
  how: late_fee_cents counts the days from due_on to returned_on and answers 0 when
    that count is zero or negative.
- criterion: A loan returned after its due date carries 100 cents for each calendar
    day between its due date and its return.
  met: true
  how: late_fee_cents multiplies the positive count of calendar days between due_on
    and returned_on, taken as the date difference's days, by LATE_FEE_CENTS_PER_OVERDUE_DAY,
    which is 100.
nodes:
- node: rules/lending/late-fee-per-overdue-day
  encoded_at:
  - lending/fees.py
  how: The rule's BRL 1.00 per calendar day is LATE_FEE_CENTS_PER_OVERDUE_DAY = 100
    integer cents, multiplied by the days between the loan's due date and its return,
    and charged only when the return is after the due date.
inferences:
- inferred: The fee is computed over the existing Loan record, reading its due_on
    and returned_on, in a new module lending/fees.py beside lending/loans.py.
  from: The inventory names lending/loans.py as the module this work depends on and
    the Loan record and its dates as what must not be duplicated.
- inferred: The calendar days between the due date and the return are the difference
    of the two dates in days, so a return the day after the due date is one day.
  from: The rule's wording "each calendar day between its due date and its return"
    and the task's criteria, read over Python date values.
- inferred: late_fee_cents is defined only over a loan whose returned_on is set; an
    unreturned loan is outside its domain and is given no answer of its own.
  from: The task's objective, which states the computation "Given a returned loan",
    and no node stating what an unreturned loan carries.
---
## What it is
A function in lending/fees.py that answers, in integer cents, the late fee a returned loan carries.

## Notes
Steps 3 and 5 ran inline in one session, which could not spawn subagents: the task-implementer's and the test-author's files were applied in place.
