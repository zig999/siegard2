---
type: invariant
statement: An unreturned loan whose due date has passed MUST accrue a fine of BRL 1.00 for each calendar day past its due date.
constrains:
  - domain/lending/loan
---

## Description

This rule fixes the late fine ("multa por atraso") a loan owes.
