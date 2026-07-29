---
paths:
  - ".claude/**"
  - "CLAUDE.md"
---

# Authoring Claude Code components

This repository targets Claude Code. Do not add vendor-neutral abstractions unless an accepted
Siegard requirement calls for one.

## Where instruction content belongs

Placement determines whether a rule reaches the agent at all. These are the harness's documented
loading semantics — choose against this table, not by preference.

| Mechanism | When it loads | Use for |
|---|---|---|
| `CLAUDE.md` | every session, in full | repository-wide rules that are always relevant |
| `@path` import in `CLAUDE.md` | eagerly at launch | organization only — it does not reduce context |
| `.claude/rules/*.md` without `paths` | at launch | nothing here; it costs the same as `CLAUDE.md` |
| `.claude/rules/*.md` with `paths` | when the agent reads a matching file | invariants tied to a path |
| `.claude/skills/<name>/SKILL.md` | on demand, by description or `/name` | multi-step procedures |
| hook | at a lifecycle event, unconditionally | enforcement that must not depend on model judgment |

Two consequences to design around:

- `CLAUDE.md` and rules are context, not enforcement. The agent may not follow them. A guarantee that
  must hold regardless of model judgment belongs in a `PreToolUse` hook or a script.
- A skill loads only when invoked or matched. Do not put a rule that must always hold into a skill.

Keep `CLAUDE.md` under 200 lines; longer files reduce adherence. When it grows, move a path-scoped
invariant to `.claude/rules/` and a procedure to a skill. Do not use `@path` imports to shrink it —
imports load eagerly and change nothing.

## Component responsibilities

The split across commands, orchestrators, specialized agents, skills, hooks, and scripts is defined in
`docs/adr/0003-orchestrator-agent-separation.md`. That ADR is `proposed`, so read it as context, not as
authority — see `docs/adr/README.md`.

These two hold regardless of how that taxonomy settles:

- Grant every agent and hook the minimum tools and permissions it needs.
- Implement durable orchestration and state logic in tested scripts, not in prompt prose.

## Relying on harness behavior

When a component depends on Claude Code behavior, cite the documentation page that specifies it, in a
comment or in the component's own text. If no page specifies it, treat the behavior as unverified:
say so, and do not build a guarantee on it.
