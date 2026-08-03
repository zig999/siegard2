---
id: ko.definition.sales.proposal-already-issued
type: definition
title: Proposal already issued
description: The domain error raised when issue is attempted on a proposal already issued.
question: Which error does a second issue of one proposal raise?
boundary: ko.boundary.sales.proposal
ddd: domain-error
attributes:
  - { name: proposal_number, type: string, max_length: 20, required: true }
status: proposed
contract_version: knowledge-object/1
generated: { by: claude-opus-5, at: 2026-07-30T13:00:00Z }
out_of_scope:
  - cancelling an issued proposal, which is ko.lifecycle.sales.proposal
---

# Proposal already issued

## Answer

Proposal already issued is the error raised when issue is attempted on a proposal already issued.

## Invariants

The error MUST carry the number of the proposal issued earlier.
