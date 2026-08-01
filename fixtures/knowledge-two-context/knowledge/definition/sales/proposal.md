---
id: ko.definition.sales.proposal
type: definition
title: Proposal
description: A priced offer issued to a customer, valid for a bounded period.
question: What is a Proposal?
boundary: ko.boundary.sales.proposal
ddd: aggregate-root
identity: { attributes: [number] }
attributes:
  - { name: number,    type: string,   max_length: 20, required: true }
  - { name: issued_at, type: datetime, required: true }
  - { name: total,     type: money,    required: true }
  - { name: state,     type: enum,     lifecycle: ko.lifecycle.sales.proposal, required: true }
  - { name: customer,  type: ref,      target: ko.definition.sales.customer, binding: by-identity, required: true }
  - { name: items,     type: list,     of: ko.definition.sales.proposal-item, binding: embedded, min_items: 1, required: true }
status: accepted
contract_version: knowledge-object/1
generated: { by: claude-opus-5, at: 2026-07-30T13:00:00Z }
out_of_scope:
  - the invoice raised after acceptance, which is ko.definition.billing.invoice
  - the states a proposal moves through, which is ko.lifecycle.sales.proposal
---

# Proposal

## Answer

A proposal is a priced offer issued to one customer.
A proposal is the root of the Proposal aggregate.

## Invariants

A proposal MUST hold at least one item.
A proposal total MUST equal the sum of the item amounts.
A proposal MUST reference exactly one customer.
