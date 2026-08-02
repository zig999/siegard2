---
paths:
  - "src/claude/**"
  - "dist/**"
  - "scripts/**"
---

# Building the distribution

`dist/.claude/` is what this repository produces. It is not a source tree, and nothing here is edited
by hand.

`foundation/0008` states what a distribution must be true of — the properties a consumer can check in the
tree they installed. This file states what *this* repository must do to build one. A consumer never
satisfies a rule below; the person or agent running `make dist` does.

## What ships

Everything under `src/claude/`, and nothing else. A file reaches the consumer because of where it sits,
not because a table in the generator names it. Adding a schema, scaffold, or executable to that tree
ships it; adding it anywhere else does not.

Two files in the output have no counterpart in the source, and both are computed rather than copied:
`hooks/hooks.json`, derived from the authored `hooks.declaration.json`, and `siegard-manifest.json`,
which records the assembly and therefore cannot precede it.

## Rules for the build

- Do not hand-edit a file under `dist/`. Change the source or the generator, then regenerate.
- Keep the output reproducible: the same committed source and generator version must produce a
  byte-identical tree. A difference between two runs is a defect in the generator, never an acceptable
  variation.
- Verify by regenerating into a temporary tree and comparing. Never write into the tree being checked —
  a check that repairs what it was meant to detect reports success on a defect.
- Exclude every development-only path: `foundation/`, `tests/`, `fixtures/`, `docs/`, `.claude/`, and this
  repository's own `schemas/`, `scripts/`, and `templates/`. `.claude/` configures the agent that
  develops the generator and never ships.
- Never place a secret, credential, token, or environment-specific value in the output. An absolute
  path true only on the build machine is such a value.
- Reject a hidden default: if an installed component behaves differently when a setting is absent,
  state that default in the component itself, not in the generator.
- A fixture is optional evidence and never a gate. Nothing is withheld from the distribution for want
  of one — `foundation/0005` R11, and `CLAUDE.md` **Scope**. This repository holds none, and the rule
  stays because it is what keeps their absence from being read as a reason to withhold anything.

`make dist` regenerates; `make dist-check` verifies. Reporting the first as if it were the second
reports success on a defect.
