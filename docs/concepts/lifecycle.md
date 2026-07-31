---
id: concept.lifecycle
type: term
title: lifecycle
description: The knowledge object type holding a definition's legal states and the total transition table between them.
status: accepted
contract_version: concept/1
tags: [knowledge, kodd, ddd, determinism]
generated: { by: claude-opus-5, at: 2026-07-30T15:19:55Z }
sources:
  - resource: foundation/0003-knowledge-ontology-and-notation.md
    title: Represent domain knowledge as a typed ontology in an AI-first notation
---

# lifecycle

The [knowledge object](knowledge-object.md) type that answers "which states may this thing hold, and which
transitions are legal": the state set of one [definition](definition.md), together with the transitions and
the explicit rejections between them.

A lifecycle exists as its own type because no set of independent [rules](rule.md) can state *these are all
the transitions*. Decomposition loses completeness, and a transition table that cannot be checked for
completeness is where a generator invents behaviour. What earns the type is not the states but the
**totality** requirement: every pairing of a state with a trigger is either a transition or a declared
rejection.

A lifecycle is the authority for its state set. An attribute holding that state references the lifecycle by
id and does not repeat the values, so the states have one home.

At most one lifecycle describes a given definition. Two would leave no single state set to generate from.
`foundation/0003-knowledge-ontology-and-notation.md` holds the totality, reachability, and cardinality
requirements.
