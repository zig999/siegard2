---
id: concept.context-package
type: term
title: context package
description: The manifest of identifiers and hashes naming exactly the knowledge one implementation task may read.
status: proposed
contract_version: concept/1
tags: [kodd, determinism, context]
generated: { by: claude-opus-5, at: 2026-07-30T01:59:07Z }
sources:
  - resource: specs/0001-knowledge-object-driven-development.md
    title: Drive every change through knowledge objects, with determinism at the boundaries
  - resource: reference/SIGARD_Context_Resolution_Specification_v0.1.md
    title: SIGARD Context Resolution Specification v0.1
---

# context package

The manifest of identifiers and content hashes naming exactly the knowledge one implementation task may
read. It is a manifest, not a bundle of copies: copies fork from the artifacts they duplicate, and a
hash records which version was actually read without storing a second one.

It is produced in two movements with different guarantees, which is the correction spec 0001 makes to
the v0.1 draft:

- **root selection is judgment**, and each root is recorded with the claim that justifies it. Judgment
  that is recorded can be reviewed and measured; judgment dressed as an algorithm can be neither.
- **expansion is deterministic**. The same roots, the same [knowledge graph](knowledge-graph.md), and the
  same budget produce a byte-identical manifest.

Where resolution cannot satisfy a selection rule, the package records the degradation and the workflow
continues — see [fail-soft](fail-soft.md). A recorded degradation reaches the acceptance gate, which
names it.

A context package is temporary and disposable. It is never versioned into a directory of its own: the
manifest plus the graph reproduces it, and a stored copy would be a second authority for knowledge the
graph already holds.
