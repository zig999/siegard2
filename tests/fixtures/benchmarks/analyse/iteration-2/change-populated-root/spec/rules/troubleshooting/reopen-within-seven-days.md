---
type: invariant
statement: A resolved case MUST NOT be reopened more than 7 days after its resolution.
constrains:
  - domain/troubleshooting/case
---

## Description

Bounds the window in which a customer's report that the problem came back returns a resolved case to investigation.
Whether a case in a given state may be reopened at all is the state machine's to decide, in rules/troubleshooting/case-transitions.
