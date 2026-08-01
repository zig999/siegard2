---
id: ko.boundary.billing.invoice
type: boundary
title: Invoice aggregate
description: The consistency boundary holding an invoice raised for a signed contract.
question: What is inside the Invoice aggregate?
boundary: ko.boundary.billing
ddd: aggregate
status: accepted
contract_version: knowledge-object/1
generated: { by: claude-opus-5, at: 2026-07-30T13:00:00Z }
out_of_scope:
  - receiving a payment, which is ko.interface.billing.payment-received
---

# Invoice aggregate

## Answer

The Invoice aggregate holds an invoice and the amount charged.
An invoice is the root of the aggregate.

## Responsibilities

An invoice MUST name the signed contract that justified the charge.
