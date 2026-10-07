---
type: aggregate-root
attributes:
  - name: name
    type: string
    required: true
operations:
  - register
---

## Description

A person or organisation the business serves, told apart from every other by its own identity.
How a customer is captured or shown is not a fact of this node.

## Responsibility

Hold what the business records about one customer from its registration on.
