---
target: backend
title: Proof for the recorded case
summary: What proves the recorded case.
implementation: sha256:f45b0f00b34342fffa4dfc4516c2aa641cc6ae21d16b13456391796a68ac94bf
tests:
- file: tests/case.spec.ts
  name: opens a case for an alert
  proves: Opening a case returns its case id.
  fails_when: the module answers with anything but the stored case id
---
## What it is
Prose for a reader.

## Notes
None.
