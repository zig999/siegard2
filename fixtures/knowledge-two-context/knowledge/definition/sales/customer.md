---
id: ko.definition.sales.customer
type: definition
title: Customer
description: The party a proposal is issued to.
question: What is a Customer?
boundary: ko.boundary.sales.customer
ddd: aggregate-root
aliases: [client]
identity: { attributes: [code] }
attributes:
  - { name: code, type: string, max_length: 20, required: true }
  - { name: name, type: string, max_length: 120, required: true }
status: proposed
contract_version: knowledge-object/1
generated: { by: claude-opus-5, at: 2026-07-30T13:00:00Z }
out_of_scope:
  - the proposal issued to a customer, which is ko.definition.sales.proposal
---

# Customer

## Answer

A customer is the party a proposal is issued to.
A customer is the root of the Customer aggregate.

## Invariants

A customer code MUST be unique across Sales.
