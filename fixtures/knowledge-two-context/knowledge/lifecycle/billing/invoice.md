---
id: ko.lifecycle.billing.invoice
type: lifecycle
title: Invoice lifecycle
description: The legal states of an invoice and the transitions between them.
question: Which states may an invoice hold, and which transitions are legal?
boundary: ko.boundary.billing.invoice
subject: ko.definition.billing.invoice
states: [draft, issued, paid]
initial: draft
terminal: [paid]
transitions:
  - { from: draft,  trigger: issue, to: issued }
  - { from: issued, trigger: pay,   to: paid, guard: ko.rule.billing.invoice-amount }
rejections:
  - { from: draft,    trigger: [pay],        error: ko.definition.billing.invoice-not-issued }
  - { from: issued,   trigger: [issue],      error: ko.definition.billing.invoice-already-issued }
  - { from: terminal, trigger: [issue, pay], error: ko.definition.billing.invoice-terminal }
status: accepted
contract_version: knowledge-object/1
generated: { by: claude-opus-5, at: 2026-07-30T13:00:00Z }
out_of_scope:
  - refunding a paid invoice, which no knowledge object in this fixture holds
---

# Invoice lifecycle

## Answer

An invoice moves from draft to issued, and from issued to paid.
A paid invoice accepts no further trigger.

## State semantics

An issued invoice is visible to the customer.
A paid invoice MUST be retained for audit.
