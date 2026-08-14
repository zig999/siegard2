# How Siegard works, for dummies

This document explains, from zero, what the seven scripts under `src/claude/bin/` do, what files
they read and write, how the eight skills and ten agents under `src/claude/` use them, and how all
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
| **The specification** | a tree of markdown files under a "specification root" | a human's material, turned into nodes by `/analyse`; extended by `/plan-work`'s decided-fact route where planning finds a fact no node states | What the system must do, in five kinds of node: Domain Model, Rule, Scenario, Contract, Architecture Constraint. This is the one authority — if code and a specification node disagree, the node is right and the code is the bug. Every fact it carries that no material stated is disclosed in `decision-log.md`, whichever entry point decided it. |
| **The plan** | a tree of markdown files under a "work root" | a human's scope, turned into nodes by `/plan-work` | The development plan: an inventory of the existing codebase, epics, and tasks. Every task names exactly which specification nodes it implements. |
| **The delivery** | a tree of markdown files under a "delivery root" | `/implement-task` (writes) and `/review-change` (adds findings) | The record of what was actually built: one implementation record and one proof (tests) record per task, plus reviews. This is evidence, not a verdict — nothing here decides whether the project is "done." |
| **The trace** | `siegard-trace.json`, beside `siegard.json` | `/implement-task` and `/reconcile` | The one fact that outlives the plan and the delivery: which specification node produced which file. The plan and the delivery can both be deleted or closed as history; the trace is what still tells you, a year later, why a given file exists. |

Two smaller files worth knowing:
- **`closure.md`** at the work root — a human marks a plan closed; the plan becomes read-only
  history that still validates, but the specification is no longer consulted for it.
- **`siegard-reconcile/<slug>.md`** — a record written by `/reconcile` to justify a bind for
  source that changed without a rebind, whatever wrote it (a hand edit, a merge resolution, a
  delivery rewriting a file another node's binding claims).

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

Every example below runs against one small, real, internally consistent project fixture, so every
command line and every line of output on this page is a genuine capture, not a reconstruction: a
`checkout-service` consumer project with a `sales` context in its specification (an `order`
aggregate root, an `invoice` value object, and one invariant rule), one initiative called
`checkout` in its plan (one epic, two tasks — `record-order` and `bill-order`, the second depending
on the first), one of those two tasks delivered (`record-order`, with its implementation and
proof), and a `target` source tree the delivery's records point at. Paths are shown relative to the
project root, `/home/dev/checkout-service`, which is also where `siegard.json` and
`siegard-trace.json` sit.

### 1. `project.py`

**General.** The one entry point onto `siegard.json`. Every skill runs this first, and no other
script in this framework ever parses `siegard.json` itself — this is the sole reader, held to
`schemas/project.json`. Dependency: `jsonschema`.

- **Reads:** `siegard.json`. **Writes:** nothing — it is read-only over its input.

#### `project.py <project-root>`

- **Function:** resolves the file and prints every field it declares, each turned into an absolute
  path.
- **When to use it:** first, always, in any session that is about to call any other script here —
  every root named on the command lines below is exactly what this prints, never retyped from
  memory or guessed from a convention.
- **Read or write:** read-only. Exit 0 whether or not `siegard.json` exists — a missing file is a
  fact this prints, not a failure. `<project-root>` need not already be the git toplevel: the
  script walks up to find one, or falls back to `<project-root>` itself where git does not hold the
  tree.

Example — `<project-root>` is any directory inside the project, here the project root itself:

```
$ python3 bin/project.py .
standard: /home/dev/checkout-service/target/standard.yaml
specification_root: /home/dev/checkout-service/specification
target backend: /home/dev/checkout-service/target
work_root: /home/dev/checkout-service/work
delivery_root: /home/dev/checkout-service/delivery
```

There is no artifact besides this screen output — `project.py` derives nothing to disk.

### 2. `spec.py`

**General.** Validates a specification against the five-class metamodel (Domain Model element,
Rule, Scenario, Contract, Architecture Constraint) and derives its projections. The path is the
identity: `domain/<context>/<slug>.md` is an element, `rules/`, `scenarios/` and `contracts/`
follow the same shape, `constraints/<slug>.md` is system-wide, and `decision-log.md` at the root is
the one mandatory non-normative file. No file carries an id or a type field, so none can disagree
with where it sits. Dependencies: PyYAML, jsonschema.

- **Reads:** every `.md` file under `<spec-root>`. **Writes:** `projections/` under `<spec-root>`,
  and only with `--project`.

#### `spec.py <spec-root>`

- **Function:** validates the whole specification: every per-file schema, plus every cross-file
  rule no per-file schema can express — every reference resolves to the class it names, an
  attribute never points at an identity-bearing element, composition stays inside its aggregate, a
  state machine is total, every element is reachable, and a `gaps`, `sources`, `rationale` or
  `proposal` field is refused outright (an unstated fact is decided and logged in the decision log,
  never marked open in the specification itself).
- **When to use it:** an ordinary validation pass, typically right after `/analyse` writes or edits
  nodes.
- **Read or write:** read-only.

```
$ python3 bin/spec.py ./specification
specification sound: 2 element(s), 1 rule(s) across 1 context(s); 0 decision(s) disclosed
```

#### `spec.py --project <spec-root>`

- **Function:** the plain validation, then (re)writes `projections/`: class diagrams per context,
  the context map, state diagrams, the capability map, and an overview — sorted throughout, so
  identical input is byte-identical output.
- **When to use it:** whenever a projection needs to be current — after any change to the
  specification that a human or another tool is about to read a diagram or the context map from.
  Never edit `projections/` by hand; this is its only writer, and it deletes any stale file the
  current input no longer derives.
- **Read or write:** writes `projections/`. Refused entirely — nothing is written — while the
  specification has problems, the same as the plain form.

```
$ python3 bin/spec.py --project ./specification
specification sound: 2 element(s), 1 rule(s) across 1 context(s); 0 decision(s) disclosed
projected 4 file(s) into specification/projections: capability-map.mmd, class-diagram-sales.mmd,
context-map.mmd, overview.md
```

Artifact generated:

```
specification/projections/capability-map.mmd
specification/projections/class-diagram-sales.mmd
specification/projections/context-map.mmd
specification/projections/overview.md
```

#### `spec.py --digest <spec-root>`

- **Function:** the plain validation, then prints one line per node, sorted by identity:
  `<identity>  sha256:<hexdigest>` — the exact digest `sha256sum <path>` computes by hand over that
  file's bytes.
- **When to use it:** whenever something outside the specification needs to pin a node's text at
  this moment, so it can later ask whether that node moved — a trace bind or a task's `implements`
  do this indirectly, through `trace.py`. Mutually exclusive with `--project`.
- **Read or write:** read-only.

```
$ python3 bin/spec.py --digest ./specification
specification sound: 2 element(s), 1 rule(s) across 1 context(s); 0 decision(s) disclosed
decision-log  sha256:19a18d53bec3cfd6dae94e727daf04dacaf4d5671c7dced2c2d7844467dfbb7a
domain/sales/_context  sha256:8323cf76415517a6d737932d145864d5ed3e5be190dfe05f97ba16713fb25c96
domain/sales/invoice  sha256:8296445581e78ffa5248951fc1b41fa5513c7c301f84403210d62ae47bb45ece
domain/sales/order  sha256:944984f5b60539ff5ce46d11d812072a7a4c27c1ca8cf8a0f9bb32f1541e1fdb
rules/sales/invoice-immutable  sha256:8bcfb4772d03b51941327678ae962fc64b3ab7049e20f9a03911983cf5fae5e5
```

#### `spec.py --node <file> <spec-root>`

- **Function:** validates one file in isolation, against its own class's schema only — no
  reference resolution, no reachability, no decision-log check, because those need the whole tree
  and a file mid-authoring has not earned them yet.
- **When to use it:** while a single node is still being written, before the rest of the tree is
  ready to check it against.
- **Read or write:** read-only. Cannot combine with `--project` or `--digest`.

```
$ python3 bin/spec.py --node ./specification/domain/sales/order.md ./specification
domain/sales/order: sound on its own. Cross-node checks did not run; they run on the whole
specification.
```

### 3. `plan.py`

**General.** Derives the plan graph from the markdown plan nodes and refuses what breaks it. The
path is the identity: `inventory/<slug>.md` and `epic/<slug>.md` are two-part nodes,
`task/<epic>/<slug>.md` sits under the epic its path names. It imports `spec.py` directly and reads
the specification through it, never through a cached index, so a plan can never be checked against
a stale view of the spec. Dependencies: PyYAML, jsonschema.

- **Reads:** every `.md` file under `<work-root>` (one initiative's directory — see the caution
  above), plus the specification. **Writes:** `plan.json` at `<work-root>`, only with the plain
  form.

#### `plan.py <work-root> [<specification-root>]`

- **Function:** validates every plan node's own schema, then the cross-node rules no per-file
  schema can express — a task's epic exists, dependencies form no cycle, every node an epic claims
  to `covers` is implemented by one of its tasks or declared `uncovered` (never silently neither) —
  then derives and writes `plan.json`.
- **When to use it:** after `/plan-work` writes or edits plan nodes, or any time the derived graph
  needs to be current.
- **Read or write:** writes `plan.json`. `<specification-root>` is required while the plan is live
  (no `closure.md` at `<work-root>`); once the plan is closed, it is optional and ignored, because
  closed history answers to the specification it was built against, never to today's.

```
$ python3 bin/plan.py ./work/checkout ./specification
derived work/checkout/plan.json: 4 node(s), 5 edge(s), contract siegard-plan/3
  1 inventory, 1 epic, 2 task; 2 specification node reference(s) implemented (2 unique)
```

Artifact generated (`work/checkout/plan.json`, excerpt):

```json
{
  "contract_version": "siegard-plan/3",
  "nodes": [
    { "id": "epic/checkout", "kind": "epic", "file": "epic/checkout.md",
      "title": "Checkout", "summary": "Everything order placement needs." },
    { "id": "inventory/order-service", "kind": "inventory", "file": "inventory/order-service.md",
      "title": "Order service", "summary": "One layered service under src/." },
    { "id": "task/checkout/bill-order", "kind": "task", "file": "task/checkout/bill-order.md",
      "title": "Bill order", "summary": "Raise the bill for a recorded order.",
      "epic": "checkout" },
    { "id": "task/checkout/record-order", "kind": "task",
      "file": "task/checkout/record-order.md", "title": "Record order",
      "summary": "Persist a placed order.", "epic": "checkout" }
  ],
  "edges": [
    { "from": "epic/checkout", "to": "domain/sales/order", "kind": "covers", "at": "covers[0]" },
    { "from": "epic/checkout", "to": "domain/sales/invoice", "kind": "covers", "at": "covers[1]" },
    { "from": "task/checkout/bill-order", "to": "task/checkout/record-order",
      "kind": "depends_on", "at": "depends_on[0]" }
  ]
}
```

#### `plan.py --check <work-root> [<specification-root>]`

- **Function:** the same validation, then compares the result against `plan.json` already on disk.
- **When to use it:** to confirm the derived index is current without touching it — the form every
  other script's own pipeline uses internally before trusting a plan.
- **Read or write:** read-only; exits 1 if `plan.json` is stale relative to what a plain run would
  derive right now.

```
$ python3 bin/plan.py --check ./work/checkout ./specification
plan checked: work/checkout/plan.json matches 4 node(s)
```

#### `plan.py --node <file> <work-root> [<specification-root>]`

- **Function:** validates one plan node against `schemas/plan-node.json` only, skipping cross-node
  checks (cycles, coverage) and the specification checks entirely.
- **When to use it:** while a single task or epic is still being drafted.
- **Read or write:** read-only. Cannot combine with `--standard`.

```
$ python3 bin/plan.py --node ./work/checkout/task/checkout/record-order.md ./work/checkout ./specification
task/checkout/record-order: sound on its own. Cross-node checks and specification checks did not
run; they run on the whole plan.
```

#### `plan.py --standard <file> --against <target-source-root> <work-root> [<specification-root>]`

- **Function:** the plain validation and write, plus a reconciliation between what the project's
  own registry (`<file>`) presupposes and what the tree at `<target-source-root>` actually holds,
  and what the plan's own tasks declare in `produces`. The two flags always travel together; naming
  one without the other is refused.
- **When to use it:** before a plan is trusted to hand tasks to `/implement-task` — it is what
  catches a rule the registry needs (e.g. a rule a tool decides, which needs a manifest to run
  against) that nothing in this plan is set up to provide yet.
- **Read or write:** writes `plan.json` on success, the same as the plain form. Cannot combine with
  `--node`.

Satisfied — `target/package.json` exists, so `PRH-01`'s presupposition holds:

```
$ python3 bin/plan.py --standard ./target/standard.yaml --against ./target ./work/checkout ./specification
derived work/checkout/plan.json: 4 node(s), 5 edge(s), contract siegard-plan/3
  1 inventory, 1 epic, 2 task; 2 specification node reference(s) implemented (2 unique)
```

Refused — `target/package.json` is temporarily removed, so the same registry cannot be applied to
this plan, and nothing is derived:

```
$ rm target/package.json
$ python3 bin/plan.py --standard ./target/standard.yaml --against ./target ./work/checkout ./specification
./target/standard.yaml presupposes package.json, which target does not hold and no task produces;
PRH-01 cannot be applied to anything this plan delivers, and /implement-task drops the check that
the tree holds what the registry presupposes, and a record whose files no rule reaches owes the
install alone instead of the build and the suite. Ordinary work declares none — drop package.json
from `produces`, or name it in target/standard.yaml's `presupposes` if that is what it really is

1 problem(s) over 4 node(s). plan.json is not derived over a plan that does not hold together.
```

### 4. `deliver.py`

**General.** Derives the delivery graph from the markdown delivery nodes and refuses what breaks
it — the largest of the seven scripts, because it is where the most cross-file rules live:
`implementation/<epic>/<slug>.md` and `proof/<epic>/<slug>.md` answer the task at
`task/<epic>/<slug>`, and `review/<slug>.md` names one review. It reads the plan through `plan.py`'s
own pipeline, never through `plan.json` directly, and the pin each record carries is the SHA-256 of
its own task's file. Dependencies: PyYAML, jsonschema.

- **Reads:** every `.md` file under `<delivery-root>` (one initiative's directory), the plan, and,
  where named, a project standard. **Writes:** `delivery.json` at `<delivery-root>`, only with the
  plain form.

#### `deliver.py <delivery-root> <work-root> <target-source-root> [<specification-root>]`

- **Function:** validates every delivery node's own schema and internal consistency, then the
  cross-file rules — the task it answers exists, a proof sits beside its implementation, every
  criterion of the task is answered exactly once, every specification node the task implements is
  accounted for, no task is delivered before the tasks it depends on — then derives and writes
  `delivery.json`.
- **When to use it:** after `/implement-task` writes an implementation and a proof record for a
  task, or any time the derived graph needs to be current.
- **Read or write:** writes `delivery.json`. `<target-source-root>` resolves every record's
  `standard` reference and is required even where no record happens to name one.
  `<specification-root>` follows the same closed/live rule as `plan.py`, inherited transitively.

```
$ python3 bin/deliver.py ./delivery/checkout ./work/checkout ./target ./specification
derived delivery/checkout/delivery.json: 2 node(s), 3 edge(s), contract siegard-delivery/2
  1 implementation, 1 proof; 1 of 2 task(s) hold a record; 0 criterion(s) recorded unmet; 0
  recorded unproven; 0 finding(s)
```

Artifact generated (`delivery/checkout/delivery.json`, excerpt):

```json
{
  "contract_version": "siegard-delivery/2",
  "nodes": [
    { "id": "implementation/checkout/record-order", "kind": "implementation",
      "file": "implementation/checkout/record-order.md",
      "title": "Record a placed order", "task": "task/checkout/record-order" },
    { "id": "proof/checkout/record-order", "kind": "proof",
      "file": "proof/checkout/record-order.md",
      "title": "Proof for recording a placed order", "task": "task/checkout/record-order" }
  ],
  "edges": [
    { "from": "implementation/checkout/record-order", "to": "domain/sales/order",
      "kind": "encodes", "at": "nodes[0]" },
    { "from": "implementation/checkout/record-order", "to": "task/checkout/record-order",
      "kind": "implements", "at": "task" }
  ]
}
```

#### `deliver.py --check <delivery-root> <work-root> <target-source-root> [<specification-root>]`

- **Function:** the same validation, then compares against `delivery.json` already on disk.
- **When to use it:** to confirm the derived index is current without touching it.
- **Read or write:** read-only; exits 1 if `delivery.json` is stale.

```
$ python3 bin/deliver.py --check ./delivery/checkout ./work/checkout ./target ./specification
delivery checked: delivery/checkout/delivery.json matches 2 node(s)
```

#### `deliver.py --outstanding <delivery-root> <work-root> <target-source-root> [<specification-root>]`

- **Function:** the same validation, then prints every task with no delivery record yet, what each
  one is waiting on (an undelivered dependency, substrate a task of this plan produces but the tree
  does not yet hold, a standing `BLOCKING` note only a person can settle), and the set that could be
  delivered right now.
- **When to use it:** any time the answer to "what is left?" is needed — this is the one place that
  answer is computed; nothing about it is ever stored, so it is always current.
- **Read or write:** read-only; never writes `delivery.json`, even when the underlying data would
  otherwise cause one to be derived.

```
$ python3 bin/deliver.py --outstanding ./delivery/checkout ./work/checkout ./target ./specification
task/checkout/bill-order: no record
deliverable now: task/checkout/bill-order — no record, nothing they wait on, no standing BLOCKING
note. Which one is the caller's to choose; nothing here orders them
```

#### `deliver.py --node <file> <delivery-root> <work-root> [<specification-root>]`

- **Function:** validates one delivery node's own schema and internal consistency only, skipping
  cross-node checks, the plan checks and the standard checks.
- **When to use it:** while a single implementation or proof record is still being written.
- **Read or write:** read-only. `<target-source-root>` is not needed by this form, since it never
  reads a standard reference.

```
$ python3 bin/deliver.py --node ./delivery/checkout/implementation/checkout/record-order.md ./delivery/checkout ./work/checkout ./specification
implementation/checkout/record-order: sound on its own. Cross-node checks and plan checks did not
run; they run on the whole delivery.
```

#### `deliver.py --standard <file> [--against <target-source-root>]`

- **Function:** validates one project registry file on its own against `schemas/standard.json`,
  needing no delivery, work or specification root at all. With `--against <target-source-root>`
  also named, additionally checks whether that tree already holds what the registry presupposes.
- **When to use it:** before any review reads the registry (a consumer's own pre-flight), and
  whenever `/plan-work` needs to know whether a presupposition is already met or still owed to a
  task's `produces`.
- **Read or write:** read-only in both forms.

Alone:

```
$ python3 bin/deliver.py --standard ./target/standard.yaml
standard checked: target/standard.yaml declares 2 rule(s) — 1 decided by reading, 1 by a tool
  pin sha256:e1fd2fa6a97b42be5d43790c5d3606f9e9bb5a841e122a3fc289c0f0f8eaf204
  the rules a tool decides run as step(s) lint (1 rule(s)); a review reads only the 1 decided by
  reading
  it declares 3 command(s): install = true (60s), lint = true (60s), test = true (60s)
    installs with install, proves with test, and the rest run as checks on both sides of the tests
  it authorizes 1 direct dependency(ies): pino. What they pull in transitively is nobody's
  approval and the lockfile's record
  it presupposes 1 artifact(s); --against <target-source-root> says whether they stand
```

With `--against`, presupposition satisfied:

```
$ python3 bin/deliver.py --standard ./target/standard.yaml --against ./target
standard checked: target/standard.yaml declares 2 rule(s) — 1 decided by reading, 1 by a tool
  ...
  against target:
  package.json: stands, and PRH-01 can be applied
```

With `--against`, presupposition absent (`target/package.json` temporarily removed) — exit 1, and
the message hands over a ready `/plan-work` invocation instead of just naming the gap:

```
$ rm target/package.json
$ python3 bin/deliver.py --standard ./target/standard.yaml --against ./target
standard checked: target/standard.yaml declares 2 rule(s) — 1 decided by reading, 1 by a tool
  ...
  against target:
  package.json: ABSENT — the script the test step below runs
      unanswerable while it is: PRH-01

1 presupposed artifact(s) absent. Source written now answers to a registry that cannot be applied
to it: the rules above go unanswered, and the absence is found once per file in a review instead of
once here. The artifact is built by a task that declares it in `produces`, planned through
/plan-work — ready below, but for the two roots only the caller knows:

  /plan-work

  Scope: the registry at target/standard.yaml presupposes package.json, absent from target.
  One cut: the task that produces it, declared in `produces`, covering the rules named above.
  Work root: <the plan this initiative runs under>
  Specification root: <the specification that plan implements against>
  Target source root: target
  Project standard: target/standard.yaml
```

### 5. `run.py`

**General.** Executes the consumer project's own build/test commands — never invented here, never
guessed from the repository — with no shell (`shlex.split`, no `&&`, `|`, `>`, `$VAR`, no
globbing), and writes exactly what they printed. No dependency beyond the standard library.

- **Reads:** nothing but its own arguments. **Writes:** `<delivery-root>/run/<slug>/`, always — this
  script has no read-only form, because there is nothing to compare a run against.

#### `run.py <delivery-root> --run <slug> --cwd <dir> --timeout-seconds <n> --step <name>="<command>" [--step <name>="<command>" ...]`

- **Function:** runs each `--step` in order, in `<dir>`, each bounded by the same
  `--timeout-seconds`; a step that fails or times out stops the run, and every step after it is
  recorded `not_run` rather than executed.
- **When to use it:** whenever a task's implementation needs to be built and tested, or a review
  needs a fresh, independently reproducible record of the suite. `--run <slug>` must be new every
  time — a slug that already exists on disk is refused, so a second attempt is always a second,
  separately readable record.
- **Read or write:** writes. `--cwd` and `--timeout-seconds` are required with no default, on
  purpose — a directory or a bound chosen in silence would produce a run against a tree, or for a
  duration, nobody named.

All steps pass:

```
$ python3 bin/run.py ./delivery/checkout --run checkout-suite --cwd ./target --timeout-seconds 60 \
      --step install="true" --step test="true"
{
  "contract_version": "siegard-run/1",
  "run": "run/checkout-suite",
  "cwd": "/home/dev/checkout-service/target",
  "timeout_seconds": 60,
  "outcome": "passed",
  "failed_step": null,
  "steps": [
    { "name": "install", "command": "true", "outcome": "passed", "exit_code": 0,
      "output": "install.log" },
    { "name": "test", "command": "true", "outcome": "passed", "exit_code": 0,
      "output": "test.log" }
  ],
  "combined_output": "run.log"
}
```

Artifact generated:

```
delivery/checkout/run/checkout-suite/run.json
delivery/checkout/run/checkout-suite/install.log
delivery/checkout/run/checkout-suite/test.log
delivery/checkout/run/checkout-suite/run.log
```

Rerunning under the same slug is refused outright, before anything executes:

```
$ python3 bin/run.py ./delivery/checkout --run checkout-suite --cwd ./target --timeout-seconds 60 \
      --step install="true" --step test="true"
cannot run: delivery/checkout/run/checkout-suite already exists; a second run under one name would
overwrite the evidence of the first — name this one differently
```

A middle step fails; the last step is recorded, never executed:

```
$ python3 bin/run.py ./delivery/checkout --run checkout-suite-3 --cwd ./target --timeout-seconds 60 \
      --step install="true" --step lint="false" --step test="true"
{
  "contract_version": "siegard-run/1",
  "run": "run/checkout-suite-3",
  "cwd": "/home/dev/checkout-service/target",
  "timeout_seconds": 60,
  "outcome": "failed",
  "failed_step": "lint",
  "steps": [
    { "name": "install", "command": "true", "outcome": "passed", "exit_code": 0,
      "output": "install.log" },
    { "name": "lint", "command": "false", "outcome": "failed", "exit_code": 1,
      "output": "lint.log" },
    { "name": "test", "command": "true", "outcome": "not_run", "exit_code": null,
      "output": null }
  ],
  "combined_output": "run.log"
}
```

### 6. `trace.py`

**General.** Resolves and maintains `siegard-trace.json`: which specification node produced which
file, the one fact that outlives both the plan and the delivery. It sits beside `siegard.json`, at
the git toplevel of `<target-root>`. Every `<file>` on the command line, and every path a bound
record names, is read relative to `<target-root>`, then converted to be relative to that toplevel
inside the file itself. Dependencies: PyYAML, jsonschema (imports `spec.py` and `project.py`).

- **Reads:** `<target-root>`'s files, and the specification through `spec.py`'s own pipeline.
  **Writes:** `siegard-trace.json`, with every form except `--check` and `--reconciliation`, which
  are read-only.

#### `trace.py <target-root>`

- **Function:** reads and validates the trace file against its schema; reports the count.
- **When to use it:** a quick sanity check — is there a trace at all, and does it hold together.
- **Read or write:** read-only.

Before anything has ever been bound:

```
$ python3 bin/trace.py ./target
no trace file: /home/dev/checkout-service/siegard-trace.json does not exist; nothing has been
bound yet
```

After one binding exists (see `--bind` below):

```
$ python3 bin/trace.py ./target
trace sound: 1 binding(s), traced against specification
```

#### `trace.py --check <target-root>`

- **Function:** recomputes every digest — the node's and every bound file's — and reports drift in
  three classes: `orphaned` (the node the file was bound to no longer exists in the specification —
  only `--prune` clears these), `moved` (the node's text changed since the bind), `code` (the bound
  file changed since the bind).
- **When to use it:** periodically, or before trusting that delivered code still says what the
  specification says — `/reconcile` and a review both start here.
- **Read or write:** read-only.

No drift:

```
$ python3 bin/trace.py --check ./target
no drift: 1 binding(s) match the specification and the code as both stand now
```

`moved` — the bound node's text changed since the bind:

```
$ python3 bin/trace.py --check ./target
domain/sales/order: bound at sha256:944984f5b60539ff5ce46d11d812072a7a4c27c1ca8cf8a0f9bb32f1541e1fdb,
now sha256:2a36464f38b8b95fe9a5062fd288ee5aa63fbdca44c8e6a2e4b3eefc44215b69; the specification
moved since this bind

1 drift finding(s) over 1 binding(s):
  0 orphaned: bound to a node the specification no longer holds — no bind can repair these, and
    `--prune` is the only thing that clears them
  1 moved: bound to a node whose text moved since the bind — rebind whoever owns the change
  0 code: bound to a file that changed or is gone — rebind whoever owns the change
```

`code` — the bound file changed without a rebind:

```
$ python3 bin/trace.py --check ./target
domain/sales/order: target/src/orders/place.ts bound at sha256:2489745f...818a, now
sha256:bd5a03aa...4151; the file changed without a rebind

1 drift finding(s) over 1 binding(s):
  0 orphaned: ...
  0 moved: ...
  1 code: bound to a file that changed or is gone — rebind whoever owns the change
```

`orphaned` — the node left the specification entirely:

```
$ python3 bin/trace.py --check ./target
domain/sales/order: no longer in the specification; the binding is stale

1 drift finding(s) over 1 binding(s):
  1 orphaned: bound to a node the specification no longer holds — no bind can repair these, and
    `--prune` is the only thing that clears them
  0 moved: ...
  0 code: ...
```

#### `trace.py --bind <target-root> <spec-root> <node> <file> [<file> ...] [--replace]`

- **Function:** reads `<node>`'s current digest and each `<file>`'s current digest, and writes the
  binding. By default this **extends** whatever that node already held: a file an earlier bind of
  the same node named, but this call does not, stays bound at the digest that earlier bind recorded
  — two tasks landing the same rule in two files is not one undoing the other. With `--replace`, it
  writes the entry **in full** instead: a file left off the new list is a file no longer claimed,
  and every path a `--replace` stops claiming is printed as a receipt.
- **When to use it:** by hand, for a single node/file pair — the general form behind what
  `/implement-task` normally does through `--bind-record` instead.
- **Read or write:** writes `siegard-trace.json` (creates it, if this is the first bind for this
  target root).

Default (extends) — a second file added to a node already bound to one:

```
$ python3 bin/trace.py --bind ./target ./specification domain/sales/order \
      src/orders/place-helpers.ts
bound domain/sales/order to 2 file(s) at /home/dev/checkout-service/siegard-trace.json
```

`--replace` — restating the node with only one file drops the other, and says so:

```
$ python3 bin/trace.py --bind ./target ./specification domain/sales/order \
      src/orders/place.ts --replace
bound domain/sales/order to 1 file(s) at /home/dev/checkout-service/siegard-trace.json
  --replace released 1 path(s) this call did not name; domain/sales/order no longer claims
  target/src/orders/place-helpers.ts. Where the fact moved out of those files, that is what
  --replace is for; where another delivery had bound one of them, that binding is gone from here,
  and the last committed trace is where it survives if anywhere
```

Artifact generated (`siegard-trace.json`, after the plain `--bind` above):

```json
{
  "specification": "specification",
  "bindings": [
    {
      "node": "domain/sales/order",
      "digest": "sha256:944984f5b60539ff5ce46d11d812072a7a4c27c1ca8cf8a0f9bb32f1541e1fdb",
      "files": [
        { "path": "target/src/orders/place.ts",
          "digest": "sha256:2489745f00e2d8a71c0a3417b7787c33a642f4ac02afb8dc051c01787a6d818a" }
      ]
    }
  ]
}
```

#### `trace.py --bind-record <target-root> <spec-root> <implementation-record> [--replace]`

- **Function:** reads one whole implementation record and binds every node/file pair it states, in
  one atomic write — refusing the entire operation if any part of the record would be refused.
- **When to use it:** this is the form `/implement-task` uses at the end of a task, instead of one
  `--bind` per node the task encoded.
- **Read or write:** writes `siegard-trace.json`.

```
$ python3 bin/trace.py --bind-record ./target ./specification \
      ./delivery/checkout/implementation/checkout/record-order.md
bound domain/sales/order to 1 file(s)
1 binding(s) written at /home/dev/checkout-service/siegard-trace.json, read from
record-order.md
```

#### `trace.py --prune <target-root>`

- **Function:** drops only the `orphaned` bindings. `moved` and `code` drift are never touched —
  only a rebind by whoever owns the change resolves those, because dropping either would discard
  the one record of which node that code answers to.
- **When to use it:** after confirming (via `--check`) that a node genuinely left the specification
  on purpose, to stop that finding from repeating on every future check.
- **Read or write:** writes `siegard-trace.json`.

```
$ python3 bin/trace.py --prune ./target
dropped domain/sales/order: the specification no longer holds it

1 binding(s) pruned at /home/dev/checkout-service/siegard-trace.json; 0 remain. What was dropped
was a link to a node that is gone — every drift with a node still in the base is still here, and
still owed a rebind.
```

#### `trace.py --reconciliation <reconciliation-record>`

- **Function:** the one form that writes nothing — holds a reconciliation record (written by
  `/reconcile`, at `siegard-reconcile/<slug>.md`) to `schemas/reconciliation.json`, so
  `--bind-record` can read it afterward exactly as it reads an implementation record.
- **When to use it:** as the first step of reconciling source that changed without a rebind — a
  hand-typed incident fix, a merge conflict resolved by hand, a file a delivery rewrote under
  another node's claim.
- **Read or write:** read-only.

```
$ python3 bin/trace.py --reconciliation ./siegard-reconcile/place-whitespace-fix.md
place-whitespace-fix.md holds: 1 file(s), 1 node(s) the judgment cleared, 0 it did not, 0 file(s)
the trace binds nothing to.
```

### 7. `terms.py`

**General.** A glossary that holds no text of its own: every term maps to a schema file and a JSON
pointer, and what gets printed is read live from the `description` at that pointer — nothing here
paraphrases a definition, so there is no copy to drift out of sync. No dependency beyond the
standard library.

- **Reads:** the schemas under `schemas/`. **Writes:** nothing — always read-only.

#### `terms.py`

- **Function:** prints every defined term, alphabetically, each with the schema file and JSON
  pointer it was read from.
- **When to use it:** to see the whole vocabulary at once — 211 lines, one short paragraph per
  term, sorted.
- **Read or write:** read-only.

```
$ python3 bin/terms.py
cause  [delivery-node.json/$defs/finding/properties/cause/description]
    Why a captured run failed, on a finding of the failures pass and nowhere else — the
    validator holds both halves of that. ...

covers (a test over a criterion)  [delivery-node.json/$defs/coverageEntry/properties/state/description]
    A test covers a criterion when it would fail if the criterion stopped holding — that is the
    whole test. ...
...
```

#### `terms.py <term> [<term> ...]`

- **Function:** prints only the named terms, in the order given.
- **When to use it:** looking up one or two words a validator's refusal used, without scrolling the
  whole glossary.
- **Read or write:** read-only. Exits 1 — printing nothing for that term rather than silently
  dropping it — if any named term is not in the table.

```
$ python3 bin/terms.py implements pin
implements  [plan-node.json/properties/implements/description]
    The specification nodes this task implements, by identity: the executor reads exactly these,
    current, from the specification itself — the specification does not change during a plan's
    execution, by convention, so there is nothing to pin. ...

pin  [delivery-node.json/$defs/pin/description]
    Content identity: the SHA-256 of the bytes of whatever artifact the field carrying it names,
    written `sha256:<hexdigest>` and computable by hand with `sha256sum`. ...
```

An unknown term:

```
$ python3 bin/terms.py gizmo
no contract defines gizmo
```

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

## The eight skills

Skills are what a human actually types (`/analyse`, `/plan-work`, ...). Each one is "one
invocation, one increment" — it does its job and stops; it never chains into the next skill on
its own.

| Skill | Turns this input… | …into this output | Scripts it calls | Agents it delegates to |
|---|---|---|---|---|
| **`/siegard-config`** | a human's stated settings | `siegard.json` | `project.py` | none |
| **`/analyse`** | material a human supplies (prose, files) | specification nodes + `projections/` | `spec.py` | none |
| **`/plan-work`** | a stated scope + the specification | plan nodes (`inventory/`, `epic/`, `task/`) + `plan.json`; specification extensions + decision-log entries where a fact was unstated | `spec.py`, `plan.py`, `deliver.py --standard` | `codebase-surveyor`, `backlog-decomposer`, `execution-contract-binder`, `unstated-fact-decider` |
| **`/implement-task`** | one planned task | source + tests + a delivery record + `delivery.json` + a trace bind | `plan.py --check`, `run.py`, `deliver.py`, `trace.py --bind-record` | `task-implementer`, `test-author` |
| **`/review-change`** | one delivered task | findings recorded under the delivery root + `delivery.json` | `plan.py --check`, `deliver.py`, `run.py`, `trace.py --check` | `coverage-auditor`, `specification-conformance-reviewer`, `standard-conformance-reviewer`, `failure-diagnostician` |
| **`/reconcile`** | source that changed without a rebind, whatever wrote it | a reconciliation record + a trace bind | `spec.py`, `trace.py` | none |
| **`/siegard-status`** | the question "where does this stand?" | a report derived from disk, writing nothing — deliveries, waits, BLOCKING notes, drift, recent decisions, ready next invocation | `project.py`, `spec.py`, `plan.py --check`, `deliver.py --outstanding`, `trace.py --check` | none |
| **`/siegard-archive`** | the human's ask to prune closed history from the tree | closed work+delivery pairs removed whole (history survives in git); the tag and commit handed ready, never run | `project.py`, `plan.py --check`, `deliver.py --check`, `spec.py`, `trace.py --check` | none |

No skill runs a shell command directly except by calling `run.py` — this is enforced by
`tests/test_agent_contract.py`, which fails the suite if any shipped agent is ever given a shell
tool. Everything a project builds or tests is run exactly once, by `run.py`, and captured; nothing
downstream re-executes it to double-check.

## The ten agents

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
  which nodes it actually implements, flagging every divergence: a contradiction stops the task
  (only a person settles it), and a fact the specification simply doesn't state is named for the
  next agent to decide.
- **`unstated-fact-decider`** — handed one fact the specification does not state — the fact
  alone, never the task that surfaced it, so the specification is never bent to fit a plan —
  it decides the fact the way `/analyse` would: reads the material first (a fact already stated
  there is found, not decided), returns the node edits that make the specification state it and
  the decision-log entry that discloses it, or reports that the specification contradicts the
  fact, which sends it back to the human. Read-only; `/plan-work` writes what it returns.

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

None of these ten agents produces a verdict, a score, or a pass/fail. Nine return **findings for
a human to read** — deciding what a finding means is deliberately kept outside every agent: "a
finding nobody can disagree with is a decision wearing a finding's clothes." The one exception
decides on purpose: the `unstated-fact-decider` settles a domain fact nobody stated, and its
decision is disclosed in the decision log precisely so a human can reject it afterwards — the
review moved after the decision instead of gating it, which is the same discipline `/analyse`
already follows for every fact the material leaves unstated.

## A complete process, start to finish

Here is what one real initiative looks like, tying every piece above into the order it actually
happens in.

```
 1. /siegard-config   → human declares roots + standard  ────────────► siegard.json
 2. /analyse           → human's material → spec nodes    ────────────► specification/, projections/
 3. /plan-work          → scope + spec → epics & tasks     ────────────► plan/, plan.json
      (survey → decompose → decide "implements", one task at a time;
       a fact the spec doesn't state is decided by a blind judge,     ────► specification/,
       written into the specification, disclosed in decision-log.md)        decision-log.md
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
- **The side door for stale bindings.** Source that changed without a rebind — an incident fix
  typed in directly, a merge conflict resolved by hand, a shared file a delivery rewrote under
  another node's claim (a bind restamps only the delivering task's own nodes) — never goes back
  through `/implement-task`. `/reconcile` is the only place that binds it: it reads what the
  trace already claims about that file, judges whether the new text still matches, and rebinds
  only what the judgment clears.

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
