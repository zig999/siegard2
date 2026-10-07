---
type: policy
statement: No two customers hold the same document.
constrains:
  - domain/customer-registry/customer
consistency: immediate
---

## Description

The material's "CPF/CNPJ deve ser único": one fiscal document registers at most one customer.
It holds across every customer, whatever the customer's status, and it says nothing about what a surface answers when a second registration is refused.
