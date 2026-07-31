---
id: concept.artifact-persistence
type: term
title: artifact persistence
description: Whether an artifact is kept in version control, recomputed from committed inputs, or discarded with the run that made it.
status: proposed
contract_version: concept/1
tags: [generation, determinism, kodd]
generated: { by: claude-opus-5, at: 2026-07-30T23:18:39Z }
sources:
  - resource: specs/0004-generation-and-reproducibility.md
    title: Produce the system from knowledge, and lock what reproduces it
---

# artifact persistence

Whether an artifact is kept in version control, recomputed from committed inputs, or discarded with the run
that produced it. One of `committed`, `claim-recorded`, or `run-scoped`.

The value is derived, not chosen. It follows from whether the artifact's body is recomputable from committed
inputs with no model involved, and from whether anything outside the run pins its identity. An artifact
recording a decision no committed input determines is `committed`; one that recomputes and whose identity a
claim pins is `claim-recorded`; one that recomputes and that nothing outside the run reads is `run-scoped`.

Persistence is not normativity and not derivation. A
[generation manifest](generation-manifest.md) is derived, committed, and normative nowhere, and a
[projection](projection.md) is derived and non-normative while still being kept. Collapsing the three axes
into one is what makes a lock look like a temporary file.

`specs/0004-generation-and-reproducibility.md` holds the rule, the assignment, and the requirements.
