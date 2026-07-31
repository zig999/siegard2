---
id: "9001"
title: Record a decision under the first ADR contract, so a migration has something to carry
status: accepted
contract_version: adr/1
---

# A decision recorded under adr/1

## Context

The `adr/1` contract was replaced by `adr/2` without a migration path or a migration test, which
`.claude/rules/compatibility.md` requires of every breaking change. `docs/bootstrap.md` recorded the
debt rather than hiding it, and nothing could detect it.

Paying that debt needs a document that actually predates the bump. Every ADR in `docs/adr/` was
rewritten to declare `adr/2` when the contract moved, so none of them is evidence of anything: a
migration tested only against documents that already migrated tests nothing.

This file is that missing input. Its id is outside the range `docs/adr/` allocates, so it can never be
mistaken for a decision this repository made.

## Decision

Hold one ADR at `contract_version: adr/1` permanently, as the input the migration test consumes.

## Consequences

`schemas/adr.v1.json` stays readable for as long as this fixture references it, which is what the
**Versioning contracts** section of `.claude/rules/compatibility.md` already requires of any prior
version with a live reference.

This document is a fixture and decides nothing about the framework. It is not loaded by
`scripts/validate_adrs.py`, which reads `docs/adr/` only.
