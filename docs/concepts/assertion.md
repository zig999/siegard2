---
id: concept.assertion
type: term
title: assertion
description: A mechanical check that rejects an implementation violating one specific knowledge object.
status: accepted
contract_version: concept/1
tags: [kodd, determinism, validation]
generated: { by: claude-opus-5, at: 2026-07-30T01:59:07Z }
sources:
  - resource: specs/0001-knowledge-object-driven-development.md
    title: Drive every change through knowledge objects, with determinism at the boundaries
---

# assertion

A mechanical check that rejects an implementation violating one specific [knowledge
object](knowledge-object.md). It is what raises a knowledge object to level 2 of the maturity ladder in
spec 0001, where the object stops binding review and starts binding rejection.

An assertion is **never required** to author or to accept a knowledge object. Requiring one at authoring
time taxes every rule to guard the few that are actually violated, and a rule too expensive to follow
gets ignored — the failure mode `.claude/rules/contracts.md` guards against by tiering the schema
requirement instead of applying it universally.

Promotion is demand-pulled, by a recorded trigger: a validation failure traced to the object, a
production incident attributed to the rule, a citation by a `regulatory` change request, a violation that
review caught, or a maintainer designating the object critical. Assertions then accumulate over exactly
the rules that are violated in practice, which is where they pay for themselves.

Assertion coverage is observability. No gate, threshold, or acceptance criterion is expressed as a
coverage figure: a number that must rise becomes a target to satisfy, and satisfying it produces
assertions nobody needed.

Where an impacted knowledge object carries no assertion, acceptance rests on independent review and says
so — see [fail-soft](fail-soft.md).
