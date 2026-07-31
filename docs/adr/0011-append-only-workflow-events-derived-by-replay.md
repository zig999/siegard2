---
id: "0011"
title: Record workflow history as an append-only event log, and replay it for state
status: accepted
contract_version: adr/1
---

# Record workflow history as an append-only event log, and replay it for state

## Context

`docs/bootstrap.md` open question 1 asked which persistence model records workflow state, and named
an append-only log with state derived by replay as the leading candidate rather than the answer. It
attached a gate — an event schema carrying `contract_version`, a derivation with a determinism test, a
transition guard tested in both directions, and a fixture running the loop end to end — and warned that
the event model costs a migration burden on every schema change, so a mutable record should win if it
turned out to be sufficient.

That question stayed open through five removed ADRs, because a candidate design for a component that
does not exist is a guess. The thin path of stage 2 is the first thing that made the question
answerable with evidence instead of preference.

Two facts from building it bear on the choice. First, the loop needs history, not only current state:
`specs/0001` R7 returns a failed validation to implementation under a stated attempt limit, so the
guard has to know how many attempts have already happened. A mutable record holding only the current
phase cannot answer that without keeping a counter beside it — a second piece of state that can
disagree with the first. Second, the interesting property turned out to be reproducibility of the
*derivation*, not durability of the record: the defect worth preventing is a state that says one thing
while the history says another.

An early draft ordered events by their timestamp. That is wrong for a reason worth recording: two
events can share a second, and a clock can move backwards, so replay would depend on something the
framework does not control.

## Decision

Workflow history is a JSONL log of entries conforming to `schemas/workflow-event.json`, and state is
computed from it by `derive()` in `scripts/workflow_lib.py`. Nothing stores state.

Four specifics this contract fixes, each because the alternative failed a test rather than because it
reads better:

- **`seq` orders a workflow's entries, not `occurred_at`.** It starts at 1 and increases by exactly 1,
  so a gap or a repeat is a lost or duplicated record rather than a new fact. Timestamps stay in the
  record as provenance and decide nothing.
- **Callers supply `event_id` and `occurred_at`.** The framework mints neither, which is what lets
  `scripts/replay_workflow.py` regenerate a fixture's log and compare it byte for byte. This is the
  same allocation of the clock that `src/claude/agents/concept-author.md` already required of its
  caller.
- **The transition table is data.** `TRANSITIONS` maps a `(phase, outcome)` pair to the next phase or
  to a terminal status, and `guard()` refuses a pair the table does not hold. `specs/0001` R5 is the
  authority for why the choice is a lookup; the table is where that choice is written down.
- **The attempt limit is a property of the workflow's own opening entry**, not of the framework. R7
  requires the limit stated; a framework-wide default would be the calibrated threshold R10 forbids
  inventing ahead of executed workflows.

`schemas/impact-analysis.json` arrives in the same change, because the loop cannot run without the
artifact R4 requires and R4 already fixes its content.

## Consequences

- Open question 1's gate is met, and `docs/bootstrap.md` records that. A met gate is evidence, not
  authority, so this ADR stayed `proposed` until a maintainer accepted it on 2026-07-31 — which makes it
  the one record in this repository promoted on evidence that was already in place rather than ahead of it.
- The migration burden the open question warned about is now real and unpaid. `workflow-event/1` has one
  version and one producer of logs, so `.claude/rules/compatibility.md` has not yet been exercised on
  persisted state — the first bump to `workflow-event/2` must carry a migration for logs already
  written, and the repository still owes the migration test noted as missing for `adr/1 → adr/2`.
- Derived state is committed per fixture (`derived-state.json`) and verified against a fresh replay.
  A change in control flow therefore shows up as a reviewable diff, and a hand-edit is a check failure.
- Two contracts were deliberately not written: a context package (R11) and a specification delta (R16).
  The loop records both phases and produces neither artifact, because nothing consumes them to choose a
  transition. They arrive with the stage that needs them.
- The guard cross-checks a validation event's evidence against the outcome it asserts. That is a
  constraint no JSON Schema can express, so it lives in the guard, and it means evidence cannot be
  decorative.
- Nothing here decides whether an orchestrator is a component class the framework ships. It decides
  that the orchestrator's logic is a tested script, which is a narrower claim; open question 3 keeps the
  rest.

## Outstanding evidence

What this document states and nothing has yet exercised. A condition kept here is a debt;
removing one because the document binds would turn an open debt into a silent one.

1. A second workflow fixture whose path differs from the first — a `none` verdict, or a workflow that
   exhausts its attempt limit — replays and is checked, showing the table generalizes beyond one
   recorded history. Both branches are currently covered by tests only.
2. The generator installs the entry point and the specialized agent into a fixture, Claude Code loads
   them, and the loop runs with an agent result the agent actually produced rather than one recorded by
   hand. This is ADR-0009 condition 2 and open question 2; until it holds, the loop is proven over
   artifacts, not over components.
3. One contract bump on `workflow-event`, with a migration for logs written under version 1 and a test
   that fails against the old behavior — which is what turns the consequence above from an accepted cost
   into a demonstrated mechanism.
