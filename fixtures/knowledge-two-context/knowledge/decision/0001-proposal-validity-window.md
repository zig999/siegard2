---
id: "0001"
title: Fix the proposal validity window at thirty days
status: accepted
contract_version: knowledge-decision/1
---

# Fix the proposal validity window at thirty days

## Context

A proposal carries a price that funding cost moves. An offer with no expiry is a price
guaranteed forever, and Sales cannot honour one.

## Decision

The operative rule is `ko.rule.sales.proposal-expiration`, which this record does not
restate. This ADR records why thirty days was chosen and what the choice cost.

## Consequences

Thirty days was chosen over sixty because a quarter holds one renegotiation either way,
and over fifteen because a customer approval cycle regularly exceeds two weeks.

The cost accepted: a proposal that expires during a slow approval is re-issued at the
current price, and a customer reads the re-issue as a price rise. Sales carries that
conversation rather than the knowledge base carrying a grace period.

What would falsify the decision: re-issue traffic above one proposal in five, which would
mean the window is shorter than the approval cycle it was sized against.

## Validation required before acceptance

Re-issue traffic measured over one quarter, against the one-in-five threshold this record
names.
