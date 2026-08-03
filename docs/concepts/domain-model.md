---
id: concept.domain-model
type: term
title: domain model
description: The DDD analysis of a request, in DDD's own vocabulary, separating what the request stated from what the modeler decided.
status: accepted
contract_version: concept/1
tags: [ddd, ingestion, provenance]
generated: { by: claude-opus-5, at: 2026-07-31T22:15:00Z }
sources:
  - resource: foundation/0003-knowledge-ontology-and-notation.md
    title: Represent domain knowledge as a typed ontology in an AI-first notation
---

# domain model

The result of analysing a request in DDD's own vocabulary — subdomains, bounded contexts and their
relationships, aggregates, entities and value objects, invariants and policies, lifecycles, published and
consumed interfaces, and the processes that span them. It is produced before anything is normalized into
the [ontology](ontology.md) and before any [knowledge object](knowledge-object.md) exists.

It is the design, not the record. A domain model states what the system should be; a
[knowledge base](knowledge-base.md) holds what a repository has decided it is. The two are separated by
two steps that do no designing: a [knowledge intake plan](knowledge-intake-plan.md) classifies each
construct into a node type, and authoring writes the object.

The vocabularies are why the steps are separate. A domain model speaks DDD, where an aggregate and an
entity are different kinds of thing. The ontology collapses that catalogue into six node types and moves
the DDD word to a field. Normalizing is mechanical once the modelling is done, and conflating the two
would put design judgment in the same capability as classification.

## It is the one artifact whose content is invented

Everywhere else in this framework, a model supplying a fact nobody stated is the defect: generation may
not supply a domain fact the knowledge base does not hold, ingestion reports a gap rather than filling it,
and authoring blocks rather than guessing an attribute. Here, modelling *is* the work — a request
describes a problem, and deciding the aggregates, the boundaries, and the invariants is what the analysis
produces.

That makes one distinction load-bearing. Every element records whether it came from the request or from
the modeler, and an element the modeler decided carries the reasoning that decided it. Without that, a
design choice is indistinguishable from a stated requirement, and everything downstream treats the two as
the same kind of fact — including a maintainer deciding whether to accept it.

## Refusing is part of modelling

A request that does not say whether an order may be partly cancelled does not authorize inventing the
answer; it authorizes asking. A domain model therefore records open questions as well as elements, and
what it considered and left out. Absence cannot be inferred from silence — the same reason a knowledge
object declares what it excludes.
