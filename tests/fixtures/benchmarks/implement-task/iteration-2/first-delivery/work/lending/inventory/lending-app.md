---
title: Lending service
summary: The area the late-fee scope lands in, one Python package under lending/.
area:
  - lending/
modules:
  - name: loans
    path: lending/loans.py
    role: depends-on
conventions:
  - statement: A domain record is a frozen dataclass with typed fields.
    seen_at: lending/loans.py
must_not_duplicate:
  - what: The Loan record and its dates
    at: lending/loans.py
---

## What it is

The survey of the lending package the late-fee task writes into.

## Notes

None.
