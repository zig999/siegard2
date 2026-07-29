# Architecture decision records

An ADR records a decision that no specification defines. ADRs are normative source 2, below accepted
specifications and above schemas.

## Status vocabulary

Every ADR carries `status` in its frontmatter. The value determines whether the decision binds.

| Status | Meaning | Normative weight |
|---|---|---|
| `proposed` | The decision is recorded and argued, but nothing has exercised it | None. Binds nothing. Cite it as context, never as authority. |
| `accepted` | The decision binds; dependent artifacts must conform | Full, at precedence level 2 |
| `superseded` | Replaced by a later ADR, named in `superseded-by` | None. Kept for history and migration. |

A `proposed` ADR is not a weaker rule — it is not a rule. This distinction is what keeps design work
from silently becoming an invariant.

## Moving from proposed to accepted

A `proposed` ADR becomes `accepted` when its **Validation required before acceptance** section is
satisfied: the components it presupposes exist, and at least one fixture or test exercises the
decision. Record what satisfied it, then change the status in the same change.

Do not accept an ADR because it still seems correct. Accept it because something exercised it.

## Format

```markdown
---
id: 0001
title: <decision, stated as an outcome>
status: proposed | accepted | superseded
superseded-by: <id, only when superseded>
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
