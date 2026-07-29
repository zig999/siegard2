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
  - resource: docs/adr/0002-generated-distribution.md
    title: Ship the framework as a generated distribution
---

# distribution

The assembled release artifact under `dist/.claude/`, produced from [framework source](framework-source.md)
by a generator and copied into target repositories.

Generated output, never a source tree, and never hand-edited. Reproducible: the same committed source
must produce the same distribution.

No generator exists yet, so no authoritative distribution exists yet either.
