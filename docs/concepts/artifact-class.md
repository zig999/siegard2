---
id: concept.artifact-class
type: term
title: artifact class
description: What a produced artifact is, named independently of how any technology expresses it.
status: proposed
contract_version: concept/1
tags: [generation, kodd]
generated: { by: claude-opus-5, at: 2026-07-30T15:26:04Z }
sources:
  - resource: specs/0004-generation-and-reproducibility.md
    title: Produce the system from knowledge, and lock what reproduces it
---

# artifact class

What a produced artifact *is* — a type, a persistence schema, a migration, a validator, a conformance test —
named independently of how any technology expresses it.

The vocabulary is closed and belongs to the framework, while the mapping from a node type to the classes it
yields belongs to a [target pack](target-pack.md), which declares it. That division exists because the
mapping presumes a technology and the vocabulary does not: "a definition yields a migration" is only true
where a database exists, and [stack knowledge](stack-knowledge.md) has no place in a framework-owned enum.

The mapping is declared rather than left to the pack's agent because two model-free things need to read it:
the [generation plan](generation-plan.md), which cannot work out what a knowledge object demands without it,
and the report that a node type yields nothing under the active pack. Owning a fact and declaring it are
different questions, and the pack answers both here.

An artifact class carries one thing a pack could not be trusted to supply informally: its
[generation track](generation-track.md). Whether a class is produced by expansion or by judgment decides
what a diff means, and that must be known before anything runs rather than inferred afterwards.

`specs/0004-generation-and-reproducibility.md` holds the vocabulary and the requirements.
