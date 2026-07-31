---
paths:
  - "src/claude/**"
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

The table's paths are the paths of an *installed* component. For a component authored under
`src/claude/`, it describes where that component lands in a target repository, not its path here:
`src/claude/rules/foo.md` loads nothing in this repository, and a hook under `src/claude/` fires
downstream and never in this session. Exercise a shippable component through the generator, a fixture,
or a test — never by observing this session's behavior.

Keep `CLAUDE.md` under 200 lines; longer files reduce adherence. When it grows, move a path-scoped
invariant to `.claude/rules/` and a procedure to a skill. Do not use `@path` imports to shrink it —
imports load eagerly and change nothing.

## The two trees

`.claude/` and `src/claude/` are different trees and never mirror each other. `.claude/` configures the
agent that develops Siegard; `src/claude/` holds what Siegard ships. `CLAUDE.md` **Repository layout**
carries the table; this file carries the boundary, because the boundary matters exactly when someone is
reading or writing a file in one of the two trees.

A component that would be installed into a target repository belongs in `src/claude/` from the moment it
is first authored, and stays inert here until the generator, a fixture, or a test exercises it — never the
ambient session. That is the same rule the paragraph under **Where instruction content belongs** applies to
a component's loading semantics, stated once for the tree as a whole.

`docs/concepts/framework-source.md` defines the tree that ships. `docs/bootstrap.md` open question 4 holds
the gate that would prove the two trees stay separate in practice, and until that gate is met the
separation is a commitment rather than a checked property.

## Component responsibilities

How work divides across orchestrators, specialized agents, skills, hooks, and scripts is not yet fixed.
`docs/bootstrap.md` names the stage that decides it, and the loading table above is what constrains the
answer in the meantime.

These hold regardless of how that taxonomy settles:

- Implement durable orchestration and state logic in tested scripts, not in prompt prose.
- State each component's tool and permission grant in the component itself. The rule is
  `docs/concepts/least-privilege.md`, stated operatively in `CLAUDE.md` under **Security**; this line
  only says where the grant is written.

## Target packs

A target pack is the unit that carries one technology stack: the specialized agents and templates that
produce the artifact classes it declares. A pack is framework work, and it is not the "architecture chosen
for one downstream system" that `CLAUDE.md` **Scope** excludes — a pack serves any repository on its stack
rather than one system.

Three limits keep that distinction real:

- a pack is admitted only when a fixture exercises it, which is `CLAUDE.md` **Scope** applied rather than
  relaxed;
- what a pack may declare, and what it must leave to its agents' own knowledge of the stack, is fixed by
  `specs/0004-generation-and-reproducibility.md` once that specification is accepted. Do not restate those
  rules here, and do not give a pack a rule file of its own;
- a pack carries no business rule and no customer-specific architecture. Those stay out of scope inside a
  pack exactly as they are everywhere else.

## Relying on harness behavior

When a component depends on Claude Code behavior, cite the documentation page that specifies it, in a
comment or in the component's own text. If no page specifies it, treat the behavior as unverified:
say so, and do not build a guarantee on it.
