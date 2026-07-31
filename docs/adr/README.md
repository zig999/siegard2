# Architecture decision records

An ADR records a decision that no specification defines. An accepted ADR binds: a dependent artifact must
conform to it. `CLAUDE.md` **Where authority lives** carries the order and is the authority for it — a
specification, then an accepted ADR, then a concept, then a schema, then code and tests, then documentation.

**Settled 2026-07-31, by a maintainer.** This file and `CLAUDE.md` had contradicted each other: this file
said an accepted ADR binds, while `CLAUDE.md` classified `docs/adr/` as "rationale, never a rule" and left
an ADR out of the precedence order altogether. The binding reading was adopted and `CLAUDE.md` was changed
to match, which is why the order above is cited rather than restated here. What survives of the older
reading is the part that was always right and is now the whole of what **What belongs in an ADR** governs:
the decision binds, and the operative rule still lives elsewhere.

An earlier version of this paragraph placed an ADR at "normative source 2" on a numbered scale of normative
sources. No such scale was ever defined in this repository — it was cited by four files and defined by
none — so it is removed rather than invented, and the order above names its sources instead of numbering
them.

## Status vocabulary

Every ADR carries `status` in its frontmatter. The value determines whether the decision binds.

| Status | Meaning | Normative weight |
|---|---|---|
| `proposed` | The decision is recorded and argued, but nothing has exercised it | None. Binds nothing. Cite it as context, never as authority. |
| `accepted` | The decision binds; dependent artifacts must conform | Full: a dependent artifact must conform, and the decision outranks a schema |
| `superseded` | Replaced by a later ADR, which this one names in its prose | None. Kept for history and migration. |

A `proposed` ADR is not a weaker rule — it is not a rule. This distinction is what keeps design work
from silently becoming an invariant.

## Changing a status

No artifact needs approval to take effect — `CLAUDE.md` **Golden rule: this file** states that, and it covers every
artifact class carrying `status`, concepts included. An ADR in `docs/adr/` is followed; a concept in
`docs/concepts/` is respected. Neither waits behind a gate.

`proposed` remains available for a decision an author wants recorded and argued while explicitly not yet
in force, and it carries the **Validation required before acceptance** section stating what would put it
there. Use it when that distinction is real. Do not use it as a holding pen: an ADR written to be followed
is written `accepted`.

## Revising and retiring a decision

Neither relation is structured. Both are ceremony this repository does not need for a set this size.

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

The frontmatter contract is `schemas/adr.json`, enforced by `make validate`. It is the only ADR
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
