---
id: concept.notation
type: term
title: notation
description: How a fact is stored — the envelope, the fence, the body sections and the identifier arithmetic — as distinct from the vocabulary of kinds written in it.
status: accepted
contract_version: concept/1
tags: [knowledge, ontology]
generated: { by: claude-opus-5, at: 2026-08-02T11:40:00Z }
sources:
  - resource: foundation/0003-knowledge-ontology-and-notation.md
    title: Represent domain knowledge as a typed ontology in an AI-first notation
  - resource: docs/adr/0025-one-vocabulary-written-once-where-it-is-read.md
    title: Let the analysis write the knowledge, and stop converting one vocabulary into another
---

# notation

How a fact is stored: the frontmatter fence, the envelope every object carries whatever it is, the two
body sections, and the arithmetic that makes an identifier and a path computable from each other.

It is not the [ontology](ontology.md). The ontology decides which kinds exist and what each demands of
its own content; the notation decides the form all of them are written in.
`foundation/0003-knowledge-ontology-and-notation.md` has held both since it was written — its title
names the two and its sections keep them apart — and what conflated them was the schema, where one file
carried the envelope and one vocabulary together.

## What belongs to it

The envelope, which is the set of fields an object carries because it is an object and not because of
what it is: its identifier and title, where it came from and who wrote it, whether the fact was stated
or decided, what it excludes, what it lacks. `schemas/knowledge-notation.json` states that set once,
and `scripts/check_notation_agreement.py` holds every profile to carrying it.

The measurement that made the separation worth stating: two profiles shipped for a time, and stripped
of their descriptions they differed in four places. Every one of the four was about whether a fact was
demanded *yet* — none was about what a kind is.

## Why it is stated rather than referenced

Composing an envelope across files is what a JSON Schema reference is for, and a shipped boundary
validator loads its schema standalone. Under the version this distribution declares, an unknown remote
reference is resolved by fetching it, and a consumer deciding whether an object is valid must not reach
the network to do so. So the envelope is written into each profile and a check is what keeps the copies
from drifting — the same bargain `schemas/contract-versions.json` makes for a constraint digest.
