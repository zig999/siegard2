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

## Amendment

An ADR may revise *part* of another ADR's decision while leaving the rest in force. That relation is
`amends: "<id>"` in the amending ADR's frontmatter, and it is not a status: the amended ADR stays
`accepted`, because most of what it decided still binds.

| Relation | The amended or replaced ADR | Use when |
|---|---|---|
| `amends` | stays `accepted`, keeps its other decisions | one statement is reversed or narrowed and the rest stands |
| `superseded_by` | becomes `superseded` and binds nothing | the decision is retired whole |

Two rules make an amendment honest rather than hidden:

- an amendment binds only while the amending ADR is `accepted`, so creating one is ordinary work and
  putting it into force is a maintainer's decision, exactly as for any status change;
- the amended ADR must cite the amending id in its body, at the point of the change. `make validate`
  rejects an amendment that is recorded only in frontmatter — a reader arrives at the decision, not at
  its metadata, and a reversed statement they cannot see is worse than no record at all.

`docs/concepts/amendment.md` defines the term. One ADR declares `amends`: ADR-0008 amends ADR-0004, which
reverses one sentence of ADR-0004's Consequences and leaves the rest of that decision in force. ADR-0004
stays `accepted` and cites the amending id at the point of the change, which is what `make validate`
checks. ADR-0008 is `proposed`, so the amendment records intent and does not yet bind — `CLAUDE.md` carries
the amended rule on its own authority in the meantime.

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

The frontmatter contract is `schemas/adr.v2.json`, enforced by `make validate`. Each ADR is validated
against the contract it declares, so `schemas/adr.v1.json` remains readable and an ADR still declaring
`adr/1` fails on that contract's terms rather than being misread — the mechanism
`.claude/rules/compatibility.md` requires. Quote the id: YAML reads an unquoted `0010` as octal 8, and an
unquoted `0008` as a string, so the unquoted form is neither safe nor type-stable.

```markdown
---
id: "0001"
title: <decision, stated as an outcome>
status: proposed | accepted | superseded
contract_version: adr/2
superseded_by: "<id>"   # only when superseded, and never otherwise
amends: "<id>"          # only when revising part of another ADR, which stays accepted
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
