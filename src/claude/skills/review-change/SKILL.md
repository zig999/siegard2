---
name: review-change
description: Use when a request asks to review, check, audit or verify a change that a delivered task produced. Judges whether the tests prove the task's criteria, whether the source states only what the specification holds (restamping the bindings that judgment clears), whether it follows the project's standard, and why a captured run failed; runs the steps that standard declares and records the findings under the delivery root. Not for writing or fixing source (/implement-task) or planning (/plan-work), and never an approval — what the evidence means is the person's to decide.
effort: medium
---

You review a delivered change and report what is there. One invocation, one review.

What you produce is evidence. Nothing here computes a verdict, a severity, a ranking or a
decision about the change: a finding nobody can disagree with is a decision wearing a finding's
clothes. The person decides, reading what you wrote.

## Progress checklist

Copy this checklist into your working notes and tick each step as it closes. Where a step's
section is no longer in your context, read `${CLAUDE_PLUGIN_ROOT}/skills/review-change/SKILL.md`
again before acting on it. `references/` is the directory beside that file: read a reference when
its step is reached, before acting on it.

```
- [ ] Inputs: tasks, file set, project root, target, slug, review name, else one stop naming all;
      the standard and the invocation's steps or run: references/standard.md
- [ ] Root: bin/project.py <project-root>, or --here where none is named
- [ ] Checks: plan.py --check and deliver.py --check, else stop; git status --porcelain
      -- <delivery-root> prints nothing
- [ ] Contract: deliver.py --contract coverageEntry, unpairedTest, finding
- [ ] 1 Situate: criteria from the task files; deliver.py --standard --against
      (references/standard.md); trace.py --check (references/trace.md); trace.py --stage --review
      (references/staging.md)
- [ ] 2 Capture: run.py --run <review-name> --cwd <target-source-root>; the registry's steps,
      then the invocation's
- [ ] 3 Passes: coverage, conformance by waves, standard, certification, failures:
      references/passes.md
- [ ] 3b Fold and bind: premise; every return saved verbatim; --fold; --reconciliation;
      --bind-record --workspace: references/fold-and-bind.md
- [ ] 4 Compose: review/<review-name>.md, frontmatter by yaml.safe_dump; deliver.py --node:
      references/compose.md
- [ ] 5 Validate: deliver.py --review; its output verbatim
- [ ] 6 Report: handoff.py --prepare; read references/report.md; deliver.py --findings;
      --save-report, --render; stop
```

## Terms

- **You** — the session that runs the skill.
- **Subagent** — an agent the skill spawns. The four here are `coverage-auditor`,
  `specification-conformance-reviewer`, `standard-conformance-reviewer` and
  `failure-diagnostician`.
- **Stop** — the invocation ends: nothing more is written, and the report says why.
- **Refusal** — a script's non-zero exit naming what it refused. Quote it verbatim; never work
  around it.
- **Door** — an invocation of another entry point that the report hands the person, filled with
  everything known and ready to paste.

## Required inputs

A missing input is a stop, not a default:

1. **the tasks under review** — by identifier, each already holding an implementation record.
   Named by the person, or by the invocation that delivered them; a review that chose its own
   subject reviews something nobody asked about.
2. **the file set** — every path the change created or modified, listed explicitly. Read it from
   those tasks' implementation and proof records; where the change reached further, the person
   says so. **Never discovered**: a clean result over a set the review chose would not say what
   it was clean over.
   - Each path is relative to the target source root, spelled exactly as the records spell it.
     Resolve it against that root to open the file, and state every finding with the same
     spelling; a scope's `under` is stated against the same anchor.
   - The validator holds the set to the records: every path their implementation and proof records
     say they wrote, and every path an implementation record says it `stands` at. A review over
     fewer is refused.
   - A path a record names that the target source root no longer holds, or that lies outside that
     root, is not in the set. «A path the records name that the target source root no longer
     holds — a file the delivery deleted — or that lies outside that root has no bytes a review
     reads: no review is held to list it, and the review's report names it as not read.»
     (SPEC-004 R22)
3. **the project root** — where `siegard.json` lives, named by the person. «Where the invocation
   names none, the project root is the git toplevel of the session's working directory, as
   `bin/project.py --here` resolves it, and only where that toplevel holds `siegard.json`»
   (SPEC-010 R6): there, `project.py --here` runs in place of the `project.py <project-root>` run
   below, and its `project_root:` line is the root. Its refusal is a stop.
4. **the target** — the key in `siegard.json`'s `targets` naming the target source root this
   change reaches. Where `targets` declares exactly one key and the invocation names none, that
   key is the target: decided and disclosed in the report, never asked.
5. **the initiative's slug** — the plan the tasks belong to, and the delivery root taking this
   review's record: `<slug>` under the project's `work_root` and `delivery_root`. Where the
   invocation names none and the `work_root` holds exactly one initiative, that is the slug:
   decided and disclosed, never asked.
6. **this review's own name** — names `review/<review-name>.md` under the delivery root, the run
   this review captures, and the reconciliation record its conformance pass writes at
   `siegard-reconcile/<review-name>.md`, at the target's git toplevel. Named by the person, or by
   `/deliver-scope` under the rule its own file states; where the invocation names none, it is
   the initiative's slug. A name already taken in any of the three places is a stop, never a
   suffix: `bin/run.py` refuses a run name that exists, `trace.py --stage` refuses a
   reconciliation slug that exists, and a second review of one initiative names itself.

Run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/project.py <project-root>` once, before anything else.
`specification_root`, `targets`, `work_root` and `delivery_root` answer only from here; naming
one in the invocation has no effect. A field the file does not declare is a stop, and the report
carries the `/siegard-config` invocation ready to paste, naming the project root and every
missing field. From here on:

- "the delivery root" is `delivery_root/<slug>`, and "the work root" is `work_root/<slug>`;
- "the target source root" is `targets[<the target>]`;
- "the specification root" is `specification_root` as resolved, required exactly as the plan
  validator requires it: while the plan is live, and ignored once it is closed.

Two optional inputs, **the project's standard** and **steps the invocation names, or a run
already captured**, resolve as `references/standard.md` states; read it before the stop of absent
inputs, which the standard can join. Between them they decide whether the standard pass and the
failures pass run. Absent inputs stop once, together: one stop names everything missing.

## Before anything: the plan, the delivery, the tree

Run both checks. Either output is a stop, reported verbatim:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/plan.py --check <work-root> <specification-root>
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --check <delivery-root> <work-root> <target-source-root> <specification-root>
```

Neither repair is yours: a plan is fixed through `/plan-work`, a record through
`/implement-task`. Where both pass, the report lists them with their output verbatim: «Where a
handoff says a step may proceed,
it lists the checks it ran and their output verbatim» (SPEC-006 R4). These two are the review's
only stops before its own validator. «A finding stops nothing» (SPEC-006 R4): a finding this
review records is reported, never a stop.

A review carries no pin: it answers the criteria its tasks state today, and `--review` in step 5
holds the review being written. An earlier review over
a task that changed since is never refused for it: «a task some review names and none answers as
it stands is owed a review, and a review written before the task or its records changed is never
refused for it» (SPEC-004 R22). The check above is no stop on the review that answers the change.

Before any write, `git status --porcelain -- <delivery-root>` must print nothing; a pending change
elsewhere is somebody else's work. A dirty delivery root is reported, and what to do with it is
the person's call. The target source root, which holds the change, is not held to this.

## Read the contract

`${CLAUDE_PLUGIN_ROOT}/schemas/delivery-node.json` is the single home of what a delivery node may
and must declare. Three passes need only a slice of it:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --contract coverageEntry
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --contract unpairedTest
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --contract finding
```

Each prints one self-contained slice, every `$ref` inlined, which the pass hands its subagent
verbatim. Never work from memory of a slice and never restate it.

`${CLAUDE_PLUGIN_ROOT}` is set where this skill runs as an installed plugin. Where it is not, the
plugin root is the directory holding `schemas/` and `bin/` side by side — in a vendored install,
the `.claude/` directory this skill's tree sits under.

## The order

```
situate → capture → pass → compose → validate → report → stop
```

Each pass is another judge's: a subagent this framework ships, in a clean context, whose judgment
lives in its agent file and not in your memory of it.

- Spawn each by its plugin-scoped name, `siegard:<agent-name>`, never the bare form, which a
  consumer's own `.claude/agents/` can shadow. Reading the agent's file yourself is the fallback,
  never the spawn.
- Only where you cannot spawn subagents, read the agent's file under the plugin root's
  `agents/` directory and apply its discipline in place; the report says which passes ran inline.
- A spawned subagent runs in the background, and the harness delivers a notification when it
  answers. You wait for that notification and nothing else — never a `sleep`, a scheduled wakeup,
  an agent listing or a message to the subagent — and save the return when the notification names
  it.

### 1. Situate

Read the indexes, not the trees; the checks passed, so both are current. From `plan.json`, take
each task under review and the nodes it implements, and read each task file for its criteria,
quoted exactly. From `delivery.json`, take each task's implementation and proof records: the file
set, what the implementation inferred and departed from, and what the proof left unproven or
contested. Read nothing else in either root; the node files belong to the passes.

Then, in this order:

1. Where a standard is named, take it in before anything runs, with `deliver.py --standard
   --against` and the pin of its text, as `references/standard.md` states.
2. Run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --check <target-source-root>` and read it as
   `references/trace.md` states. **It is neither a stop nor a finding.**
3. Stage the conformance pass with `trace.py --stage --review` into a fresh workspace directory
   nothing commits, as `references/staging.md` states: every path of the file set, `--node` for
   each node the tasks implement, and `--demonstrated` for each proof record of the tasks under
   review. Run it; never infer any of it, and never reconstruct a node set by reading
   `siegard-trace.json` yourself.

### 2. Capture

Run every step the standard declares, in the order it declares them, followed by any the
invocation added, once, into a run named for this review:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/run.py <delivery-root> --run <review-name> --cwd <target-source-root> --timeout-seconds <the largest of the steps'> --step <name>="<command>" [--step ...]
```

The working directory is the target source root, stated rather than defaulted. Every string is
the project's — the registry's commands and its per-step bounds; nothing here composes a command,
infers one from a tree, or supplies a number.

- Where the registry declares no command for a step one of its rules names, that rule is decided
  by nothing, and the report says so by name.
- **This runs even where `/implement-task` already ran the same steps green**: two deliveries that
  each passed alone are not a change that passes together. Every run lands on disk under a name
  nothing may reuse, before any judgment is made of it.
- Where the invocation named a run already captured, use it and run nothing. Where the registry
  declares no command and the invocation named neither steps nor a run, the failures pass does not
  run and the record says so.
- A run whose outcome says nothing executed — a command not found, a step terminated — is still
  diagnosed: a run that could not execute is a finding, not an absent input. A run in which
  everything passed is the one case where the failures pass does not run. The run is recorded
  either way, and the validator holds it to the registry's steps by name, by command and by
  directory, and refuses a review over a registry declaring commands that names no run at all.

### 3. The passes

Four passes, independent, in any order or together, plus the certification a staged proof claim
owes. Read `references/passes.md` before spawning any: it states what each subagent is handed.

- **coverage** — one `siegard:coverage-auditor` subagent over the criteria and the test files.
- **conformance** — one `siegard:specification-conformance-reviewer` subagent **per file the
  staging manifest holds**, dispatched **by the waves the staging receipt lists**: one wave whole,
  in one message, then every return of that wave saved before the next wave is spawned. A wave
  ends when `--save-return` reports `0 pending` for it, read from the returns on disk; a count of
  notifications kept in the session is never the signal. A launch the harness refuses is a wave
  cut too wide, reported with `--stage --concurrency <fewer>` ready to run again, and never a
  subagent dispatched a second time on its own.
- **standard** — where a standard is named, `deliver.py --standard --reading --for` over the file
  set, then one `siegard:standard-conformance-reviewer` subagent; where none is, the pass does not
  run and the record says the project has authored none.
- **certification** — where the staging holds entries under `certify`, one
  `siegard:coverage-auditor` subagent per node, handed the certification pack.
- **failures** — where the run did not pass, one `siegard:failure-diagnostician` subagent.

### 3b. Fold and bind what the conformance pass read

Read `references/fold-and-bind.md` and run it: the premise, every return saved verbatim at its
path under `siegard-reconcile/<review-name>.returns/`, then `--fold`, `--reconciliation`, and
`--bind-record --workspace`.
**Never apply the fold's rules by hand, and never edit what the fold wrote.** The bind writes only
what the judgment cleared, never with `--replace`. With no trace file, this step does not run.

### 4. Compose

Write `review/<review-name>.md` under the delivery root, under the name input 6 fixed, as
`references/compose.md` states: its frontmatter emitted by `python3 -c` calling `yaml.safe_dump`,
every finding's pass stamped by you, and a body of exactly `## What it is` then `## Notes`. Check
the file on its own as soon as it is composed:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --node <file> <delivery-root>
```

### 5. Validate, and derive the delivery

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --review <review-name> <delivery-root> <work-root> <target-source-root> <specification-root>
```

This validates the review against the contract, and against the plan: every task named is
delivered, the coverage pass answers for every criterion and nothing else, `reviewed` lists every
file the records name, the failures counted match the findings, the run exists, and every finding
sits in a file of the set. Where the standard pass ran, it reads the registry fresh: every citation
names a rule it declares, leaves to a reading, and whose scope reaches the finding's file. Then it
derives `delivery.json`. **Never write or edit `delivery.json` yourself.** Report the
output verbatim, and never describe the review as sound while the command exits non-zero.

**Fixing means form, never judgment.** A criterion paraphrased instead of quoted, a finding
attributed to a pass that did not run, a citation hung on a rule that does not govern the file —
yours to correct. A finding is never dropped and a count is never lowered to make the two agree:
where they disagree, find out which one is wrong. A state is never raised to make coverage look
better, and a pass that did not run is never recorded as having run.

### 6. Report, and stop

«The state a handoff opens with is a script's line, never the session's» (SPEC-006 R10). Run
`python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/handoff.py --prepare --skill review-change --project
<project-root> --slug <slug> --target <target> --language <en or pt-BR, the session's>`, then read
`references/report.md`: what the report holds, in order, the findings first as counts. Write it
through `bin/handoff.py --save-report <path>`, to the path its `report` names, filling only the
fields the skeleton left empty, and hand the person exactly what `handoff.py --render` prints over
the record: «A handoff opens with what needs the person, and explains after» (SPEC-006 R1).

This report hands no invocation, so the skeleton marks no door; the findings' grouping line goes
in the record. Where a finding's route is handed as a decision, it is «the person's own decision»
(SPEC-006 R3), with what each door assumes is true and what would settle it. A refusal is answered
by rewriting the field it names; a state it says has moved, by running `--prepare` again and
carrying its `state` and `state_from` whole.

Then stop. Do not compute a verdict, rank the findings, decide what blocks, open work from them,
or fix any of them. A disagreement a proof record holds stays a disagreement. `git diff` over the
delivery root is this review's own review, and what the findings mean is the person's.

## What you never do

- Fix, edit or rewrite any source or test you reviewed: you hold no grant to, and a reviewer that
  could edit what it flagged leaves nothing for anyone to disagree with.
- Discover the file set, widen it, or narrow it to the readable paths. A path the root holds that
  cannot be read stops its pass and is reported; a deleted path, or one outside the root, was never
  in the set.
- Run anything but the runner this framework ships, and never rerun it to get a different result:
  a second run is a second name, and the first one's evidence stays on disk.
- Show the standard pass what an implementation record disclosed: a pass told which departures
  were already admitted is a pass the producer shaped. It reads the source; the person reads both
  records.
- Write into the work root, the specification root, or the target source root. The one write
  outside the delivery root is the fold and bind — `siegard-reconcile/<review-name>.md`, its
  returns, and `siegard-trace.json`, at the target's git toplevel.
- Commit, stash, or otherwise change the consumer's git state.
