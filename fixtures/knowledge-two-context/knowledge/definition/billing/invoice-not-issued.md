---
id: ko.definition.billing.invoice-not-issued
type: definition
title: Invoice not issued
description: The domain error raised when payment is attempted on a draft invoice.
question: Which error does a draft invoice raise for a payment?
boundary: ko.boundary.billing.invoice
ddd: domain-error
attributes:
  - { name: invoice_number, type: string, max_length: 20, required: true }
status: proposed
contract_version: knowledge-object/1
generated: { by: claude-opus-5, at: 2026-07-30T13:00:00Z }
out_of_scope:
  - the trigger that issues an invoice, which is ko.lifecycle.billing.invoice
---

# Invoice not issued

## Answer

Invoice not issued is the error raised when payment is attempted on a draft invoice.

## Invariants

The error MUST carry the number of the invoice still in draft.
