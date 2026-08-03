---
id: ko.definition.sales.customer-proposals
type: definition
title: Customer proposals
description: The proposals currently open for one customer, read across two aggregates.
question: Which proposals are open for a customer?
boundary: ko.boundary.sales
ddd: read-model
identity: { attributes: [customer] }
attributes:
  - { name: customer,   type: ref,     target: ko.definition.sales.customer, binding: by-identity, required: true }
  - { name: proposals,  type: list,    of: ko.definition.sales.proposal, binding: by-identity, required: true }
  - { name: open_total, type: money,   required: true }
status: proposed
contract_version: knowledge-object/1
generated: { by: claude-opus-5, at: 2026-07-30T13:00:00Z }
out_of_scope:
  - the states that count as open, which is ko.lifecycle.sales.proposal
  - the acceptance of a proposal, which is ko.process.sales.proposal-approval
---

# Customer proposals

## Answer

Customer proposals lists the proposals currently open for one customer, with the sum of the open totals.
The read model spans the Customer and Proposal aggregates and owns neither.

## Invariants

Every proposal named here MUST be referenced by identity, because each one belongs to another aggregate.
The open total MUST equal the sum of the totals of the proposals named here.
