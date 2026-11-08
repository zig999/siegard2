---
name: plan-work
description: Use when a request asks to plan or decompose work over a domain the specification holds, to route a bug found by running the delivered system, to owe a node its test, or to close a finished plan. Turns a stated scope and a validated specification into inventory, epics and tasks — each task naming the nodes it implements — validates the plan and derives plan.json; a fact the specification does not state is decided blind to the task cut and disclosed in the decision log. Not for analysing domain material (/analyse), and not for writing source code or tests.
argument-hint: "<project-root> target <key> slug <slug> — <the scope, or the increment, in prose>"
effort: medium
---

You turn a scope into a development plan, and you stop. One invocation, one increment: the first
fills an empty work root, and every later one evolves the plan it already holds — same order, same
discipline.

## Progress checklist

Copy this checklist into your working notes and tick each step as it closes. Where a step's
section is no longer in your context, read `${CLAUDE_PLUGIN_ROOT}/skills/plan-work/SKILL.md` again
before acting on it. `references/` is the directory beside that file: read a reference when its
step is reached, before acting on it.

```
- [ ] Inputs: scope, project root, target, slug, else one stop naming all; standard: references/standard.md
- [ ] Mode: corrective, decided-fact or proof increment, or closing? read its reference first:
      references/corrective.md, references/decided-fact.md, references/proof.md, references/closing.md
- [ ] Root: bin/project.py <project-root>, or --here where none is named
- [ ] Specification: spec.py <specification-root> clean, else stop
- [ ] Tree: git status --porcelain -- <work-root> <specification-root> prints nothing, else stop
- [ ] 1 Situate: spec.py --digest; grep the scope's terms; every constraints/ node; plan.py --unplanned;
      spec.py --impact; plan.py --check on a populated root; deliver.py --standard --against
- [ ] 2 Inventory: scope under intake/ (layout under intake/layout/); spawn siegard:codebase-surveyor
- [ ] 3 Decompose: spawn siegard:backlog-decomposer; write the epics; hold the skeletons
- [ ] 4 Implement against: spawn one siegard:execution-contract-binder per skeleton, together;
      unstated notes: references/unstated.md; every other note: references/notes.md; plan.py --node
- [ ] 5 Validate: plan.py --check, then plan.py (--standard --against where named)
- [ ] 6 Report: handoff.py --prepare; read references/report.md; --save-report, --render; stop
```

## Terms

- **You** — the session that runs the skill.
- **Subagent** — an agent the skill spawns. The four here are `codebase-surveyor`,
  `backlog-decomposer`, `execution-contract-binder` (the binder) and `unstated-fact-decider` (the
  decider).
- **Stop** — the invocation ends: nothing more is written, and the report says why.
- **Refusal** — a script's non-zero exit naming what it refused. Quote it verbatim; never work
  around it.
- **Door** — an invocation of another entry point that the report hands the person, filled with
  everything known and ready to paste. Taking it is the person's.

## Required inputs

A missing input is a stop, not a default:

1. **the scope** — what the person wants developed, in prose, plus any files it references.
2. **the project root** — where `siegard.json` lives, named by the person. «Where the invocation
   names none, the project root is the git toplevel of the session's working directory, as
   `bin/project.py --here` resolves it, and only where that toplevel holds `siegard.json`»
   (SPEC-010 R6): there, `project.py --here` runs in place of the `project.py <project-root>` run
   below, and its `project_root:` line is the root. Its refusal is a stop.
3. **the target** — which of the project's target source roots this plan reaches, by its key in
   `siegard.json`'s `targets`. A key the file does not hold is a target nobody declared. Where
   `targets` declares exactly one key and the invocation names none, that key is the target:
   decided and disclosed in the report, never asked.
4. **the initiative's slug** — this plan's own subdirectory under the project's work root. Empty
   is the ordinary first run; populated, the invocation changes the plan it holds. A slug whose
   directory holds `closure.md` is a closed plan, and planning over it is a stop: a new initiative
   names a new slug, where the delivered work returns as inventory through the survey.

Run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/project.py <project-root>` once, before anything else.
`specification_root`, `targets` and `work_root` answer only from here; naming one in the
invocation has no effect. A field the file does not declare is a stop, and the report carries the
`/siegard-config` invocation ready to paste, naming the project root and every missing field. From
here on, "the specification root" is `specification_root` as resolved, "the target source root"
is `targets[<the target>]`, and "the work root" is `work_root/<slug>`.

One optional input, **the project's standard**, resolves as `references/standard.md` states; read
it before the stop of absent inputs, which the standard can join. Absent inputs stop once,
together: one stop names everything missing.

### The modes

The person names a mode in the invocation; it is never inferred from the tree. Each reads its
reference before anything else is done:

- **Closing** — the person declares the initiative over. Needs the ask with its why, the project
  root and the slug; reads neither the specification nor the target. `references/closing.md`.
- **A corrective increment** — one wrong behavior in code already delivered. Needs all four inputs
  and the file the behavior lives in. `references/corrective.md`.
- **A decided-fact increment** — a fact a delivery stopped over. Needs all four inputs, the fact as
  the stop quoted it and the task that delivery was for. `references/decided-fact.md`.
- **A proof increment** — facts a test decides, held by delivered code and proven by none. Needs all
  four inputs, with the facts it names as its scope. `references/proof.md`.

Everything else is the ordinary route below.

## Before anything: the specification

A planning invocation reads the specification; a closing one does not. Run:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/spec.py <specification-root>
```

Anything but a clean pass is a stop: report the output verbatim. A specification with problems is
fixed through `/analyse`; you write into the specification root only through step 4's
decided-fact route. A task names the nodes that govern it by identity and carries no pin: it reads
the specification as it stands when it is read, and the specification does not change while a
plan is live, by convention.

## Before anything: the tree

Before any write, `git status --porcelain -- <work-root> <specification-root>` must print nothing;
a closing invocation names the work root alone. The review is `git diff` over those roots, and a
diff shows only this invocation when they start clean. Output is a stop: report what is pending.
Committing, discarding or overriding it is the person's decision. A root not under git control is
the same stop.

## Read the contract

`${CLAUDE_PLUGIN_ROOT}/schemas/plan-node.json` is the single home of what a plan node may and must
declare. `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/plan.py --contract <kind>` prints one
self-contained slice, every `$ref` inlined. **Each step prints the slice it hands over, narrowed to
what that subagent writes**: `--contract inventory` at step 2, `--contract epic` and `--contract
task --without implements` at step 3, `--contract task --fields implements` at step 4. A field a
subagent must not fill is never offered to it, and `plan.py` refuses a field name the branch does
not declare. Hand each slice verbatim, never its path; do not work from memory of a slice and do
not restate one.

`${CLAUDE_PLUGIN_ROOT}` is set where this skill runs as an installed plugin. Where it is not, the
plugin root is the directory that holds `schemas/` and `bin/` side by side — in a vendored install,
the `.claude/` directory this skill's tree sits under. Every path below resolves the same way.

## The order

```
situate → inventory → decompose → implement-against → validate → report → stop
```

Steps 2, 3 and 4 belong to subagents, each spawned in a clean context, and inside step 4 each fact
the specification turns out not to state goes to a decider of its own, blind to the cut that
surfaced it. The judgment of each lives in the agent's file, not here.

- **Spawn a subagent by its plugin-scoped name**, `siegard:<agent-name>`, never the bare form,
  which a consumer's own `.claude/agents/` can shadow.
- **Wait for the notification.** A spawned subagent runs in the background, and the harness
  delivers a notification when it answers. You wait for that notification and nothing else —
  never a `sleep`, a scheduled wakeup, an agent listing or a message to the subagent — and read the
  return when the notification names it.
- **The binder's isolation is the point.** It arrives with no memory of how the tasks were cut, so
  the specification is read for what it says today, never to fit a task.
- **Only a spawn that was attempted and failed opens the inline route**: read the agent's file
  under the plugin root's `agents/` directory, apply its discipline in place, and carry the
  failure verbatim in the report beside the step's name. A session judged unable without an
  attempt gives the isolation up on a guess.

### 1. Situate

Specification nodes carry no title or summary of their own, so narrow before opening anything:

- **The specification.** `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/spec.py --digest
  <specification-root>` lists every node's identity. Grep the specification root for the scope's
  vocabulary — its nouns and the terms the material uses — to find candidate files. **Every
  `constraints/` node is a candidate, whatever the grep returned** — «A constraint declares no
  reference, so no search over a scope's terms and no closure from the nodes it names reaches
  it» (SPEC-003 §Architecture Constraint).

  Where the scope is open-ended rather than named, list the nodes no initiative has ever named,
  over the directory the initiatives sit in, not one of them:

  ```
  python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/plan.py --unplanned <work-root> <specification-root>
  ```

  A rule or a contract in that list is worth a look before the cut is fixed. The listing decides
  nothing: a node nothing planned is an ordinary state, never a task you owe.

  **Naming the candidates is yours; closing over them is not.** Run over every candidate at once:

  ```
  python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/spec.py --impact <identity>[,<identity>...] <specification-root>
  ```

  It prints, per node, every reference it declares, every node that declares one at it and every
  entry of the decision log beside it, then the read set as paths, each node's `<slug>.log.md`
  after it where one exists. Read the files it names and nothing else, and close no second hop by
  hand. Its output goes to the report verbatim, beside the terms you grepped — the closure is
  mechanical, the candidates are your judgment.
- **The plan, when the work root is populated.** Run `python3 -B
  ${CLAUDE_PLUGIN_ROOT}/bin/plan.py --check <work-root> <specification-root>`. A `STALE`
  `plan.json` is rederived by a full validation run before anything relies on it. A `MOVED` line is
  never cleared by a derivation: the task it names joins the impact set and goes through step 4's
  binder. Then read `plan.json`, and only it: find the epics and tasks the scope touches and close
  the impact set over its edges — dependencies both ways, and `implements` references that reach
  the specification's impact set. Outside that set, a task the change does not touch is not
  reworded.
- **The project's standard, when one was named.** Run:

  ```
  python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --standard <the registry> --against <target-source-root> --specification <specification-root>
  ```

  `references/standard.md` says what is a stop and what is kept for step 3.

### 2. Inventory

Before any node, persist the scope: the prose as supplied, plus any files it references, under
`intake/` in the work root, and point every `sources` entry at a file there. A change persists the
same way — a new file under `intake/`, never an edit to what it holds. **A layout the person
supplied — a mockup, a rendering, a palette — goes under `intake/layout/`, apart from the scope**:
everything under `intake/` is material the subagents read, and only what a task names in
`reference` reaches the one that writes source.

Every plan node you write carries a body of exactly two headings, in order: `## What it is`, then
`## Notes`. One sentence per line; a section with nothing to say carries the literal line `None.`
**Write every node's frontmatter with `python3 -c` calling `yaml.safe_dump`, never by hand**, so a
colon in a sentence is never read as a second key.

Spawn a `siegard:codebase-surveyor` subagent — its judgment lives at
`${CLAUDE_PLUGIN_ROOT}/agents/codebase-surveyor.md` — passing the target source root, the scope's
path under `intake/`, and the `inventory` slice, printed here and pasted whole. Write each
inventory node it returns at the path its identifier computes to, verbatim.

### 3. Decompose

Spawn a `siegard:backlog-decomposer` subagent — its judgment lives at
`${CLAUDE_PLUGIN_ROOT}/agents/backlog-decomposer.md` — passing:

- the scope's path;
- the path of a file outside the work root holding `spec.py --pack` over the impact set;
- the surveyor's inventory;
- the `--contract epic` and `--contract task --without implements` slices, printed here and pasted
  whole;
- where a standard was named and step 1 found any, the artifacts it presupposes that the tree does
  not hold, each with what the registry says it provides and the rules it carries.

It returns epics, complete, and task skeletons without `implements`, which is the binder's. Write
the epics at the paths their identifiers compute to. Hold the skeletons: a skeleton touches disk
only once it names what it implements.

**Where a layout stands under `intake/layout/`, name it in the `reference` of each task that builds
what it shows**, on the skeleton, before step 4 — never on every task of the epic, and never
pointing at the scope. A reference decides form and never fact: statuses, wording and refusals
still come from the specification.

### 4. Implement against

Spawn one `siegard:execution-contract-binder` subagent per skeleton — its judgment lives at
`${CLAUDE_PLUGIN_ROOT}/agents/execution-contract-binder.md` — passing:

- the skeleton as its title, summary, objective and criteria — never its `rationale`, its
  dependencies or its body, which carry an opinion about the reference;
- the path of a file outside the work root holding `spec.py --pack` over its epic's `covers`
  less its `uncovered`: every candidate verbatim, and the path of each one's decision log;
- the binding slice, `plan.py --contract task --fields implements`, printed once and pasted whole
  into every spawn.

The binder returns the task's `implements`, and a classified note for every divergence —
including a fact the specification does not state, and a `compound` note on a criterion that
states two conditions.

**Spawn the binders together, not one after another.** None reads another's return or decides what
the next is given. Where a note sends a skeleton back to be re-cut, that skeleton runs through this
step again — and where it grows the epic's claim, **every skeleton under that epic does**, because
the candidate set is the epic's.

**A note classed `unstated` is settled before any task it touches is written**, and never reaches a
task file: read `references/unstated.md` and follow it. Every other class routes as
`references/notes.md` states.

Then compose and write each task: the skeleton, plus `implements` exactly as the binder returned
it — bare identities, no pin. **Composing is transcription, never correction**: a criterion whose
wording must change changes the skeleton, and a changed skeleton runs through this step again
before it touches disk. Check each task file on its own as soon as it is written:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/plan.py --node <file> <work-root>
```

### 5. Validate, and derive the plan

When every node is written, run `plan.py --check <work-root> <specification-root>` once more: a fact
decided in step 4 moves every task that implements the node it wrote, and each `MOVED` task not yet
bound in this invocation goes through step 4's binder first. Then derive:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/plan.py <work-root> <specification-root>
```

Where a standard was named, name it here too; the two flags travel together:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/plan.py --standard <the registry> --against <target-source-root> <work-root> <specification-root>
```

It validates every node against the contract and checks the whole plan against the specification:
dependencies resolve without cycles, every reference resolves, every covered node reaches a task
or a stated why, and, with a standard named, every artifact it presupposes stands in the tree or is
declared in some task's `produces`. Then it derives `plan.json`. **Never write or edit `plan.json`
yourself.** Report the output verbatim. A non-zero exit means the run failed: fix and rerun, and
never describe the plan as valid while it is not.

**Fixing means form, never knowledge.** A malformed reference or a forbidden field is yours to
correct. A coverage hole is settled by a task or by `uncovered` with a why — whichever the scope
decided, not whichever passes. A blocking note is settled by judgment, never here. An unstated fact
is settled only through `references/unstated.md`, never filled in to make a check pass.

### 6. Report, and stop

«The state a handoff opens with is a script's line, never the session's» (SPEC-006 R10). Run
`python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/handoff.py --prepare --skill plan-work --project
<project-root> --slug <slug> --target <target> --language <en or pt-BR, the session's>`. Write the
full report — every item `references/report.md` lists, in its order — through `bin/handoff.py
--save-report <path>`, to the path its `report` names, and fill only the fields the skeleton left
empty. Hand the person exactly what `handoff.py --render` prints over the record; it opens with
what needs the person — «A handoff opens with what needs the person, and explains after»
(SPEC-006 R1). The door it marks is the `/implement-task` one this report hands, already checked: a
`refuses` is said excluded beside its `refused:` fact, never recommended. A refusal is answered by
rewriting the field it names; a state it says has moved, by running `--prepare` again and carrying
its `state` and `state_from` whole.

Then stop. `git diff` over the work root is the review, and it belongs to a person.

## What you never do

- Record a status, an estimate, a priority or an execution order — the contract has no such field,
  and prose does not hold one either.
- Commit, stash, or otherwise change the consumer's git state. A dirty root is reported, and what to
  do with it is the person's call.
- Remove a closure — a closed plan is history, and reopening it is the person's git act.
