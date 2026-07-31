---
id: concept.specification
type: term
title: specification
description: A normative document in foundation/, the highest precedence source for this repository.
status: accepted
contract_version: concept/1
tags: [governance, normative-source]
generated: { by: claude-opus-5, at: 2026-07-30T01:59:07Z }
sources:
  - resource: schemas/spec.json
    title: Siegard specification frontmatter
  - resource: docs/adr/README.md
    title: Architecture decision records
---

# specification

A normative document in `foundation/`, governing the framework Siegard builds. An [accepted](accepted.md)
specification is the highest authority `CLAUDE.md` **Where authority lives** names: it outranks an ADR, a
schema, a concept, and an implementation, and a conflict is resolved by correcting the lower source.

A specification states requirements that can be cited individually and violated observably. Its
frontmatter contract is `schemas/spec.json`; `scripts/validate_specs.py` enforces both the
frontmatter and the body's structure, including that requirement identifiers are unique and sequential
so a test, an impact artifact, or an acceptance report can cite one and mean one statement.

A `proposed` specification binds nothing, exactly as a `proposed` ADR binds nothing. Only a maintainer,
or a deterministic approval mechanism this repository defines, changes that status.

An ADR records a decision no specification defines. Where a specification and an ADR both speak to a
question, the specification is the authority and the ADR is either narrower in scope or wrong.

A specification is not a [specification delta](specification-delta.md), which is a temporary downstream
artifact produced per change request.
