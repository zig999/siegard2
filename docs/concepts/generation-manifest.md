---
id: concept.generation-manifest
type: term
title: generation manifest
description: The lock that records where each produced artifact went, so a later run reuses the placement instead of deciding it again.
status: proposed
contract_version: concept/1
tags: [generation, determinism, traceability, kodd]
generated: { by: claude-opus-5, at: 2026-07-30T15:26:04Z }
sources:
  - resource: specs/0004-generation-and-reproducibility.md
    title: Produce the system from knowledge, and lock what reproduces it
---

# generation manifest

The record of what one generation produced: for each artifact, the [knowledge object](knowledge-object.md),
the [artifact class](artifact-class.md), the target path, a content hash, and the
[target pack](target-pack.md) version that produced it.

The manifest does two jobs, and the first is the one that carries the reproducibility claim.

**It locks placement.** Where a produced artifact goes is [stack knowledge](stack-knowledge.md), so a
specialized agent decides it — and an agent is a model, which cannot be relied on to decide identically
twice. Recording the decision once and reading it thereafter makes regeneration reproducible even though
the first placement was judgment. The pattern is a dependency lockfile's: resolve once, then obey the record.

Moving a produced file is therefore an explicit recorded unlock, never a consequence of an agent choosing
differently later. Without that rule a relocation appears in a diff as a deletion and an addition,
indistinguishable from a change in knowledge.

**It records execution**, which is what makes reverse impact a query and regenerate-and-diff decidable. It
replaces the element-granularity software graph an earlier design proposed, at a fraction of the nodes and
with no synchronization to maintain.

A manifest records and never decides. Nothing reads it for a rule.
