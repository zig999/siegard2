---
type: entity
aggregate: case
attributes:
  - name: statement
    type: string
    required: true
  - name: evidence
    type: evidence
    many: true
---

## Description

One candidate explanation for the problem under investigation.

## Responsibility

Carry the evidence that confirms or refutes one explanation.
