---
type: policy
statement: A loan MUST NOT be renewed while its copy holds a reservation.
constrains:
  - domain/lending/loan
  - domain/lending/reservation
consistency: eventual
---

## Description

The reservation is read as the copy last recorded it.
