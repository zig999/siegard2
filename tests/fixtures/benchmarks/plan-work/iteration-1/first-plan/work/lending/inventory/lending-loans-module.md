---
title: Lending loans module
summary: 'The area the renewal scope lands in: one dataclass module for loans under
  lending/, with a pytest suite under tests/.'
sources:
- intake/scope.md
area:
- lending/
- tests/
modules:
- name: loans
  path: lending/loans.py
  role: touched
- name: loans-tests
  path: tests/test_loans.py
  role: adjacent
conventions:
- statement: A loan is a frozen dataclass holding its dates as datetime.date values.
  seen_at: lending/loans.py
- statement: Tests import from the lending package through a conftest that puts the
    target root on sys.path.
  seen_at: tests/conftest.py
must_not_duplicate:
- what: The Loan dataclass with borrowed_on, due_on, returned_on and renewed
  at: lending/loans.py
risks:
- risk: Loan is frozen and its positional fields are constructed directly; a change
    to its field order or a required new field breaks positional construction.
  consumers:
  - tests/test_loans.py
---
## What it is
The lending package holds one module, loans.py, with a frozen Loan dataclass and no behavior.
No renewal, due-date computation or reservation exists in the tree.

## Notes
Loan already carries a renewed flag defaulting to False.
No module models a copy, a member or a reservation.
