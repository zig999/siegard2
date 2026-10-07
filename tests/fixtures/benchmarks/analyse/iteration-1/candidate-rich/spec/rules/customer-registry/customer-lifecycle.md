---
type: state-machine
statement: A customer moves between active and inactive only along the declared transitions.
subject: domain/customer-registry/customer
status: domain/customer-registry/customer-status
initial: active
transitions:
  - from: active
    trigger: deactivate
    to: inactive
  - from: inactive
    trigger: activate
    to: active
rejections:
  - from: active
    trigger: activate
  - from: inactive
    trigger: deactivate
---

## Description

A customer is active when registered, is deactivated into inactive, and is activated back into active.
Neither state is final, and a trigger that would leave a customer in the state it already holds is rejected.
