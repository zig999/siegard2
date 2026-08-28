---
name: deliver-scope
description: Carries one stated scope end to end through the entry points the consumer rules name — /plan-work, /implement-task over each deliverable task, /review-change — committing between steps with a pathspec, recording each step in an orchestration log, and stopping at everything only a human settles. Use only where the human's own message states that the whole route is wanted — an end-to-end ask quoted verbatim, or a standing automation whose condition names this skill. An intent inferred from anything less is a stop. Not for a single phase (invoke that entry point directly), and never for /analyse — the specification is authored, reviewed and committed by a person before this skill runs.
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
gate → plan → commit → [deliver → commit, per task] → review → commit → report → stop
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
  python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --outstanding <delivery-root> <work-root> <target-source-root> <specification-root>
  ```

  run fresh before each delivery, never a reading of the plan or a memory of the last run. A stop
  the script reports is this skill's stop.

The steps:

1. **Plan.** Invoke `/plan-work` with the ask as the scope, the project root, the target and the
   slug. On a populated work root, this is that skill's ordinary evolution of the plan it holds;
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
   commit nothing further, and go to the report. A task whose delivery gave up is not
   re-attempted in this run: the same invocation again is a decision about cost, and it is the
   human's.
4. **Review.** When the deliverable set is empty, invoke `/review-change` from the last
   delivery's handoff: the tasks being every task this run delivered, the file set being the
   union of the paths their reports named. The run ends when the review record is written — the
   findings are relayed whole in the report and never acted on here: which route a finding
   deserves, or whether it deserves one, is the decision that skill deliberately does not make,
   and this skill inherits the same restraint. Repairing anything a finding names is a new ask.
   Commit the delivery root — `deliver-scope <slug>: review`.

**The orchestration log.** After each step, append one line to `orchestration.md` at the delivery
root — what was invoked, the commit that followed by its hash, and the outcome, one sentence per
line. It is a marker, never a node, exactly as `closure.md` is: no contract holds it, the
validator keeps it the way it keeps `intake/`, and it is the one place the run's own decisions —
the slug derived, the target decided, the order taken, the stop that ended it — survive the
conversation that made them.

## What ends the run

Every stop below ends the run with the doors the stopping report already carried, relayed
verbatim, and with the log's last line naming it. None is worked around, and none is retried:

- a `BLOCKING, from the specification —` note standing on every task the set has left;
- a specification silence — the `/analyse` invocation is the human's to take, always;
- a suite whose diagnosis names a disagreement between the two producers;
- a delivery that gave up, or an infrastructure failure the diagnosis read twice;
- a field `siegard.json` does not declare, or a standard that resolves nowhere;
- a pending change this skill did not make, anywhere the pathspec above reaches.

## Report, and stop

Report, in this order: where `HEAD` stood when the run began; every commit this run made, by hash
and message, and the `git log` range that holds them, because the range is the review and it
belongs to a person; every input this skill decided rather than was told — the slug derived, the
target decided, the order taken — each disclosed; every step invoked with its outcome, and the
path of `orchestration.md`; the review's findings, relayed whole, with that report's own account
of which passes did not run; what ended the run, where it ended early, with the stopping report's
doors verbatim; and what this skill never did — no `/analyse`, no repair of any finding, no step
beyond the route.

Then stop. The commit range is the review, and it belongs to a person.

## What you never do

- Invoke `/analyse`, or write into the specification root — the gate is the point of the design.
- Compose an invocation no report handed over, or fill a slot the authorization does not cover.
- Act on a finding, judge the work, or re-attempt a delivery that gave up.
- Commit without a pathspec, sweep the tree, create a branch, push, stash, or rewrite history.
- Infer the authorization — an ask that does not state the whole route takes a single entry
  point, and the report says which.
- Override, soften or skip any stop an entry point raised — its rules bind its invocation whole,
  and this skill's only grant over a stop is to relay it.
- Write `orchestration.md` as anything but append-only prose, or let a node contract near it.
