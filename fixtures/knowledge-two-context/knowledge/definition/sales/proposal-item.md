---
id: ko.definition.sales.proposal-item
type: definition
title: Proposal item
description: One priced line inside a proposal, with no identity outside the proposal.
question: What is a Proposal item?
boundary: ko.boundary.sales.proposal
ddd: value-object
attributes:
  - { name: description, type: string,  max_length: 120, required: true }
  - { name: amount,      type: decimal, precision: 12, scale: 2, required: true }
status: accepted
contract_version: knowledge-object/1
generated: { by: claude-opus-5, at: 2026-07-30T13:00:00Z }
out_of_scope:
  - how a line amount is calculated, which no knowledge object in this fixture holds
---

# Proposal item

## Answer

A proposal item is one priced line inside a proposal.
A proposal item has no meaning outside the proposal that holds the line.

## Invariants

A proposal item amount MUST be greater than zero.
