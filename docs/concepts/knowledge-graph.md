---
id: concept.knowledge-graph
type: term
title: knowledge graph
description: The graph of knowledge objects and their explicit relationships, derived from artifact frontmatter rather than maintained by hand.
status: accepted
contract_version: concept/1
tags: [knowledge, kodd, determinism]
generated: { by: claude-opus-5, at: 2026-07-30T01:59:07Z }
sources:
  - resource: foundation/0001-knowledge-object-driven-development.md
    title: Drive every change through knowledge objects, with determinism at the boundaries
---

# knowledge graph

The graph whose nodes are [knowledge objects](knowledge-object.md), and whose edges are the relationships
those objects declare in their own frontmatter.

It is **derived**, not authored: a script materializes it from the artifacts, and the materialized form
is never hand-edited. A hand-maintained graph drifts from the knowledge it indexes, and the drift is
invisible until a selection silently misses a node.

Two rules make traversal decidable:

- only declared relationships are edges. A relationship inferred from prose is not an edge, because two
  readings of the same paragraph produce two different graphs.
- every node has a stable identifier, and an edge naming an identifier the graph does not hold is a
  defect the materializer reports — together with orphans and cycles — rather than a gap it repairs.

The graph is what [impact analysis](impact-analysis.md) classifies against and what expansion traverses
to build a [context package](context-package.md). It holds permanent knowledge only: a request, a plan,
or evidence is never a node.
