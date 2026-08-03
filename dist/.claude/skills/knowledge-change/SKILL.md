---
name: knowledge-change
description: Starts or resumes a knowledge change workflow in a repository Siegard governs, driving the change request through impact analysis, authoring, validation, and acceptance. Use when a change requires a term or knowledge object to be defined, revised, or retired, or when an interrupted knowledge workflow must continue from its recorded state. Not for changing a contract, and not for accepting a workflow — acceptance is a maintainer's decision.
disable-model-invocation: true
---

You start and resume knowledge change workflows. You validate inputs, delegate work, and record
what happened. You never choose the next phase: the orchestrator reads that from the log.

Two rules govern everything below, and neither is yours to relax:

- **You do not decide transitions.** `orchestrate.py` chooses the next phase by looking up a closed
  field of an artifact that passed its contract. If you find yourself reasoning about what should
  happen next, stop — read the derived state instead.
- **You do not accept a workflow.** Acceptance requires a maintainer's decision or a deterministic
  approval mechanism the governed repository defines. Record the acceptance a maintainer gives you;
  never supply one.

## Required inputs

Collect these before running anything. A missing input is a stop, not a default:

1. **the framework script root** — the directory holding `orchestrate.py` and `replay_workflow.py`.
   There is no default: installation decides this path, and a component that guessed it would fail
   silently in a repository laid out differently.
2. **the event log path** — where this repository persists workflow events.
3. **the workflow id** — `wf_` followed by lowercase words joined by hyphens. Reuse the existing id
   to resume; mint a new one only for a new request.
4. **the change request** — what is being asked, and its `cr_` identifier.
5. **the attempt limit** — how many implementation attempts this workflow permits. State it; the
   framework will not invent one.
6. **the bundle root and its contract** — the directory of knowledge files and the path of the JSON
   Schema that governs them, both needed by the authoring agent.
7. **an instant and an event id for every event you record** — `ev_` followed by twelve hex digits,
   and a UTC timestamp. You own the clock; the framework refuses to, because a log whose identifiers
   came from a clock could not be replayed and compared.

## Resuming

Always start here, including on a first run:

```
<script root>/orchestrate.py state --log <log> --workflow <id>
```

The output is the whole of what is known: `phase` is where the workflow stands, `status` is `open`
or terminal, `attempts` and `attempt_limit` decide whether another implementation attempt exists.
Act on that, never on your memory of the conversation — conversation history is not a record.

A terminal `status` means the workflow is over. Report it and stop.

## Driving a phase

For each phase the state reports, do the phase's work, then record it. Two ways in:

**A phase whose verdict comes from an artifact** — impact analysis, and implementation. Write the
artifact, then let the orchestrator read it:

```
<script root>/orchestrate.py consume --log <log> --workflow <id> \
    --result <artifact> --event-id <ev_...> --at <instant> --subject-path <stable path>
```

The orchestrator validates the artifact against its declared contract and rejects it rather than
repairing it. A rejection is a defect in the artifact — fix the artifact and run again. Never
hand-write the event that a `consume` would have produced.

**A phase you record directly** — the change request, context resolution, the specification delta,
validation, and a maintainer's acceptance. Write one event as JSON and append it:

```
<script root>/orchestrate.py record --log <log> --event <event file>
```

The guard applies identically here. If it rejects your event, the event is wrong about the workflow;
do not edit the log to make it fit.

## What each phase owes

- **change request** — outcome `recorded`, carrying the `attempt_limit`. This is the workflow's
  opening entry and the only place the limit is stated.
- **impact analysis** — an artifact with a verdict of `none`, `update`, or `create`, naming every
  implicated knowledge object, ADR, and concept by identifier. Run it for every request, including
  one you expect to be `none`.
- **context resolution** — outcome `resolved`, or `degraded` with the degradation named. Resolution
  never blocks: where a root cannot be located, a cycle cannot be resolved, knowledge contradicts, or
  a budget is exhausted, record it and continue. A recorded degradation is an input to acceptance.
- **specification delta** — outcome `recorded`. Describe only the requested change, referencing
  knowledge objects and ADRs by identifier instead of restating them.
- **implementation** — delegate to `concept-author`, one concept per delegation. Give it the bundle
  root, the contract path, the term, what forces the change, the source artifacts, and the timestamp
  and producer identity for its `generated` field. Its result is a contract, not prose: pass the
  result file to `consume`.
- **validation** — run the bundle's own validators. Record outcome `passed` or `failed` with evidence
  naming what ran, each check's result, and enough detail to reproduce it. Evidence that disagrees
  with the outcome is rejected by the guard.
- **acceptance** — outcome `accepted` with `decided_by` naming the maintainer or the approval
  mechanism that decided. Report, for each impacted knowledge object, whether an assertion decided it
  mechanically or a review decided it, and name every gap. Review is not a guarantee; presenting it
  as one is a false report.

## When validation fails

The orchestrator returns the workflow to implementation while attempts remain. When the attempt
limit is reached, the only legal outcome is `exhausted`, which is terminal and reports the failure.
It is never an acceptance, and you may not raise the limit to avoid it — the limit is a property of
this workflow's own record.

## When you are blocked

Record outcome `blocked` with a `blocking_reason` naming the missing input or the conflict, in
whatever phase you stand. Do not improvise past a missing input, and do not delegate again hoping for
a different answer.
