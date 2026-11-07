---
target: app
title: Review of the late-fee delivery
summary: The coverage and standard readings of task/fees/compute-late-fee over lending/fees.py and tests/test_fees.py, with the conformance pass not run.
reviewed:
- lending/fees.py
- tests/test_fees.py
tasks:
- task/fees/compute-late-fee
passes:
- pass: coverage
- pass: conformance
  missing: 'a specification-conformance-reviewer subagent: no agent of this plugin is registered in this session, and the session that would run the pass inline wrote both files under review, so the pass stopped rather than run inline'
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
- criterion: A loan returned after its due date carries 100 cents for each calendar day between its due date and its return.
  state: covered
  tests:
  - file: tests/test_fees.py
    name: test_a_loan_returned_one_day_late_carries_one_hundred_cents
  - file: tests/test_fees.py
    name: test_a_loan_returned_days_late_across_a_month_end_carries_one_hundred_cents_per_calendar_day
unpaired: []
standard:
  at: standard.yaml
  pin: sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6
run: run/lending
---

## What it is

The review of the one task delivered under epic/fees, over the two files its records name.

## Notes

The coverage and standard passes ran inline in the session, because no agent of this plugin is registered in it, and that session also wrote the source and the tests under review.
The conformance pass did not run, so no reconciliation record was folded and no binding was restamped by this review.
The standard pass had PY-01 in scope, the one rule decided by reading whose scope reaches lending/fees.py, and found no departure; PY-02 is decided by the build step of run/lending, which passed.
This review does not judge whether lending/fees.py states only what the specification holds.
