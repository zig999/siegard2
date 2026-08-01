---
id: ko.rule.sales.proposal-response-time
type: rule
title: Proposal response time
description: Issuing a proposal answers within two seconds at the ninety-ninth percentile.
question: How fast must issuing a proposal answer?
boundary: ko.boundary.sales
ddd: quality-attribute
examples:
  - given: { load: nominal }
    when:  { trigger: issue }
    then:  { p99_ms: 2000, outcome: allowed }
  - given: { load: nominal }
    when:  { trigger: issue }
    then:  { p99_ms: 4200, outcome: rejected }
status: accepted
contract_version: knowledge-object/1
generated: { by: claude-opus-5, at: 2026-07-30T13:00:00Z }
out_of_scope:
  - the response time of Billing, which is recorded against ko.boundary.billing if it is recorded
  - which infrastructure delivers the budget, which is stack knowledge
depends_on: [ko.process.sales.proposal-approval]
---

# Proposal response time

## Answer

Issuing a proposal MUST answer within two seconds at the ninety-ninth percentile.
The budget covers the Sales context and no other.

## Conditions

The percentile is measured over one calendar day of nominal load.
A quality attribute spanning another context MUST be recorded against that context.
