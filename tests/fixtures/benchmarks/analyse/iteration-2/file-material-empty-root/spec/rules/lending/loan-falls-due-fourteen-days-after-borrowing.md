---
type: invariant
statement: A loan that has not been renewed MUST fall due fourteen calendar days after the day its copy was borrowed.
constrains:
  - domain/lending/loan
---

## Description

This rule sets a loan's first due date; a renewal moves it.
