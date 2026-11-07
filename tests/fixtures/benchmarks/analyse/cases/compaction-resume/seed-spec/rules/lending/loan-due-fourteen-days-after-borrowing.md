---
type: invariant
statement: A loan's due date MUST be fourteen calendar days after the day its copy was borrowed, until the loan is renewed.
constrains:
  - domain/lending/loan
---

## Description

Calendar days count every day, weekends and holidays included ("dias corridos" in the material).
