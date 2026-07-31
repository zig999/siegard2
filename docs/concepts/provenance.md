---
id: concept.provenance
type: term
title: provenance
description: The recorded origin of a material decision, sufficient to reproduce it.
status: accepted
contract_version: concept/1
tags: [traceability, determinism]
generated: { by: claude-opus-5, at: 2026-07-29T16:33:28Z }
sources:
  - resource: .claude/rules/contracts.md
    title: Inter-agent artifact contracts
  - resource: docs/adr/0005-okf-derived-concept-model.md
    title: Base the concept model on OKF
---

# provenance

The recorded origin of a material decision: which inputs, evidence, actor, and
[contract version](contract-version.md) produced it. Enough to reproduce the decision without asking
the agent that made it.

In a concept file, provenance is carried in frontmatter as `generated: { by, at }` for authorship,
`sources` for the materials the concept derives from, and `verified` for later confirmation events.
Those three field names come from OKF v0.2, whose provenance model Siegard adopted rather than
inventing its own — see `schemas/concept.json`.
