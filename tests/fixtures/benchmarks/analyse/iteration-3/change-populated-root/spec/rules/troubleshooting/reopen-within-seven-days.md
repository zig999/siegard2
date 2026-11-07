---
type: invariant
statement: A resolved case MUST be reopened only within 7 days of its latest resolution.
expression: reopening.reopened_at <= latest(resolution.resolved_at) + 168 hours
constrains:
  - domain/troubleshooting/case
  - domain/troubleshooting/resolution
---

## Description

Bounds how long after its resolution a customer can have a case reopened.
It does not decide which states accept a reopening; rules/troubleshooting/case-transitions does.
