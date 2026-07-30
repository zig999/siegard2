---
id: ko.definition.billing.invoice-already-issued
type: definition
title: Invoice already issued
description: The domain error raised when issue is attempted on an invoice already issued.
question: Which error does a second issue of one invoice raise?
boundary: ko.boundary.billing.invoice
ddd: domain-error
attributes:
  - { name: invoice_number, type: string, max_length: 20, required: true }
status: proposed
contract_version: knowledge-object/1
generated: { by: claude-opus-5, at: 2026-07-30T13:00:00Z }
out_of_scope:
  - paying an issued invoice, which is ko.lifecycle.billing.invoice
---

# Invoice already issued

## Answer

Invoice already issued is the error raised when issue is attempted on an invoice already issued.

## Invariants

The error MUST carry the number of the invoice issued earlier.
