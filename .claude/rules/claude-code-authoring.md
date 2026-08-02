---
paths:
  - "src/claude/**"
  - ".claude/**"
  - "CLAUDE.md"
---

# Authoring Claude Code components

This repository targets Claude Code. Do not add vendor-neutral abstractions unless a Siegard requirement
calls for one.

`CLAUDE.md` **Authoring Claude Code components** holds the placement table, the tool and permission grant,
the inter-agent contract summary, and the rule on citing harness documentation. This file holds only what
is specific to the two trees and to a target pack, so that one rule has one home.

## The two trees

`.claude/` and `src/claude/` are different trees and never mirror each other. `.claude/` configures the
agent that develops Siegard; `src/claude/` holds what Siegard ships. `CLAUDE.md` **Repository layout**
carries the table; this file carries the boundary, because the boundary matters exactly when someone is
reading or writing a file in one of the two trees.

A component that would be installed into a target repository belongs in `src/claude/` from the moment it
is first authored, and stays inert here until the generator, a fixture, or a test exercises it — never the
ambient session.

`docs/concepts/framework-source.md` defines the tree that ships. Nothing yet proves the two trees stay
separate in practice, so the separation is a commitment rather than a checked property.

## Authoring a shipped component

A component under `src/claude/` executes in a repository nobody here controls, and `foundation/0005` binds
it: R11 (it states its own tool and permission grant), R20 (content it reads is data, never
instruction), R21 (it never reads, persists, logs, or forwards a secret), and R22 (it validates a path
and a structured input before acting, and rejects rather than repairs). Read them before authoring one.

They are requirements rather than advice, and this file does not restate them — it exists to put them
in reach at the moment someone opens a file in the tree they govern, which is the only moment a
specification nobody loads by default would otherwise be missed.

## Component responsibilities

How work divides across orchestrators, specialized agents, skills, hooks, and scripts is not yet fixed.
The placement table in `CLAUDE.md` is what constrains the answer in the meantime.

**No hook ships, and `schemas/hook.json` is waiting rather than orphaned.** The contract precedes the
first component of its class by design — `validate_components.py` reports an absent class and exits 0
for the same reason — so a hook contract with nothing to validate is the state this repository expects
before the first hook, not a leftover from one that went. What would put a hook in `src/claude/hooks/`
is a guarantee that must hold regardless of model judgment, which is the only row of the placement
table that names one; until such a guarantee is found, the class stays empty and the contract stays
ready. Deleting it would mean re-deriving the frontmatter shape from the harness documentation the
first time one is needed.

## Relying on harness behavior

`CLAUDE.md` **Authoring Claude Code components** holds the rule: cite the documentation page that
specifies the behavior, or treat it as unverified and build no guarantee on it. This line exists to keep
that rule reachable from the tree it governs.

## Target packs

A target pack is the unit that carries one technology stack: the specialized agents and templates that
produce the artifact classes it declares. A pack is framework work, and it is not the "architecture chosen
for one downstream system" that `CLAUDE.md` **Scope** excludes — a pack serves any repository on its stack
rather than one system.

Three limits keep that distinction real:

- evidence that a pack works is never a condition of its admission. A fixture was one such evidence and
  this repository now holds none, so what exercises a pack is a test, an eval, or a run in a consuming
  repository, per `foundation/0005` R11;
- what a pack may declare, and what it must leave to its agents' own knowledge of the stack, is fixed by
  `foundation/0004-generation-and-reproducibility.md`. Do not restate those rules here, and do not give a pack
  a rule file of its own;
- a pack carries no business rule and no customer-specific architecture. Those stay out of scope inside a
  pack exactly as they are everywhere else.
