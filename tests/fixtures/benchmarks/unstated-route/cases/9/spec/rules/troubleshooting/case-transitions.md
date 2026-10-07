---
type: state-machine
statement: A case moves only along the declared transitions.
subject: domain/troubleshooting/case
status: domain/troubleshooting/case-status
initial: open
terminal:
  - resolved
  - cancelled
transitions:
  - from: open
    trigger: start-investigation
    to: investigating
  - from: investigating
    trigger: resolve
    to: resolved
  - from: open
    trigger: cancel
    to: cancelled
  - from: investigating
    trigger: cancel
    to: cancelled
rejections:
  - from: open
    trigger: resolve
  - from: investigating
    trigger: start-investigation
---

## Description

The lifecycle of a case, total over its states and triggers.
