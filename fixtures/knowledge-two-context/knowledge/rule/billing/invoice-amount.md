---
id: ko.rule.billing.invoice-amount
type: rule
title: Invoice amount matches the contract
description: An invoice may be paid only while the amount equals the total the signed contract carried.
question: Which amount may an invoice be paid for?
boundary: ko.boundary.billing.invoice
ddd: domain-rule
expression: "invoice.amount == invoice.contract_total"
examples:
  - given: { invoice.amount: "1200.00", invoice.contract_total: "1200.00" }
    when:  { trigger: pay }
    then:  { outcome: allowed }
  - given: { invoice.amount: "1300.00", invoice.contract_total: "1200.00" }
    when:  { trigger: pay }
    then:  { outcome: rejected }
status: proposed
contract_version: knowledge-object/1
generated: { by: claude-opus-5, at: 2026-07-30T13:00:00Z }
out_of_scope:
  - how the contract total was priced, which is ko.boundary.sales
depends_on: [ko.definition.billing.invoice]
---

# Invoice amount matches the contract

## Answer

An invoice MUST be paid only for the total the signed contract carried.

## Conditions

The comparison uses the currency declared as the system default.
A rounding difference MUST be rejected rather than absorbed.
