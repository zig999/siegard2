---
id: ko.boundary.sales.proposal
type: boundary
title: Proposal aggregate
description: The consistency boundary holding a proposal and the items priced inside it.
question: What is inside the Proposal aggregate?
boundary: ko.boundary.sales
ddd: aggregate
status: accepted
contract_version: knowledge-object/1
generated: { by: claude-opus-5, at: 2026-07-30T13:00:00Z }
out_of_scope:
  - the customer a proposal is issued to, which is ko.boundary.sales.customer
---

# Proposal aggregate

## Answer

The Proposal aggregate holds a proposal and the items priced inside a proposal.
A proposal is the root of the aggregate.

## Responsibilities

Every change to an item MUST pass through the proposal.
A reference leaving the aggregate MUST be a reference by identity.
