---
id: concept.generation-scope
type: term
title: generation scope
description: The closed, frozen set of knowledge objects one generation compiles, and part of what a reproducibility claim names.
status: accepted
contract_version: concept/1
tags: [generation, determinism, kodd]
generated: { by: claude-opus-5, at: 2026-07-30T15:26:04Z }
sources:
  - resource: specs/0004-generation-and-reproducibility.md
    title: Produce the system from knowledge, and lock what reproduces it
---

# generation scope

The closed set of [knowledge object](knowledge-object.md) ids, with content hashes, that one generation
compiles — derived by expansion from declared roots over traversed edges, then frozen.

A scope exists because nobody generates everything. A project generates a bounded context, an aggregate, a
feature, or a change, so a reproducibility claim over "the knowledge base" means nothing until the compiled
subset is named. The scope is part of the identity a claim must state.

A scope resembles a [context package](context-package.md) and differs on the axis that matters most.
A context package is [fail-soft](fail-soft.md): a member it cannot resolve becomes a recorded degradation and
resolution continues. A scope is fail-closed: a member it cannot resolve stops generation entirely.

The two therefore stay separate artifacts. Merging them would carry fail-soft into generation, and a
generation that degrades quietly produces less software than was asked for with no signal that it did.

Freezing is what makes the scope an identity rather than a query. After a scope is frozen, a change to any
member invalidates it instead of quietly altering what gets compiled.

Its [persistence](artifact-persistence.md) is `claim-recorded`: the body is not committed, and the claim
records the declared roots and the frozen content hash instead. Expansion is deterministic, so the members
recompute — and comparing a recomputed hash against the recorded one is what turns invalidation from a
statement into a check.

`specs/0004-generation-and-reproducibility.md` holds the requirements.
