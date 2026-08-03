---
id: ko.process.billing.invoice-issue
type: process
title: Invoice issue
description: The ordered path from a signed contract to a paid invoice.
question: In which order is an invoice issued and paid?
boundary: ko.boundary.billing
ddd: use-case
steps:
  - { ko: ko.definition.billing.invoice }
  - { ko: ko.lifecycle.billing.invoice }
  - { ko: ko.rule.billing.invoice-amount }
  - { ko: ko.interface.billing.payment-received }
status: proposed
contract_version: knowledge-object/1
generated: { by: claude-opus-5, at: 2026-07-30T13:00:00Z }
out_of_scope:
  - publishing the signed contract, which is ko.process.sales.proposal-approval
---

# Invoice issue

## Answer

Issue raises the invoice, applies the issue transition, checks the amount rule, and waits for the settlement event.

## Outcomes

A settlement matching the invoice amount MUST move the invoice to paid.
A settlement failing the amount rule MUST leave the invoice issued.
