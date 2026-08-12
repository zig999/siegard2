# How Siegard works, for dummies

This document explains, from zero, what the six scripts under `src/claude/bin/` do, what files
they read and write, how the six skills and nine agents under `src/claude/` use them, and how all
of it adds up to one complete development process — from a human's idea to source code someone
else can trust.

It assumes no prior knowledge of this repository. If you already know the vocabulary, the
skills' own `SKILL.md` files and the scripts' module docstrings are the precise, load-bearing
version of everything summarized here; this page exists so a reader does not have to open nine
files to get the shape of the thing.

## The one idea to hold onto

Siegard never keeps a "status" anywhere. There is no field that says "70% done" or "in review."
Every question — *what is left to build?*, *did this pass review?*, *does this code still match
the spec?* — is answered by reading files on disk and recomputing the answer from scratch, every
time. A script that reports something never remembers it between runs. This is why nothing in
Siegard can go stale without someone noticing: the report is never separate from the thing it
reports on.

Everything below is either **a file that holds a fact** (an artifact) or **a script that checks
those facts and refuses when they disagree** (a validator). Skills orchestrate scripts and, for
the parts that need judgment instead of a rule, delegate to agents.

## The five artifacts

These are the nouns. Each is a set of files on disk, never a database, never a cache.

| Artifact | Where it lives | Written by | What it is |
|---|---|---|---|
| **`siegard.json`** | at the consumer project's git root | a human, through `/siegard-config` | The project's own settings: where its specification, plan, delivery and trace live, and which file is its "standard" (its own house rules). Every other skill reads this once instead of asking the human to retype paths every time. |
| **The specification** | a tree of markdown files under a "specification root" | a human's material, turned into nodes by `/analyse` | What the system must do, in five kinds of node: Domain Model, Rule, Scenario, Contract, Architecture Constraint. This is the one authority — if code and a specification node disagree, the node is right and the code is the bug. |
| **The plan** | a tree of markdown files under a "work root" | a human's scope, turned into nodes by `/plan-work` | The development plan: an inventory of the existing codebase, epics, and tasks. Every task names exactly which specification nodes it implements. |
| **The delivery** | a tree of markdown files under a "delivery root" | `/implement-task` (writes) and `/review-change` (adds findings) | The record of what was actually built: one implementation record and one proof (tests) record per task, plus reviews. This is evidence, not a verdict — nothing here decides whether the project is "done." |
| **The trace** | `siegard-trace.json`, beside `siegard.json` | `/implement-task` and `/reconcile` | The one fact that outlives the plan and the delivery: which specification node produced which file. The plan and the delivery can both be deleted or closed as history; the trace is what still tells you, a year later, why a given file exists. |

Two smaller files worth knowing:
- **`closure.md`** at the work root — a human marks a plan closed; the plan becomes read-only
  history that still validates, but the specification is no longer consulted for it.
- **`siegard-reconcile/<slug>.md`** — a record written by `/reconcile` to justify a bind for
  source that changed *outside* any task (a hand edit, a merge resolution).

## The seven scripts

These are the verbs. Every one of them is read-only over its inputs except for the one file it is
explicitly allowed to derive (a `--check`/plain distinction runs through all of them: the plain
form writes the derived index, `--check` only compares and never writes). None of them has any
notion of what a "test" or a "build" is for any particular technology — that knowledge belongs
entirely to the consumer project.

A root passed on any of these command lines is always a real filesystem path, already resolved —
never a bare field copied out of `siegard.json`. In particular, **`<work-root>` and
`<delivery-root>` are always one initiative's directory**, `<work_root>/<slug>` and
`<delivery_root>/<slug>`, never the bare `work_root`/`delivery_root` fields themselves — those
fields only name the container all initiatives share. Passing the container by mistake does not
fail loudly with a wrong-root message: `plan.py` and `deliver.py` walk every `.md` file under
whatever root they are given and classify each by its path relative to that root, so pointing
either script at the shared container makes the initiative's slug the first path segment instead
of `inventory`/`epic`/`task`/`intake`, and every single file — including correctly-shaped ones —
is reported as unclassifiable. Seeing every file in a plan fail the same way, all at once, is the
signature of this mistake.

1. **`project.py`** — reads `siegard.json` and prints what it says. Every skill runs this first.

   ```
   project.py <project-root>
   ```

   - `<project-root>` — any directory inside the consumer project. The script does not require this
     to already be the git toplevel: it walks up to find one (or falls back to `<project-root>`
     itself where git does not hold the tree) and reads `siegard.json` there.

   There is exactly one form — no flags. It prints one line per field `siegard.json` declares
   (`standard`, `specification_root`, each entry under `targets`, `work_root`, `delivery_root`),
   each resolved to an absolute path. If the file is missing or a field is absent, this script does
   not guess a default: it just says so (exit 0 either way — a missing file is a fact, not a
   failure), and it is the calling skill's job to decide whether that absence is a stop. Run this
   first, always: every root named on every other command below is exactly what this script just
   printed, never retyped from memory. `standard` is the one field an invocation elsewhere may
   override; this script's report is what says whether the file's own value or an override won.

2. **`spec.py`** — validates the specification against the five-class metamodel and derives its
   projections.

   ```
   spec.py <spec-root>
   spec.py --project <spec-root>
   spec.py --digest <spec-root>
   spec.py --node <file> <spec-root>
   ```

   - `<spec-root>` — the specification root (`siegard.json`'s `specification_root`).
   - `--project` — after validating, (re)writes `projections/` under `<spec-root>`: class diagrams,
     the context map, state diagrams, the capability map, the overview. Refused entirely while the
     specification has problems — a projection over a broken specification would report a shape
     nobody decided. Never edit `projections/` by hand; this is its only writer, and it clears
     stale files the next input no longer derives.
   - `--digest` — after validating, prints one line per node, sorted by identity:
     `<identity>  sha256:<hexdigest>` — the same digest `sha256sum <path>` computes by hand. Used
     elsewhere (a trace bind, a task's pin) to detect when a node's text has moved since something
     else was written against it. `--project` and `--digest` are mutually exclusive.
   - `--node <file>` — validates one file in isolation, against its own class's schema only: no
     reference resolution, no reachability, no decision-log check — those need the whole tree, and
     a file mid-authoring has not earned them yet. Cannot combine with `--project` or `--digest`.

   Checks the plain form runs that no per-file schema can express: every cross-reference resolves
   and lands on the class the field demands, an attribute never points at an identity-bearing
   element, composition stays inside its aggregate, a state machine is total, every element is
   reachable, and — importantly — a `gaps`, `sources`, `rationale` or `proposal` field is refused
   outright: an unstated fact must be decided and logged in the decision log, never marked as an
   open question inside the specification itself. Use the plain form for an ordinary validation
   pass (after `/analyse` writes or edits nodes); `--project` whenever a projection needs to be
   current; `--digest` when something else needs to pin a node's text at this moment; `--node`
   only while a single file is still being authored.

3. **`plan.py`** — derives the plan graph from the markdown plan nodes, and refuses what breaks it.

   ```
   plan.py <work-root> [<specification-root>]
   plan.py --check <work-root> [<specification-root>]
   plan.py --node <file> <work-root> [<specification-root>]
   plan.py --standard <file> --against <target-source-root> <work-root> [<specification-root>]
   ```

   - `<work-root>` — **one initiative's** plan directory (see the caution above).
   - `<specification-root>` — required while the plan is live; optional and ignored once a
     `closure.md` at `<work-root>` marks the plan closed, because closed history answers to the
     specification it was built against, never to today's.
   - `--check` — validates, then compares against the `plan.json` already on disk; writes nothing.
     Exits 1 if that file is stale relative to what a plain run would derive right now.
   - `--node <file>` — validates one plan node against `schemas/plan-node.json` only; skips
     cross-node checks (dependency cycles, epic coverage) and the specification checks entirely.
     Cannot combine with `--standard`.
   - `--standard <file> --against <target-source-root>` — the two flags always travel together (one
     without the other is refused): reconciles what the project's own registry (`<file>`)
     presupposes against what actually exists at `<target-source-root>`, and against every task's
     `produces`. Cannot combine with `--node` — a standard's presuppositions are a fact about the
     whole plan, not about one file.

   It imports `spec.py` directly and reads the specification through it, never through a cached
   index, so the plan can never be checked against a stale view of the spec — a specification that
   does not hold together is itself a refusal to run `plan.py` at all (fix it with `spec.py`
   first). The plain form (no flags beyond the roots) is the only writer of `plan.json`.

4. **`deliver.py`** — derives the delivery graph from the markdown delivery nodes. The largest
   script, because it is where the most cross-file rules live.

   ```
   deliver.py <delivery-root> <work-root> <target-source-root> [<specification-root>]
   deliver.py --check <delivery-root> <work-root> <target-source-root> [<specification-root>]
   deliver.py --outstanding <delivery-root> <work-root> <target-source-root> [<specification-root>]
   deliver.py --node <file> <delivery-root> <work-root> [<specification-root>]
   deliver.py --standard <file> [--against <target-source-root>]
   ```

   - `<delivery-root>` and `<work-root>` — again, one initiative's directories each:
     `<delivery_root>/<slug>` and `<work_root>/<slug>` (see the caution above — the same
     misclassification happens here if either is given as the shared container instead).
   - `<target-source-root>` — resolves every delivery record's `standard` reference (e.g.
     `siegard.json`'s `targets.backend`). Required by the plain, `--check` and `--outstanding`
     forms even if no record in this delivery happens to name a standard; `--node` is the one form
     that drops the requirement, since it never reads a standard reference at all.
   - `<specification-root>` — same rule as `plan.py`: required while the plan behind this delivery
     is live, ignored once it is closed (this script reads the plan through `plan.py`'s own
     pipeline, so the same closure rule applies transitively).
   - `--check` — compares against `delivery.json` already on disk; writes nothing.
   - `--outstanding` — never writes. Prints every task with no delivery record yet, what each one
     is waiting on (an undelivered dependency, substrate a task of this plan produces but the tree
     does not yet hold, a standing `BLOCKING` note only a person can settle), and the set that
     could be delivered right now. This is the command that answers "what is left?" — call it
     fresh every time; nothing about its answer is ever stored.
   - `--node <file>` — validates one delivery node's own schema and internal consistency only:
     skips cross-node checks, the plan checks and the standard checks — and, because of that, does
     not need `<target-source-root>` either.
   - `--standard <file> [--against <target-source-root>]` — stands entirely alone: validates one
     project registry file, needing no delivery, work, or specification root at all. Add
     `--against <target-source-root>` to also check whether that tree already holds what the
     registry presupposes (exit 1 while any of it is still absent).

   The plain form (no flags beyond the four roots) is the only writer of `delivery.json`.

5. **`run.py`** — executes the consumer project's own build/test commands (never invented here)
   and records exactly what they printed.

   ```
   run.py <delivery-root> --run <slug> --cwd <dir> --timeout-seconds <n> \
          --step <name>="<command>" [--step <name>="<command>" ...]
   ```

   - `<delivery-root>` — positional, the same per-initiative root `deliver.py` takes; the run's
     output lands at `<delivery-root>/run/<slug>/`.
   - `--run <slug>` — names this run. A slug that already exists on disk is refused outright —
     nothing here is ever overwritten; a rerun always gets a new name, so every attempt stays a
     separately readable record.
   - `--cwd <dir>` — required, the directory every step's command runs from. Never guessed or
     defaulted, because a directory chosen in silence would run against a tree nobody named.
   - `--timeout-seconds <n>` — required, one ceiling applied to every step. There is no built-in
     default: a number this framework shipped would be a number nobody calibrated for the actual
     suite.
   - `--step <name>="<command>"` — repeatable, one per build/test step, executed in the order
     given. `<name>` is lowercase words joined by hyphens. Each `<command>` is split with
     `shlex.split` and run directly, with no shell: no `&&`, `|`, `>`, `$VAR` expansion, no
     globbing. A step that fails or times out stops the run; every step after it is recorded as
     not run, never executed against a tree the previous step left broken.

   There is no `--check`/plain distinction here — every invocation both runs the commands and
   writes the record, so there is nothing separate to compare against. `run.py` holds no notion of
   what a "test" or a "build" is for any technology: the steps and their commands are always the
   caller's.

6. **`trace.py`** — resolves and maintains `siegard-trace.json`, the one fact that outlives both
   the plan and the delivery: which specification node produced which file.

   ```
   trace.py <target-root>
   trace.py --check <target-root>
   trace.py --bind <target-root> <spec-root> <node> <file> [<file> ...] [--replace]
   trace.py --bind-record <target-root> <spec-root> <implementation-record> [--replace]
   trace.py --prune <target-root>
   trace.py --reconciliation <reconciliation-record>
   ```

   - `<target-root>` — the target source root (e.g. `siegard.json`'s `targets.backend`), where
     `siegard-trace.json` sits beside `siegard.json` at that tree's git toplevel. Every `<file>` on
     the command line, and every path a bound record names, is read relative to this root.
   - `<spec-root>` — the specification root, read through the same pipeline `spec.py` uses.
   - `--check` — recomputes both digests (the node's and every bound file's) and reports drift in
     three classes, writing nothing: `orphaned` (the node the file was bound to no longer exists in
     the specification — a human must decide; `--prune` is the only way to clear it), `moved` (the
     node's text changed since the bind), `code` (the bound file changed since the bind).
   - `--bind <node> <file> [<file> ...]` — writes or extends one binding by hand: reads `<node>`'s
     current digest and each `<file>`'s current digest, and writes the entry. By default this
     extends whatever that node already held — a file an earlier bind of the same node named but
     this call does not is left bound at the digest that earlier bind recorded.
   - `--replace` — a modifier on `--bind` or `--bind-record`, not a form of its own: writes the
     entry in full instead of extending it, so a file left off the list is a file no longer
     claimed. Every path a `--replace` stops claiming is printed as a receipt once the write
     succeeds — never a silent drop.
   - `--bind-record <implementation-record>` — reads one whole implementation record and binds
     every node/file pair it states, atomically, refusing the whole write if any part of the record
     would be refused. This is the form `/implement-task` uses, instead of one `--bind` per node.
   - `--prune` — drops only the `orphaned` bindings. `moved` and `code` drift are never dropped this
     way, only rebound by whoever owns the change — pruning either would discard the one record of
     which node that code answers to.
   - `--reconciliation <reconciliation-record>` — the one form that writes nothing: validates a
     reconciliation record (written by `/reconcile`, at `siegard-reconcile/<slug>.md`) against
     `schemas/reconciliation.json`, so `--bind-record` can read it afterward exactly as it reads an
     implementation record.

7. **`terms.py`** — a glossary that holds no text of its own.

   ```
   terms.py
   terms.py <term> [<term> ...]
   ```

   - No arguments — prints every defined term, alphabetically.
   - One or more `<term>` — prints only those terms; exits 1 if any named term is not in the table,
     rather than silently dropping it from the output.

   Every term maps to a schema file and a JSON pointer; what gets printed is read live from the
   `description` at that pointer — nothing here paraphrases a definition, so there is no copy to
   drift out of sync. A pointer that stops resolving (a field renamed elsewhere) is a refusal,
   naming the term and the broken pointer, never a silently stale entry. A word the framework uses
   normatively but no contract defines is still listed, under "no definition holds these" — a
   disclosed gap, never an omission.

```
project.py   — reads siegard.json
     │
     ▼
  spec.py    — validates the specification
     │
     ▼
  plan.py    — imports spec.py; validates the plan against the live specification
     │
     ▼
deliver.py   — reads the plan through plan.py's own pipeline; validates the delivery
     │
     ├── run.py    — executes build/test commands the delivery's records point at
     └── trace.py  — imports project.py + spec.py; outlives both plan and delivery
```

## The six skills

Skills are what a human actually types (`/analyse`, `/plan-work`, ...). Each one is "one
invocation, one increment" — it does its job and stops; it never chains into the next skill on
its own.

| Skill | Turns this input… | …into this output | Scripts it calls | Agents it delegates to |
|---|---|---|---|---|
| **`/siegard-config`** | a human's stated settings | `siegard.json` | `project.py` | none |
| **`/analyse`** | material a human supplies (prose, files) | specification nodes + `projections/` | `spec.py` | none |
| **`/plan-work`** | a stated scope + the specification | plan nodes (`inventory/`, `epic/`, `task/`) + `plan.json` | `spec.py`, `plan.py`, `deliver.py --standard` | `codebase-surveyor`, `backlog-decomposer`, `execution-contract-binder` |
| **`/implement-task`** | one planned task | source + tests + a delivery record + `delivery.json` + a trace bind | `plan.py --check`, `run.py`, `deliver.py`, `trace.py --bind-record` | `task-implementer`, `test-author` |
| **`/review-change`** | one delivered task | findings recorded under the delivery root + `delivery.json` | `plan.py --check`, `deliver.py`, `run.py`, `trace.py --check` | `coverage-auditor`, `specification-conformance-reviewer`, `standard-conformance-reviewer`, `failure-diagnostician` |
| **`/reconcile`** | source someone hand-edited outside any task | a reconciliation record + a trace bind | `spec.py`, `trace.py` | none |

No skill runs a shell command directly except by calling `run.py` — this is enforced by
`tests/test_agent_contract.py`, which fails the suite if any shipped agent is ever given a shell
tool. Everything a project builds or tests is run exactly once, by `run.py`, and captured; nothing
downstream re-executes it to double-check.

## The nine agents

Agents exist for exactly the parts a script cannot decide mechanically — reading prose,
judging whether a sentence in source states a fact the specification does not, deciding what a
task should implement. Every agent below is **read-only except where noted**, returns its answer
as text to the skill that spawned it, and writes no file the skill did not ask it to write. None
of them has a shell.

**Used by `/plan-work`** (building the plan):
- **`codebase-surveyor`** — reads the target source tree and returns an inventory: existing
  modules, conventions already in use, reuse points, risks. Read-only.
- **`backlog-decomposer`** — cuts a scope into epic and task skeletons (objectives, falsifiable
  criteria, dependencies). It never decides what a task implements — that is deliberately left to
  a different agent, in a context that never saw this one's reasoning, so the specification isn't
  quietly bent to fit the tasks that were already written.
- **`execution-contract-binder`** — for each task, rereads the specification fresh and decides
  which nodes it actually implements, flagging every divergence (including a fact the
  specification simply doesn't state).

**Used by `/implement-task`** (building the code):
- **`task-implementer`** — writes the source for one task. Can write and edit files, but only
  source: no tests, no commands, no git.
- **`test-author`** — writes the tests for one task, deliberately a *different* agent than the one
  that wrote the source, re-reading the code cold. Can write and edit files, but only tests.

**Used by `/review-change`** (judging what was built) — its four passes, independent of each
other and running in any order:
- **`coverage-auditor`** — pairs every criterion a task states with the test that would fail if
  it stopped holding; says which criteria have no such test. Read-only.
- **`specification-conformance-reviewer`** — checks whether the source states only facts the
  specification actually holds. Read-only.
- **`standard-conformance-reviewer`** — checks the source against the project's own house rules
  (the ones a human has to read to apply — the ones a tool can check mechanically are run through
  `run.py` instead, as a build/test step). Read-only.
- **`failure-diagnostician`** — reads a captured run's output and explains why each failure
  failed. It never re-runs anything; the run it reads is `run.py`'s record, not its own.

None of these nine agents produces a verdict, a score, or a pass/fail. They all return **findings
for a human to read**. Deciding what a finding means is deliberately kept outside every agent:
"a finding nobody can disagree with is a decision wearing a finding's clothes."

## A complete process, start to finish

Here is what one real initiative looks like, tying every piece above into the order it actually
happens in.

```
 1. /siegard-config   → human declares roots + standard  ────────────► siegard.json
 2. /analyse           → human's material → spec nodes    ────────────► specification/, projections/
 3. /plan-work          → scope + spec → epics & tasks     ────────────► plan/, plan.json
      (survey → decompose → decide "implements", one task at a time)
 4. /implement-task     → one task, repeated per task:
      write source → write tests → build → run suite       ────────────► delivery/, delivery.json,
                                                                           siegard-trace.json
 5. /review-change      → one delivered task, four passes  ────────────► delivery/ (findings added)
 6. a human reads the findings and decides
      ├─ nothing wrong           → move to the next task, back to step 4
      ├─ code is wrong           → fix it, a new /implement-task-style pass, or hand-edit + /reconcile
      └─ the spec was wrong      → back to step 2, /analyse evolves the specification
```

Two things this diagram cannot show, because they only show up once an initiative is already
moving:

- **The corrective path.** If someone finds one wrong behavior in code that is already delivered
  — not something a task's criteria cover — `/plan-work` can route it in directly as a single
  task, skipping the survey and decomposition, because there is nothing to survey: the code
  already exists.
- **The side door for hand edits.** Source changes outside of any task — an incident fix typed in
  directly, a merge conflict resolved by hand — never go through `/implement-task`. `/reconcile`
  is the only place that binds them: it reads what the trace already claims about that file,
  judges whether the new text still matches, and rebinds only what the judgment clears.

At every step, the report is derived from the files on disk at the moment you ask — never from
memory of an earlier run, never from a status field. Ask `deliver.py --outstanding` a year into
an initiative and it walks the plan and the delivery fresh, exactly the way it would on day one.

## Where it all sits on disk (a worked example)

```
consumer-project/
├── siegard.json                    ← written by /siegard-config
├── siegard-trace.json              ← written by /implement-task, /reconcile
├── siegard-reconcile/
│   └── fix-typo-in-pricing.md      ← written by /reconcile
├── specification/                  ← "specification root", written by /analyse
│   ├── domain/checkout/cart.md
│   ├── rules/free-shipping-over-100.md
│   ├── decision-log.md
│   └── projections/                ← derived by spec.py --project, never edited by hand
├── plan/                           ← "work root", written by /plan-work
│   ├── inventory/checkout-module.md
│   ├── epic/checkout.md
│   ├── task/checkout/apply-free-shipping.md
│   └── plan.json                   ← derived by plan.py, never edited by hand
└── delivery/                       ← "delivery root", written by /implement-task, /review-change
    ├── implementation/checkout/apply-free-shipping.md
    ├── proof/checkout/apply-free-shipping.md
    ├── review/apply-free-shipping.md
    ├── run/checkout-apply-free-shipping-suite/
    └── delivery.json                ← derived by deliver.py, never edited by hand
```

Every `.json` file above with a comment saying "derived" is a file no human, no skill and no
agent ever hand-edits. If one of them looks wrong, the fix is always to fix the markdown nodes and
rederive it — never to patch the JSON directly.
