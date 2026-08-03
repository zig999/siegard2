---
id: concept.process
type: term
title: process
description: The knowledge object type holding an ordered sequence of steps that reference other knowledge objects by id.
status: accepted
contract_version: concept/1
tags: [knowledge, kodd, ddd]
generated: { by: claude-opus-5, at: 2026-07-30T15:19:55Z }
sources:
  - resource: foundation/0003-knowledge-ontology-and-notation.md
    title: Represent domain knowledge as a typed ontology in an AI-first notation
---

# process

The [knowledge object](knowledge-object.md) type that answers "in which order, and with what outcome": a
domain service, a saga or process manager, or an application use case.

A process exists as a type because **order is knowledge that its parts do not contain**. A sequence of
steps can be read off no [definition](definition.md), [rule](rule.md), or [interface](interface.md), so a
composition of those objects loses the one fact a process carries.

A process references its steps by id and restates none of their content. A step that repeats what its
target says creates a second copy of a rule, and the copy is the one that decays.

A process is not a [lifecycle](lifecycle.md). A lifecycle says which transitions are legal for one thing; a
process says in what order work happens across several. `foundation/0003-knowledge-ontology-and-notation.md`
holds the requirements.
