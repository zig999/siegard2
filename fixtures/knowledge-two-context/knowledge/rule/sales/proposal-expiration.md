---
id: ko.rule.sales.proposal-expiration
type: rule
title: Proposal expiration
description: A proposal expires 30 days after issue and cannot be accepted afterwards.
question: When does a proposal expire?
boundary: ko.boundary.sales.proposal
ddd: invariant
expression: "now() - proposal.issued_at <= P30D"
examples:
  - given: { proposal.issued_at: "2026-07-01T09:00:00Z" }
    when:  { now: "2026-07-25T09:00:00Z", trigger: accept }
    then:  { outcome: allowed }
  - given: { proposal.issued_at: "2026-07-01T09:00:00Z" }
    when:  { now: "2026-08-05T09:00:00Z", trigger: accept }
    then:  { outcome: rejected, error: ko.definition.sales.proposal-expired }
status: proposed
contract_version: knowledge-object/1
generated: { by: claude-opus-5, at: 2026-07-30T13:00:00Z }
out_of_scope:
  - a proposal already accepted, whose acceptance is final
depends_on: [ko.definition.sales.proposal, ko.definition.sales.proposal-expired]
governed_by: [adr.0001]
---

# Proposal expiration

## Answer

A proposal expires 30 days after the proposal issue date.
An expired proposal MUST NOT be accepted.

## Conditions

The window counts calendar days from the issue date, exclusive.
A proposal with no issue date MUST be rejected before this rule is evaluated.
