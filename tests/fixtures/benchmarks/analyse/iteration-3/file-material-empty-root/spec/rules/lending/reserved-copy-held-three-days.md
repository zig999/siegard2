---
type: invariant
statement: A returned copy under a reservation MUST stay available to the reserving member for three calendar days after that member is notified.
constrains:
  - domain/lending/reservation
---

## Description

This rule bounds how long a returned copy waits for the member who reserved it.
It does not decide what happens to the reservation once the three days pass.
