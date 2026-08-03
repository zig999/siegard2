---
id: concept.generation-manifest
type: term
title: generation manifest
description: The lock that records where each produced artifact went, so a later run reuses the placement instead of deciding it again.
status: accepted
contract_version: concept/1
tags: [generation, determinism, traceability, kodd]
generated: { by: claude-opus-5, at: 2026-07-30T15:26:04Z }
sources:
  - resource: foundation/0004-generation-and-reproducibility.md
    title: Produce the system from knowledge, and lock what reproduces it
---

# generation manifest

The record of what one generation produced: for each artifact, the [knowledge object](knowledge-object.md),
the [artifact class](artifact-class.md), the target path, a content hash, and the
[target pack](target-pack.md) version that produced it.

The manifest does two jobs, and the first is the one that carries the reproducibility claim.

**It locks placement.** Where a produced artifact goes is [stack knowledge](stack-knowledge.md), so the
pack decides it — and where a model makes that call it cannot be relied on to decide identically twice.
Recording the decision once and reading it thereafter makes regeneration reproducible even though the first
placement was judgment. The pattern is a dependency lockfile's: resolve once, then obey the record.

The manifest is also where the [placement decision](placement-decision.md) of a first generation lands. That
transcription is what lets the decision itself stay `run-scoped`: if both were kept, placement would have
two records that can disagree, and one of them would be a proposal wearing a lock's authority.

Moving a produced file is therefore an explicit recorded unlock, never a consequence of a later run choosing
differently. Without that rule a relocation appears in a diff as a deletion and an addition,
indistinguishable from a change in knowledge.

**It records execution**, which is what makes reverse impact a query and regenerate-and-diff decidable. It
replaces the element-granularity software graph an earlier design proposed, at a fraction of the nodes and
with no synchronization to maintain.

A manifest records and never decides. Nothing reads it for a rule.

Its [persistence](artifact-persistence.md) is `committed`, and that is not a storage preference. Placement is
the one thing no committed input determines, so a manifest regenerated per run would leave the decision to
be made again on every run — which is the failure the lock exists to prevent.
