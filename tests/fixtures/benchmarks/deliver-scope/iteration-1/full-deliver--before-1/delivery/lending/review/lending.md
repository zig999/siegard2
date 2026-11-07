---
target: app
title: Review of the late-fee delivery
summary: Coverage and standard readings over the late-fee function and its tests, with the conformance
  pass stopped because no separate judge could be spawned.
reviewed:
- lending/fees.py
- tests/test_fees.py
tasks:
- task/fees/compute-late-fee
passes:
- pass: coverage
- pass: conformance
  missing: 'a judge context apart from the one that wrote the delivery: siegard:specification-conformance-reviewer
    could not be spawned in this session, and this session wrote lending/fees.py and tests/test_fees.py
    itself, so the pass stopped and its fold, certification and bind did not run rather than running inline'
- pass: failures
  missing: run/lending passed; there was no failure to read
- pass: standard
coverage:
- criterion: A loan returned on or before its due date carries a late fee of 0 cents.
  state: covered
  tests:
  - file: tests/test_fees.py
    name: test_a_loan_returned_on_its_due_date_carries_no_fee
  - file: tests/test_fees.py
    name: test_a_loan_returned_before_its_due_date_carries_no_fee
- criterion: A loan returned after its due date carries 100 cents for each calendar day between its due
    date and its return.
  state: covered
  tests:
  - file: tests/test_fees.py
    name: test_a_loan_returned_one_day_late_carries_one_hundred_cents
  - file: tests/test_fees.py
    name: test_the_fee_is_one_hundred_cents_for_each_calendar_day_late
unpaired: []
standard:
  at: standard.yaml
  pin: sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6
run: run/lending
---
## What it is

A review of task/fees/compute-late-fee over lending/fees.py and tests/test_fees.py, named lending.

## Notes

The coverage and standard passes ran inline in this session, because no agent of the plugin could be spawned; each agent's file was read and applied in place.
The conformance pass did not run: this session wrote the files under review, and the fold step stops that pass rather than running it inline where the judge would be the writer.
No certification of rules/lending/late-fee-per-overdue-day landed, because its return is folded by the conformance step that did not run.
The standard pass read PY-01, the one rule a reading decides whose scope reaches lending/fees.py; PY-02 is decided by the build step, which passed in run/lending.
This review judges no performance, security or style the project's standard does not state.
