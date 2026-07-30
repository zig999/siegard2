---
id: concept.ontology
type: term
title: ontology
description: The schema level of the knowledge model — which node types and edges exist, with what cardinality and meaning.
status: proposed
contract_version: concept/1
tags: [knowledge, kodd]
generated: { by: claude-opus-5, at: 2026-07-30T15:19:55Z }
sources:
  - resource: specs/0003-knowledge-ontology-and-notation.md
    title: Represent domain knowledge as a typed ontology in an AI-first notation
---

# ontology

The schema level of the knowledge model: which node types exist, which edges connect them, with what
cardinality, and what each means.

An ontology is not a [knowledge graph](knowledge-graph.md). The ontology has no instances; the graph has no
authority. The ontology is decided by a specification and expressed in a schema; the graph is materialized
from the [knowledge base](knowledge-base.md) by a script and holds the objects one repository happens to
have.

The distinction matters because cardinality is only statable at the schema level. "A definition has at most
one lifecycle" is an ontology statement; "this definition has none yet" is a graph observation. Collapsing
the two turns a missing constraint into an apparent fact about the data.

`specs/0003-knowledge-ontology-and-notation.md` fixes Siegard's ontology and forbids using the two terms
interchangeably.
