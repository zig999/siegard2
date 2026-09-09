---
target: backend
title: Record an opened case
summary: The entry point that persists an opened case.
task: sha256:fd8b6fdbd9585f0ebde1b6556b85954fb4c200fd03a9752367484953337fde76
files:
- path: src/troubleshooting/case.ts
  effect: holds the case aggregate and its status vocabulary
criteria:
- criterion: Opening a case returns its case id.
  met: true
  how: the constructor takes the id and the module answers with it
nodes:
- node: domain/troubleshooting/case
  encoded_at:
  - src/troubleshooting/case.ts
  how: the case's identity and status vocabulary are the shape this module holds
---
## What it is
Prose for a reader.

## Notes
None.
