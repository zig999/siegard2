---
target: app
title: Review of the late fee of a returned loan
summary: What the coverage, conformance and standard passes found over lending/fees.py and tests/test_fees.py,
  delivered by task/fees/compute-late-fee.
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
run: run/fees-review
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
  why: 'The test holds the 100 cents added by each further calendar day from the second to the fortieth
    day late, and bounds the fee of a return n days late between (n-1)*100 and n*100 cents, but no test
    asserts the fee of any one return absolutely: an implementation answering (n-1)*100 cents, which does
    not count the return day, passes it as the one answering n*100 does, so which calendar days count
    as "between its due date and its return" (and so whether a loan returned one day after its due date
    carries 100 cents or 0) is unexercised. The criterion itself leaves that count open.'
unpaired: []
findings:
- pass: conformance
  file: lending/fees.py
  where: late_fee_cents, line 7, the count of overdue days
  evidence: overdue_days = (loan.returned_on - loan.due_on).days
  cost: The node charges "for each calendar day between its due date and its return" and states nothing
    about whether the return day counts; this line decides that a loan returned one day after its due
    date carries one day of fee rather than none, and that decision lives only here, so a reader of the
    specification cannot tell what a return one day late owes.
  correction: The specification states how the calendar days between the due date and the return are counted
    (whether the return day counts), and the subtraction in line 7 is then read against it.
  kind: unstated
---
## What it is
A review of task/fees/compute-late-fee over lending/fees.py and tests/test_fees.py in target app.

## Notes
No agent of this plugin was registered in this session, so the coverage, conformance and standard passes ran inline, by the session reading each agent file and applying its discipline.
The conformance returns could not be saved: trace.py --save-return refused each inline return as not a subagent transcript, so the fold, the reconciliation record and the bind did not run and siegard-trace.json was not restamped.
The standard pass read PY-01, the one rule decided by reading whose scope reaches the file set; it reaches lending/fees.py and not tests/test_fees.py, and found no departure.
The rule the standard leaves to a tool runs as the build step of run/fees-review, which passed.
No proof record claims a test demonstrates rules/lending/late-fee-per-overdue-day, so no certification was staged.
The conformance pass looked past the fee being answered as an int of cents while domain/lending/loan declares late_fee as a decimal amount in BRL, since how money is represented is the standard question.
This review reads no security, performance or style beyond the one rule of the standard decided by reading.
