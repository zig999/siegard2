---
contract_version: siegard-reconcile/11
title: Review fees-review of the late fee delivery
summary: The delivery of task/fees/compute-late-fee under the initiative lending wrote these files.
delivered: fees-review
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
  how: 'lending/fees.py: held at late_fee_cents, the product of overdue_days and LATE_FEE_CENTS_PER_DAY
    — return overdue_days * LATE_FEE_CENTS_PER_DAY'
  encoded_at:
  - lending/fees.py
unstated:
- file: lending/fees.py
  where: late_fee_cents, the branch on overdue_days
  evidence: "if overdue_days <= 0:\n        return 0"
  cost: The fee of a loan returned on or before its due date is decided in code and in no node, so a change
    to it answers to no rule a reader can open.
unbound:
- tests/test_fees.py
notes: 'Judged by 2 subagent(s), one per file; folded mechanically by trace.py --fold from the returns
  under siegard-reconcile/fees-review.returns/.

  Staged by a review over files a delivery wrote: every pair a delivery or a hand stamped was judged,
  and a pair was omitted only where a reconciliation''s judgment had cleared it at these very bytes; the
  plan''s node(s) rules/lending/late-fee-per-overdue-day were read on every file and answered for, and
  bound from nowhere here — a binding this record writes is one the trace already held.

  Candidates: 0 opened across 0 of 2 subagent(s); each return lists its own under `candidates_opened`.

  Unstated: 1 fact(s) the source states that no node holds, over 1 file(s), listed under `unstated`. They
  block no binding here and no rebind closes them — the route is the analysis that gives each fact a node.'
---

## Folded
This record was folded by `trace.py --fold` from the subagent returns under `siegard-reconcile/fees-review.returns/`, which are the evidence behind every entry above.
