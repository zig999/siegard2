---
title: Proof for the recorded case
summary: What proves the recorded case.
implementation: sha256:61b3ee9606f8a087b0ead1bccedae7e16669fbbe00bb410dc529cc4eaee79606
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
