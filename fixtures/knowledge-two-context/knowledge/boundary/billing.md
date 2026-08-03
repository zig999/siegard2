---
id: ko.boundary.billing
type: boundary
title: Billing
description: The bounded context that charges for a proposal Sales has recorded as accepted.
question: What does the Billing context own?
ddd: bounded-context
subdomain_type: supporting
owner: billing
status: accepted
contract_version: knowledge-object/1
generated: { by: claude-opus-5, at: 2026-07-30T13:00:00Z }
out_of_scope:
  - pricing a proposal, which is ko.boundary.sales
---

# Billing

## Answer

Billing owns the invoice raised for a signed contract.
Billing consumes the signed contract Sales publishes.

## Responsibilities

Billing MUST raise exactly one invoice for one signed contract.
Billing MUST NOT change the amount Sales priced.
