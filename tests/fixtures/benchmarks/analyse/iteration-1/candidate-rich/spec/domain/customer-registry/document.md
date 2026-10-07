---
type: value-object
attributes:
  - name: kind
    type: document-kind
    required: true
  - name: number
    type: string
    required: true
---

## Description

The fiscal document a customer is registered under, either a CPF or a CNPJ.
Two documents of the same kind and number are the same document.

## Responsibility

Carry the one fiscal identification by which a customer is told apart from every other.
