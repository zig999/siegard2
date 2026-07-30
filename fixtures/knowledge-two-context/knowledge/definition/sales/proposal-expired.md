---
id: ko.definition.sales.proposal-expired
type: definition
title: Proposal expired
description: The domain error raised when acceptance is attempted after the validity window closed.
question: Which error does an expired proposal raise?
boundary: ko.boundary.sales.proposal
ddd: domain-error
attributes:
  - { name: proposal_number, type: string,   max_length: 20, required: true }
  - { name: expired_at,      type: datetime, required: true }
status: proposed
contract_version: knowledge-object/1
generated: { by: claude-opus-5, at: 2026-07-30T13:00:00Z }
out_of_scope:
  - the length of the validity window, which is ko.rule.sales.proposal-expiration
---

# Proposal expired

## Answer

Proposal expired is the error raised when acceptance is attempted after the validity window closed.

## Invariants

The error MUST carry the number of the proposal that expired.
