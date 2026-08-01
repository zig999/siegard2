---
id: concept.knowledge-intake-plan
type: term
title: knowledge intake plan
description: The validated classification of received domain material into the ontology, naming what each construct becomes and what it is missing.
status: accepted
contract_version: concept/1
tags: [ontology, ingestion, ddd, determinism]
generated: { by: claude-opus-5, at: 2026-07-31T19:00:00Z }
sources:
  - resource: foundation/0003-knowledge-ontology-and-notation.md
    title: Represent domain knowledge as a typed ontology in an AI-first notation
---

# knowledge intake plan

The validated classification of domain material a repository received into the
[ontology](ontology.md), produced before any [knowledge object](knowledge-object.md) is authored. For
each construct in the source material it names the node type the construct becomes, its `ddd` value,
the [boundary](boundary.md) it will belong to, the identifier it will take, and every required fact
the source material does not supply.

It exists because the mapping is judgment and the authoring is not. Deciding that a construct is an
aggregate root rather than an entity, or a policy rather than an invariant, is reading meaning out of
prose; writing the file that records that decision is mechanical once the decision is made. Splitting
the two puts the judgment in one validated artifact a reviewer can disagree with, ahead of any file
being written.

It is a plan and not an authority. The `ddd` value an entry carries is checked against the node type
when the object is authored, by the contract that governs a knowledge object — this artifact records
what was decided, and never becomes a second home for the per-type vocabulary.

## Gaps are the expected content, not a failure

Domain material arriving from analysis is generatively incomplete by construction: it carries
attributes and relationships, and it does not carry the retrieval question, the declared out-of-scope,
the type parameters, or the identity strategy the ontology requires. An intake plan names each of
those per entry.

Naming them is the whole point. Nothing downstream may supply a domain fact the source did not state —
see [generative completeness](generative-completeness.md) — so an intake plan that reported no gaps
over material that has them would have invented the difference.

A construct the ontology's mapping has no home for is recorded as unmapped rather than forced into the
nearest type. The mapping is closed, and a construct with no entry in it is not recorded until the
mapping names its home.

## Provenance travels with it

A knowledge object derived from material that already existed is born `proposed` and records the source
it was read from, and a maintainer promotes it. The intake plan carries that source so the objects
authored from it can record it — see [provenance](provenance.md). Deriving knowledge from an existing
artifact cannot canonize a defect as a rule, which is why the promotion is a decision and not a step.
