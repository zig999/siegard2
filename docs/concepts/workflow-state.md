---
id: concept.workflow-state
type: term
title: workflow state
description: Current state of a workflow, derived from the record of what happened rather than stored independently of it.
status: accepted
contract_version: concept/1
tags: [determinism, state]
generated: { by: claude-opus-5, at: 2026-07-30T23:18:39Z }
sources:
  - resource: CLAUDE.md
    title: Siegard Code repository instructions
  - resource: specs/0001-knowledge-object-driven-development.md
    title: Drive every change through knowledge objects, with determinism at the boundaries
  - resource: docs/adr/0010-projection-names-the-graph-derived-artifact.md
    title: The term projection names the graph-derived artifact, and derived workflow state is renamed
---

# workflow state

Current state of a workflow, derived by reading the [event log](event-log.md) rather than stored
independently of it.

Derivation is reproducible: reading the same records yields the same state. If state can drift from the
records that produced it, it is not derived state — it is a second source of truth.

`CLAUDE.md` under **Determinism and state** requires workflow state to be persisted outside the
conversation, and [event log](event-log.md) holds why conversation history is not that record. Which
persistence model records it is not decided, so the derivation above names the candidate rather than a
settled mechanism — see `docs/bootstrap.md`.

`projection` names the graph-derived artifact and not this one.
`docs/adr/0010-projection-names-the-graph-derived-artifact.md` records why the two are kept apart.
