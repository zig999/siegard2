---
id: ko.definition.sales.proposal-not-issued
type: definition
title: Proposal not issued
description: The domain error raised when a draft proposal receives a trigger that requires issue.
question: Which error does a draft proposal raise for a trigger requiring issue?
boundary: ko.boundary.sales.proposal
ddd: domain-error
attributes:
  - { name: proposal_number, type: string, max_length: 20, required: true }
status: accepted
contract_version: knowledge-object/1
generated: { by: claude-opus-5, at: 2026-07-30T13:00:00Z }
out_of_scope:
  - the trigger that issues a proposal, which is ko.lifecycle.sales.proposal
---

# Proposal not issued

## Answer

Proposal not issued is the error raised when a draft proposal receives a trigger that requires issue.

## Invariants

The error MUST carry the number of the proposal still in draft.
