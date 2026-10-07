---
type: aggregate-root
attributes:
  - name: id
    type: string
    required: true
  - name: raised_at
    type: datetime
    required: true
---

## Description

One anomaly detected on a watched system.

## Responsibility

Carry what was detected until somebody acts on it.
