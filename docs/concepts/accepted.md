---
id: concept.accepted
type: term
title: accepted
description: The status of a specification or ADR whose decision binds.
status: accepted
contract_version: concept/1
tags: [governance, normative-source]
generated: { by: claude-opus-5, at: 2026-07-29T16:33:28Z }
sources:
  - resource: schemas/spec.json
    title: Specification frontmatter contract
    title: Architecture decision records
---

# accepted

The status of a specification or ADR whose decision binds. Mechanically: `status: accepted` in the
artifact's frontmatter.

An artifact with `status: proposed` records a decision under consideration and binds nothing — it
carries no normative weight in the precedence order. A `proposed` artifact is not a weaker rule; it is
not a rule.

The vocabulary is `proposed | accepted | superseded`, and it is closed: `schemas/spec.json` encodes it
as an enum. Moving away from `proposed` is a maintainer's act or that of a deterministic approval
mechanism this repository defines — never an agent's, and never a side effect of the artifact being
written.
