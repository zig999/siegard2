---
id: ko.rule.sales.proposal-validity
type: rule
title: Proposal validity
description: The retired sixty-day validity window, replaced by the thirty-day expiration rule.
question: How long was a proposal valid before the window was shortened?
boundary: ko.boundary.sales.proposal
ddd: invariant
expression: "now() - proposal.issued_at <= P60D"
status: superseded
superseded_by: ko.rule.sales.proposal-expiration
contract_version: knowledge-object/1
generated: { by: claude-opus-5, at: 2026-07-30T13:00:00Z }
out_of_scope:
  - the window in force now, which is ko.rule.sales.proposal-expiration
depends_on: [ko.definition.sales.proposal]
governed_by: [adr.0001]
---

# Proposal validity

## Answer

A proposal was valid for 60 days after the proposal issue date.
This rule is retained for history and binds nothing.

## Conditions

A proposal issued before the window was shortened MUST be read against this rule.
