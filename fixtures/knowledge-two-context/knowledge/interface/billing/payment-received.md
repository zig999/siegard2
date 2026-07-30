---
id: ko.interface.billing.payment-received
type: interface
title: Payment received
description: The event Billing consumes from the payment provider when money settles.
question: What does Billing consume when a payment settles?
boundary: ko.boundary.billing
ddd: integration-event
version: "2.1.0"
schema: interface/payment-received.v2.json
ownership: consumed
status: proposed
contract_version: knowledge-object/1
generated: { by: claude-opus-5, at: 2026-07-30T13:00:00Z }
out_of_scope:
  - the invoice the payment settles, which is ko.definition.billing.invoice
---

# Payment received

## Answer

Payment received is the event Billing consumes when money settles at the provider.
The payload carries the invoice number and the settled amount.

## Semantics

A consumed interface is exempt from the version-bump discipline of this repository.
Billing MUST reject a payload naming an invoice Billing does not hold.
