---
id: concept.target-pack
type: term
title: target pack
description: The distributable unit carrying one technology stack — the specialized agents and templates that produce the classes it declares.
status: proposed
contract_version: concept/1
tags: [generation, distribution, kodd]
generated: { by: claude-opus-5, at: 2026-07-30T15:26:04Z }
sources:
  - resource: specs/0004-generation-and-reproducibility.md
    title: Produce the system from knowledge, and lock what reproduces it
  - resource: specs/0008-distribution-layout.md
    title: Ship the framework as a plugin, so enabling it installs the enforcement
  - resource: specs/0012-target-pack-model.md
    title: Admit one stack at a time, and let a pack assume its technology instead of abstracting over it
---

# target pack

The distributable unit that carries one technology stack: the [specialized agents](specialized-agent.md) and
templates that produce the [artifact classes](artifact-class.md) it declares, authored under `src/claude/`
like any other component and shipped as a plugin of its own. One producer per declared class — a template
for a deterministic class, an agent for a judged one — because
`specs/0006-capability-model.md` R5 gives a specialized agent exactly one artifact class. A pack is not part of the framework [distribution](distribution.md) —
`specs/0008-distribution-layout.md` R23 and `specs/0012-target-pack-model.md` R8 make it separately
installed and separately versioned, so adding a stack needs no framework release.

A pack is where [stack knowledge](stack-knowledge.md) lives once the [knowledge base](knowledge-base.md) has
excluded it. Naming conventions, directory layout, layering, idiom, and how a reference becomes a storage
representation are the pack's business and appear in no authored artifact.

A pack declares almost nothing. Its identity, its version, and the artifact classes it produces with the
[track](generation-track.md) of each and the node types each is yielded by — and nothing else. A pack that
declared path derivation, expansion order, or naming rules would be re-authoring what its own agent knows,
which is the economy `specs/0002-knowledge-economy-principles.md` exists to protect. The node-type mapping
is the exception that proves where the line runs: it names no path and no filename, and without it nothing
model-free can work out which artifacts a knowledge object demands.

Exactly one pack is active in a governed repository. One pack is what lets a template assume its technology
instead of abstracting over it, and `.claude/rules/claude-code-authoring.md` forbids a vendor-neutral
abstraction absent an accepted requirement for one.

That a pack is framework work rather than the "architecture chosen for one downstream system" that
`CLAUDE.md` **Scope** excludes is settled; `.claude/rules/claude-code-authoring.md` **Target packs** holds
the distinction and the fixture gate. What a pack contains is still a proposal, because
`specs/0004-generation-and-reproducibility.md` is not yet accepted.
