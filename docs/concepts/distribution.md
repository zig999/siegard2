---
id: concept.distribution
type: term
title: distribution
description: The assembled release artifact under dist/.claude/, produced from framework source.
status: accepted
contract_version: concept/1
tags: [packaging, generated]
generated: { by: claude-opus-5, at: 2026-07-29T16:33:28Z }
sources:
  - resource: .claude/rules/distribution.md
    title: Generated distribution
  - resource: CLAUDE.md
    title: Siegard Code repository instructions
---

# distribution

The assembled release artifact under `dist/.claude/`, produced from [framework source](framework-source.md)
by a generator and installed into target repositories as a Claude Code plugin: enabling it installs every
[capability](capability.md) it carries, and rewrites no file the consumer maintains. What an installation
records about itself is the [distribution manifest](distribution-manifest.md).

Generated output, never a source tree, and never hand-edited. Reproducible: the same committed source
must produce the same distribution.

No generator exists yet, so no authoritative distribution exists yet either.
