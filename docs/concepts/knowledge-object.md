---
id: concept.knowledge-object
type: term
title: knowledge object
description: One durable concept of a governed repository's knowledge, stated independently of the code that implements it.
status: accepted
contract_version: concept/1
tags: [knowledge, kodd]
generated: { by: claude-opus-5, at: 2026-07-30T01:59:07Z }
sources:
  - resource: foundation/0001-knowledge-object-driven-development.md
    title: Drive every change through knowledge objects, with determinism at the boundaries
---

# knowledge object

One durable concept of a governed repository's knowledge — a domain rule, an entity, an integration
contract — stated independently of the code that implements it. It answers one question, and a second
independent question means a second knowledge object.

A knowledge object is permanent. An implementation task, a request, a plan, and evidence are temporary
and never become one. It changes when knowledge changes — a new rule, a regulation, an architectural
decision — and not because code changed.

## What it binds

Nothing, by itself. What a knowledge object binds is its level on the maturity ladder in spec 0001:
`proposed` binds nothing and enters context only; `accepted` enters the [knowledge
graph](knowledge-graph.md) and selection, and binds review; `accepted` plus an [assertion](assertion.md)
binds mechanical rejection at validation. The level is derived from the artifact, never declared
separately.

## Not a Siegard concept file

A knowledge object holds a *governed repository's* domain knowledge. A concept file in
`docs/concepts/` — this file, for instance — holds *this framework's* vocabulary. Both are markdown with
frontmatter, and confusing them puts business rules into the framework's vocabulary, which `CLAUDE.md`
places out of scope. The two contracts are separate for that reason.
