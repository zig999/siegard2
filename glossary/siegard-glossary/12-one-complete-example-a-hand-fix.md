> [← Glossary](../siegard-glossary.md) · Previous: [Informal words you may meet](11-informal-words-you-may-meet.md) · Next: [Alphabetical index](13-alphabetical-index.md)

## 12. One complete example: a hand fix

**The situation.** During an incident, someone added a guard to `src/billing/raise.ts` so an order
cannot get two invoices, and committed it. The behaviour is correct.

**1. Something notices.** A CI runs:

```
$ trace.py --check backend
backend/src/billing/raise.ts: the file changed without a rebind — 1 binding(s): rules/sales/invoice-immutable
...
1 code over 1 file(s): …
```

**2. You invoke the route**, naming the file set, project root and a new slug:

```
/siegard:reconcile  file set: src/billing/raise.ts   project root: .   slug: hand-fix-invoicing
```

**3. Stage.** The skill runs:

```sh
trace.py --stage backend specification hand-fix-invoicing /tmp/ws src/billing/raise.ts
```

The workspace now holds `manifest.json`, `packs/src__billing__raise.ts.md` (the text of
`rules/sales/invoice-immutable`), and `candidates.txt`; the empty folder
`siegard-reconcile/hand-fix-invoicing.returns/` exists.

**4. Judge.** One `siegard:specification-conformance-reviewer` reads the file against its pack. It
returns (saved verbatim as `siegard-reconcile/hand-fix-invoicing.returns/src__billing__raise.ts.yaml`):

```yaml
findings:
  - where: the guard added to raise(), line 12
    evidence: |-
      if (order.invoices.length >= 1) return existing
    cost: |-
      the at-most-one-invoice rule lives only here
    node: rules/sales/invoice-immutable
    kind: contradicts
read:
  - node: rules/sales/invoice-immutable
    held_at: nowhere
    evidence: |-
      the rule governs modification of a raised invoice; the guard states a cap no node holds
candidates_opened:
  - rules/sales/invoice-immutable
```

**5. Fold.** The skill writes the premise ("added by hand during an incident; correct") and runs
`trace.py --fold …`. The record says `conforms: false`, `observed_at: [src/billing/raise.ts]`.
`trace.py --reconciliation` passes.

**6. Bind.** `trace.py --bind-record … --workspace /tmp/ws` binds nothing (no node has
`encoded_at`) and its receipt says so.

**7. Report.** Two doors, and the skill chooses neither:
- **The code is right, the specification is behind** → `/analyse` with the finding as material,
  so a node gains "an order carries at most one invoice"; then `/reconcile` again over the same
  file under a new slug.
- **The specification is right, the code is wrong** → `/plan-work` corrective increment.

**8. Later.** `trace.py --owed backend` keeps listing the finding until a record clears the pair.

Had the only problem been a comment — say `// an order may only have one invoice` above code
that already enforces a rule node — the judge would have filed `kind: restates`, the node would
have bound, and the report would have handed the comment route: delete the comment, commit,
`/reconcile` that file under a new slug. Had it instead been the **error message** the system
returns, saying the same thing as the node, there would have been no finding at all: that is
behaviour agreeing with the node.

---
> [← Glossary](../siegard-glossary.md) · Previous: [Informal words you may meet](11-informal-words-you-may-meet.md) · Next: [Alphabetical index](13-alphabetical-index.md)
