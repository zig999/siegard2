---
target: app
title: Review fees-review of the late fee delivery
summary: What the coverage, conformance and standard passes found over the late fee
  source and its tests, with the green run fees-review.
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
standard:
  at: standard.yaml
  pin: sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6
coverage:
- criterion: A loan returned on or before its due date carries a late fee of 0 cents.
  state: covered
  tests:
  - file: tests/test_fees.py
    name: test_a_loan_returned_on_its_due_date_carries_no_late_fee
  - file: tests/test_fees.py
    name: test_a_loan_returned_before_its_due_date_carries_no_late_fee
- criterion: A loan returned after its due date carries 100 cents for each calendar
    day between its due date and its return.
  state: partial
  tests:
  - file: tests/test_fees.py
    name: test_each_further_calendar_day_after_the_due_date_adds_100_cents
  why: The fee of a loan returned exactly one calendar day after its due date is held
    to a range of 0 to 100 cents, not to 100 cents, so the first day of lateness is
    unexercised.
unpaired: []
findings:
- pass: conformance
  kind: unstated
  file: lending/fees.py
  where: late_fee_cents, the branch on overdue_days
  evidence: "if overdue_days <= 0:\n        return 0"
  cost: The fee of a loan returned on or before its due date is decided in code and
    in no node, so a change to it answers to no rule a reader can open.
run: run/fees-review
reconciliation: siegard-reconcile/fees-review.md
---

## What it is
The review fees-review of task/fees/compute-late-fee under the initiative lending, over lending/fees.py and tests/test_fees.py in the target app.
The coverage, conformance and standard passes ran inline, in this session, because no agent of the plugin was registered and every spawn failed.
The failures pass did not run, because run/fees-review passed with the registry's steps build and test.

## Notes
The certification pass did not run: the staging held no entry under certify, because the proof's tests carry no demonstrates and its untested names the node.
The standard pass held PY-01 in scope by reading; PY-02 is decided by the registry's step build, and the run carries it.
The standard pass looked past the tests' date arithmetic, which no rule in scope names.
The conformance judgment of tests/test_fees.py looked past the tests asserting the fee in cents per day, which is the coverage pass's to weigh.
The fold bound rules/lending/late-fee-per-overdue-day to lending/fees.py; tests/test_fees.py stays unbound.
