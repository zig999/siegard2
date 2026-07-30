---
id: concept.rule
type: term
title: rule
description: The knowledge object type that states one falsifiable condition, and the only type an assertion can bind to.
status: proposed
contract_version: concept/1
tags: [knowledge, kodd, ddd, validation]
generated: { by: claude-opus-5, at: 2026-07-30T15:19:55Z }
sources:
  - resource: specs/0003-knowledge-ontology-and-notation.md
    title: Represent domain knowledge as a typed ontology in an AI-first notation
---

# rule

The [knowledge object](knowledge-object.md) type that answers "under which condition does what hold": an
invariant, a business rule, a policy, a specification-pattern predicate, or a quality attribute.

A rule collapses four DDD constructs and one non-functional category into one type, because splitting them
would produce no check that a single type does not already enable. What distinguishes them is a field.

A rule is the type that carries mechanical force. An [assertion](assertion.md) binds to a rule and to
nothing else, which is what raises that rule to the level of the maturity ladder where an implementation is
rejected rather than reviewed.

A rule must be expressible or exemplified. A rule stated only in prose can enter an agent's context but
cannot become a validator or a test, so `specs/0003-knowledge-ontology-and-notation.md` requires one of the
two structured forms. Why a rule was decided belongs to an ADR and never to the rule, per
[operative-rule](operative-rule.md).
