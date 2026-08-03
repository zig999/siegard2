---
id: "0013"
title: Keep a capability declaration beside the harness contract rather than inside it
status: accepted
contract_version: adr/1
---

# Keep a capability declaration beside the harness contract rather than inside it

## Context

`foundation/0007` requires every capability to carry a declaration and lists the twelve parts one holds.
Its **Outstanding evidence** condition 4 left one question open, because answering it wrong is expensive
in a direction that is hard to reverse: does a declaration extend `schemas/skill.json` and
`schemas/agent.json`, or is it a separate artifact that references them?

Three facts decided it, and none of them was available when the condition was written.

Both harness contracts are closed objects.
`docs/adr/0009-component-contracts-from-anthropic-documentation.md` records the reason, from pages
retrieved 2026-07-29: the harness ignores an unknown frontmatter field silently, so a misspelled `tool:`
for `tools:` ships an agent that inherits every tool. Closing the object is the only thing that catches
that, and it is the single failure mode those contracts were shaped around.

Two of the six capability classes have no frontmatter at all. A script and a template are loaded by
nothing that reads frontmatter, so a declaration that lived in frontmatter would reach four classes at
most, against a requirement that binds all six.

The repository had already answered the question twice without naming it as this question.
`src/claude/hooks/hooks.declaration.json` and the target pack declaration are both separate authored
artifacts, and the generator computes what ships from the first rather than shipping it.

## Decision

A declaration is a separate authored artifact that references the frontmatter contract of its class, is
authored under the framework source, and is not installed. `foundation/0007` R21 through R23 are the
operative rules and this record does not reproduce them.

## Consequences

`schemas/skill.json` and `schemas/agent.json` stay what ADR-0009 made them: a record of the harness's
documented constraints, closed, with every field cited. No Siegard-only field enters either, so the
silent-typo check keeps working.

The cost is two authored records of one fact. A `name` and a `description` now live in the component and
in its declaration, and nothing about separate files prevents them from disagreeing. `foundation/0007`
R22 answers that with one validator over both rather than two validators over one each, which is what
condition 4 asked for in the half still open.

A consumer cannot read a declaration. R23 keeps declarations out of the distribution, so until
`foundation/0008` says what carries the derived catalog, the readable surface a declaration exists to
provide does not reach anyone. That is recorded as owed in `foundation/0007` **Outstanding evidence**
rather than treated as delivered, and the bump it needs is blocked on a contract-naming convention this
repository does not yet have.

Extending the harness contracts was the alternative, and it was rejected on the first fact rather than
on preference: it requires relaxing `additionalProperties: false`, which reopens a failure mode a binding
decision closed. It would also have been cheaper in the one respect this decision pays for — one file per
capability, and no possibility of the two records drifting.

What would falsify this: a capability whose declaration cannot be written without duplicating most of its
frontmatter, or a validator that cannot decide agreement because the two artifacts describe the same field
at different granularities. Either would mean the overlap is larger than two fields and the separation
costs more than the closure it protects.
