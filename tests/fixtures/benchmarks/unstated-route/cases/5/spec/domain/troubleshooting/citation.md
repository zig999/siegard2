---
type: value-object
attributes:
  - name: name
    type: string
    required: true
relationships:
  - target: diagnostic-capability
    type: reference
    cardinality: "1"
---

## Description

A reference from a piece of evidence to one output of a diagnostic capability, by the output's name.

## Responsibility

None.
