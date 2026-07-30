---
id: concept.framework-source
type: term
title: framework source
description: The tree under src/claude/ holding the components Siegard ships, distinct from the development environment.
status: accepted
contract_version: concept/1
tags: [packaging, source, scope]
generated: { by: claude-opus-5, at: 2026-07-29T18:50:25Z }
sources:
  - resource: CLAUDE.md
    title: Siegard Code repository instructions
---

# framework source

The tree under `src/claude/` holding the components Siegard ships: the generator's only component
input, and the origin of every file in the [distribution](distribution.md).

Framework source is not the development environment. `.claude/` configures the agent that develops
Siegard and never ships; `src/claude/` holds what ships and is inert in this repository. A component
that would be installed into a target repository belongs in framework source from the moment it is
first authored — a [capability](capability.md) has no other origin.

`src/claude/` does not exist yet: no distributable component has been authored.
