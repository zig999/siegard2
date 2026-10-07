---
type: value-object
attributes:
  - name: kind
    type: evidence-type
    required: true
  - name: value
    type: string
    required: true
  - name: collected_at
    type: datetime
    required: true
---

## Description

One collected fact supporting or refuting a hypothesis. Where a piece of evidence cites
a source, citations are by name and never by identifier.

## Responsibility

None.
