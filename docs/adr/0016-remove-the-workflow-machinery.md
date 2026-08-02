---
id: "0016"
title: Remove the workflow machinery, and leave the method it implemented unimplemented
status: accepted
contract_version: adr/1
---

# Remove the workflow machinery, and leave the method it implemented unimplemented

## Context

`foundation/0001-knowledge-object-driven-development.md` fixes a seven-phase workflow: R2 the phases and
their order, R5 an orchestrator choosing a transition by lookup on a closed field, R7 an attempt limit
with a terminal exhaustion, R8 workflow state persisted outside the conversation and every transition
reconstructible from records alone. An earlier record chose the persistence model — append-only
events, with state derived by replay — and the implementation followed: a transition table, a guard, a replay, an
event contract, and a skill that drove them.

A maintainer raised the objection this record exists for. Deciding what runs and when is the harness's
work; what Siegard should guarantee is that an artifact declares its prerequisites, its inputs, and its
outputs, so that a sequence follows from the artifacts rather than from a table Siegard maintains.

The counter-argument is real and is recorded here because it was not answered. A prerequisite graph
expresses order. It does not express refusal: not the attempt limit of R7, not the terminal exhaustion
that "is never an acceptance", not R21's rule that no workflow accepts its own output, and not the
guard's check that a validation claiming to pass carries no failing evidence. Of the guard's seven
conditions, exactly one was the ordering table; the other six were about history and about refusing a
false report. Handing sequence to the harness also hands control flow to a model, which is the defect
`foundation/0001` was written to correct — and nothing documented makes a harness obey a declared
prerequisite, so obedience would be a hope rather than a guarantee.

What settled it was not that argument but scope. The objective in front of this repository is to make
Siegard produce its first artifacts from received domain material. The workflow machinery is not on that
path, and the work it was pulling in — completing declarations so an order could be derived from them,
then reconciling that derivation with the table — was framework surgery with no bearing on the
objective.

## Decision

The workflow machinery is removed outright:

| Removed | Was |
|---|---|
| `bin/orchestrate.py` | the thin-path orchestrator: boundary validation, then the transition |
| `bin/workflow_lib.py` | the transition table, the guard, the replay-derived state |
| `bin/replay_workflow.py` | fixture replay and its verification |
| `schemas/workflow-event.json` | the `workflow-event/1` contract |
| `skills/knowledge-change/` | the skill that drove the seven phases |
| `fixtures/knowledge-change-loop/`, the log half of `fixtures/consumer-knowledge/` | the end-to-end evidence |
| `tests/test_workflow_events.py` | 582 lines holding the guard to both directions |

The decision that chose the event model is superseded by this record, and removed with the
machinery it decided.

Ingestion replaces the one path that had a caller: `skills/ingest-domain/` turns received domain
material into a knowledge base as a straight procedure — classify, author in strategic-before-tactical
order, validate, regenerate the derived files — with no event log, no phases, and no transitions.

## Consequences

**`foundation/0001` R2, R5, R7, R8 and `foundation/0005` R14 were left unimplemented by this change**,
rather than deleted: `foundation/` states what the distributed framework must do, and removing an
implementation does not change what the method is.

They were settled afterwards, and the settlement is not this record's. `foundation/0005` R23 fixed the
architecture that replaces the machinery, retiring R6 and R14 there; `foundation/0001` then decided its
own — R2 demoted to guidance, R5 and R8 retired, R7 kept with the absence of a mechanism stated in the
requirement, and R21 found to be unaffected. Each specification's **Provenance** carries the reasoning,
which is where a reader of the requirement will be standing.

**`foundation/0006` R15 was not followed.** It requires a capability to pass through `deprecated` before
`retired`, and calls removing an installed one without that step "a breaking change made silently".
`knowledge-change` went from `active` to absent in one change. The step was skipped on a maintainer's
decision, with the inventory of what would go stated before the removal; what makes it not silent is
this record, which is the weaker substitute the requirement was written to refuse. Nothing here claims
the requirement was satisfied.

**Four artifacts lost their mechanical consumer.** `impact-analysis/2`, `specification-delta/1`,
`concept-authoring-result/1`, and `validation-evidence/1` were read by the orchestrator. Their contracts
and their producing agents remain, and each schema now records that its consumer is the caller rather
than naming a file that no longer exists. They are the obvious candidates for the next removal, and they
are kept for now because nothing was asked of them: the scope confirmed was the machinery, not the phase
agents.

**One deletion went too far and was reversed.** `fixtures/consumer-knowledge/` held the event log *and*
`context-package.json`, which is evidence for context resolution — a capability that survives. The
package and its README were restored; only the log and its inputs are gone.

**One debt is discharged by removal.** `foundation/0013` recorded the `workflow-event/1` contract as
having been bumped without a migration test. The contract no longer exists, so the exposure is closed by
subtraction rather than by satisfying R11.

### What was rejected

**Deriving the order from the declarations**, which is what the objection asked for. The audit killed it
on facts rather than on preference: 3 of 13 transitions derived from declared artifact prerequisites when
it was measured, because `knowledge-author` declared no artifact input while receiving another
capability's decision as bare values, nothing declares `validation-evidence` as an output, and acceptance
is a person. `foundation/0007` R24 later closed the first of those; the count stands as what was true when
this decision was taken. The remaining
nine are outcome control flow — a skip, a back edge, two terminals — or phases whose producer is not a
capability the framework ships. On top of that, `capabilities.declaration.json` does not reach the
distribution under `foundation/0007` R23, so an installed orchestrator cannot read it at run time and the
derivation would have had to be generated at build time into a third computed file — which would have
required a `CLAUDE.md` edit only a maintainer makes.

**Deprecating rather than removing**, per `foundation/0006` R15. It preserves every guarantee and keeps
about 1,700 shipped lines alive in the distribution for a path nothing calls. Rejected because the
inventory was confirmed explicitly; recorded because the requirement asked for it and it was refused.

**Keeping the machinery and building ingestion beside it.** This was the state before this change and it
is what made the workflow look load-bearing: `ingest-domain` would have had to explain why it does not
record events, and the next reader would have reconciled the two rather than reading one.

### What would falsify this

An ingestion, or any later capability, that needs to resume after an interruption. Resuming is what the
event log bought: state derived from a durable record rather than from a conversation. `foundation/0001` R8
required it and has since been retired, with the loss of resumption named in its place. A straight procedure that fails halfway
leaves a partially authored knowledge base and no record of where it stopped. If that turns out to bite,
the answer is not this machinery restored wholesale — it is the smallest durable record that says which
entries of a classification were authored.
