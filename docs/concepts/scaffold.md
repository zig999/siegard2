---
id: concept.scaffold
type: term
title: scaffold
description: A generator that produces a conforming empty skeleton of an artifact this repository authors, distinct from a template.
status: proposed
contract_version: concept/1
tags: [tooling, contracts]
generated: { by: claude-opus-5, at: 2026-07-31T03:56:52Z }
sources:
  - resource: CLAUDE.md
    title: Repository layout
  - resource: specs/0011-template-system.md
    title: Hold a template to byte identity, and give it no way to reach outside its inputs
---

# scaffold

A generator that expands the frontmatter fields of an artifact **this repository authors** into a
skeleton conforming to that artifact's schema. Scaffolds live in `templates/`, are development tooling,
and never ship.

A scaffold is not a [template](target-pack.md). The two were one word until the inventory of what the
framework builds put them side by side, and the collision is the kind
`docs/adr/0010-projection-names-the-graph-derived-artifact.md` exists to prevent: `projection` named two
referents once already.

| | scaffold | template |
|---|---|---|
| Authority | `CLAUDE.md` **Repository layout** — "artifact generators that conform to schemas" | `specs/0011-template-system.md` R1 |
| Expands | the frontmatter of an artifact a person or an agent authors | structured [domain knowledge](domain-knowledge.md) |
| Produces | a specification, an ADR, a concept, a [knowledge object](knowledge-object.md), a component | one [artifact class](artifact-class.md) from the closed vocabulary of `specs/0004` R8 |
| Lives in | `templates/`, never distributed | a [target pack](target-pack.md), distributed as its own plugin |
| Guarantee | output validates against its schema before it is written | byte identity for identical input, no model in the loop |

The distinction is not cosmetic. `specs/0011` R2 states that a template which cannot hold byte identity
is not a weaker template — its artifact class moves to the judged track and a
[specialized agent](specialized-agent.md) produces it. A scaffold makes no such promise and owes none:
it produces a skeleton a human then fills, so there is no knowledge it could have expanded
deterministically. Applying R2 to a scaffold would retire a mechanism for failing a guarantee it never
made.

What a scaffold and a template do share is the rule that neither mints a value the caller owns. A
timestamp, an identifier, and a version come from the caller and are recorded, never invented — `specs/0011`
R5 states it for templates, and a scaffold that invented one would make the artifact it produced
irreproducible in the same way.
