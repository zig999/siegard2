---
id: "0010"
title: The term projection names the graph-derived artifact, and derived workflow state is renamed
status: accepted
contract_version: adr/2
---

# The term projection names the graph-derived artifact, and derived workflow state is renamed

## Context

`projection` named two different things at once, and both were `accepted`.

`specs/0003-knowledge-ontology-and-notation.md` R50 and R51 use it for the three artifacts generated from the
knowledge graph — the bundle `index.md`, a glossary, and a context map — and require each to be reproducible
from the graph and normative nowhere. `docs/concepts/projection.md` defined it as current workflow state
derived by replaying an event log. The two differ in source of record, in subject, and in what
reproducibility means for each, so this was not one concept described twice.

The collision has a history worth recording, because it explains how two accepted artifacts disagreed without
anyone editing either. `docs/adr/0001-event-sourced-workflow-state.md` recorded the event-sourced design and
was one of the five ADRs removed once their operative rules were held by `CLAUDE.md` alone. The vocabulary it
introduced stayed in the bundle, re-sourced to `CLAUDE.md`, and `specs/0003` later took the same word for a
different object. A concept outliving the decision that minted it is how a bundle drifts while every
individual file still validates.

Two asymmetries decided which referent kept the word.

Precedence: `specs/0003` is an accepted specification at normative source 1, and the concept bundle is source
3. `CLAUDE.md` **Conflict protocol** resolves the highest-level source first, and `CLAUDE.md` **Authority
placement** corrects the concept rather than the specification.

Mechanism: `scripts/project_knowledge.py`, `tests/test_projections.py`, three generated files under
`fixtures/knowledge-two-context/knowledge/`, and a check inside `make validate` all depend on the graph
meaning. The persistence model the other meaning describes is open question 1 in `docs/bootstrap.md`, and
`docs/concepts/event-log.md` states that the append-only log is one candidate rather than a decision.
Renaming the enforced side to accommodate the unimplemented one would have inverted which artifact carried
risk.

## Decision

`projection` names the graph-derived artifact. `docs/concepts/projection.md` defines it, and
`specs/0003-knowledge-ontology-and-notation.md` R50 and R51 govern it.

Derived workflow state is `workflow state`, defined by `docs/concepts/workflow-state.md`. That is the name
`CLAUDE.md` **Determinism and state** and `specs/0001-knowledge-object-driven-development.md` R8 already use
for it, so the rename adopts an existing term rather than minting one.

A maintainer chose this on 2026-07-30, among the three options recorded below.

## Consequences

Three options were on the table.

The one taken assigns `projection` to the graph meaning and renames the other. Its cost is five edits on the
unenforced side: `docs/concepts/transition-guard.md`, `.claude/rules/compatibility.md`, and three places in
`docs/bootstrap.md`. It leaves R50, R51, `scripts/project_knowledge.py`, `tests/test_projections.py`, and the
generated fixture headers untouched.

The second would have kept `projection` for derived workflow state and renamed the three generated artifacts
in `specs/0003`. It was rejected on both grounds above: it edits an accepted specification at source 1 to
accommodate a concept at source 3, and it changes the side that has executing code and a check in
`make validate`.

The third would have generalized `projection` to the property both uses share — derived from a source of
record, reproducible from it, never a second source of truth — with two named instances beneath it. It was
rejected because a definition broad enough to cover both stops deciding which artifacts are permitted, which
is what R50 exists to do, and `specs/0002-knowledge-economy-principles.md` R2 removes an element that
neither generates nor verifies.

One cost is accepted with open eyes. Event-sourcing literature calls derived state a projection, so if the
persistence model in open question 1 is eventually built on an event log, this repository's vocabulary will
diverge from the usual usage of the people building it. The alternative was worse: a term that means one
thing in a specification and another in a rule file is not a vocabulary at all, and the graph meaning is the
one with a validator behind it today.

What would falsify this decision: an event-sourced design whose component contracts or schemas cannot avoid
the word `projection` for derived state without becoming unreadable to their implementers. If that happens,
revisit rather than paper over it — the third option becomes cheaper once the second referent has a mechanism.

## What satisfied acceptance

All four conditions this record stated are met, and a maintainer accepted it on 2026-07-30:

1. `docs/concepts/projection.md` carries the graph meaning with `specs/0003-knowledge-ontology-and-notation.md`
   in its `sources`, and `docs/concepts/workflow-state.md` carries the retired definition with a row in
   `docs/concepts/index.md`. `make validate` passes over 45 concepts.
2. Every artifact that used the term for derived workflow state names `workflow state` instead:
   `docs/concepts/transition-guard.md`, `.claude/rules/compatibility.md`, three places in `docs/bootstrap.md`,
   and the Definitions table of `specs/0001-knowledge-object-driven-development.md`, which had listed a term
   its body never used.
3. Every artifact that uses the term for the graph-derived artifact is unchanged: R47, R49, R50 and R51,
   `scripts/project_knowledge.py`, `tests/test_projections.py`, `schemas/knowledge-graph.v1.json`, the three
   generated files under `fixtures/knowledge-two-context/knowledge/`, and the enforcement row at
   `docs/bootstrap.md` line 99.
4. `make test` passes 87 tests, which is what shows the rename did not disturb the side that has executing
   code — the asymmetry this decision rests on.

Acceptance changes one thing beyond this record's own status. `docs/concepts/workflow-state.md` was created
carrying `accepted`, on the reasoning that a rename preserves the status of the definition it moves rather
than promoting it. That reasoning is no longer what holds the status up: an accepted ADR now uses the term
normatively, which is the condition `docs/adr/README.md` states for a concept to be `accepted`. The tier is
derivable from a binding citation instead of from an agent's judgment about a rename.

What remains unclosed is the failure mode rather than this instance of it. Nothing mechanically detects one
term carrying two referents, because no check compares meanings.

One guard against the mechanism that produced it is now built. `scripts/validate_concepts.py` rejects a
`sources` entry that resolves to no file, which is the constraint `schemas/concept.v1.json` already stated and
nothing enforced. It is the check this history asked for: the first version of `docs/concepts/projection.md`
was sourced from `docs/adr/0001-event-sourced-workflow-state.md`, and when that ADR was deleted the dangling
reference was replaced with `CLAUDE.md` rather than reported. That silent replacement is the moment the
definition lost its anchor. `tests/test_concept_sources.py` covers both outcomes, including the exact
deleted path.

A second guard was considered and rejected on measurement: requiring a specification that links a concept to
appear in that concept's `sources`. It would have fired on this case, and it fires on 38 links in the current
tree, because `sources` is declared as the material a concept derives from rather than the artifacts that cite
it. Making one field carry both relations is the defect this record exists to resolve, one level up. A
citation index is a separate field and a separate decision.

What neither guard reaches: a source that resolves says nothing about whether the definition still matches
what that source decided. The bound is stated rather than closed.
