---
contract_version: siegard-reconcile/11
title: Hand rename of the late fee constant in lending/fees.py
summary: The late fee constant in lending/fees.py was renamed by hand and a comment was added; the person
  states the behavior did not change and the code is correct.
said: /reconcile /tmp/rcb/full-reconcile--before-1/p files lending/fees.py target app slug fees-hand-edit
  — renamed the late fee constant in lending/fees.py by hand and added a comment; the behavior did not
  change and the code is correct
target: app
files:
- path: lending/fees.py
  change: 'nothing about the behavior: late_fee_cents() still charges 100 cents per overdue day and nothing
    for a loan returned on or before its due date; only the constant''s name and a comment changed'
nodes:
- node: rules/lending/late-fee-per-overdue-day
  conforms: true
  how: 'lending/fees.py: held at the constant FEE_CENTS_PER_OVERDUE_DAY, line 3, and the body of late_fee_cents(),
    lines 8-11 — FEE_CENTS_PER_OVERDUE_DAY = 100 / overdue_days = (loan.returned_on - loan.due_on).days
    / if overdue_days <= 0: return 0 / return overdue_days * FEE_CENTS_PER_OVERDUE_DAY'
  encoded_at:
  - lending/fees.py
restates:
- file: lending/fees.py
  where: the comment opening late_fee_cents(), line 7
  evidence: '# A loan returned after its due date pays 100 cents for each overdue day.'
  cost: the comment restates rules/lending/late-fee-per-overdue-day while the code on lines 3 and 8-11
    holds the same fact; the day the node's amount or day count changes, the code is corrected and the
    comment goes on stating the old rule as if it were current, with nothing that checks it
  node: rules/lending/late-fee-per-overdue-day
notes: 'Judged by 1 subagent(s), one per file; folded mechanically by trace.py --fold from the returns
  under siegard-reconcile/fees-hand-edit.returns/.

  Candidates: 0 opened across 0 of 1 subagent(s); each return lists its own under `candidates_opened`.

  Restates: 1 place(s) where text in the source restates a node''s fact the code holds, over 1 file(s),
  listed under `restates`. The pair conforms, so none blocks a binding — the route is removing the text,
  and reconciling the file after.'
---

## Folded
This record was folded by `trace.py --fold` from the subagent returns under `siegard-reconcile/fees-hand-edit.returns/`, which are the evidence behind every entry above.
