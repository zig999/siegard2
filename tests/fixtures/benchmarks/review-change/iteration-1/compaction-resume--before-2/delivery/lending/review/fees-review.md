---
target: app
title: Late fee of a returned loan, review fees-review
summary: What the coverage, conformance and standard passes found over the late fee computation and its tests, and a captured run that passed.
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
  missing: the captured run run/fees-review passed, so there was no failure to diagnose
standard:
  at: standard.yaml
  pin: sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6
run: run/fees-review
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
  why: The fee of a loan returned exactly one calendar day after its due date is held to a range of 0 to 100 cents, not to 100 cents, so the first day of lateness is unexercised.
unpaired: []
findings:
- pass: conformance
  kind: unstated
  file: lending/fees.py
  where: late_fee_cents, the branch on overdue_days
  evidence: "if overdue_days <= 0:\n        return 0"
  cost: The fee of a loan returned on or before its due date is decided in code and in no node, so a change to it answers to no rule a reader can open.
reconciliation: siegard-reconcile/fees-review.md
---
## What it is
What the coverage, conformance and standard passes found over the late fee computation and its tests, and a captured run that passed.

## Notes
The coverage, conformance and standard passes ran inline: no agent of this plugin was registered in the session, so every spawn failed. The failures pass did not run because the captured run passed.
