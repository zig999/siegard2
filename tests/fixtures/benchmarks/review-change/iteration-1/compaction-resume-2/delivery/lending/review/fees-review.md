---
target: app
title: Review fees-review of the late fee delivery
summary: What the coverage, conformance and standard passes found over lending/fees.py and tests/test_fees.py,
  delivered for task/fees/compute-late-fee.
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
- criterion: A loan returned after its due date carries 100 cents for each calendar day between its due
    date and its return.
  state: partial
  tests:
  - file: tests/test_fees.py
    name: test_each_further_calendar_day_after_the_due_date_adds_100_cents
  why: The fee of a loan returned exactly one calendar day after its due date is held to a range of 0
    to 100 cents, not to 100 cents, so the first day of lateness is unexercised.
unpaired: []
standard:
  at: standard.yaml
  pin: sha256:f295edd2e53e53bafffc479da7ab02aa101541b0aecce9ef89dfd76303b34ae6
run: run/fees-review
reconciliation: siegard-reconcile/fees-review.md
findings:
- pass: conformance
  kind: unstated
  file: lending/fees.py
  where: late_fee_cents, the branch on overdue_days
  evidence: "if overdue_days <= 0:\n        return 0"
  cost: The fee of a loan returned on or before its due date is decided in code and in no node, so a change
    to it answers to no rule a reader can open.
---
## What it is
A review of the change task/fees/compute-late-fee delivered over lending/fees.py and tests/test_fees.py in the target app.
The coverage, conformance and standard passes ran; the failures pass did not run because run/fees-review passed.

## Notes
Every subagent spawn failed in this session, so the coverage, conformance and standard passes ran inline, each applying its agent file in place.
The conformance pass judged one return per file, and trace.py --fold folded them into siegard-reconcile/fees-review.md.
The standard pass read rule PY-01 as in scope over the file set; PY-02 is decided by the tool step build rather than by a reading.
The standard pass looked past the tests' date arithmetic, which no rule in scope names.
The conformance pass over tests/test_fees.py looked past the tests asserting the fee in cents per day, which is the coverage pass's to weigh.
No staged proof claim owed a certification: the proof's tests carry no demonstrates, and its untested names the node.
