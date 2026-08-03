# Architecture decision records

An ADR records a decision that no specification defines. ADRs are normative source 2, below accepted
specifications and above schemas.

## Status vocabulary

Every ADR carries `status` in its frontmatter. The value determines whether the decision binds.

| Status | Meaning | Normative weight |
|---|---|---|
| `proposed` | The decision is recorded and argued, but nothing has exercised it | None. Binds nothing. Cite it as context, never as authority. |
| `accepted` | The decision binds; dependent artifacts must conform | Full, at precedence level 2 |
| `superseded` | Replaced by a later ADR, which this one names in its prose | None. Kept for history and migration. |

A `proposed` ADR is not a weaker rule — it is not a rule. This distinction is what keeps design work
from silently becoming an invariant.

## Changing a status

No artifact needs approval to take effect — `CLAUDE.md` **Golden rule** states that, and it covers every
artifact class carrying `status`, concepts included. An ADR in `docs/adr/` is followed; a concept in
`docs/concepts/` is respected. Neither waits behind a gate.

`proposed` remains available for a decision an author wants recorded and argued while explicitly not yet
in force, and it carries the **Validation required before acceptance** section stating what would put it
there. Use it when that distinction is real. Do not use it as a holding pen: an ADR written to be followed
is written `accepted`.

## Revising and retiring a decision

Neither relation is structured. `superseded_by` and `amends` were removed on 2026-07-31 by maintainer
decision, as ceremony this repository does not need for a set this size.

An ADR that revises part of another states so in its own prose and cites the id it revises; the revised
ADR stays `accepted`, because most of what it decided still binds. An ADR retired whole takes
`status: superseded` and names its replacement in prose. No validator resolves either target, so a
citation that goes nowhere is now a reading error rather than a build failure.

## What belongs in an ADR, and what does not

An ADR records what a decision cost, not the rule it produced. The operative rule — the imperative an
agent follows while working — is held by `CLAUDE.md`, a specification, a rule file, or a schema. The ADR
holds the alternative that was rejected, the cost deliberately accepted, and what would falsify the
decision. That content has no other home. The imperative already has one.

So `## Decision` names the operative authority and cites it, and does not repeat it. Two copies of a rule
diverge, and the copy in the ADR is the one nobody is reading while they author.

`scripts/validate_adrs.py` enforces this: it rejects a line in `## Decision` whose similarity to a line in
`CLAUDE.md` or `.claude/rules/*.md` reaches 0.65. To reproduce an operative rule deliberately — quoting the
exact words a decision reverses, for instance — mark it as a blockquote, which the check exempts. A
quotation a reader can see is not a second authority.

Two limits, named rather than solved: the check reads `## Decision` only, because `## Context` legitimately
describes rules that already exist, so a restatement moved into `## Consequences` is not caught; and
similarity is textual, so a paraphrase passes. It bounds the failure rather than closing it.

## Format

The frontmatter contract is `schemas/adr.v1.json`, enforced by `make validate`. It is the only ADR
contract: a maintainer decided on 2026-07-31 that this repository does not manage ADR versions, so a
change to that schema is made in place and recorded rather than carried as a second version. Quote the
id: YAML reads an unquoted `0010` as octal 8, and an unquoted `0008` as a string, so the unquoted form is
neither safe nor type-stable.

```markdown
---
id: "0001"
title: <decision, stated as an outcome>
status: proposed | accepted | superseded
contract_version: adr/1
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
