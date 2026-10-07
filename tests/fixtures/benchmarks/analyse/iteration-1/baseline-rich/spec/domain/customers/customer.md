---
type: aggregate-root
attributes:
  - name: id
    type: customer-id
    required: true
  - name: name
    type: string
    required: true
  - name: document
    type: document
    required: true
  - name: email
    type: string
    required: false
  - name: status
    type: customer-status
    required: true
operations:
  - register
  - activate
  - deactivate
---

## Description

A person or company the business does business with, registered under a name and a document.
Its status says whether the customer is currently active.

## Responsibility

Be the one record the business holds for a customer.
