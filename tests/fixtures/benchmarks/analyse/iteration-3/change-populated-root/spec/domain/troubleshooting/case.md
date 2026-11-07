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
  - name: reopenings
    type: reopening
    many: true
relationships:
  - target: investigation
    type: composition
    cardinality: "1"
  - target: resolution
    type: composition
    cardinality: "0..*"
operations:
  - open
  - start-investigation
  - resolve
  - cancel
  - reopen
---

## Description

A customer problem submitted to the troubleshooting process.

## Responsibility

Control the investigation from opening to resolution or cancellation, and back to investigation when a resolved case is reopened.
