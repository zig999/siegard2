---
type: state-machine
statement: A customer moves between active and inactive only along the declared transitions.
subject: domain/customers/customer
status: domain/customers/customer-status
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

Governs which status a customer holds when registered and how it changes afterwards.
It does not decide who may activate or deactivate a customer.
