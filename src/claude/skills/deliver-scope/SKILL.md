---
name: deliver-scope
description: Use when the person's own message states that one scope is to be carried end to end — an end-to-end ask quoted verbatim, or a goal condition the person armed naming this skill. Carries the scope through /plan-work, /implement-task over each deliverable task and /review-change, committing each step with a pathspec, logging each step, and stopping at everything only a person settles. An intent inferred from anything less is a stop. Not for a single phase (invoke that entry point directly), and never for /analyse, except once, before the plan, under a goal whose condition asks to specify its objective.
effort: medium
---

You carry one stated scope through the route — plan, deliveries, review — committing between steps,
and you stop. One invocation, one scope delivered. You own no judgment: every judgment belongs to
the entry point that holds it, invoked whole. What you add is the taking of the handoffs the reports
already carry, and the commits between them — the two acts the person handed over in the ask.

## Progress checklist

Copy this checklist into your working notes and tick each step as it closes. Where a step's section
is no longer in your context, read `${CLAUDE_PLUGIN_ROOT}/skills/deliver-scope/SKILL.md` again
before acting on it. `references/` is the directory beside that file: read a reference when its step
is reached, before acting on it.

```
- [ ] Inputs: ask quoted verbatim, project root, target, slug, reach; else one stop naming all
- [ ] Root: bin/project.py <project-root>, or --here where none is named
- [ ] Gate: spec.py over a committed specification root; /analyse only under a goal that asks
      to specify: references/goal.md
- [ ] Tree: git status --porcelain over the roots, siegard-trace.json and siegard-reconcile
      prints nothing; note HEAD
- [ ] Contract: read schemas/plan.json
- [ ] 1 Plan: skipped where the ask names a reach; else /plan-work
- [ ] 2 Commit the plan
- [ ] 3 Deliver: --outstanding, then /implement-task, per task; commit each; a stop:
      references/doors.md, references/stops.md; under a goal: references/goal.md
- [ ] 4 Review: /review-change under the name the rule gives; commit
- [ ] 5 Prove what the review left testable, once: references/prove.md
- [ ] 6 Measure: telemetry.py --probe; commit; after a stop too
- [ ] Log: a line per step in <delivery_root>/<slug>/orchestration.md; the stop line:
      references/stops.md
- [ ] Report: handoff.py --prepare; references/report.md; --save-report, --render; stop
```

## Terms

- **You** — the session that runs the skill.
- **The person** — whoever invoked the skill and decides what only a person decides.
- **Subagent** — an agent the skill spawns. The one here is `door-decider`, under a goal.
- **Stop** — the invocation ends: nothing more is written, and the report says why.
- **Refusal** — a script's non-zero exit naming what it refused.
- **Door** — an invocation of another entry point that the report hands the person, filled with
  everything known and ready to paste.

## Required inputs

A missing input is a stop, not a default:

1. **the ask** — the person's own words stating that this scope is to be carried end to end, quoted
   verbatim. It is never inferred: a request that names one phase gets that entry point, not this
   one, and an intent read into a message that does not state it is a stop.
   - A goal condition naming this skill is such a statement, and so is a condition the plugin's
     `Stop` hook repeats from a goal armed by `goal.py --arm`, which only the person's own
     invocation of `/siegard-goal --arm` runs. You deciding that a message "meant" the whole route
     is not.
   - Where such a condition names its objective by a file and a digest, the file's text, read whole,
     is the ask's objective. A file whose digest no longer matches is a stop: the words are no
     longer the ones the person armed.
   - A route resumed after a compaction reads the ask from what `ask.py --read` prints, run as the
     `read:` line `ask.py --record` printed names it — path and digest — in place of a summary: «A
     route resumed after a compaction reads its authorization from a recorded ask, printed by
     `ask.py --read`, in place of a summary of an earlier context» (SPEC-010 R3).
2. **the project root** — where `siegard.json` lives, named by the person. «Where the invocation
   names none, the project root is the git toplevel of the session's working directory, as
   `bin/project.py --here` resolves it, and only where that toplevel holds `siegard.json`»
   (SPEC-010 R6): there, `project.py --here` runs in place of the `project.py <project-root>` run
   below, and its `project_root:` line is the root. Its refusal is a stop.
3. **the target** — by the key `siegard.json`'s `targets` names it. Where `targets` declares exactly
   one key and the ask names none, that key is the target: decided and disclosed, never asked.
4. **the initiative's slug** — named in the ask, or derived from it and disclosed in the report. A
   slug whose work root holds `closure.md` is a stop: a closed plan is history, and a new scope
   names a new slug. A slug whose work root holds a live plan is a resume: continue from the
   deliverable set as it stands, and the report says so.
5. **the scope's reach** — the whole plan, unless the ask names an epic, `epic/<name>`, or tasks,
   `task/<epic>/<name>`, of the slug's live plan. Named, the run carries those tasks and every task
   they depend on: «A scope restricted to an epic or a set of tasks carries with it every task of
   the same plan it depends on that holds no record, transitively» (SPEC-008 R5). An id the plan
   does not hold is a stop, and so is a reach named over a slug with no live plan — a new plan is
   planned from prose, never from ids.

Run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/project.py <project-root>` once, before anything else.
Every root and the standard answer only from there. A field the file does not declare is a stop, and
the report carries the `/siegard-config` invocation ready to paste; that skill is closed to model
invocation.

Absent inputs stop once, together, so the person answers once.

## Before anything: the gate, the tree and the branch

**The specification gate.** Run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/spec.py <specification-root>`,
and hold the specification root to `git status --porcelain`: anything but a clean pass over a
committed root is a stop. An uncommitted specification is one nobody reviewed.

**This skill never invokes `/analyse`** — not to open the run, not to unblock it. A fact the
specification turns out not to state mid-route — the implementer's stop over a silence — goes to
`/plan-work`'s decided-fact route (`references/doors.md`), the one writer the run admits into the
specification root, under its own decision log; the `/analyse` invocation beside it is relayed
verbatim. The one exception is a goal whose condition asks to specify a prose objective: `/analyse`
once, before the plan and never to unblock a stop — read `references/goal.md` before the plan.

**The tree.** Before any step,
`git status --porcelain -- <work-root> <delivery-root> <target-source-root> <specification-root>`
must print nothing, and neither may `git status --porcelain -- siegard-trace.json siegard-reconcile`
at the target's git toplevel. Output is a stop: a pending change you did not make is somebody's work
in progress.

**The branch.** Commit where `HEAD` already points. This skill never creates a branch, never pushes,
never stashes: a branch cut for the run is the person's act, offered in the report's opening line,
which names where `HEAD` stood when the run began.

## Read the contract

Read `${CLAUDE_PLUGIN_ROOT}/schemas/plan.json`, and take every remaining answer from
`bin/deliver.py`, whose `--outstanding` run below is the only reading of the plan you make. Do not
re-derive either from memory.

`${CLAUDE_PLUGIN_ROOT}` is set where this skill runs as an installed plugin. Where it is not, the
plugin root is the directory that holds `schemas/` and `bin/` side by side.

## The two rules

Two rules bind every step:

- **Paste, never compose.** Each entry point's report ends with the next invocation ready to paste.
  Take that handoff verbatim and fill only the slots the ask covers — the scope with the ask, the
  task with the script's answer, the file set and the names with what the report carried. This skill
  never composes an invocation a report did not hand over, and never edits one beyond its slots. The
  receiving skill rereads every root from disk and stops on anything the handoff got wrong; rely on
  those stops, never on your memory of what a report said.
- **Every routing decision is a script's answer.** Which tasks remain, what each waits on, what is
  deliverable now, and in what order:

  ```
  python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --outstanding <delivery-root> <work-root> <target-source-root> <specification-root> [--scope <id>]...
  ```

  One `--scope` per id the reach names, none where it is the whole plan. Run it fresh before each
  delivery, never a reading of the plan or a memory of the last run. A stop it reports is your stop.
  Relay in the report, verbatim and from the last run that printed them, the lines it prints of
  records pinning no standard or another than `siegard.json` declares for their target — «A delivery
  record that pins no standard, or a standard other than the one its target declares, is reported
  beside the outstanding tasks and refused nowhere.» (SPEC-007 R1) — or an earlier version of it —
  «a step declared after a record was written is owed by the records written after it»
  (SPEC-007 R3). They route nothing here.

Every commit this skill makes names its paths; none sweeps the tree. Each message is
`deliver-scope <slug>: <step>`, as each step below names it.

### 1. Plan

Where the ask names a reach, the plan already holds it: skip to step 3, and commit nothing here.
Otherwise invoke `/plan-work` with the ask as the scope, the project root, the target and the slug.
On a resume where the plan already answers the ask, skip to step 3 — `--outstanding` says whether
anything is left to plan against. A task `/plan-work` reports with a
`BLOCKING, from the specification —` note is not yet a stop: step 3 delivers the deliverable set,
and stops where the set is exhausted while such a note still stands.

### 2. Commit the plan

Commit the work root and the specification root in one commit, `deliver-scope <slug>: plan` — the
decided-fact route writes into both.

### 3. Deliver, one task per invocation

Run `deliver.py --outstanding`. While the deliverable set is non-empty, take `/implement-task`'s
invocation from the previous report's handoff, fill the one open slot with one task from the set,
and invoke. After each delivery that wrote both its records — the implementation and the proof —
commit the delivery root, the target source root and the trace file in one commit,
`deliver-scope <slug>: deliver <task>`, and append the step's line to the log.

A delivery that ends in a stop instead of records ends the loop, unless `references/doors.md` or,
under a goal, `references/goal.md` answers it. Read `references/stops.md`: relay that report's own
doors whole, commit nothing further but the measure, and go to step 6. A delivery that stopped is
never committed but for runs `references/doors.md` names: what it wrote is the person's to read,
keep or discard. A task whose delivery gave up is not re-attempted in this run: the same invocation
again is the person's decision about cost.

### 4. Review

When the deliverable set is empty, invoke `/review-change` from the last delivery's handoff: the
tasks are every task this run delivered, the file set is the union of the paths their reports named,
and the review's name is the one you give it:

- the slug, where `review/<slug>.md` and `run/<slug>` under the delivery root and
  `siegard-reconcile/<slug>.md` and `siegard-reconcile/<slug>.returns/` at the target's git toplevel
  are all free;
- otherwise `<slug>-<N>` for the least `N` from 2 that frees all four.

Read the four with `ls`, and state the name in the invocation and in the report — never a name
already taken, and never a suffix of any other form.

The review is done when its record is written. Its findings are relayed whole in the report, opened
by the counts that review's own report opens with, and never acted on here: which route a finding
deserves, or whether it deserves one, is the decision that skill does not make, and neither do you.
Repairing anything a finding names is a new ask.

Commit the delivery root, the trace file and `siegard-reconcile/`, where the review's conformance
pass writes, in one commit, `deliver-scope <slug>: review`.

### 5. Close what the review left testable, once

Where the review refused a certification over a node one of this run's own tasks implements, with
`remainder: testable`, read `references/prove.md`: a proof-only re-delivery per task, then one
review again. This step runs once per run. Where no certification was refused, go to step 6.

### 6. Measure

At the end of every run, the one a stop ended included: what a run cost is lost once the harness
drops its transcripts. Run `telemetry.py --probe --since <the instant step 1 began>` over the
project root; announce the read as that script requires; run it. Commit the telemetry root
`project.py` answers under `deliver-scope <slug>: measure`. A probe that cannot read is a line in
the report, never a stop.

A stop ends the route, never the measure: step 6 runs after it, and its commit is the one that
follows a stop.

## The orchestration log

After each step, append one line to `orchestration.md` at the initiative's delivery root,
`<delivery_root>/<slug>/` — never at `delivery_root` itself, where three initiatives' lines would
read as one: what was invoked, the commit that followed by its hash, and the outcome, one sentence
per line. It is a marker, never a node: no contract holds it, and the validator keeps it by name at
the delivery root as `plan.py` keeps `closure.md` at the work root. The run's own decisions — the
slug derived, the target decided, the order taken, the stop that ended it — are written there.

A run a stop ended closes the log with one stop line, and each door taken is one `decided:` line:
`references/stops.md` and `references/doors.md` give both forms.

## Report, and stop

«The state a handoff opens with is a script's line, never the session's» (SPEC-006 R10). Run
`python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/handoff.py --prepare --skill deliver-scope --project
<project-root> --slug <slug> --target <target> --language <en or pt-BR, as you converse>` — where
a step stopped the run, `--skill` names that step instead, so the doors it marks are the ones that
step's report hands. Then read `references/report.md`: what the report holds, in order.

Write it through `bin/handoff.py --save-report <path>`, to the path its `report` names, and fill
only the fields the skeleton left empty — the stopping report's recommendation and doors among them,
carried. Hand the person exactly what `handoff.py --render` prints over the record: «A handoff opens
with what needs the person, and explains after» (SPEC-006 R1). A refusal is answered by rewriting
the field it names; a state it says has moved, by running `--prepare` again and carrying its `state`
and `state_from` whole.

«A finding stops nothing» (SPEC-006 R4): a finding the review relayed is reported, and what ended
the run is a stop a step's own file names. Where the report says a step proceeded, it lists the
`--outstanding` run and the checks the step ran, with their output verbatim — «Where a handoff says
a step may proceed, it lists the checks it ran and their output verbatim» (SPEC-006 R4).

Then stop. The commit range is the review, and it belongs to the person.

## What you never do

- Invoke `/analyse`, or write into the specification root, outside the one invocation
  `references/goal.md` names, before the plan.
- Commit without a pathspec, sweep the tree, create a branch, push, stash, or rewrite history.
- Carry this skill's steps, or commit under its name, outside an invocation of it that accepted the
  ask. Where the ask is refused — a goal whose condition does not name this skill — the report says
  what the condition lacks and that `/goal clear` and the composed condition answer it, and you
  carry nothing on by hand.
- Override, soften or skip any stop an entry point raised — its rules bind its invocation whole, and
  your grant over a stop is to relay it or take its derived door (`references/doors.md`).
