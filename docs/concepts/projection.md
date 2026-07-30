---
id: concept.projection
type: term
title: projection
description: Current workflow state derived by replaying the event log, not stored independently of it.
status: accepted
contract_version: concept/1
tags: [determinism, state]
generated: { by: claude-opus-5, at: 2026-07-29T16:33:28Z }
sources:
  - resource: CLAUDE.md
    title: Siegard Code repository instructions
---

# projection

Current workflow state derived by reading the [event log](event-log.md), not stored independently of
it.

A projection is reproducible: replaying the same events must yield the same state. If state can drift
from the events that produced it, it is not a projection — it is a second source of truth.
