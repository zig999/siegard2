---
name: reconcile
description: Use when source changed without a rebind — edited by hand, resolved in a merge, or rewritten by a delivery while other nodes' bindings still claim it — or when the person asks to audit standing bindings or to adopt source no delivery wrote. Reads which nodes a named file set is bound to, holds the source to them through the conformance judgment, records the answer per node, and rebinds only what the judgment cleared. Not for changing the specification (/analyse), routing a wrong behavior into a task (/plan-work), reviewing a delivered task (/review-change), or writing source.
effort: medium
---

You reconcile source that changed without a rebind — whatever wrote it — with the specification
it is bound to, and you stop. One invocation, one file set.

A bind restamps only a delivering task's own nodes, so a binding goes stale other ways: a
correction typed in during an incident, a file resolved by hand in a merge, a delivery rewriting a
file other nodes' bindings still claim. The trace then asserts a digest that is no longer there,
and only `--check` says so.

What you produce is a rebind and the record that justifies it. **You never write source, and you
never write a specification node.** Where a node cannot be reconciled — the source now states
something that node does not hold — you bind that node nothing and hand back the doors that could
resolve it, without choosing between them. The nodes the judgment cleared are bound in the same
act: the judgment is per node, and so is the bind.

## Progress checklist

Copy this checklist into your working notes and tick each step as it closes. Where a step's
section is no longer in your context, read `${CLAUDE_PLUGIN_ROOT}/skills/reconcile/SKILL.md`
again before acting on it. `references/` is the directory beside that file: read a reference when
its step is reached, before acting on it.

```
- [ ] Inputs: file set, project root, target, slug, else one stop naming all; certifications,
      a rewrite or adoption only where named
- [ ] Root: bin/project.py <project-root>, or --here where none is named
- [ ] Tree: git status --porcelain -- <named paths> <proof paths> <specification root> prints
      nothing; siegard-trace.json clean; the target under git
- [ ] Contract: read schemas/reconciliation.json
- [ ] 1 Situate: spec.py; trace.py <target-source-root>; siegard-reconcile/<slug>.md free
- [ ] 2 Stage: trace.py --carry, --check, --stage into a fresh workspace: references/stage.md;
      certifications: references/certify.md; adoption: references/adoption.md
- [ ] 3 Judge: one conformance subagent per file, by waves; every return saved verbatim:
      references/judge.md; one coverage-auditor per certification: references/certify.md
- [ ] 3b Capture: run.py into siegard-reconcile/<slug>.returns, or skip and say so:
      references/capture.md
- [ ] 4 Fold: premise; trace.py --fold; trace.py --reconciliation: references/fold.md
- [ ] 5 Bind: trace.py --stage-release and its judges first, never skipped; then --bind-record
      --workspace, once: references/bind.md
- [ ] 6 Commit as reconcile <slug>; report: handoff.py --prepare; references/report.md;
      --save-report, --render; stop
```

## Terms

- **You** — the session that runs the skill.
- **The person** — whoever invoked the skill and decides what only a person decides.
- **Subagent** — an agent the skill spawns. The two here are
  `specification-conformance-reviewer` and `coverage-auditor`.
- **Stop** — the invocation ends: nothing more is written, and the report says why.
- **Refusal** — a script's non-zero exit naming what it refused. Quote it verbatim; never work
  around it.
- **Door** — an invocation of another entry point that the report hands the person, filled with
  everything known and ready to paste.

## Required inputs

A missing input is a stop, not a default:

1. **the file set** — every path this reconciliation covers, listed explicitly, each relative to
   the target source root. Named by the person. **Never discovered**: what a reconciliation writes
   is the one claim kept after every plan and delivery root is gone.
2. **the project root** — where `siegard.json` lives, named by the person. «Where the invocation
   names none, the project root is the git toplevel of the session's working directory, as
   `bin/project.py --here` resolves it, and only where that toplevel holds `siegard.json`»
   (SPEC-010 R6): there, `project.py --here` runs in place of the `project.py <project-root>` run
   below, and its `project_root:` line is the root. Its refusal is a stop.
3. **the target** — which of the project's target source roots these files sit under, by the key
   `siegard.json`'s `targets` names it. Where `targets` declares exactly one key and the
   invocation names none, that key is the target: decided and disclosed in the report, never
   asked.
4. **the slug** — this reconciliation's own name, under `siegard-reconcile/` at the target's git
   toplevel. A slug already taken is a stop and not a suffix: the record it would overwrite
   justifies a binding still in the trace.

Two optional inputs, and one mode, each named and never inferred:

- **certifications** — per node, the test file(s) the person offers as its proof and the registry
  step that runs them. Absent, every binding stays decided by reading. `references/certify.md`
  states how they are staged and judged.
- **a rewrite** — the person's statement that the files changed by one mechanical rewrite and
  nothing else, and the registry steps whose run shows the rewritten tree builds and passes. You
  transcribe what they state; you never read one off a diff and propose it. Absent, every drifted
  pair goes to a judge. `references/stage.md` states how it is staged.
- **adoption** — the file set is source no delivery wrote, and the invocation also names the
  **candidates**, the nodes `/analyse` wrote from material read from that source, which its report
  lists and which are never discovered here, and optionally the files kept **outside** the
  judgment. «A binding of adopted source rests on a reconciliation
  record whose judgment cleared the pair» (SPEC-005 R3). Without the word, a file the trace binds
  nothing to is reported and goes no further. `references/adoption.md` states the differences.

Run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/project.py <project-root>` once, before anything else.
`specification_root` and `targets` answer only from here; naming one in the invocation has no
effect. A field the file does not declare is a stop, and the report carries the `/siegard-config`
invocation ready to paste, naming the project root and every missing field. From here on, "the
target source root" is `targets[<the target>]`, and "the specification root" is
`specification_root` as resolved.

**No work root, no delivery root, no task, no plan.** The judgment already existed and was
reachable only through a delivery, which a hand edit does not have.

Absent inputs stop once, together: one stop names everything missing.

## Before anything: the tree

Here a pending change is the subject, not somebody's work in progress.

- **The named files, every proof a certification names and every candidate node's file must be
  committed.** `git status --porcelain -- <each named path> <each proof path> <the specification
  root>` must print nothing: a bind records a digest on both sides, and a digest of an uncommitted
  edit points at content the next checkout erases. Output is a stop naming what is pending;
  committing or discarding is the person's decision.
- **`siegard-trace.json` must be clean**, because it is what the invocation writes, and a diff says
  what this run did only from a committed state.
- **A target source root not under git control is a stop**: the record points at a commit that has
  to exist.

The rest of the repository is not this skill's business. The pathspec is the scope.

## Read the contract

Read `${CLAUDE_PLUGIN_ROOT}/schemas/reconciliation.json`. It is the single home of what a
reconciliation record may and must declare, with one example per outcome. The fold writes the
record against it; you author the premise, held to its `summary` and `files[].change`
descriptions. Never work from memory of it, and never restate it.

`${CLAUDE_PLUGIN_ROOT}` is set where this skill runs as an installed plugin. Where it is not, the
plugin root is the directory holding `schemas/` and `bin/` side by side — in a vendored install,
the `.claude/` directory this skill's tree sits under.

## The order

```
situate → stage → judge → capture → fold → bind → report → stop
```

Each judgment is a subagent's, in a clean context, and lives in its agent file.

- Spawn each by its plugin-scoped name, `siegard:<agent-name>`, never the bare form, which a
  consumer's own `.claude/agents/` can shadow.
- Only where you cannot spawn subagents, read the agent's file under the plugin root's `agents/`
  directory and apply its discipline in place, file by file in the same shape; the report says
  the pass ran inline. **Not even then where you wrote any node the judgment will read**, its own
  set or its candidates: that is grading your own writing. The stop is to report and wait, saying
  why the spawn failed — a spend or rate limit passes, and the person runs it again.
- A spawned subagent runs in the background, and the harness delivers a notification when it
  answers. You wait for that notification and nothing else — never a `sleep`, a scheduled wakeup,
  an agent listing or a message to the subagent — and save the return when the notification names
  it.

### 1. Situate

- **The specification must hold together.** Run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/spec.py
  <specification-root>`. Anything but a clean pass is a stop reported verbatim: the invocation
  does not repair a root an earlier one left broken.
- **The trace must hold together.** Run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py
  <target-source-root>`. A trace file that does not exist is a stop: nothing was ever bound here,
  and what the person wants is a delivery — or, for source no delivery wrote, an adoption, the one
  invocation that begins without a trace.
- **The record's path must be free.** `siegard-reconcile/<slug>.md`, at the git toplevel `git -C
  <target-source-root> rev-parse --show-toplevel` prints, beside `siegard.json` and
  `siegard-trace.json`. A path that exists is the stop input 4 describes.

### 2. Stage

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --carry <target-source-root>
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --check <target-source-root>
```

Drift is all `--check` reports: the `code` class lists one line per file, naming every binding
the change staled. Keep the lines whose path is in the file set. Then stage the whole file set
into a fresh workspace directory nothing commits (`mktemp -d`):

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --stage <target-source-root> <specification-root> \
    <slug> <workspace> <each named path> [--audit] [--certify <certifications file>] \
    [--rewrite <rewrite file>] [--node <each node the person named as written since the bind>]
```

It computes every node each file is bound to, writes the manifest, one node pack per file and the
candidate index, separates every pair whose re-judgment would buy nothing, and creates
`siegard-reconcile/<slug>.returns/` empty. Run it; never infer any of it, and never reconstruct a
node set by reading `siegard-trace.json` yourself. Read `references/stage.md` before acting on its
receipt: the path anchor, `--audit`, the states it separates, the `mechanical` tier, the rewrite,
and nodes written since the bind. **What is judged is every node the trace binds to the set,
never a chosen subset.**

### 3. Judge

Spawn one `siegard:specification-conformance-reviewer` subagent per file the manifest holds nodes
for, dispatched by the waves the staging receipt lists: one wave whole, in one message, then every
return of that wave saved before the next wave is spawned. A wave ends when `--save-return`
reports `0 pending` for it, read from the returns on disk; a count of notifications kept in the
session is never the signal. A launch the harness refuses ran no judge and is a wave cut too wide:
the report hands `--stage --concurrency <fewer>` ready to run again, and no judge is dispatched a
second time on the invocation's own account.

Read `references/judge.md` before spawning any: what each subagent is handed, the three kinds a
finding answers, and how each return is saved verbatim at its path under
`siegard-reconcile/<slug>.returns/`. For each entry the manifest holds under `certify`, spawn one
`siegard:coverage-auditor` subagent as `references/certify.md` states.

**Do not read the files yourself and decide.** The person's premise is that the source is
correct; answering from the context that accepted it is answering from the premise. **A subagent
answers once**: an unusable return is a fresh subagent with the prompt fixed, never a follow-up
question.

### 3b. Capture the run the mechanical tier and the rewrite are answered by

Where the staging separated nothing under `mechanical` and carried nothing under `rewritten`, skip
this step and say so in the report. Where it did, run the step(s) it named, once, as
`references/capture.md` states:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/run.py siegard-reconcile/<slug>.returns \
    --run <slug> --cwd <target-source-root> --timeout-seconds <the registry's bound> \
    --step <name>="<the registry's command>" [--step ...]
```

**A red step is a result, not a stop**, except a step the rewrite names. Never re-run to get a
green.

### 4. Fold

Write the premise — the one part of the record that is the person's — as `references/fold.md`
states: `title`, `summary`, `said` (the person's own words, verbatim), `target`, and one `files`
entry per named file with its `change`. Then:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --fold <target-source-root> <workspace> \
    <the premise> siegard-reconcile/<slug>.md \
    [--run siegard-reconcile/<slug>.returns/run/<slug>]
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --reconciliation <the record>
```

The fold writes the record whatever the judgment returned. **Never apply its rules by hand, and
never edit what the fold wrote.** Anything but a clean `--reconciliation` is a stop, reported
verbatim.

### 5. Bind

**Whatever the judgment cleared, and never anything else:**

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --bind-record <target-source-root> <specification-root> <the record> --workspace <workspace>
```

`--workspace` names the staging's own. Run it whether the judgment cleared everything or not, and
run it once. **This skill never passes `--replace`.** Read `references/bind.md` for what lands,
what it refuses and what its receipt names, and carry the receipt into the report.

### 6. Report

Commit the trace and `siegard-reconcile/<slug>.*` as the plugin's rules state: `reconcile <slug>`.

«The state a handoff opens with is a script's line, never the session's» (SPEC-006 R10). Run
`python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/handoff.py --prepare --skill reconcile --project
<project-root> --target <target> --language <en or pt-BR, the session's>` — with `--slug` only
where a live initiative's slug is what the `/plan-work` door carries, never this reconciliation's
own. Then read `references/report.md`: what the report holds, in order, and the doors it hands.
Write it through `bin/handoff.py --save-report <path>`, to the path its `report` names, filling
only the fields the skeleton left empty, and hand the person exactly what `handoff.py --render`
prints over the record: «A handoff opens with what needs the person, and explains after»
(SPEC-006 R1).

The doors the skeleton marks are the `/analyse` and `/plan-work` ones the report hands, each with
what its entry point answered or why nothing checked it; a `refuses` is said excluded beside its
`refused:` fact, never recommended. A refusal is answered by rewriting the field it names; a state
it says has moved, by running `--prepare` again and carrying its `state` and `state_from` whole.

Then stop.

## Adoption

The same order, with four differences the scripts hold: stage with `--adopt` over the ledger,
judge and fold as always, bind with `--bind-record --workspace`, and report what an adoption
adds. Read `references/adoption.md` at step 2.

## What this never does

- **It never writes source and never writes a specification node.** Both have entry points.
- **It never decides that a file is correct.** The person asserts that; the record holds the
  assertion as theirs.
- **It never certifies a test itself.** The fold writes `decided_by: test` from the auditor's
  `covered` and from nothing else.
- **It never decides that a node is testable.** That is the auditor's, read from the fact as the
  node states it; what closes a testable remainder is a test the person writes and offers again.
- **It is not a review.** It says nothing about coverage, the standard or proof; those are
  `/review-change`'s, over a delivery.
- **It commits what it wrote and nothing else** — never a source file, a push or a rewrite.
