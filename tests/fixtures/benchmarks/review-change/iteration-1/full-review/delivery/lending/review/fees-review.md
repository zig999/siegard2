---
target: app
title: Late fee of a returned loan, reviewed as fees-review
summary: What the coverage, conformance and standard passes found over lending/fees.py and tests/test_fees.py,
  and the green run the registry's steps produced.
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
- criterion: A loan returned after its due date carries 100 cents for each calendar day between its due
    date and its return.
  state: partial
  tests:
  - file: tests/test_fees.py
    name: test_each_further_calendar_day_after_the_due_date_adds_100_cents
  why: The step of 100 cents for each further calendar day, from the second to the fortieth day after
    the due date, is exercised; the amount a given return carries is not, because the test accepts any
    fee from (days_late - 1) * 100 to days_late * 100 cents, so a count of the days between the due date
    and the return that is off by one in either direction still passes, and no test pins the fee of a
    loan returned one calendar day after its due date. The criterion itself does not say whether the due
    date or the return day is counted among the days between them.
unpaired: []
findings:
- pass: conformance
  kind: unstated
  file: lending/fees.py
  where: the day count in late_fee_cents, line 7
  evidence: overdue_days = (loan.returned_on - loan.due_on).days
  cost: the node's "each calendar day between its due date and its return" does not say whether the due
    date or the return day counts; the code decides that the count is the dates' difference, so a loan
    returned one day late carries BRL 1.00, and that decision lives only in this line
  correction: rules/lending/late-fee-per-overdue-day states how the calendar days between the due date
    and the return are counted (which end, if any, counts), and the code is read against it
- pass: conformance
  kind: unstated
  file: lending/fees.py
  where: the guard in late_fee_cents, lines 8-9
  evidence: "if overdue_days <= 0:\n    return 0"
  cost: the node states the fee only of a loan returned after its due date; that a loan returned on or
    before its due date carries no fee lives only here and in the task's criterion, so the next reader
    looks for it in the specification and does not find it
  correction: a node, most plausibly rules/lending/late-fee-per-overdue-day, gains the statement that
    a loan returned on or before its due date carries no late fee
run: run/fees-review
reconciliation: siegard-reconcile/fees-review.md
---
## What it is
The review of task/fees/compute-late-fee over lending/fees.py and tests/test_fees.py, under the initiative lending.
The registry's build and test steps ran green as run/fees-review.

## Notes
No subagent of this plugin was registered in the session, so every spawn failed and the coverage, conformance and standard passes ran inline, each under its agent file's discipline.
The inline conformance returns were placed verbatim at siegard-reconcile/fees-review.returns/ because trace.py --save-return accepts only a subagent transcript.
The standard pass read PY-01, the one rule decided by reading; its scope reaches lending/fees.py and not tests/test_fees.py, and nothing departed from it.
The rule decided by a tool rests on the build step, which passed.
The conformance pass looked past the fee being an int of cents while domain/lending/loan declares late_fee as a decimal amount in BRL, a representation PY-01 governs.
No proof record carries a demonstrates claim, so no certification was staged; the proof's untested entry says the rule as a whole is not decided by a finite test because the node does not state whether an end day counts.
This review does not judge performance, security beyond the registry's own steps, or anything outside the two files.
