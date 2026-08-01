---
id: ko.lifecycle.sales.proposal
type: lifecycle
title: Proposal lifecycle
description: The legal states of a proposal and the transitions between them.
question: Which states may a proposal hold, and which transitions are legal?
boundary: ko.boundary.sales.proposal
subject: ko.definition.sales.proposal
states: [draft, issued, accepted, expired, cancelled]
initial: draft
terminal: [accepted, expired, cancelled]
transitions:
  - { from: draft,  trigger: issue,  to: issued }
  - { from: issued, trigger: accept, to: accepted, guard: ko.rule.sales.proposal-expiration }
  - { from: issued, trigger: expire, to: expired }
  - { from: draft,  trigger: cancel, to: cancelled }
  - { from: issued, trigger: cancel, to: cancelled }
rejections:
  - { from: draft,    trigger: [accept, expire], error: ko.definition.sales.proposal-not-issued }
  - { from: issued,   trigger: [issue],          error: ko.definition.sales.proposal-already-issued }
  - { from: terminal, trigger: [issue, accept, expire, cancel], error: ko.definition.sales.proposal-terminal }
status: accepted
contract_version: knowledge-object/1
generated: { by: claude-opus-5, at: 2026-07-30T13:00:00Z }
out_of_scope:
  - renewal after expiry, which no knowledge object in this fixture holds
---

# Proposal lifecycle

## Answer

A proposal moves from draft to issued, and from issued to accepted, expired, or cancelled.
A terminal state accepts no further trigger.

## State semantics

An issued proposal is visible to the customer.
An expired proposal MUST be retained for audit.
