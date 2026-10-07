---
type: policy
statement: A customer's document MUST be held by no other customer.
constrains:
  - domain/customers/customer
  - domain/customers/document
consistency: immediate
---

## Description

Governs the uniqueness of a document across every registered customer, whatever the customer's status.
It does not decide whether a document is well-formed.
