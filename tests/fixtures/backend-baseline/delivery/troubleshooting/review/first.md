---
title: Troubleshooting, first review
summary: What the four passes found.
reviewed:
- src/troubleshooting/case.ts
- tests/case.spec.ts
tasks:
- task/troubleshooting/record-case
passes:
- pass: coverage
- pass: conformance
- pass: standard
  missing: no standard was named to this review
- pass: failures
  missing: no run was captured
coverage:
- criterion: Opening a case returns its case id.
  state: covered
  tests:
  - file: tests/case.spec.ts
    name: opens a case for an alert
---
## What it is
Prose for a reader.

## Notes
None.
