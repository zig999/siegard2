---
id: concept.placement-decision
type: term
title: placement decision
description: The validated, frozen record of where a pack puts each artifact the manifest does not already lock.
status: proposed
contract_version: concept/1
tags: [generation, determinism, kodd]
generated: { by: claude-opus-5, at: 2026-07-31T03:00:10Z }
sources:
  - resource: specs/0004-generation-and-reproducibility.md
    title: Produce the system from knowledge, and lock what reproduces it
---

# placement decision

The record of where a [target pack](target-pack.md) puts each artifact the
[generation manifest](generation-manifest.md) does not already lock — validated before use, and frozen
before a [generation plan](generation-plan.md) is derived from it. Which producer inside the pack proposes a
path, and whether a deterministic class derives its own instead, is deliberately open in
`specs/0004-generation-and-reproducibility.md`.

It exists because placement is [stack knowledge](stack-knowledge.md) that
`specs/0002-knowledge-economy-principles.md` R4 keeps out of the [knowledge base](knowledge-base.md), while
the plan is derived with no model in the loop. A target path the manifest does not hold has exactly one
source, and that source is a model. Naming the artifact is what turns that from a hole in the derivation
into an input with a boundary.

It is the single judged step in an otherwise deterministic pipeline, which is why it is validated rather
than trusted: a path outside the governed repository, a class the pack does not declare, or two entries
claiming one path are rejected before any plan is derived, and never repaired.

Its [persistence](artifact-persistence.md) is `run-scoped`. That is the one refinement of the rule in
`specs/0004-generation-and-reproducibility.md`, which would otherwise make a model-produced body
`committed`: the manifest records the same paths on success and is the committed authority for them, so
keeping the decision too would give placement two records that can disagree.

No byte identity is claimed for it. Two first generations over the same knowledge may place an artifact
differently — identity begins at the second run, where the manifest is read instead.
