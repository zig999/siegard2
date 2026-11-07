---
contract_version: siegard-reconcile/11
title: Hand edit to the late fee constant in lending/fees.py
summary: The person renamed the late fee constant in lending/fees.py by hand and added a comment, and
  states that the behavior did not change and that the code is correct.
said: /reconcile /tmp/rcs/full-reconcile/p files lending/fees.py target app slug fees-hand-edit — renamed
  the late fee constant in lending/fees.py by hand and added a comment; the behavior did not change and
  the code is correct
target: app
files:
- path: lending/fees.py
  change: 'nothing in its behavior, as the person states it: the late fee constant is renamed and a comment
    is added, and late_fee_cents() answers as it did before the edit'
nodes:
- node: rules/lending/late-fee-per-overdue-day
  conforms: true
  how: 'lending/fees.py: held at the constant FEE_CENTS_PER_OVERDUE_DAY, line 3, and the overdue branch
    of late_fee_cents(), lines 8-11 — FEE_CENTS_PER_OVERDUE_DAY = 100 / overdue_days = (loan.returned_on
    - loan.due_on).days / if overdue_days <= 0: return 0 / return overdue_days * FEE_CENTS_PER_OVERDUE_DAY'
  encoded_at:
  - lending/fees.py
restates:
- file: lending/fees.py
  where: the comment inside late_fee_cents(), line 7
  evidence: '# A loan returned after its due date pays 100 cents for each overdue day.'
  cost: the comment states the late-fee rule a second time beside the code that holds it; the day the
    constant or the node changes and the comment does not, a reader has two statements of the fee and
    no way to tell which was decided
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
