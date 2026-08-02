---
id: concept.projection
type: term
title: projection
description: A human-readable artifact generated from the knowledge graph, reproducible from it and normative nowhere.
status: accepted
contract_version: concept/1
tags: [knowledge, ontology, determinism]
generated: { by: claude-opus-5, at: 2026-07-30T23:18:39Z }
sources:
  - resource: foundation/0003-knowledge-ontology-and-notation.md
    title: Represent domain knowledge as a typed ontology in an AI-first notation
    title: The term projection names the graph-derived artifact, and derived workflow state is renamed
---

# projection

A human-readable artifact generated from the [knowledge graph](knowledge-graph.md), never authored.

A projection is reproducible from the graph: regenerating it from the same graph yields the same bytes. An
artifact that can drift from the graph it came from is not a projection — it is a second authority for
knowledge the graph already holds.

A projection is never a normative source. It exists to compensate the human cost of a form chosen for
machine consumption, which is why it may repeat what the graph states and why nothing may cite it as the
home of that statement.

The set is closed. `foundation/0003-knowledge-ontology-and-notation.md` R50 limits it to the bundle `index.md`, a
glossary, and a context map, and a fourth requires a recorded case that demands it. R51 holds both
properties above.

Derived workflow state was never a projection in this repository's vocabulary, and had a term of its own.
That term has since left the bundle with the machinery that used it, so the distinction it drew no longer
has a second side — a projection is now the only thing this word covers.
