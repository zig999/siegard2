---
id: ko.definition.billing.invoice-terminal
type: definition
title: Invoice terminal
description: The domain error raised when any trigger reaches a paid invoice.
question: Which error does a paid invoice raise for any trigger?
boundary: ko.boundary.billing.invoice
ddd: domain-error
attributes:
  - { name: invoice_number, type: string, max_length: 20, required: true }
  - { name: state,          type: enum,   lifecycle: ko.lifecycle.billing.invoice, required: true }
status: accepted
contract_version: knowledge-object/1
generated: { by: claude-opus-5, at: 2026-07-30T13:00:00Z }
out_of_scope:
  - which states are terminal, which is ko.lifecycle.billing.invoice
---

# Invoice terminal

## Answer

Invoice terminal is the error raised when any trigger reaches a paid invoice.

## Invariants

The error MUST carry the terminal state that refused the trigger.
