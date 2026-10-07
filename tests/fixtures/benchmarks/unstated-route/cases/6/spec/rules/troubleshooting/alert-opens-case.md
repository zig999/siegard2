---
type: policy
statement: An alert unresolved for 24 hours MUST open a case.
constrains:
  - domain/monitoring/alert
  - domain/troubleshooting/case
consistency: eventual
---

## Description

Stale alerts converge into cases; the two contexts need not agree in one transaction.
