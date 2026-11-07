---
type: invariant
statement: A reservation's pickup deadline MUST be three calendar days after the day its copy was returned.
constrains:
  - domain/lending/reservation
---

## Description

Until the pickup deadline the copy is held for the member who reserved it.
