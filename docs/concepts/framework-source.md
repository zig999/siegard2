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

What `src/claude/` holds is not restated here. The count drifted twice — it said two components while
the tree held more, then kept naming a skill after that skill was removed — and a number maintained by
reading is the defect this bundle exists to avoid. The distribution manifest records what shipped, and it
is derived on every assembly.
