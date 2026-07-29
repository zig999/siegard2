---
id: "0001"
title: Derive workflow state from an append-only event log
status: proposed
contract_version: adr/1
---

# Derive workflow state from an append-only event log

## Context

Workflow state that lives in the conversation is lost, truncated, or silently rewritten. Claude Code
compacts context, auto memory reflects what was true when written, and neither is a durable record.
A framework whose product is orchestration cannot keep its control state there.

Two candidate models: store current state directly and mutate it, or append facts and derive state
from them.

## Decision

Persist workflow facts as an append-only event log outside the conversation. Derive current state as a
projection over that log rather than storing it independently. Replaying the same events must yield the
same state.

Transition guards read projected state and must be deterministic and testable — decidable by a script
or hook, not by model judgment.

## Consequences

- Workflow history becomes reproducible and auditable; a decision can be replayed from its inputs.
- Every state question becomes a projection to define and test, which is more work than reading a
  mutable record.
- Event schemas become persisted contracts. Changing one incompatibly invalidates recorded history, so
  events are among the most expensive artifacts in the framework to get wrong — see
  `.claude/rules/compatibility.md`.
- Costs accepted: higher authoring cost per state question, and a migration burden on every event
  schema change.

## Validation required before acceptance

This decision presupposes components that do not exist. It binds nothing until:

1. one event schema exists in `schemas/` with a `contract_version`;
2. one projection derives state by replaying events, with a test asserting that replay is
   deterministic;
3. one transition guard reads projected state and is covered by a test for both outcomes;
4. a fixture in `fixtures/` exercises the loop end to end.

If building the thin path in `docs/bootstrap.md` shows a mutable record is sufficient for the
workflows the framework actually runs, reject this ADR instead of accepting it.
