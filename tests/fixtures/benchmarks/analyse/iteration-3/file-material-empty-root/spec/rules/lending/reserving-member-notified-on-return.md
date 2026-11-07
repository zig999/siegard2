---
type: policy
statement: When a copy under a reservation is returned, the member holding that reservation MUST be notified.
constrains:
  - domain/lending/loan
  - domain/lending/reservation
consistency: eventual
---

## Description

This rule tells the reserving member that the copy is back.
