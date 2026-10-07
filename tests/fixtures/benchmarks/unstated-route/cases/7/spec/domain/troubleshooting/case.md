---
type: aggregate-root
attributes:
  - name: id
    type: case-id
    required: true
  - name: status
    type: case-status
    required: true
  - name: opened_at
    type: datetime
    required: true
  - name: resolved_at
    type: datetime
relationships:
  - target: investigation
    type: composition
    cardinality: "1"
  - target: resolution
    type: composition
    cardinality: "0..1"
operations:
  - open
  - start-investigation
  - resolve
  - cancel
---

## Description

A customer problem submitted to the troubleshooting process.

## Responsibility

Control the investigation from opening to resolution or cancellation.
