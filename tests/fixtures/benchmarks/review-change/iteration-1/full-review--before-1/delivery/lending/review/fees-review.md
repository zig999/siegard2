---
target: app
title: Review of the late fee of a returned loan
summary: Coverage, specification conformance and standard readings over lending/fees.py and tests/test_fees.py for task/fees/compute-late-fee, with the registry's steps captured green at run/fees-review.
reviewed:
- lending/fees.py
- tests/test_fees.py
tasks:
- task/fees/compute-late-fee
passes:
- pass: coverage
- pass: conformance
- pass: standard
- pass: failures
  missing: run/fees-review passed; there was no failure to read
coverage:
- criterion: A loan returned on or before its due date carries a late fee of 0 cents.
  state: covered
  tests:
  - file: tests/test_fees.py
    name: test_a_loan_returned_on_its_due_date_carries_no_late_fee
  - file: tests/test_fees.py
    name: test_a_loan_returned_before_its_due_date_carries_no_late_fee
- criterion: A loan returned after its due date carries 100 cents for each calendar day between its due date and its return.
  state: partial
  tests:
  - file: tests/test_fees.py
    name: test_each_further_calendar_day_after_the_due_date_adds_100_cents
  why: 'The 100 cents each further calendar day adds is exercised from the second to the fortieth day late, but the amount a given late return carries is not pinned: the test accepts any fee between (n-1)*100 and n*100 cents for a return n days late, so an implementation charging (n-1)*100 cents passes as well as one charging n*100, and the fee of a return one calendar day after its due date is never asserted at all.'
unpaired: []
standard:
  at: standard.yaml
  pin: sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6
run: run/fees-review
reconciliation: siegard-reconcile/fees-review.md
findings:
- pass: conformance
  file: lending/fees.py
  where: line 7, the overdue-day count in late_fee_cents
  evidence: overdue_days = (loan.returned_on - loan.due_on).days
  cost: the node charges BRL 1.00 "for each calendar day between its due date and its return" and does not say whether the return day counts, so the count this line takes (a return one day after the due date is one day, 100 cents) is a decision that lives only in code; the next reader looks for it in the specification and does not find it, and a reading that counts only the days strictly between the two dates would charge 100 cents less for every late return
  correction: the specification states how the calendar days between the due date and the return are counted (whether a return the day after the due date carries one day's fee), as a decided fact of rules/lending/late-fee-per-overdue-day, and the code is then read against it
  kind: unstated
---
## What it is
A review of the delivery of task/fees/compute-late-fee over lending/fees.py and tests/test_fees.py, target app.
The coverage, conformance and standard passes ran inline in the session, because no agent of this plugin was registered and every spawn failed.
The failures pass did not run: run/fees-review passed both registry steps, so there was no failure to read.

## Notes
No node the task implements is demonstrated by a test: the proof's tests carry no `demonstrates`, so no certification was staged.
The standard's rule PY-01 reaches lending/fees.py and no rule reaches tests/test_fees.py.
This review does not read performance, security beyond the registry, concurrency, or anything outside the two reviewed files.
