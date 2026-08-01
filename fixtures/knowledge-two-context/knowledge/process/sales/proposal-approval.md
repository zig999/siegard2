---
id: ko.process.sales.proposal-approval
type: process
title: Proposal approval
description: The ordered path from an issued proposal to a published signed contract.
question: In which order is a proposal approved?
boundary: ko.boundary.sales
ddd: use-case
steps:
  - { ko: ko.definition.sales.proposal }
  - { ko: ko.rule.sales.proposal-expiration }
  - { ko: ko.lifecycle.sales.proposal }
  - { ko: ko.interface.sales.contract-signed }
status: accepted
contract_version: knowledge-object/1
generated: { by: claude-opus-5, at: 2026-07-30T13:00:00Z }
out_of_scope:
  - raising the invoice, which is ko.process.billing.invoice-issue
---

# Proposal approval

## Answer

Approval reads the proposal, evaluates the expiration rule, applies the accept transition, and publishes the signed contract.

## Outcomes

An approval that passes the expiration rule MUST publish a signed contract.
An approval that fails the expiration rule MUST raise the expiry error.
