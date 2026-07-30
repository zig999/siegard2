---
id: ko.interface.sales.contract-signed
type: interface
title: Contract signed
description: The event Sales publishes when a proposal reaches acceptance.
question: What does Sales publish when a proposal is accepted?
boundary: ko.boundary.sales
ddd: domain-event
version: "1.0.0"
schema: interface/contract-signed.v1.json
ownership: published
status: proposed
contract_version: knowledge-object/1
generated: { by: claude-opus-5, at: 2026-07-30T13:00:00Z }
out_of_scope:
  - the invoice a consumer raises from this event, which is ko.definition.billing.invoice
depends_on: [ko.definition.sales.proposal]
---

# Contract signed

## Answer

Contract signed is the event Sales publishes when a proposal reaches acceptance.
The payload carries the proposal number, the customer code, and the total.

## Semantics

A consumer MUST treat the total as priced by Sales.
A breaking change to the payload MUST raise the declared version.
