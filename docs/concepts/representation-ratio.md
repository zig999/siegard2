---
id: concept.representation-ratio
type: term
title: representation ratio
description: Permanent knowledge volume measured against the source volume it produces, instrumented so representation cost stays visible.
status: accepted
contract_version: concept/1
tags: [knowledge, kodd, observability]
generated: { by: claude-opus-5, at: 2026-07-30T14:49:05Z }
sources:
  - resource: specs/0002-knowledge-economy-principles.md
    title: Hold the minimum knowledge specialized agents need to reproduce the system
---

# representation ratio

The volume of permanent knowledge in the [knowledge base](knowledge-base.md) measured against the volume
of source that knowledge produces.

It exists because "hold the minimum" is a slogan without a number. A rising ratio means the representation
is absorbing work rather than removing it: the effort of maintaining the description approaches the effort
of writing the software the description replaces, and the system stops being worth its elegance.

A rising ratio is answered by **removing** elements from the ontology, not by adding validators. Adding
enforcement to a representation that is already too large makes the representation both large and rigid.

The ratio is instrumentation, not a gate. No threshold or acceptance criterion is expressed as a ratio
figure, for the reason spec 0001 R25 gives about assertion coverage: a number that must move becomes a
target to satisfy, and satisfying it produces artifacts nobody needed.

Its unit and its useful range are undecided, because a ratio needs two generated systems before it means
anything.
