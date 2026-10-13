> [← Glossary](../siegard-glossary.md) · Previous: [The agents](10-the-agents.md) · Next: [One complete example: a hand fix](12-one-complete-example-a-hand-fix.md)

## 11. Informal words you may meet

These words show up in conversations, session notes or commit messages. They are **not** fields
or flags of the framework; here is the official term each one stands for.

| You may hear | It means | Official term |
|---|---|---|
| **fold** | Combining the saved judge returns + premise into the record. | `trace.py --fold` |
| **refold / re-fold** | Running `--fold` again over the **same saved returns** — typically after a framework fix changed a fold rule, and before the record is committed. Possible only because the returns are kept verbatim and the fold is mechanical. It is never a hand edit of the record, and never asks the judges again. | `trace.py --fold` (again) |
| **unfold / unfolded** | Appears only as an internal name in `deliver.py`: a review whose conformance pass ran over a traced target but **folded no reconciliation record**. `deliver.py` prints a receipt for it: the other nodes bound to the reviewed files still carry old digests, and a `/reconcile` over those files closes them. | the "unreconciled review" receipt |
| **certificate** | A certification that held. | `decided_by: test` (+ `step`, `proof`) |
| **comment findings** | `restates` findings where the text is a code **comment** or docstring. | `kind: restates` |
| **emitted-text findings** | Findings about text the **running system emits** — a tool/API description, an error message, a prompt, a log line. Since 4.21.3 such text is behaviour, never `restates`: agreeing with its node it is no finding, disagreeing it is `contradicts`. (Before 4.21.3 a description restating a fact code enforced was filed `restates`, so older records may still carry such entries.) | no finding, or `kind: contradicts` |
| **unheld** | *(this one is official)* an adoption candidate no file holds. | `unheld` in the record |
| **the corpus** | All records under `siegard-reconcile/`, read together. | read by `--owed` |
| **pair** | One node + one of its files. | node-file pair |
| **clear / cleared** | The judgment found nothing against a node: it conforms and gets bound. | `conforms: true` + `encoded_at` |
| **stamp / restamp** | Writing current digests into the trace. | bind / rebind |
| **judge** | An agent delegated a judgment. | a delegation |
| **door** | A ready-to-paste invocation a report hands you. | "the invocation ready to paste" |

---
> [← Glossary](../siegard-glossary.md) · Previous: [The agents](10-the-agents.md) · Next: [One complete example: a hand fix](12-one-complete-example-a-hand-fix.md)
