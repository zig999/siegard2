---
id: concept.skill
type: term
title: skill
description: A distributable procedure or knowledge unit at src/claude/skills/<name>/SKILL.md, invocable as /name.
status: accepted
contract_version: concept/1
tags: [component, framework-source]
generated: { by: claude-opus-5, at: 2026-07-29T20:54:56Z }
sources:
  - resource: docs/adr/0009-component-contracts-from-anthropic-documentation.md
    title: Derive component contracts from Anthropic's documented constraints
  - resource: https://code.claude.com/docs/en/skills
    title: Extend Claude with skills (retrieved 2026-07-29)
---

# skill

A distributable procedure or knowledge unit shipped from
[framework source](framework-source.md) as `src/claude/skills/<name>/SKILL.md`, loaded on demand by
description match or invoked as `/name`. The frontmatter contract is `schemas/skill.v1.json`.

There is no separate command class: Claude Code merged custom commands into skills, and Siegard
ships only the skill form. A user-invocable entry point is a skill; whether the model may also
invoke it is the skill's own frontmatter decision.

A skill is instruction content, not enforcement. A guarantee that must hold regardless of model
judgment belongs in a hook or a script, never in a skill.
