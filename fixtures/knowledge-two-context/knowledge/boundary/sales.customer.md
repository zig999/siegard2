---
id: ko.boundary.sales.customer
type: boundary
title: Customer aggregate
description: The consistency boundary holding the party a proposal is issued to.
question: What is inside the Customer aggregate?
boundary: ko.boundary.sales
ddd: aggregate
status: accepted
contract_version: knowledge-object/1
generated: { by: claude-opus-5, at: 2026-07-30T13:00:00Z }
out_of_scope:
  - the proposal issued to a customer, which is ko.boundary.sales.proposal
---

# Customer aggregate

## Answer

The Customer aggregate holds the party a proposal is issued to.
A customer exists independently of any proposal.

## Responsibilities

A proposal MUST reference a customer by identity.
