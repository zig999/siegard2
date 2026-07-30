---
id: ko.definition.sales.proposal-terminal
type: definition
title: Proposal terminal
description: The domain error raised when any trigger reaches a proposal in a terminal state.
question: Which error does a terminal proposal raise for any trigger?
boundary: ko.boundary.sales.proposal
ddd: domain-error
attributes:
  - { name: proposal_number, type: string, max_length: 20, required: true }
  - { name: state,           type: enum,   lifecycle: ko.lifecycle.sales.proposal, required: true }
status: proposed
contract_version: knowledge-object/1
generated: { by: claude-opus-5, at: 2026-07-30T13:00:00Z }
out_of_scope:
  - which states are terminal, which is ko.lifecycle.sales.proposal
---

# Proposal terminal

## Answer

Proposal terminal is the error raised when any trigger reaches a proposal in a terminal state.

## Invariants

The error MUST carry the terminal state that refused the trigger.
