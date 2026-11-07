---
contract_version: siegard-reconcile/11
title: Late fee of a returned loan, reviewed as lending
summary: 'The delivery of task/fees/compute-late-fee, under the initiative lending, wrote lending/fees.py
  and tests/test_fees.py: a function that answers, in integer cents, the late fee a returned loan carries,
  and three tests holding it to the task''s two criteria.'
delivered: lending
target: app
files:
- path: lending/fees.py
  change: late_fee_cents(loan) answers 0 for a loan returned on or before its due date, and 100 cents
    for each calendar day between its due date and its return otherwise
- path: tests/test_fees.py
  change: written by the delivery of task/fees/compute-late-fee
nodes:
- node: rules/lending/late-fee-per-overdue-day
  conforms: true
  how: 'lending/fees.py: held at the return statement of late_fee_cents, line 10, over the constant LATE_FEE_CENTS_PER_DAY
    at line 3 — line 3, "LATE_FEE_CENTS_PER_DAY = 100"; line 10, "return overdue_days * LATE_FEE_CENTS_PER_DAY"'
  encoded_at:
  - lending/fees.py
unstated:
- file: lending/fees.py
  where: the day count in late_fee_cents, line 7
  evidence: overdue_days = (loan.returned_on - loan.due_on).days
  cost: the node's "each calendar day between its due date and its return" does not say whether the due
    date or the return day counts; the code decides that the count is the dates' difference, so a loan
    returned one day late carries BRL 1.00, and that decision lives only in this line
- file: lending/fees.py
  where: the guard in late_fee_cents, lines 8-9
  evidence: "if overdue_days <= 0:\n    return 0"
  cost: the node states the fee only of a loan returned after its due date; that a loan returned on or
    before its due date carries no fee lives only here and in the task's criterion, so the next reader
    looks for it in the specification and does not find it
unbound:
- tests/test_fees.py
notes: 'Judged by 2 subagent(s), one per file; folded mechanically by trace.py --fold from the returns
  under siegard-reconcile/lending.returns/.

  Staged by a review over files a delivery wrote: every pair a delivery or a hand stamped was judged,
  and a pair was omitted only where a reconciliation''s judgment had cleared it at these very bytes; the
  plan''s node(s) rules/lending/late-fee-per-overdue-day were read on every file and answered for, and
  bound from nowhere here — a binding this record writes is one the trace already held.

  Candidates: 0 opened across 0 of 2 subagent(s); each return lists its own under `candidates_opened`.

  Unstated: 2 fact(s) the source states that no node holds, over 1 file(s), listed under `unstated`. They
  block no binding here and no rebind closes them — the route is the analysis that gives each fact a node.'
---

## Folded
This record was folded by `trace.py --fold` from the subagent returns under `siegard-reconcile/lending.returns/`, which are the evidence behind every entry above.
