---
id: concept.amendment
type: term
title: amendment
description: A recorded revision of part of an accepted decision, leaving the rest of that decision in force.
status: proposed
contract_version: concept/1
tags: [governance, normative-source]
generated: { by: claude-opus-5, at: 2026-07-30T01:59:07Z }
sources:
  - resource: docs/adr/README.md
    title: Architecture decision records
---

# amendment

A recorded revision of part of an [accepted](accepted.md) decision, leaving the rest of that decision in
force. Mechanically: `amends: "<id>"` in the amending ADR's frontmatter, plus a citation of the amending
id in the amended ADR's body.

An amendment is not a status. The amended ADR stays `accepted`, because most of what it decided still
binds. Supersession is the other relation: it retires a decision whole, and the retired ADR binds
nothing.

Amendment exists because the alternative is worse in both directions. Superseding an ADR to reverse one
sentence drags its unrelated decisions through a restatement, and duplicated decisions diverge. Leaving
the reversal in prose alone gives `make validate` nothing to check, and a reader of the amended decision
no warning that it moved.

An amendment binds only while the amending artifact is accepted, so authoring one is ordinary work and
putting it into force is a maintainer's decision — the same restriction that governs every status change.
