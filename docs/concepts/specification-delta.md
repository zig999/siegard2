---
id: concept.specification-delta
type: term
title: specification delta
description: The temporary artifact describing one requested change by reference to permanent knowledge.
status: accepted
contract_version: concept/1
tags: [workflow, kodd]
generated: { by: claude-opus-5, at: 2026-07-30T01:59:07Z }
sources:
  - resource: foundation/0001-knowledge-object-driven-development.md
    title: Drive every change through knowledge objects, with determinism at the boundaries
---

# specification delta

The temporary artifact describing one requested change, in a repository Siegard governs. It states the
delta and nothing else: it references [knowledge objects](knowledge-object.md) and ADRs by identifier
rather than restating their content.

Restating knowledge inside it would create a second authority for the same rule, and the copy is the one
that goes stale. Referencing by identifier keeps the [knowledge graph](knowledge-graph.md) the single
place a rule lives, and keeps the delta small enough to read as a change.

It is temporary: consumed by implementation, then closed. It is not a [knowledge
object](knowledge-object.md) and never becomes one.

## Not a Siegard specification

A [specification](specification.md) is a normative document in this repository's `foundation/` directory,
governing the framework. A specification delta is an artifact the framework's workflow produces
downstream, per change request. They share a word in ordinary usage and are separated here because
`CLAUDE.md` requires one name per concept: a rule about "the specification" that could mean either is an
interpretation waiting to drift.
