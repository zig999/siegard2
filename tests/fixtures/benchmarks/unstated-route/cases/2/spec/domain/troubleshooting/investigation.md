---
type: entity
aggregate: case
attributes:
  - name: started_at
    type: datetime
    required: true
relationships:
  - target: hypothesis
    type: composition
    cardinality: "0..*"
---

## Description

The diagnostic work performed inside one case.

## Responsibility

Hold the hypotheses raised while diagnosing the case.
