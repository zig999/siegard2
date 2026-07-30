---
id: concept.target-pack
type: term
title: target pack
description: The distributable unit carrying one technology stack — a specialized agent and the templates it expands.
status: proposed
contract_version: concept/1
tags: [generation, distribution, kodd]
generated: { by: claude-opus-5, at: 2026-07-30T15:26:04Z }
sources:
  - resource: specs/0004-generation-and-reproducibility.md
    title: Produce the system from knowledge, and lock what reproduces it
---

# target pack

The distributable unit that carries one technology stack: a [specialized agent](specialized-agent.md) and
the templates it expands, shipped together under `src/claude/` like any other component.

A pack is where [stack knowledge](stack-knowledge.md) lives once the [knowledge base](knowledge-base.md) has
excluded it. Naming conventions, directory layout, layering, idiom, and how a reference becomes a storage
representation are the pack's business and appear in no authored artifact.

A pack declares almost nothing. Its identity, its version, and the [artifact classes](artifact-class.md) it
produces with the [track](generation-track.md) of each — and nothing else. A pack that declared path
derivation, expansion order, or naming rules would be re-authoring what its own agent knows, which is the
economy `specs/0002-knowledge-economy-principles.md` exists to protect.

Exactly one pack is active in a governed repository. One pack is what lets a template assume its technology
instead of abstracting over it, and `.claude/rules/claude-code-authoring.md` forbids a vendor-neutral
abstraction absent an accepted requirement for one.

That a pack is framework work rather than the "architecture chosen for one downstream system" that
`CLAUDE.md` **Scope** excludes is settled; `.claude/rules/claude-code-authoring.md` **Target packs** holds
the distinction and the fixture gate. What a pack contains is still a proposal, because
`specs/0004-generation-and-reproducibility.md` is not yet accepted.
