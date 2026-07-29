# Architecture decision records

An ADR records a decision that no specification defines. ADRs are normative source 2, below accepted
specifications and above schemas.

## Status vocabulary

Every ADR carries `status` in its frontmatter. The value determines whether the decision binds.

| Status | Meaning | Normative weight |
|---|---|---|
| `proposed` | The decision is recorded and argued, but nothing has exercised it | None. Binds nothing. Cite it as context, never as authority. |
| `accepted` | The decision binds; dependent artifacts must conform | Full, at precedence level 2 |
| `superseded` | Replaced by a later ADR, named in `superseded_by` | None. Kept for history and migration. |

A `proposed` ADR is not a weaker rule — it is not a rule. This distinction is what keeps design work
from silently becoming an invariant.

## Moving from proposed to accepted

A `proposed` ADR becomes `accepted` when its **Validation required before acceptance** section is
satisfied: the components it presupposes exist, and at least one fixture or test exercises the
decision. Record what satisfied it, then change the status in the same change.

Do not accept an ADR because it still seems correct. Accept it because something exercised it.

## Who may change a status

Whether the validation section is satisfied is a judgment about evidence, not a mechanical check, so an
agent does not decide it. An agent creates and revises `proposed` ADRs as ordinary work, and may state
that the conditions now appear satisfied. Only a maintainer, or a deterministic approval mechanism this
repository defines, changes a status to `accepted` or `superseded`.

This file states what must be true before a status changes; `CLAUDE.md` states who may apply it. The
restriction covers every artifact class carrying `status`, including `docs/concepts/`.

## Format

The frontmatter contract is `schemas/adr.v1.json`, enforced by `make validate`. Quote the id: YAML reads
an unquoted `0010` as octal 8, and an unquoted `0008` as a string, so the unquoted form is neither safe
nor type-stable.

```markdown
---
id: "0001"
title: <decision, stated as an outcome>
status: proposed | accepted | superseded
contract_version: adr/1
superseded_by: "<id>"   # only when superseded, and never otherwise
---

# <title>

## Context
What forces the decision. What breaks without one.

## Decision
The decision, stated so a reader can conform to it or violate it.

## Consequences
What this costs and what it forecloses. Include costs deliberately accepted.

## Validation required before acceptance
(proposed only) What must exist or pass for this to bind.
```

## Naming

`docs/adr/<4-digit-id>-<kebab-case-title>.md`. Ids are sequential and never reused.
