---
id: "0002"
title: Ship the framework as a generated distribution under dist/.claude/
status: proposed
contract_version: adr/1
---

# Ship the framework as a generated distribution under `dist/.claude/`

## Context

The framework's product is an installable set of Claude Code components. Target repositories need a
tree they can copy in. This repository additionally holds specifications, tests, fixtures, and docs
that must not reach a target repository.

Two candidate models: treat `.claude/` as both source and shippable tree, or assemble a separate
distribution from source.

## Decision

Assemble the distribution under `dist/.claude/` from framework source using a generator. `dist/` is a
release artifact, not a source tree: reproducible from committed source, never hand-edited, and free of
source-only paths and environment-specific values.

Where that framework source lives is decided by ADR-0006, not here. This ADR governs only how the
distribution is produced from it.

## Consequences

- A clean boundary between what the framework develops with and what it ships.
- A generator becomes a required component, with its own tests, before the distribution can be trusted.
- Two trees exist for the same components, so drift is possible whenever the generator is out of date.
  Regeneration must be part of every change that touches distribution inputs.
- Cost accepted: no shippable output at all until the generator exists.

## Validation required before acceptance

This ADR is currently unenforceable — no generator exists, so `dist/` cannot be produced. The rule
"do not hand-edit generated artifacts" would be violated by the first commit that created `dist/` by
hand. It binds nothing until:

1. a generator exists in `scripts/` and `make dist` runs it;
2. running it twice from the same source produces identical output;
3. a test asserts that no source-only path (`specs/`, `tests/`, `fixtures/`, `docs/`) appears in the
   output;
4. a test asserts no secrets or environment-specific values appear in the output.

Until then, do not create `dist/` by hand to make this ADR look satisfied.
