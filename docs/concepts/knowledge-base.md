---
id: concept.knowledge-base
type: term
title: knowledge base
description: The authored set of knowledge objects a governed repository holds, distinct from the graph materialized from it.
status: accepted
contract_version: concept/1
tags: [knowledge, kodd]
generated: { by: claude-opus-5, at: 2026-07-30T14:49:05Z }
sources:
  - resource: foundation/0003-knowledge-ontology-and-notation.md
    title: Store the domain analysis as a typed ontology, and derive the graph from it
  - resource: foundation/0001-knowledge-object-driven-development.md
    title: Start every change from a recorded request, and say what it touches before touching it
---

# knowledge base

The authored set of [knowledge objects](knowledge-object.md) a governed repository holds — the files a
person or an agent writes and a maintainer accepts.

It is not the [knowledge graph](knowledge-graph.md). The base is authored and authoritative; the graph is
materialized from the base by a script and is never hand-edited. Confusing the two puts authority in a
derived artifact, which is the defect the graph's own definition guards against.

What a base is permitted to hold is decided by `foundation/0002-knowledge-economy-principles.md`, which admits
[domain knowledge](domain-knowledge.md) and excludes [stack knowledge](stack-knowledge.md). This file
defines the container; that specification holds the obligation, and stating it in both would put one rule in
two places. What the accumulation costs is the representation ratio.
