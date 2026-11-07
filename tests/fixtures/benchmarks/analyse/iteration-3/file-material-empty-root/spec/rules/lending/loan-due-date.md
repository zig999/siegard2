---
type: invariant
statement: A loan's due date MUST be fourteen calendar days after its checkout date, plus fourteen more calendar days once it is renewed.
constrains:
  - domain/lending/loan
---

## Description

This rule fixes when a loan's copy is due back.
It does not decide how many times a loan may be renewed.
