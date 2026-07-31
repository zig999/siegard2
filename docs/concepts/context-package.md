---
id: concept.context-package
type: term
title: context package
description: The manifest of identifiers and hashes naming exactly the knowledge one run of context resolution puts in scope.
status: accepted
contract_version: concept/1
tags: [kodd, determinism, context]
generated: { by: claude-opus-5, at: 2026-07-30T01:59:07Z }
sources:
  - resource: foundation/0001-knowledge-object-driven-development.md
    title: Drive every change through knowledge objects, with determinism at the boundaries
  - resource: foundation/0009-context-assembly.md
    title: Fix the context package as a contract, and measure whether resolution earns its place
---

# context package

The manifest of identifiers and content hashes naming exactly the knowledge one run of context resolution
puts in scope. It is a manifest, not a bundle of copies: copies fork from the artifacts they duplicate, and
a hash records which version was actually read without storing a second one.

It is produced in two movements with different guarantees, which is the correction spec 0001 makes to
the v0.1 draft:

- **root selection is judgment**, and each root is recorded with the claim that justifies it. Judgment
  that is recorded can be reviewed and measured; judgment dressed as an algorithm can be neither.
- **expansion is deterministic**. The same roots, the same [knowledge graph](knowledge-graph.md), and the
  same budget produce a byte-identical manifest.

Where resolution cannot satisfy a selection rule, the package records the degradation and the workflow
continues — see [fail-soft](fail-soft.md). A recorded degradation reaches the acceptance gate, which
names it.

The degradations are a list, and they are not the stop reason. One traversal can lose a root, meet a cycle,
and then run out of budget; it stops on one of the three and records all of them, because the gate that
reads the package is owed what happened rather than what happened last —
`foundation/0009-context-assembly.md` R15 and R16 hold the two vocabularies and how they line up.

A context package is never committed. Its [artifact persistence](artifact-persistence.md) is
`claim-recorded` under `foundation/0009-context-assembly.md` R13: the roots, the graph, the budget, and the
expansion's [contract version](contract-version.md) reproduce it, so it recomputes, while the hashes and the
recorded run identity are what a later decision is traced back through. A stored copy would be a second
authority for knowledge the graph already holds.
