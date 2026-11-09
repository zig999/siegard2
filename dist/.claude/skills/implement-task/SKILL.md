---
name: implement-task
description: Use when a request asks to implement, build, code or deliver one task the plan already holds. Writes the task's source and the tests that prove it through two subagents, runs the install, build and suite steps the project's standard declares through bin/run.py, writes and validates the implementation and proof records, binds the trace, and hands /review-change. Not for planning or decomposing work (/plan-work), analysing domain material (/analyse), reviewing what was written (/review-change), or more than one task.
effort: medium
---

You carry one planned task from the plan into written source and the tests that prove it, and
you stop. One invocation delivers one task, so each delivery can be reviewed on its own.

## Progress checklist

Copy this checklist into your working notes and tick each step as it closes. Where a step's
section is no longer in your context, read `${CLAUDE_PLUGIN_ROOT}/skills/implement-task/SKILL.md`
again before acting on it. `references/` is the directory beside that file: read a reference when
its step is reached, before acting on it.

```
- [ ] Inputs: task, project root, target, slug, else one stop naming all; standard: references/standard.md
- [ ] Root: bin/project.py <project-root>, or --here where none is named
- [ ] Plan: plan.py --check clean, else stop
- [ ] Tree: git status --porcelain over delivery root, target, task file, trace: nothing, else stop
- [ ] Contract: deliver.py --contract implementation, proof, finding
- [ ] 1 Situate: deliver.py --outstanding; BLOCKING note: references/blocking.md; re-delivery or
      stands: references/redelivery.md; deliver.py --standard, keep its three phase lines
- [ ] 2 Set up: run.py --run <epic>-<slug>-setup where the registry declares an install
- [ ] 3 Implement: read references/delegation.md; spawn siegard:task-implementer with its block;
      a return carrying `stands`, or none: references/implementer-returns.md
- [ ] 4 Build: run.py --run <epic>-<slug>-build; red: references/red-build.md; produces:
      references/substrate.md; read references/records.md; deliver.py --write-implementation
- [ ] 5 Prove: spawn siegard:test-author with the block references/delegation.md holds
- [ ] 6 Suite: run.py --run <epic>-<slug>-suite; red: references/red-suite.md; deliver.py --write-proof
- [ ] 7 Validate: deliver.py --unrecorded, then deliver.py; read references/finish.md
- [ ] 8 Bind: trace.py --bind-record; keep any stale-bindings receipt; commit: finish.md
- [ ] 9 Report: handoff.py --prepare; read references/report.md; --save-report, --render; stop
```

## Terms

- **You** — the session that runs the skill. Every step below is yours.
- **Subagent** — an agent the skill spawns.
- **Producer** — a subagent that writes what a delivery is made of — `task-implementer` the
  source, `test-author` the tests. The `failure-diagnostician` reads a red suite and writes
  nothing.
- **Re-enter** — send a subagent that has returned a new message in its own context, instead of
  spawning a fresh one. `references/delegation.md` says when.
- **Stop** — the invocation ends: nothing more is written, and the report says why.
- **Refusal** — a script's non-zero exit naming what it refused. Quote it verbatim; never work
  around it.
- **Door** — an invocation of another entry point that the report hands the person, filled with
  everything known and ready to paste. Taking it is the person's.

## Required inputs

A missing input is a stop, not a default:

1. **the task** — by identifier, named by the person or by a request that names exactly one. A
   request naming several is a stop that asks which. A request naming none is a stop unless the
   deliverable set step 1 computes holds exactly one task; that task is then decided and disclosed
   in the report, never asked.
2. **the project root** — where `siegard.json` lives, named by the person. «Where the invocation
   names none, the project root is the git toplevel of the session's working directory, as
   `bin/project.py --here` resolves it, and only where that toplevel holds `siegard.json`»
   (SPEC-010 R6): there, `project.py --here` runs in place of the `project.py <project-root>` run
   below, and its `project_root:` line is the root. Its refusal is a stop.
3. **the target** — the key in `siegard.json`'s `targets` of the target source root this task
   delivers into. Where `targets` declares exactly one key and the invocation names none, that key
   is the target: decided and disclosed, never asked.
4. **the initiative's slug** — `<slug>` names both the plan under the project's `work_root` and
   the delivery root under its `delivery_root`. The work side must already hold the task; the
   delivery side is created empty where absent. Where the invocation names none and `work_root`
   holds exactly one initiative without `closure.md`, that is the slug: decided and disclosed,
   never asked. A work root holding `closure.md` is a closed plan, and writing new source
   against it is a stop; reviewing what it delivered stays `/review-change`'s.

Run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/project.py <project-root>` once, before anything else.
`specification_root`, `targets`, `work_root` and `delivery_root` answer only from here; naming one
in the invocation has no effect. A field the file does not declare is a stop, and the report
carries the `/siegard-config` invocation ready to paste, naming the project root and every
missing field. From here on:

- "the work root" is `work_root/<slug>`;
- "the delivery root" is `delivery_root/<slug>`;
- "the target source root" is `targets[<the target>]`;
- "the specification root" is `specification_root` as resolved, required exactly as the plan
  validator requires it — while the plan is live, and ignored once it is closed.

Absent inputs stop once, together: one stop names everything missing, including the task where
the request named none and step 1's deliverable set holds more than one. An input a singleton
decided is not missing; the report discloses it instead of asking. One optional input, **the
project's standard**, resolves as `references/standard.md` states; read it before that stop,
which the standard can join.

## Before anything: the plan

Run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/plan.py --check <work-root> <specification-root>`.
Anything but a clean pass is a stop: report the output verbatim. A plan with problems is fixed
through `/plan-work`, and a stale index by whoever owns the plan; you never write into the work
root or the specification root.

## Before anything: the tree

Before any write, this must print nothing:

```
git status --porcelain -- <delivery-root> <target-source-root> <work-root>/task/<epic>/<slug>.md
```

and over the trace file. The commit at the end takes the roots you write, so they start clean, with
the one task file you read and pin. A pending change elsewhere in the work root is somebody else's
work in progress and does not stop you. Output is a stop: report what is pending. Committing,
discarding or overriding it is the person's decision. A root not under git control is the same stop.

## Read the contract

`${CLAUDE_PLUGIN_ROOT}/schemas/delivery-node.json` is the single home of what a delivery node may
and must declare. Run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --contract <kind>` for each
of `implementation`, `proof` and `finding`. Each prints one self-contained slice with every `$ref`
inlined. Steps 3 and 5 and the diagnosis hand their subagent the slice pasted whole, never the
file's path. Do not work from memory of a slice and do not restate one: the validator applies the
slice, not your memory of it.

Where `${CLAUDE_PLUGIN_ROOT}` is not set, the plugin root is the directory holding `schemas/` and
`bin/` side by side — in a vendored install, the `.claude/` directory this skill sits under.

## Every run is captured

**Nothing here is run by narration.** Every execution goes through
`${CLAUDE_PLUGIN_ROOT}/bin/run.py`, with the commands the project's registry declares, into a
directory under the delivery root's `run/`, with `--excerpt 40`. A command run any other way did not
happen. `run.py` refuses a run name that already exists, so every attempt keeps its own directory
and the record points at the one that passed; iterating is allowed. **You run; the subagents do
not.** A red run goes back to the producer that wrote the files, and you never patch a file to make
a run pass.

Set up, build and suite run only where the standard names commands. Where none was named, or the
registry declares none, they do not run, the report says so, and you hand over source alone — a
narrower answer, never presented as a clean one.

## The producers

Steps 3 and 5 belong to the producers, each spawned in a clean context. The judgment of each lives
in the agent's file, not here. Code and tests written in one pass agree by construction, including
where both are wrong, so the two stay separate. Spawn by the plugin-scoped name,
`siegard:<agent-name>`, never the bare form, which a consumer's own `.claude/agents/` can shadow.
Only where the session cannot spawn subagents, read the agent's file under the plugin root's
`agents/` directory, apply its discipline in place, and say in the report which steps ran inline.
Before the first spawn, read `references/delegation.md`.

### 1. Situate

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --outstanding <delivery-root> <work-root> <target-source-root> <specification-root>
```

It validates the delivery and lists every task without a record and what it waits on: a dependency
with no record yet, an artifact a task of this plan produces and the tree does not hold, a standing
blocking note. Then it lists the set deliverable now, which decides an unnamed task as input 1
states. Anything but a clean run is a stop, reported verbatim. Two answers are stops before anything
is written:

- **A task this one builds on has no record.** Stop and name it: a dependency is delivered first.
- **The named task is not in the plan.** Stop, and end the report with a `/plan-work` invocation
  naming the project root, the target by its key and the slug, leaving only the scope for the
  person to state. Name no roots in it: `/plan-work` reads them from the project file.

Then open the task file and read its `## Notes`: **an entry opening
`BLOCKING, from the specification —` is a stop**, whether or not `--outstanding` listed it.
`references/blocking.md` says what the stop quotes and the two doors it hands.

A record already at the path this task computes to makes this a re-delivery; a task carrying
`stands` delivers without writing source; and only the person names a proof-only re-delivery. For
any of the three, read `references/redelivery.md` before anything is written.

Where a standard was named, check it before anything is written:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --standard <the project's registry> --against <target-source-root> --specification <specification-root>
```

**Where the task declares `produces`, drop `--against`** (`references/substrate.md`); its refusals
are in `references/standard.md`. Anything but a clean pass is a stop, reported verbatim. A clean
pass prints each delivery phase — setup, build, suite — composed for `bin/run.py`, timeout
included. **Keep those three lines; the runs below paste them in verbatim**, and the validator
holds each captured run to exactly that selection.

Then read the rest of the task file and the plan's inventory nodes, found through `plan.json`. Hand
the implementer only the inventory nodes whose `area` reaches where this task lands: an inventory of
another territory carries conventions this task must not follow. Read the epic only for what it
covers. Read no other task.

### 2. Set up

Where the standard declares a command whose role is `install`, run it before anything is written,
so the implementer reads the types of what the project already declares:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/run.py <delivery-root> --run <epic>-<slug>-setup --cwd <target-source-root> --excerpt 40 <the setup phase step 1's registry check printed>
```

Three cases skip it, and the report says which: the task `produces` the manifest, so the first
install is the build below; the registry declares no install; or no standard was named, and you
hand over source alone. A red setup is a stop before a line is written: what the installer printed
is not yours to guess at or route around.

### 3. Implement

Spawn a `siegard:task-implementer` subagent — its judgment lives at
`${CLAUDE_PLUGIN_ROOT}/agents/task-implementer.md` — and hand it the step 3 block of
`references/delegation.md`, filled by the rules beside it. Every path is absolute and the slice
pasted.

A return carrying `stands`, or no mapping at all, is never improvised around: read
`references/implementer-returns.md`.

### 4. Build

Run every step the registry declares except the one whose role is `suite`, in its order, install
first so whatever the implementer added to the manifest is real before anything reads it:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/run.py <delivery-root> --run <epic>-<slug>-build --cwd <target-source-root> --excerpt 40 <the build phase step 1's registry check printed>
```

The timeout and the step list are the registry check's `build:` line, verbatim — the validator
holds the run to that line. `run.py` stops at the first step that does not pass. Where that step
is one the registry check listed as deciding a constraint, the red is that constraint's: name the
constraint beside the step when the run goes back to the producer and again in the report.

A task declaring `produces` may run less than that: read `references/substrate.md` before the run.
A red build: read `references/red-build.md` and follow it — the retries, a red only a test
answers, and a red no change to this task's own files answers.

Write `implementation/<epic>/<slug>.md` through the writer, never by hand, with the task's epic and
slug, because the path is what names the task a record answers:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --write-implementation <delivery-root> task/<epic>/<slug> --target <the target's key> --task-file <absolute path of work-root/task/<epic>/<slug>.md> --run run/<the build run that passed> --standard <the registry's path relative to the target source root> --standard-file <absolute path of the registry> --from <the subagent's transcript> [--what "…"]... [--note "…"]...
```

What the writer reads, stamps and writes in the body is in `references/records.md`; read it before
the first write.

### 5. Prove

Where the task declares `produces`, read `references/substrate.md` first: a task delivered as the
substrate alone writes no proof.

Spawn a `siegard:test-author` subagent — its judgment lives at
`${CLAUDE_PLUGIN_ROOT}/agents/test-author.md` — and hand it the step 5 block of
`references/delegation.md`, filled by the same rules as at step 3.

Each node is an obligation of the proof, not a reference: «Where a node the task implements states a
fact a finite test decides, the proof carries a test that fails if that fact stops holding, whole,
and names the node on that test» (SPEC-004 R10). The test-author decides whether a finite test
decides each fact. A node it leaves without a test it names under `untested` with why. A node under
neither is one the report says is open.

### 6. Suite

Run every step the registry declares, in order, ending with the one whose role is `suite`:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/run.py <delivery-root> --run <epic>-<slug>-suite --cwd <target-source-root> --excerpt 40 <the suite phase step 1's registry check printed>
```

The timeout and the step list are the registry check's `suite:` line, verbatim. The build's checks
run again: a rule about where a test sits or how it is named reaches files new since the build.

A red suite: read `references/red-suite.md` and follow it — the diagnosis owed, the five ways out,
and the one that is forbidden. Where the registry declares no command at all, this step does not
run, the tests stand unexecuted, and the report says so. A task delivered as the substrate alone
reaches neither this step nor step 5.

Write `proof/<epic>/<slug>.md`, same epic and slug, through the writer the same way; its stamps and
its `--note` lines are in `references/records.md`:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --write-proof <delivery-root> task/<epic>/<slug> --target <the target's key> --run run/<the suite run that passed> --standard <the registry's path relative to the target source root> --standard-file <absolute path of the registry> --from <the subagent's transcript> [--what "…"]... [--note "…"]...
```

### 7. Validate, and derive the delivery

When both records are written, hold the tree to them — every record you wrote, and on a
proof-only re-delivery the standing implementation record beside the new proof:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --unrecorded <target-source-root> <implementation record> [<proof record>]
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py <delivery-root> <work-root> <target-source-root> <specification-root>
```

How each printed path is named, what `uncarried:` means, what the validator holds and why fixing
means form and never knowledge are in `references/finish.md`.

### 8. Bind the trace

Name the record you just wrote, once:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --bind-record <target-source-root> <specification-root> <the implementation record>
```

What the bind binds, refuses and may print — a stale-bindings receipt the report keeps whole — is
in `references/finish.md`.

### 9. Report, and stop

«The state a handoff opens with is a script's line, never the session's» (SPEC-006 R10). Run
`python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/handoff.py --prepare --skill implement-task --project
<project-root> --slug <slug> --target <target> --language <en or pt-BR, the session's>`. Write the
full report — every item `references/report.md` lists, in its order — through `bin/handoff.py
--save-report <path>`, to the path its `report` names, and fill only the fields the skeleton left
empty. Hand the person exactly what `handoff.py --render` prints over the record; it opens with what
needs the person — «A handoff opens with what needs the person, and explains after» (SPEC-006 R1).
The doors it marks are the `/review-change` and `/reconcile` ones this report hands, each with what
its entry point answered: a `refuses` is said excluded beside its `refused:` fact, never
recommended. A refusal is answered by rewriting the field it names. A state it says has moved is
answered by running `--prepare` again and carrying its `state` and `state_from` whole.

Then stop. The commit is the review, and it belongs to a person.

## What you never do

- Write or edit `delivery.json` by hand.
- Record a status, a readiness, an approval or a progress figure — the contract has no such field,
  and prose does not hold one either.
- Judge whether the work is correct, done well enough, or fit to merge: a producer that certified
  its own output would be the validator of its own work.
- Run a command the project's registry does not declare, or compose one. Every step is the
  registry's string, run through `bin/run.py`.
- Write the tests in the context that wrote the source, except on the inline fallback, declared in
  the report.
- Commit past what you wrote, or stash, branch, push or rewrite. A dirty tree is
  reported, and what to do with it is the person's call.
- Record which rules of the standard were in scope: the pin and the files written already answer
  it.
- Treat a disclosed departure as leave to depart. Disclosure settles nothing: the review holds the
  same source to the same rules and is not shown what was disclosed.
