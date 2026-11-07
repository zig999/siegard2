---
type: policy
statement: When a reserved copy is returned, the member who reserved it MUST be notified and the copy MUST be held for that member for three calendar days.
constrains:
  - domain/lending/loan
  - domain/lending/reservation
consistency: eventual
---

## Description

This rule sets the reservation's collection deadline and notifies the reserving member when the copy comes back.
