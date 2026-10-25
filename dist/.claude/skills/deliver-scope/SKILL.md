---
name: deliver-scope
description: Carries one stated scope end to end through the entry points — /plan-work, /implement-task over each deliverable task, /review-change — committing between steps with a pathspec, recording each step in an orchestration log, and stopping at everything only a human settles. Use only where the human's own message states that the whole route is wanted — an end-to-end ask quoted verbatim, or a standing automation whose condition names this skill. An intent inferred from anything less is a stop. Not for a single phase (invoke that entry point directly), and never for /analyse — the specification is authored, reviewed and committed by a person before this skill runs.
effort: medium
---

You carry one stated scope through the route — plan, deliveries, review — committing between
steps, and you stop. One invocation, one scope delivered. This skill owns no judgment of its own:
every judgment belongs to the entry point that holds it, invoked whole, and every routing decision
is a script's answer. What this skill adds is only the taking of the handoffs the reports already
carry, and the commits between them — the two acts that were the human's, delegated once, in the
ask.

## Required inputs

A missing input is a stop, not a default:

1. **the ask** — the human's own words stating that this scope is to be carried end to end,
   quoted verbatim. The authorization is the statement itself, and it is never inferred: a
   request that names one phase gets that entry point, not this one, and an intent read into a
   message that does not state it is a stop, exactly as the corrective increment in `/plan-work`
   is named and never inferred. A standing automation the human armed — a goal condition naming
   this skill — is such a statement; this skill deciding on its own that a session "meant" the
   whole route is not.
2. **the project root** — where `siegard.json` lives. Named by the human; inferred rather than
   named, its absence is a stop.
3. **the target** — by the key `siegard.json`'s `targets` names it. Where `targets` declares
   exactly one key and the ask names none, that key is the target: decided and disclosed, never
   asked.
4. **the initiative's slug** — named in the ask, or derived from it and disclosed in the report.
   A slug whose work root holds `closure.md` is a stop: a closed plan is history, and a new
   scope names a new slug. A slug whose work root already holds a live plan is a resume, not an
   error: this skill continues from the deliverable set as it stands, and the report says so.
5. **the scope's reach** — the whole plan, unless the ask names an epic, `epic/<name>`, or tasks,
   `task/<epic>/<name>`, of the slug's live plan. Named, the run carries those tasks and every
   task they depend on: «A scope restricted to an epic or a set of tasks carries with it every
   task of the same plan it depends on that holds no record, transitively» (SPEC-008 R5). An id
   the plan does not hold is a stop, and so is a reach named over a slug with no live plan — a
   new plan is planned from prose, never from ids.

Run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/project.py <project-root>` once, before anything else.
Every root and the standard answer only from there, exactly as they do for every entry point this
skill invokes; a field the file does not declare is a stop, and the report carries the
`/siegard-config` invocation ready to paste — that skill is closed to model invocation, so the
paste is the human's.

Absent inputs stop once, together, so the human answers once — never a question at a time.

## Before anything: the specification gate

This skill begins where the specification ends, and that boundary is the one gate the whole
arrangement keeps for a person. Run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/spec.py
<specification-root>`, and hold the specification root to `git status --porcelain`: anything but
a clean pass over a committed root is a stop. A specification still uncommitted is a specification
nobody reviewed, and carrying work over it would build the route on the one diff this skill exists
to leave in a person's hands.

**This skill never invokes `/analyse`.** Not to open the run, not to unblock it: a fact the
specification turns out not to state mid-route — the implementer's stop over a silence — ends the
run, and the `/analyse` invocation that stop already hands over is relayed to the human verbatim.
The one writer this run admits into the specification root is `/plan-work`'s own decided-fact
route, which runs inside that skill's invocation under its own discipline and its own decision
log, exactly as it does when a human invokes it.

## Before anything: the tree, and the branch

Before any step, `git status --porcelain -- <work-root> <delivery-root> <target-source-root>
<specification-root>` must print nothing: a pending change this skill did not make is somebody's
work in progress, and committing it under a run's message would bury it. Output is a stop.

This skill commits where `HEAD` already points and never creates a branch, never pushes, never
stashes: starting the run on a branch cut for it is the human's act, offered in the report's
opening line, which names where `HEAD` stood when the run began.

## Read the contract

Read `${CLAUDE_PLUGIN_ROOT}/schemas/plan.json` — the contract of the index this skill reads to
follow the plan's shape — and take every remaining answer from `bin/deliver.py`, whose
`--outstanding` run below is the only reading of the plan this skill makes. Do not re-derive
either from memory.

`${CLAUDE_PLUGIN_ROOT}` is set where this skill runs as an installed plugin. Where it is not, the
plugin root is the directory that holds `schemas/` and `bin/` side by side.

## The order

```
gate → plan → commit → [deliver → commit, per task] → review → commit
     → [prove → commit, per task left testable] → review → commit → measure → commit
     → report → stop
```

Two rules bind every step, and they are what this skill is:

- **Paste, never compose.** Each entry point's report ends with the next invocation ready to
  paste; this skill takes that handoff verbatim and fills only the slots its authorization
  covers — the scope with the ask, the task with the script's answer, the file set and the names
  with what the report itself carried. It never composes an invocation a report did not hand
  over, and it never edits one beyond its slots. The handoff lives in conversation, and
  conversation is not state — what makes the paste safe is the receiving skill, which rereads
  every root from disk and stops on anything the handoff got wrong; this skill relies on those
  stops rather than on its own memory of what a report said.
- **Every routing decision is a script's answer.** Which tasks remain, what each waits on, what
  is deliverable now, and in what order:

  ```
  python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --outstanding <delivery-root> <work-root> <target-source-root> <specification-root> [--scope <id>]...
  ```

  with one `--scope` per id the reach names, and none where it is the whole plan — run fresh
  before each delivery, never a reading of the plan or a memory of the last run. A stop
  the script reports is this skill's stop. The lines it prints of records pinning no standard, or
  another than the one `siegard.json` declares for their target — «A delivery record that pins no standard, or a standard other than the one its target declares, is reported beside the outstanding tasks and refused nowhere.» (SPEC-007 R1) — or an earlier version of it — «a step declared after a record was written is owed by the records written after it» (SPEC-007 R3) — are relayed in the report below, verbatim, from the last run that printed them; they route nothing here.

The steps:

1. **Plan.** Where the ask names a reach, the plan already holds it: skip to the loop, and commit
   nothing here. Otherwise invoke `/plan-work` with the ask as the scope, the project root, the
   target and the slug. On a populated work root, this is that skill's ordinary evolution of the plan it holds;
   on a resume where the plan already answers the ask, skip to the loop — `--outstanding` is what
   says whether anything is left to plan against. A task `/plan-work` reports as carrying a
   `BLOCKING, from the specification —` note is not yet this skill's problem to stop on: the loop
   below delivers the deliverable set, and stops where the set is exhausted while such a note
   still stands.
2. **Commit the plan**: the work root and the specification root in one commit — the decided-fact
   route writes into both, and the two diffs are one increment — under the message
   `deliver-scope <slug>: plan`. Every commit this skill makes names its paths; none sweeps the
   tree.
3. **Deliver, one task per invocation.** Run `deliver.py --outstanding`; while the deliverable
   set is non-empty, take `/implement-task`'s invocation from the previous report's handoff,
   fill the one open slot with one task from the set, and invoke. After each delivery that wrote
   records, commit the delivery root, the target source root and the trace file in one commit —
   `deliver-scope <slug>: deliver <task>` — and append to the log below. A delivery that ends in
   a stop instead of records — a red build given up, a suite whose diagnosis only a person
   settles, a silence handed to `/analyse` — ends the loop: relay that report's own doors whole,
   commit nothing further but the measure below, and go to it. A task whose delivery gave up is not
   re-attempted in this run: the same invocation again is a decision about cost, and it is the
   human's.
4. **Review.** When the deliverable set is empty, invoke `/review-change` from the last
   delivery's handoff: the tasks being every task this run delivered, the file set being the
   union of the paths their reports named. The review is done when its record is written — the
   findings are relayed whole in the report, opened by the counts that review's own report
   opens with, and never acted on here: which route a finding deserves, or whether it deserves
   one, is the decision that skill deliberately does not make, and this skill inherits the same
   restraint. Repairing anything a finding names is a new ask.
   Commit the delivery root, the trace file and `siegard-reconcile/` — the review's conformance
   pass writes its record and returns there and restamps the trace — in one commit,
   `deliver-scope <slug>: review`.
5. **Close what the review left testable, once.** A certification the review refused over a node
   one of this run's own tasks implements, with `remainder: testable`, is the handoff that
   review's report names — the proof-only re-delivery of `/implement-task` over that task,
   handed the node, the assertion and the proof file, all read from the review's record — and
   taking it is inside the ask: carrying the scope end to end is carrying its nodes to the proof
   the specification prefers. «A finite test is preferred to a reading, and to a registry
   step's decision, wherever one exists» (SPEC-004 R10). Fill those slots from the record, one
   re-delivery per task, commit each as `deliver-scope <slug>: prove <task>`, then invoke
   `/review-change` once more over exactly those tasks and commit it as `deliver-scope <slug>:
   review again`. This step runs once per run: a certification refused again is relayed with
   its new remainder, and a third attempt is the human's decision about cost. A remainder over a
   node no task of this run implements is not this run's; the report hands it on as `trace.py
   --owed` does.
6. **Measure**, at the end of every run, the one a stop ended included: what an ended run cost is
   the half of its record a person cannot reconstruct once the harness drops its transcripts. Run
   `telemetry.py --probe --since <the instant step 1 began>` over the project root; announce the
   read as that script requires; run it. Commit the telemetry root `project.py` answers under
   `deliver-scope <slug>: measure`. A probe that cannot read is a line in the report, never a
   stop.

**The orchestration log.** After each step, append one line to `orchestration.md` at the
initiative's delivery root, `<delivery_root>/<slug>/` — never at `delivery_root` itself, where
three initiatives' lines would read as one — what was invoked, the commit that followed by its hash, and the outcome, one sentence per
line. It is a marker, never a node, exactly as `closure.md` is: no contract holds it, the
validator keeps it by name at the delivery root the way `plan.py` keeps `closure.md` at the work
root, and it is the one place the run's own decisions —
the slug derived, the target decided, the order taken, the stop that ended it — survive the
conversation that made them.

## What ends the run

Every stop below ends the run with the doors the stopping report already carried, relayed
verbatim, and with the log naming it — where that report recommended a door, on a line of its
own, «`recommended: <door> — <criterion> — <deciding fact>`»
(SPEC-006 R5): its door and deciding fact copied from the report, and its criterion the name the
handoff's specification gives the ground the report stated in plain words — never a
recommendation the report did not make.
None is worked around, and none is retried. Each carries its class, in backticks after it:

- a `BLOCKING, from the specification —` note standing on every task the set has left —
  `blocking`;
- a specification silence — the `/analyse` invocation is the human's to take, always —
  `silence`;
- a task `deliver.py --outstanding` lists as waiting on a re-bind — a node it implements moved
  since the plan was derived, and the door is `/plan-work` over the slug, never a derivation —
  `rebind`;
- a suite whose diagnosis names a disagreement between the two producers — `producers`;
- a delivery that gave up — `gave-up`;
- an infrastructure failure the diagnosis read twice — `infrastructure`;
- a field `siegard.json` does not declare, or a standard that resolves nowhere — `project-file`;
- a pending change this skill did not make, anywhere the pathspec above reaches —
  `pending-change`;
- a specification the gate above does not pass — `specification`.

The log then closes on the stop, one line of its own after every other, `stop: <class> — <fact>`: «A run a
stop ended closes its orchestration log with one stop line: its class names the stop from the
list R3 holds, and its fact is the stopping report's own words.» (SPEC-008 R4) A goal's state is
read from that line, so nothing is appended after it — the measure's commit carries it.

A stop ends the route, never the measure: step 6 runs after it, and its commit is the one that
follows a stop.

## Report, and stop

Open as «A handoff opens with what needs the person, and explains after» (SPEC-006 R1)
states; what follows is the report that opening sits above.

Report, in this order: where `HEAD` stood when the run began; every commit this run made, by hash
and message, and the `git log` range that holds them, because the range is the review and it
belongs to a person; every input this skill decided rather than was told — the slug derived, the
target decided, the order taken — each disclosed; every step invoked with its outcome, and the
path of `orchestration.md`; every line the last `deliver.py --outstanding` printed of records
pinning no standard or another than their target declares, verbatim and as a fact; the review's
findings, relayed whole, with that report's own account
of which passes did not run; which nodes this run left decided by a test, which certifications
were refused again and with what remainder, and — for any testable remainder over a node no task
of this run implements — `trace.py --owed`'s closing invocation, relayed; the telemetry report the
measure wrote, by path, or the line saying why it could not read; what ended the run, where it ended early, with the stopping report's
doors verbatim and its recommendation where it made one, and whether the report called it a
judgment; and what this skill never did — no `/analyse`, no repair of any finding, no step
beyond the route. «A finding stops nothing» (SPEC-006 R4): a finding the review relayed is
reported, and what ended the run is a stop a step's own file names. Where this report says a
step proceeded, it lists the `--outstanding` run and the checks the step ran, with their output
verbatim — «Where a handoff says a step may proceed, it lists the checks it ran and their output verbatim» (SPEC-006 R4).

Then stop. The commit range is the review, and it belongs to a person.

## What you never do

- Invoke `/analyse`, or write into the specification root — the gate is the point of the design.
- Commit without a pathspec, sweep the tree, create a branch, push, stash, or rewrite history.
- Override, soften or skip any stop an entry point raised — its rules bind its invocation whole,
  and this skill's only grant over a stop is to relay it.
