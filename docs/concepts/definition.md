---
id: concept.definition
type: term
title: definition
description: The knowledge object type that says what a domain concept is and which attributes it holds.
status: proposed
contract_version: concept/1
tags: [knowledge, kodd, ddd]
generated: { by: claude-opus-5, at: 2026-07-30T15:19:55Z }
sources:
  - resource: specs/0003-knowledge-ontology-and-notation.md
    title: Represent domain knowledge as a typed ontology in an AI-first notation
---

# definition

The [knowledge object](knowledge-object.md) type that answers "what is X, and what does X hold": a domain
concept together with its typed attributes and its identity.

A definition carries the DDD tactical vocabulary as a field rather than as a separate type. An entity, a
value object, an aggregate root, a read model, and a domain error are all definitions distinguished by that
field, because none of them requires a frontmatter field the others lack.

A definition is the type whose attributes must be fully typed. An attribute with a free-text type cannot be
expanded into a column or a class, so an incompletely typed definition is where a generator would guess —
which is why `specs/0003-knowledge-ontology-and-notation.md` requires the attribute type system rather than
recommending it.

A definition is not a [boundary](boundary.md): a definition says what a thing is, a boundary says what a
consistency scope contains.
