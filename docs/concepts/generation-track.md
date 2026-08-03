---
id: concept.generation-track
type: term
title: generation track
description: Whether an artifact class is produced by template expansion or by agent judgment, and therefore what guarantee it carries.
status: accepted
contract_version: concept/1
tags: [generation, determinism, kodd]
generated: { by: claude-opus-5, at: 2026-07-30T15:26:04Z }
sources:
  - resource: specs/0004-generation-and-reproducibility.md
    title: Produce the system from knowledge, and lock what reproduces it
---

# generation track

Whether an [artifact class](artifact-class.md) is produced by template expansion or by agent judgment. The
track decides what guarantee the artifact carries, which is why it is declared rather than discovered.

**Deterministic** — expansion over structured knowledge, with no model in the loop. Identical input yields
byte-identical output.

**Judged** — a [specialized agent](specialized-agent.md) authors the artifact, and the guarantee is
behavioural conformance against a suite derived from the knowledge, not identity of text.

The two are one term rather than two because they are the values of one distinction, and splitting a pair of
values into separate definitions is the representation excess
`specs/0002-knowledge-economy-principles.md` removes.

Conflating the guarantees is the reporting failure this term exists to prevent. A passing conformance suite
is not byte identity, and presenting one as the other overstates what the mechanism delivered. The share of
source on the deterministic track is the measurement that says whether the generative premise holds at all —
see [representation ratio](representation-ratio.md) for the companion measurement on the knowledge side.
