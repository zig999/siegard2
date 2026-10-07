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

A party the business has registered as a customer.
It is named, carries one fiscal document, may carry an email, and is at any time in one of the states customer-status declares.
What a document may be is document's to decide, and which status changes are allowed is the customer lifecycle rule's.

## Responsibility

Be the one record of a customer, under which its name, document, email and status change together.
