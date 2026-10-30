---
id: "SPEC-008"
title: The goal
status: proposed
contract_version: spec/1
---

# The goal

## Scope

This specification fixes what a goal the person arms over `/deliver-scope` ends on, and how that
end is read. It binds `/deliver-scope`, the script that answers a goal's state, the script and the
skill that compose a goal's condition, and telemetry's count of the harness's evaluations.

A goal is the harness's own mechanism: a condition the person sets once, that the harness
repeats whenever the session tries to stop, and that a model reading the transcript judges met or
not. This specification decides what the condition says, what decides that it is met, and what
ends a run that cannot be carried further without a person — so that a goal always ends, in one
of two states, each read from disk.

Grounds: every `/goal` session of three consumers (`newcatalog`, `productcatalog`,
`productorder`) between 2026-10-13 and 2026-10-25, Siegard 5.18.0–5.28.1, read from their
transcripts on 2026-10-25 — 15 sessions. The harness recorded 467 evaluations judging the
condition not met and 10 judging it met; six sessions never ended met. Read session by session,
each park had one of four causes: a decision this framework reserves to a person — a finding's
worth, a plan's closure, a standing BLOCKING note, `--bind --replace`, a skill closed to the
model — which the condition demanded and the session could not take; an environment the run could
not have, such as a container engine or production data; a condition the evaluator could never
read as met — an order of steps, "follow the standards", an item that did not exist; and a
session that stopped while its subagents were still running. The harness refuses a condition longer than
4,000 characters, and the conditions written by hand restated rules the skills already hold.

### Decided elsewhere, deliberately not restated here

- What stops a run, and what each stop hands the person — `/deliver-scope`'s own file.
- What a handoff opens with and recommends — `specs/handoff.md` (SPEC-006).
- What authorizes a commit — this repository's `CLAUDE.md` and the session rules.

## Definitions

- **Goal** — a condition the person sets through the harness, repeated by it whenever the
  session tries to stop, until a model reading the transcript judges it met.
- **Goal condition** — the text of a goal.
- **Scope** — what a goal carries: an initiative's whole plan, one epic of a live plan, or a set
  of tasks of a live plan.
- **Stop line** — the last line of a stopped run's orchestration log: `stop: <class> — <fact>`.
- **State A** — the scope is delivered, proven, reviewed and measured; the substrate alone is delivered and owes no proof.
- **State B** — the run stopped where only a person moves it, and what it did is committed and
  measured.

## Requirements

### What a goal ends on

- **R1** — A goal's state is a script's answer, read from disk and git alone: its first line is `state A`, `state B` or `not yet`, and every check it ran follows with its output verbatim.
- **R2** — State A holds when every task of the scope holds an implementation record and a proof record, or an implementation record of the substrate alone, which owes no proof; no implementation record of the scope records a criterion unmet; every task of the scope whose records changed since the goal began is named by a review record committed after them; the delivery and the plan check against their sources; the specification is sound; a measure is committed after the last record and the last review; the tree holds no change but those the condition declared untouched; every commit since the goal began names a skill and the slug, or is a reconciliation that touches only the trace and its own record; none of those commits is on a remote; and the plugin runs the version the goal began under.
- **R3** — State B holds when the initiative's orchestration log, changed since the goal began, ends with a stop line whose class is one of `blocking`, `silence`, `rebind`, `producers`, `gave-up`, `infrastructure`, `project-file`, `pending-change`, `specification`, `contradiction`, `budget`, `stands`, `analyse`, `outside-task`, `already-met`, `unclassified`, and the measure, commit and remote conditions of R2 hold; what the tree still holds is reported as left for the person, because a delivery that stopped leaves its files for a person to read. A plugin whose version changed since the goal began is state B on its own, and so is a commit since the goal began that touches the project file or a standard it declares: the rules the goal ran under are no longer the ones that answer, or what only the person authors changed under a goal.
- **R11** — A commit since the goal began that names no skill and the slug, and is no reconciliation R2 admits, is state B on its own: the route never rewrites history, so that commit stands until a person reads it, and a goal waiting for it to disappear never ends.
- **R12** — A scope that holds every condition of R2 but one — an implementation record of it records a criterion unmet — is state B, each such criterion named beside its task: the record says the source does not satisfy the criterion, and state A would say the scope is delivered.
- **R13** — The answer names every criterion that a review committed since the goal began, naming a task of the scope, left other than covered, beside that review; the list fails no check, because a criterion no suite reaches is a reading for a person, not a state.

### What a stopped run writes

- **R4** — A run a stop ended closes its orchestration log with one stop line: its class names the stop from the list R3 holds, and its fact is the stopping report's own words. Every stop the orchestrating skill's file names carries exactly one class. A stop no other class names carries `unclassified`, and its fact is the whole of what a person reads.

  Grounds: the 19 stop lines the sales consumers' orchestration logs held on 2026-10-30, read
  against their own facts. Seven carried `gave-up`, and one of those was a delivery that gave up;
  two were a red whose fix lay in files the task does not write — another task's, or none's — two
  a task whose implementer found every criterion already met by source the task never wrote, and
  two framework defects since corrected. Two more carried `unclassified`, outside the list: a
  build red over a tree the delivery had not changed, and a fix that needed another task's file.
  Under a goal, `gave-up` is a judged choice the door decider may answer by trying the same
  delivery again, which a fix outside the task cannot reward; and a class outside the list left
  the goal without state B, though only a person could move the run.

### What a goal carries

- **R5** — A scope restricted to an epic or a set of tasks carries with it every task of the same plan it depends on that holds no record, transitively, and the deliverable set within a scope is a script's answer.
- **R6** — A goal condition names the route, the authorization, the scope and the invocation that answers its state, and states no rule: the rules are those of the plugin version the invocation pins. The condition is composed by a script that checks, before any goal is armed, what the first step of the route would refuse, and it is armed by the person; no skill sets a goal. An objective in prose is written to a file under the telemetry root and named in the condition by path and digest, so the condition is one line whatever the objective's length; an objective the person cites — text already in the conversation they point at and adopt — is copied whole into that file, never cut to fit the route, and the evaluator reads the state command rather than the objective. Where the person gives them, the condition states the budget of judged doors the run may take and the findings policy, and a policy names only findings a route corrects: conformance findings of kind `contradicts`, which the corrective increment answers.

### What a goal answers without a person

- **R8** — Under a goal, a delivery that stopped over a fact no node states is answered by planning's decided-fact route, and a task waiting on a re-bind by planning over its slug, each once per task, before the run resumes; a second time over one task is a stop.
- **R9** — Under a goal whose findings policy names a finding's kind, each such finding of the run's review is answered by one corrective increment over the file it names, delivered and reviewed in the same run, once: what that review finds is reported and never corrected again.

- **R10** — Under a goal whose condition asks to specify a prose objective, the orchestrating entry point invokes `/analyse` once, before the plan, over the objective as the person armed it, and commits the specification root apart. A stop of `/analyse` over material that states no fact, or that names nodes and changes none, is nothing to specify, and the plan follows; every other stop of it ends the run. Each of those two stops is printed as one line of its own, `stop: no-fact — <what the material would have to state>` or `stop: no-change — <the nodes it names>`.

### What is counted

- **R7** — Telemetry counts the goal evaluations the harness recorded in each session of its window, those judging the condition met and those judging it not met.

## Validation required before acceptance

1. Tests hold `goal.py --state` to R2, R3, R11, R12 and R13 over fixture repositories: one
   answering each state, one per condition of R2 failing alone, a foreign commit answering state
   B, a criterion recorded unmet answering state B with the criterion named, and a criterion a
   review left uncovered named under state A.
2. A test holds the stop list of `/deliver-scope`'s file to R3's classes, one class per stop.
3. A test holds `deliver.py --outstanding --scope` to R5: an epic, a task set, a dependency
   outside the scope, and an id the plan does not hold.
4. A consumer goal composed under this specification is read for the evaluations telemetry
   counts (R7). The baseline is the grounds' 467 judged not met over 15 goals; a goal composed by
   `goal.py --compose` that the harness judged not met more than once while `--state` answered
   `state A` or `state B` is a defect in what the condition says, never grounds to widen it.

## Readings

- 2026-10-28 — grounds for R11–R13, read from `salese2e`'s transcript and repository under
  Siegard 5.35.1. R11: the person committed `aa7b89c` from another session inside the first
  goal's window; `commits` failed for good, neither state could be reached, the harness judged
  the condition not met 12 times in 67 seconds and paused the goal after 9 consecutive blocks, and
  the person cleared it by hand. R12: the walking-skeleton delivery held 7 criteria recorded unmet
  in two implementation records — six of `fictitious-module-entry`, each needing a repository no
  task writes — and R2 as it then stood would have answered state A over them. R13: the second goal
  ended state A over a review leaving one criterion partial, and the walking-skeleton review left
  59 criteria uncovered or partial, the exit criterion of the phase among them, with no line of the
  state's answer saying so. Reversal for R12: a run that ends state B on criteria recorded unmet
  which a later delivery of the same task meets without a person is a route the goal should take
  itself, and narrows R12 to what that route cannot answer.

- 2026-10-26 — grounds for R10, read before it had run: `/analyse`-origin decisions were revised
  31 of 162 times (19%, eternal, read 2026-10-07), and the person's review before a
  specification commit took a median 1.7 minutes over 108 consumer transcripts (2026-10-06) — the
  gate R10 removes was mostly nominal. Its reversal: decisions landed by a goal's `analyse`
  commit revised at a higher rate than `/analyse`'s outside a goal narrow the goal back to a
  closed specification.

- 2026-10-25 — not yet read: no goal has been composed under this specification.
