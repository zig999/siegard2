---
id: ko.boundary.sales
type: boundary
title: Sales
description: The bounded context that issues priced offers and records their acceptance.
question: What does the Sales context own?
ddd: bounded-context
subdomain_type: core
owner: sales
status: accepted
contract_version: knowledge-object/1
generated: { by: claude-opus-5, at: 2026-07-30T13:00:00Z }
out_of_scope:
  - charging for an accepted proposal, which is ko.boundary.billing
context_relationships:
  - { with: ko.boundary.billing, pattern: customer-supplier }
---

# Sales

## Answer

Sales owns the proposal issued to a customer and the acceptance of a proposal.
Sales publishes an accepted proposal to other contexts as a signed contract.

## Responsibilities

Sales MUST publish a signed contract when a proposal reaches acceptance.
Sales MUST NOT compute an invoice amount.
