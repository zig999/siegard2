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
  - resource: docs/adr/0003-orchestrator-agent-separation.md
    title: Separate orchestration from specialized agent work
---

# specialized agent

An agent with one declared role and the minimum tools that role requires.

Used for context separation, tool restriction, or work that genuinely requires model judgment. Work
that can be decided mechanically belongs in a hook or a script instead.

The component taxonomy this term belongs to is recorded in ADR-0003, which is `proposed` — see
[accepted](accepted.md).
