---
id: ko.definition.billing.invoice
type: definition
title: Invoice
description: The charge raised for a signed contract Sales published.
question: What is an Invoice?
boundary: ko.boundary.billing.invoice
ddd: aggregate-root
identity: { attributes: [number] }
attributes:
  - { name: number,          type: string, max_length: 20, required: true }
  - { name: contract_number, type: string, max_length: 20, required: true }
  - { name: amount,          type: money,  required: true }
  - { name: state,           type: enum,   lifecycle: ko.lifecycle.billing.invoice, required: true }
status: proposed
contract_version: knowledge-object/1
generated: { by: claude-opus-5, at: 2026-07-30T13:00:00Z }
out_of_scope:
  - pricing the proposal the contract came from, which is ko.boundary.sales
depends_on: [ko.interface.sales.contract-signed]
---

# Invoice

## Answer

An invoice is the charge raised for one signed contract.
An invoice names the signed contract by the contract number carried in the event.

## Invariants

An invoice amount MUST equal the total the signed contract carried.
An invoice MUST name exactly one signed contract.
