---
id: concept.specialized-agent
type: term
title: specialized agent
description: An agent with one declared role and the minimum tools that role requires.
status: accepted
contract_version: concept/1
tags: [orchestration, agents]
generated: { by: claude-opus-5, at: 2026-07-29T16:33:28Z }
sources:
  - resource: CLAUDE.md
    title: Siegard Code repository instructions
---

# specialized agent

An agent with one declared role and the minimum tools that role requires.

Used for context separation, tool restriction, or work that genuinely requires model judgment. Work
that can be decided mechanically belongs in a hook or a script instead.

The component classes this term belongs to are not yet fixed. `CLAUDE.md` under **Authority placement**
requires one authoritative definition per concept, which constrains how the classes may divide work
without settling what they are; `docs/bootstrap.md` names the stage that decides it.
