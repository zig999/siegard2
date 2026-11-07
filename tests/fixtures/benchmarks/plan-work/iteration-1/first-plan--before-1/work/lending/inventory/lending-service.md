---
title: Lending service
summary: 'The area the renewal scope lands in: one Python package, lending, holding
  a frozen Loan record, with pytest tests beside it.'
area:
- app/
modules:
- name: loans
  path: app/lending/loans.py
  role: touched
- name: loan-tests
  path: app/tests/test_loans.py
  role: adjacent
conventions:
- statement: A domain record is a frozen dataclass whose dates are datetime.date values.
  seen_at: app/lending/loans.py
- statement: Tests import the package directly, with conftest.py placing the target
    root on sys.path.
  seen_at: app/tests/conftest.py
must_not_duplicate:
- what: The Loan record with its borrowed_on, due_on, returned_on and renewed fields
  at: app/lending/loans.py
risks:
- risk: Changing the Loan constructor's positional fields breaks the existing test
    that builds a Loan positionally.
  consumers:
  - app/tests/test_loans.py
sources:
- intake/scope.md
---

## What it is
The lending package holds one module, loans.py, defining an immutable Loan with a renewed flag that nothing yet sets.
No operation borrows, renews or returns a loan, and no reservation or copy type exists in the tree.

## Notes
None.
