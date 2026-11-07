---
title: Lending service
summary: The area the renewal scope lands in, one Python package under lending/.
sources:
  - intake/scope.md
area:
  - lending/
modules:
  - name: loans
    path: lending/loans.py
    role: touched
conventions:
  - statement: A domain record is a frozen dataclass with typed fields.
    seen_at: lending/loans.py
must_not_duplicate:
  - what: The Loan record and its dates
    at: lending/loans.py
---

## What it is

The survey of the lending package the renewal tasks write into.

## Notes

None.
