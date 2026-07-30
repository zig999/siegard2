---
id: concept.boundary
type: term
title: boundary
description: The knowledge object type holding a scope — a bounded context or an aggregate — whose membership is derived rather than listed.
status: proposed
contract_version: concept/1
tags: [knowledge, kodd, ddd]
generated: { by: claude-opus-5, at: 2026-07-30T15:19:55Z }
sources:
  - resource: specs/0003-knowledge-ontology-and-notation.md
    title: Represent domain knowledge as a typed ontology in an AI-first notation
---

# boundary

The [knowledge object](knowledge-object.md) type that answers "what is the scope, and who owns it": a DDD
bounded context or an aggregate.

A boundary is a composition, which every other knowledge object type is not. What keeps it from becoming a
second copy of facts its members already hold is that **membership is derived**: each object declares the
one boundary it belongs to, and the boundary never lists its members. A hand-maintained membership list
drifts from the objects it indexes, and the drift is invisible until a selection silently misses one.

A boundary carries two things nothing else does. A bounded context declares its subdomain classification —
core, supporting, or generic — which is where the strategic analysis survives without a `subdomain` type.
And a bounded context declares its relationships to other contexts using DDD's context-map patterns, which
is what makes an anti-corruption layer or a conformist relationship a recorded fact rather than a diagram.

A boundary is also the unit of scope for selection and for generation, which is what makes the partition
worth its cost. `specs/0003-knowledge-ontology-and-notation.md` holds the requirements.
