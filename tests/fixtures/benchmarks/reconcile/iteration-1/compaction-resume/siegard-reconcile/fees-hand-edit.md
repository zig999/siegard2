---
contract_version: siegard-reconcile/11
title: Reconcile the hand edit of lending/fees.py
summary: The late fee constant in lending/fees.py was renamed by hand and a comment added; the person
  states the behavior did not change and the code is correct.
said: renamed the late fee constant in lending/fees.py by hand and added a comment; the behavior did not
  change and the code is correct
target: app
files:
- path: lending/fees.py
  change: late_fee_cents(loan) answers 0 for a loan returned on or before its due date, and 100 cents
    for each calendar day between its due date and its return otherwise, through the constant FEE_CENTS_PER_OVERDUE_DAY
nodes:
- node: rules/lending/late-fee-per-overdue-day
  conforms: true
  how: 'lending/fees.py: held at late_fee_cents, the product of overdue_days and FEE_CENTS_PER_OVERDUE_DAY
    — return overdue_days * FEE_CENTS_PER_OVERDUE_DAY'
  encoded_at:
  - lending/fees.py
unstated:
- file: lending/fees.py
  where: late_fee_cents, the branch on overdue_days
  evidence: "if overdue_days <= 0:\n        return 0"
  cost: The fee of a loan returned on or before its due date is decided in code and in no node, so a change
    to it answers to no rule a reader can open.
restates:
- file: lending/fees.py
  where: late_fee_cents, the comment above overdue_days
  evidence: '# A loan returned after its due date pays 100 cents for each overdue day.'
  cost: The comment is a second home for the late fee rule the node holds and the code computes, so a
    change to the rule leaves it stating the old one.
  node: rules/lending/late-fee-per-overdue-day
notes: 'Judged by 1 subagent(s), one per file; folded mechanically by trace.py --fold from the returns
  under siegard-reconcile/fees-hand-edit.returns/.

  Candidates: 0 opened across 0 of 1 subagent(s); each return lists its own under `candidates_opened`.

  Unstated: 1 fact(s) the source states that no node holds, over 1 file(s), listed under `unstated`. They
  block no binding here and no rebind closes them — the route is the analysis that gives each fact a node.

  Restates: 1 place(s) where text in the source restates a node''s fact the code holds, over 1 file(s),
  listed under `restates`. The pair conforms, so none blocks a binding — the route is removing the text,
  and reconciling the file after.'
---

## Folded
This record was folded by `trace.py --fold` from the subagent returns under `siegard-reconcile/fees-hand-edit.returns/`, which are the evidence behind every entry above.
