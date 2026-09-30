# Siegard glossary

A plain-language guide to the words Siegard uses: what each one means, where you meet it, and
what it looks like on disk or on the command line.

It describes Siegard **4.21.3**. Where this page and a skill's `SKILL.md`, a script's `--help`
or a schema under `schemas/` disagree, those files win: they are what actually runs. This page
explains them; it does not replace them.

---

## How to use this page

- **Section 1** is the one-minute picture. Read it first; every other term hangs off it.
- **Sections 2–9** group the terms by the moment you meet them: setting up a project, writing the
  specification, planning, delivering, reviewing, the trace, reconciliation, and the helper
  commands.
- **Section 10** lists every agent (the "judges" and "producers" Siegard delegates to).
- **Section 11** translates informal words people use in conversation (`unfold`, `refold`,
  `certificate`, "comment findings", "emitted-text findings") into the official terms.
- **Section 12** walks through one complete example, a hand-made fix, from start to finish.
- **Section 13** is an alphabetical index pointing back to each entry.

Commands are written the way the skills run them:

```sh
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/<script>.py ...
```

`${CLAUDE_PLUGIN_ROOT}` is the folder where the Siegard plugin is installed (it holds `bin/`,
`schemas/`, `skills/`, `agents/` and `hooks/`). To keep things short, this page writes
`trace.py ...` where the full form is `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py ...`.

---

## 1. The one-minute picture

Siegard is a framework for Claude Code that keeps **one written source of truth about what the
business decided** (the *specification*) and makes every line of code answer to it.

```
          what the business decided                 what gets built
 ┌──────────────────────────────┐        ┌────────────────────────────────┐
 │  SPECIFICATION (nodes, .md)  │        │   SOURCE CODE (your repo)      │
 │  rules/, domain/, contracts/ │        │   src/..., tests/...           │
 └──────────────┬───────────────┘        └───────────────▲────────────────┘
                │                                        │
   /analyse  ───┘   /plan-work → /implement-task → /review-change
  (writes it)       (plan)       (writes code+tests) (judges it)
                                         │
                                         ▼
                        siegard-trace.json  ("the trace")
             node  ⇄  file(s), each pinned with a SHA-256 digest
                                         │
                   later, someone edits a file by hand…
                                         ▼
                  trace.py --check  →  "drift"  →  /reconcile
```

Five ideas carry almost everything else:

| Idea | In one sentence |
|---|---|
| **Specification** | Markdown files ("nodes") stating what the business decided. It is the authority. |
| **Plan** | Tasks cut from a scope, each naming the specification nodes it implements. |
| **Delivery** | Records of what was written for each task, the tests that prove it, and the review. |
| **Trace** | A file saying which code file holds which node's fact, with fingerprints of both. |
| **Reconciliation** | The route that re-reads code that changed outside a task and re-links it. |

And one rule underneath: **a judgment is never made by the same context that produced the thing
being judged**. That is why Siegard spawns separate agents ("judges") and saves what they return
verbatim.

---

## 2. Setting up a project

### `siegard.json` — the project file
**What it is.** The one file where a project declares its roots, so nobody has to retype them.
It sits at the project root and is committed.
**Who writes it.** Only `/siegard-config`. Never hand-edit it.
**Example.**

```json
{
  "specification_root": "specification",
  "targets": { "backend": "backend" },
  "work_root": "work",
  "delivery_root": "delivery",
  "standard": { "backend": "backend/standard.yaml" },
  "telemetry_root": "telemetry",
  "edits_freely": ["frontend"]
}
```

Every skill starts by running `project.py <project-root>` to read this file.

### Project root
The directory that holds `siegard.json`. Every skill asks for it and never guesses it.

### Target, target source root
A **target** is one code base the project delivers into (`backend`, `frontend`…), named by a key
in `targets`. The **target source root** is its folder (`targets["backend"]`). Almost every path
in Siegard records is written *relative to the target source root*: `src/orders/place.ts`, not
`backend/src/orders/place.ts`.

### Git toplevel
The top folder of the git repository that contains the target. The trace
(`siegard-trace.json`), the reconciliation records (`siegard-reconcile/`) and the check records
(`siegard-check/`) live there, beside `siegard.json`.

> Two spellings of a path exist, and mixing them up is a common mistake. Things `trace.py`
> **prints** are spelled from the git toplevel (`backend/src/case.ts`). Everything you **write**
> (file sets, premises, findings) is spelled from the target source root (`src/case.ts`).
> `--stage` refuses the wrong spelling and tells you the right one.

### `specification_root`, `work_root`, `delivery_root`, `telemetry_root`
The folders where the specification, the plans, the delivery records and the telemetry reports
live. `work_root` and `delivery_root` are *containers*: one subfolder per initiative, with the
same slug in both.

### Initiative
One piece of development work, from plan to delivery. It has a **slug** (a kebab-case name such
as `order-placement`) and gets `work/<slug>/` and `delivery/<slug>/`.

### Slug
A name reduced to kebab-case (`case-transitions`, `hand-fix-invoicing`). Used for node file
names, initiatives, runs and reconciliations. A slug already taken is refused — records are
never overwritten.

### Standard (the registry)
**What it is.** The project's own rules about how its code is arranged (naming, layering,
lint…), in a YAML/JSON file the project writes. Siegard ships the *contract*
(`schemas/standard.json`), never a rule.
**Where you meet it.** `/siegard-standard` drafts it; `/review-change` and `/check-source` read
it; `/implement-task` runs its commands.
**Example.**

```yaml
contract_version: siegard-standard/1
standard: backend
summary: How the backend's TypeScript is arranged and checked.
rules:
  - id: ARC-01
    statement: A service or controller never constructs a dependency.
    because: A constructed dependency cannot be replaced in a test.
    decided_by: reading
    applies_to:
      - { under: src, suffix: .service.ts, nested: true }
  - id: STK-02
    statement: The code compiles with no type error.
    because: A type error is a defect the compiler already found.
    decided_by: tool
    tool: typecheck
    applies_to:
      - { under: src, suffix: .ts, nested: true }
commands:
  - step: install
    role: install
    command: npm ci
    timeout_seconds: 300
  - step: typecheck
    command: npx tsc --noEmit
    timeout_seconds: 120
  - step: test
    role: suite
    command: npm test
    timeout_seconds: 600
```

`deliver.py --standard <file>` validates it and prints what each phase of a delivery will run.

Terms inside the standard:

| Term | Meaning |
|---|---|
| `rules[].id` | Permanent identifier a finding cites (`ARC-01`). Never renamed, never reused. |
| `decided_by: reading` | A person or an agent must *read* the code to tell if the rule holds. |
| `decided_by: tool` | A command decides it (`tool` names the step). No agent reads it. |
| `applies_to` | Where the rule reaches: `under` a folder, files ending in `suffix`, `nested` or not. |
| `commands[]` | The project's own commands, each a `step` name, the exact `command` and a `timeout_seconds`. |
| `role` | `prepare` (set up a fresh worktree), `install`, or `suite` (the tests that prove the work). |
| `decides` | Architecture Constraints this step checks (see §3). |
| `presupposes` | Files the rules assume already exist (a `package.json`, a `tsconfig.json`). |
| `dependencies` | The **allowlist** of packages a delivery may install without asking. |
| `elsewhere` | What the standard deliberately does not hold, and where it lives instead. |

### `edits_freely`
A list of targets whose *surface* (labels, colours, spacing, column order) a person may change
without a task. It only changes one report: `trace.py --check` stops listing `code` drift for
files under those targets (and says how many it held back; `--all` shows them). It relaxes no
rule about business facts.

### The rules file (`hooks/rules.md`)
The short set of session rules Siegard places into every session and every agent, by hook. The
most important ones: which **route** a change takes (see below), never hand-edit derived files,
never state a business fact the specification does not hold, and **source carries no comments**.

### Routes
The six ways a change enters a project. A person chooses the route; it is never inferred.

| What changed | Route |
|---|---|
| A business fact (a status, a refusal, who may see what) | `/analyse` → `/plan-work` → `/implement-task` → `/review-change` |
| A capability's surface the specification already holds (a screen, a state) | `/plan-work` → `/implement-task` → `/review-change` |
| One wrong behaviour in code already delivered | `/plan-work` **corrective increment** → `/implement-task` |
| **Only a comment** (prose in source breaking the comment rule) | remove the comment by hand, then `/reconcile` over that file |
| **Only the surface** (label, colour, spacing) | edit directly, on a target declared `edits_freely` |
| **Source no delivery wrote** (adopting Siegard) | `/analyse` from the source alone → `/reconcile` as an **adoption** |

### The comment rule
**Source carries no comments**, with two exceptions: a directive a named tool consumes
(`// eslint-disable-next-line …`) and the reason the standard requires beside a suppression.
What a comment would have said goes to its proper home: the fact to its node, the rationale to
the decision log, the file-to-node link to the trace. A comment that restates a node's fact is
reported by a judge as a `restates` finding (see §8).

---

## 3. The specification

### Specification, specification root
The set of markdown files that states what the business decided, under one folder. Every file is
a **node**. It is validated by `spec.py`. It is the authority: when code and a node disagree, the
node is what the business decided.

### Node
One markdown file of the specification: YAML frontmatter (the fields) plus a short body
(`## Description`). Example — a Rule node:

```markdown
---
type: invariant
statement: A hypothesis MUST hold at least one piece of evidence before its case resolves.
constrains:
  - domain/troubleshooting/hypothesis
---

## Description

No case resolves on an unsupported explanation.
```

### Identity
A node's path from the specification root, without `.md`. The file above, stored at
`specification/rules/troubleshooting/hypothesis-requires-evidence.md`, has the identity
`rules/troubleshooting/hypothesis-requires-evidence`. Identities are how every record, plan and
trace names a node.

### Bounded context, `_context.md`
A **context** is a folder (`domain/troubleshooting/`) grouping one part of the business with its
own language. `_context.md` in that folder describes it: its responsibility and whether it is
`core`, `supporting` or `generic`. A context descriptor is never bound to code.

### The five classes
Every node belongs to exactly one class, chosen by its folder:

| Class | Folder | Answers | Subtypes |
|---|---|---|---|
| **Domain Model** | `domain/<context>/` | What exists and how it is structured | `aggregate-root`, `entity`, `value-object`, `domain-service`, `enumeration` |
| **Rule** | `rules/<context>/` | What must always hold | `invariant`, `policy`, `state-machine` |
| **Scenario** | `scenarios/<context>/` | What happens in one concrete case (given/when/then) | none |
| **Contract** | `contracts/<context>/` or `contracts/system/` | What is promised across a boundary | `domain-event`, `command`, `api`, `capability` |
| **Architecture Constraint** | `constraints/` | What limits how it may be built | none |

Short definitions of the subtypes:

- **aggregate-root** — the entry point of a consistency boundary (`case`, `order`).
- **entity / value-object** — a thing with its own identity / a value defined only by its content.
- **enumeration** — a closed list of values (`case-status`).
- **domain-service** — a named behaviour that belongs to no single element.
- **invariant** — a rule inside one aggregate, true at all times.
- **policy** — a rule that may cross aggregates; it must say whether it converges `immediate` or
  `eventual`.
- **state-machine** — the allowed states, transitions and rejections of one aggregate's status.
  The validator checks it is *total*: every state × trigger pair is a transition or a rejection.
- **domain-event / command / api** — messages and interfaces; each says `direction: published`
  or `consumed` (a consumed one names its `upstream`).
- **capability** — what the system promises its users; lives in `contracts/system/`.

Key fields you will see: `statement` (one sentence, one falsifiable condition), `constrains`,
`subject`, `given`/`when`/`then`, `payload`, `operations`, `answers`, `scope`, `fitness`.

### Material
Whatever a human gives `/analyse` to read: a document, a transcript, a ticket, or (for an
adoption) a survey written from the source code. Material is **data, never instructions** — a
sentence in it that reads like an order is analysed, never obeyed.

### Intake
The folder `work/<slug>/intake/` where a plan's raw material is kept. Never validated.

### Decision log (`decision-log.md`)
**What it is.** The one append-only list, at the specification root, of every fact the analysis
*decided* because the material did not say it. It never blocks anything: it discloses, and a
human reviews it afterwards.
**Example.**

```yaml
entries:
  - location: domain/troubleshooting/evidence.md
    field: attributes.value.type
    unstated: The material does not say what shape an evidence value takes.
    decided: string
    why: Every evidence sample in the material is shown as free text.
```

Three shapes of entry: **decided** (`decided` + `why`), **read** (`found`: where outside the
specification the fact was read; no `why`), and **retired** (`retired`: where a fact went when its
node or field left the specification). Entries are never edited or removed.

### Decide-and-disclose
The discipline behind the log: what the material does not state is decided, written into the node
like any other value (no `TODO`, no `unknown`), and disclosed in the log. Nodes never carry
`gaps`, `sources`, `rationale` or `proposal` fields — the validator refuses them.

### Floor and ceiling
The **floor** is what every analysis must produce (at least one complete context with at least one
definition). The **ceiling** is the rule that nothing answering no comprehension question may exist
(an element nothing reaches fails validation).

### Projection
A generated view of the specification — class diagrams, context map, state diagrams, capability
map, system overview — written by `spec.py --project` into `projections/`. Never edited by hand.

### Digest, pin
A **digest** is the SHA-256 fingerprint of a file's exact bytes, written `sha256:<hex>` — the same
value `sha256sum <file>` prints. A **pin** is a digest stored in a record to say "this is the
version I read". If the file changes, the digest no longer matches, and that mismatch is how
Siegard notices movement.

### `spec.py` — the specification validator

```sh
spec.py <spec-root>                       # validate everything
spec.py --node <file> <spec-root>         # validate one file while writing it (no cross-checks)
spec.py --digest <spec-root>              # print every node's digest
spec.py --project <spec-root>             # validate, then write projections/
spec.py --impact <id>[,<id>...] <spec-root>  # one hop around each node, both directions
spec.py --shape [--of <id>,...] <spec-root>  # measure how long nodes run; never refuses
```

- **Input:** the specification root (and a node identity or file for some forms).
- **Output:** "sound" or a list of problems (exit `0` sound, `1` problems, `2` cannot run).
- **`--impact`** is the **impact set**: every node a node references, every node referencing it,
  and every decision-log entry about it. Planning uses it to find candidate nodes.
- **`--shape`** is a report, never a refusal: statement lengths, multi-sentence statements,
  phrases repeated across nodes, prose naming nodes. `--of` marks the nodes you are responsible
  for so they show up even past the cut.

---

## 4. Planning (`/plan-work`)

### `/plan-work`
Turns a stated **scope** plus a valid specification into a **plan**: inventory, epics and tasks
as markdown files under `work/<slug>/`. It also handles three special modes: the **corrective
increment**, the **proof increment**, and **closing** a plan.

### Scope
What the human asks to be built, in their words. Planning never widens it on its own.

### Plan nodes: inventory, epic, task
| Kind | Path | What it holds |
|---|---|---|
| **inventory** | `inventory/<slug>.md` | What already exists where the change lands: `modules`, `conventions` (each with where it was seen), `must_not_duplicate`, `risks` |
| **epic** | `epic/<slug>.md` | A group of tasks and the nodes it answers for (`covers`), plus what it deliberately leaves out (`uncovered`, each with why) |
| **task** | `task/<epic>/<slug>.md` | One falsifiable `objective`, its `criteria`, the nodes it `implements`, its `depends_on` |

Example task:

```markdown
---
title: Record an opened case
summary: The entry point that persists an opened case.
objective: An opened case is persisted and retrievable by its case id.
criteria:
- Opening a case returns its case id.
implements:
- domain/troubleshooting/case
---
## What it is
…
## Notes
None.
```

Task fields you will meet:

| Field | Meaning |
|---|---|
| `objective` | The one outcome this task delivers. Two outcomes = two tasks. |
| `criteria` | Conditions, each falsifiable alone, under which the objective is met. |
| `implements` | The specification nodes this task implements (decided by the binder, see below). |
| `depends_on` | Tasks whose outcome this one builds on (dependency, never order). |
| `produces` | Files the delivery must create (the checkable half of the objective). |
| `stands` | Files where the implementation already exists — used by a proof increment, which writes only tests. |
| `reference` | Material the delivery must read, such as a mockup under `intake/layout/`. |

There is no status, priority or estimate field: progress lives in git and in the delivery records.

### `covers` / `uncovered`
An epic's `covers` lists the nodes it answers for. Every one must be implemented by one of its
tasks or listed under `uncovered` with a `why` — a deliberate, stated remainder, never a gap.

### Binder and notes
The **execution-contract-binder** agent decides, per task, which nodes the task `implements`. It
never rewrites the task: every mismatch comes back as a **note** in the task's `## Notes`, with a
**class**:

| Class | Question it answers | Effect |
|---|---|---|
| `compound` | Does a criterion state two conditions? | The task is re-cut, once. |
| `blocking` | Does a node *state* something the task contradicts or exceeds? | **Stops the task.** Only a person settles it. Shown as `BLOCKING, from the specification — …` |
| `unstated` | Does the task rest on a fact no node states at all? | Sent to the **unstated-fact-decider**; the specification gains the fact. |
| `underdetermined` | Is there a wrong implementation that still passes every criterion? | Kept; the test author must write a test excluding it. |
| `remainder` | Does a clause of a rule belong to another task? | Records where it belongs. |
| `advisory` | Anything else. | Information only. |

### Unstated fact, unstated-fact-decider
When planning finds a fact no node states, it is not a stop. The **unstated-fact-decider** agent
receives the fact alone — never the task that surfaced it ("decided blind") — and returns the node
edits plus a decision-log entry. A fact the specification *contradicts* is never decided: that is
`blocking`.

### Anchor, re-bind
When `plan.py` derives `plan.json`, it stores the digest of every node each task implements (the
**anchor**). If a node changes after planning, the task "waits on a **re-bind**": the binder must
read the node again before anyone delivers that task.

### Corrective increment
A one-task plan for **one wrong behaviour in delivered code**: no survey, no decomposition. It is
the route for a bug found by running the system — never a fix typed straight into the file.

### Proof increment
A plan whose tasks write **only tests**, one task per fact: facts a finite test can decide, already
held by delivered code (`stands`), proven by no test. The review that reads the proof then
**certifies** the node (see §8).

### Closing a plan, `closure.md`
When the human declares an initiative over, `/plan-work` writes `closure.md` at the work root.
A closed plan takes no more tasks; `/siegard-archive` may later remove it from the tree.

### `plan.json`
The derived index of a plan (nodes and edges). Written by `plan.py`, never by hand.

### `plan.py` — the plan validator

```sh
plan.py <work-root> <spec-root>           # validate, then write plan.json
plan.py --check <work-root> <spec-root>   # validate and compare, write nothing
plan.py --node <file> <work-root>         # validate one file
plan.py --standard <file> --against DIR <work-root> <spec-root>
                                          # also check what the standard presupposes vs `produces`
plan.py --unplanned <work-root-parent> <spec-root>
                                          # which nodes no initiative ever named (a query, exit 0)
plan.py --contract <branch> [--fields a,b | --without a,b]
                                          # print one slice of plan-node.json for an agent
```

---

## 5. Delivering (`/implement-task`, `/deliver-scope`)

### `/implement-task`
Delivers **one task**: writes the source, writes the tests, installs allowed packages, runs the
project's steps until it builds and the suite passes, writes the records, validates them, binds
the trace. Its order:

```
situate → set up → implement → build → prove → suite → validate → bind → report → stop
```

Two of those steps are other agents' (`task-implementer` writes source, `test-author` writes
tests) — in separate contexts, so the code and its tests do not agree "by construction".

### Delivery root and delivery records
`delivery/<slug>/` holds three kinds of record (markdown with frontmatter):

| Record | Path | Written by | Holds |
|---|---|---|---|
| **implementation** | `implementation/<epic>/<task>.md` | `/implement-task` | the files written, every criterion answered, every node answered |
| **proof** | `proof/<epic>/<task>.md` | `/implement-task` | every test, what it proves, what would make it fail |
| **review** | `review/<name>.md` | `/review-change` | the passes that ran, findings, coverage |

Example implementation record:

```yaml
target: backend
title: Record an opened case
summary: The entry point that persists an opened case.
task: sha256:fd8b6fdb…          # pin of the task file as read
files:
- path: src/troubleshooting/case.ts
  effect: holds the case aggregate and its status vocabulary
criteria:
- criterion: Opening a case returns its case id.
  met: true
  how: the constructor takes the id and the module answers with it
nodes:
- node: domain/troubleshooting/case
  encoded_at:
  - src/troubleshooting/case.ts
  how: the case's identity and status vocabulary are the shape this module holds
```

Fields worth knowing:

| Field | Meaning |
|---|---|
| `encoded_at` | The file(s) where a node's fact now lives. **This is what gets bound in the trace.** Absent means the node governed the work without a fact of its own reaching code ("honoured, not encoded"). |
| `how` | How the source answers the node or the criterion — something a reader can go and look at. |
| `inferences` | What the implementer decided that nothing stated, and from what. |
| `divergences` | Where the code departs from the task, the inventory or the standard, with why. |
| `deferred` | What was found and deliberately not changed. |
| `preserved` | What had to keep working, written before the change. |
| `installed` | Packages added (each must be in the standard's allowlist). |
| `tests[].proves` / `fails_when` | What a test demonstrates / what would have to break for it to fail. |
| `tests[].demonstrates` | A node the test claims to prove — a *claim* the review certifies or not. |
| `untested` | Behaviour left unproven, stated plainly. |
| `contested` | Where the test author believes the implementation is wrong. |
| `not_applicable` | Edge cases the task does not raise, each with why. |

### Captured run, `run.py`
**What it is.** The only way Siegard executes a command. `run.py` runs the project's own commands
(no shell), saves everything they printed, and records the outcome. It refuses a run name that
already exists, so every attempt stays readable.

```sh
run.py <delivery-root> --run <slug> --cwd <target-source-root> --timeout-seconds 600 \
    --step install="npm ci" --step test="npm test" [--excerpt 40]
```

- **Input:** where to write, a new run slug, the folder to run in, a timeout, one or more steps.
- **Output:** `run/<slug>/run.json` plus one log per step and a combined log. Exit `0` every step
  passed, `1` a step failed / timed out / was not found, `2` cannot run.
- A failed step stops the run; later steps are recorded `not_run`.
- `--excerpt N` prints the tail of the failed step to the screen only.

Step outcomes: `passed`, `failed`, `timed_out`, `not_found`, `not_run`.

### `delivery.json`
The derived index of a delivery root. Written by `deliver.py`, never by hand.

### Substrate, `presupposes`, `produces`
**Substrate** is what must already exist before a task can be delivered — the files the standard
`presupposes` or that an earlier task `produces`. A delivery over missing substrate is refused
before it writes anything.

### Deliverable set, `--outstanding`
The tasks that can be delivered **now**: no record yet, dependencies delivered and proven,
substrate present, no standing `BLOCKING` note, no pending re-bind.

```sh
deliver.py --outstanding <delivery-root> <work-root> <target-source-root> <spec-root>
```

It prints every task without a record, what each waits on, and the deliverable set. It is how
Siegard answers "what is left?" — there is no status field anywhere.

### `--unrecorded`
Before a delivery validates, it checks that every file it changed under the target is named by one
of its records. A changed test file nobody recorded would be a change no review ever reads.

```sh
deliver.py --unrecorded <target-source-root> <record> [<record> ...]
```

### Worktree batch
When the deliverable set holds several independent tasks, they may be delivered in parallel, one
git worktree each. Only `delivery.json` and `siegard-trace.json` can conflict on merge, and both
are re-derived rather than merged by hand. `deliver.py --worktreeinclude` lists the gitignored
files a fresh worktree needs.

### `/deliver-scope`, `orchestration.md`
Runs one scope **end to end** — plan, each task, review, and a proof round — committing between
steps. It is the only component allowed to `git commit`, and only when the human's own message
asks for the whole route. It keeps its log in `orchestration.md` at the delivery root.

```
gate → plan → commit → [deliver → commit, per task] → review → commit
     → [prove → commit, per task left testable] → review → commit → report → stop
```

### `deliver.py` — the delivery validator

```sh
deliver.py <delivery-root> <work-root> <target-source-root> <spec-root>   # validate, write delivery.json
deliver.py --check ...                                  # validate and compare, write nothing
deliver.py --outstanding ...                            # what is left, and why
deliver.py --node <file> <delivery-root>                # validate one record
deliver.py --standard <file> [--against DIR] [--specification DIR]   # validate a standard
deliver.py --standard <file> --reading [--for <path> ...]            # only the rules a reading decides
deliver.py --check-record <record> <target-source-root>              # validate a /check-source record
deliver.py --unrecorded <target-source-root> <record> ...            # changed paths no record names
deliver.py --worktreeinclude <file> <target-source-root> [--write]  # .worktreeinclude lines
deliver.py --contract <branch>                          # one slice of delivery-node.json for an agent
```

---

## 6. Reviewing (`/review-change`)

### `/review-change`
Reviews a delivered change from four angles, runs the project's steps over the whole change, and
writes a **review record**. It produces evidence, never an approval.

```
situate → capture → pass → compose → validate → report → stop
```

### Passes
The four independent judgments of a review. Each is a separate agent; none reads another's output.

| Pass | Agent | Question |
|---|---|---|
| **coverage** | `coverage-auditor` | Would the tests fail if a criterion stopped holding? |
| **conformance** | `specification-conformance-reviewer` (one per file) | Does the code state only what the specification holds? |
| **standard** | `standard-conformance-reviewer` | Does the code follow the project's own reading rules? |
| **failures** | `failure-diagnostician` | Why did a captured run fail? |

A pass that could not run is recorded with `missing: <what was absent>`. A review reported clean
over a pass that never ran is exactly what this prevents.

### Finding
One thing a judgment found, always with quoted evidence. Fields:

| Field | Meaning |
|---|---|
| `file` | Where it was seen (spelled from the target source root). |
| `where` | The line or construct. |
| `evidence` | **Quoted** from the source, never paraphrased. |
| `cost` | The consequence, in terms a reader can weigh — not "violates rule X". |
| `correction` | What would have to change (optional; not a decision). |
| `cites` | The one standard rule broken (standard pass only). |
| `cause` | `code`, `test`, `setup` or `build` (failures pass only). |

There is **no severity and no verdict**. A finding says what it costs; a person decides what it
means.

### Coverage states
Used for a task's criterion in a review, and for a node in a certification:

| State | Meaning |
|---|---|
| `covered` | The named tests would fail if it stopped holding — the whole test of a test. |
| `partial` | A stated part goes unexercised. |
| `uncovered` | Nothing exercises it. |
| `unauditable` | It cannot be read well enough to look for. |

### `unpaired`
Tests in the set that bear on **no** criterion of any task under review, each with what it
asserts. A reading, never a recommendation to delete.

### Test discipline words (SPEC-004)
- **Obligation** — something a proof owes evidence to: a criterion, a node's fact, or an
  `underdetermined` note.
- **Evidence** — a test that fails when the obligation is violated.
- **Finite test** — a test that decides a fact whole: one input against one expected result, or
  every pairing of a finite set (e.g. every state × trigger of a state machine).
- **Redundant test** — a test whose removal leaves every obligation protected. Not written.

### `/check-source`, `siegard-check/`
Reads files **no task delivered** against the standard's reading rules, and writes a record at
`siegard-check/<slug>.md` beside the trace. It runs nothing and never writes source. Validated by
`deliver.py --check-record`.

---

## 7. The trace

### Trace, `siegard-trace.json`
**What it is.** The one long-lived link between the specification and the code. Plans and
delivery records may be archived; the trace stays. For each node it holds the node's digest and the
file(s) holding its fact, each with its digest.
**Who writes it.** Only `trace.py`. Never hand-edit it.
**Example.**

```json
{
  "specification": "specification",
  "bindings": [
    {
      "node": "domain/troubleshooting/case",
      "digest": "sha256:9e85d914…",
      "files": [
        { "path": "backend/src/troubleshooting/case.ts",
          "digest": "sha256:dce326b5…",
          "judged": true }
      ]
    },
    {
      "node": "rules/sales/invoice-immutable",
      "digest": "sha256:…",
      "files": [ { "path": "backend/src/billing/raise.ts", "digest": "sha256:…" } ],
      "decided_by": "test",
      "step": "test",
      "proof": [ { "path": "backend/tests/billing/raise.spec.ts", "digest": "sha256:…" } ]
    }
  ]
}
```

(Paths inside the trace file are relative to the trace file's own folder, the git toplevel.)

### Binding
One entry of the trace: *this node's fact lives in these files*. A **node-file pair** is one node
plus one of its files; most of reconciliation reasons pair by pair.

`judged` on a file means a reconciliation's judgment cleared that pair at that digest. Absent means
it was stamped by a delivery (or by hand) and not re-read since.

### Bind
Writing or extending a binding. Normally done by a skill from a record:

```sh
trace.py --bind-record <target-root> <spec-root> <record>                 # from an implementation record
trace.py --bind-record <target-root> <spec-root> <record> --workspace <dir>  # from a reconciliation record
```

It binds exactly the nodes the record lists with `encoded_at`, and nothing else. By default it
**adds** to what a node already held (the "union"): a file an earlier bind put on the node stays.

`--bind <target-root> <spec-root> <node> <file> ...` is the raw form no record backs; it prints a
warning that the judgment behind the entry lives nowhere.

### Rebind
Binding a node again so the trace's digests match what is on disk now. It happens when a delivery
restamps its task's nodes, or when a reconciliation clears a pair. "Changed without a rebind" is
the core problem: someone edited a file and nobody updated the trace.

### `--replace`
Makes a bind **substitute the whole entry** instead of adding to it — for when a fact genuinely
moved *out* of a file. Every path it stops claiming is printed as a **receipt**. `/reconcile` never
passes it; it hands you the command to run yourself.

### Receipt
The lines a command prints about what it did *not* do or what it dropped (nodes not bound, paths
released, certifications released, drift held back). Carry receipts into the report; they are the
only place a partial action says it was partial.

### Drift, `--check`
**Drift** is any mismatch between the trace and what is on disk now. `--check` recomputes every
digest and reports drift in four **classes**:

| Class | Meaning | Answered by |
|---|---|---|
| `orphaned` | Bound to a node the specification no longer holds | `trace.py --prune` |
| `moved` | The node's text changed since the bind | `/reconcile` over the bound files, or a delivery implementing the node |
| `code` | A bound file changed (or is gone) | `/reconcile` over the file; `--release` if it is gone |
| `proof` | The test that decides a certified binding changed | a new certification |

Real output (from a test fixture):

```
$ trace.py --check backend
domain/troubleshooting/gone-from-the-base: no longer in the specification; the binding is stale
domain/troubleshooting/evidence: bound at sha256:0000…, now sha256:52f0…; the specification moved since this bind
backend/src/troubleshooting/case.ts: the file changed without a rebind — 1 binding(s): domain/troubleshooting/case

3 drift finding(s) over 3 binding(s):
  1 orphaned: …
  1 moved: …
  0 proof: …
  1 code over 1 file(s): …
```

Exit `0` means no drift; `1` means drift (a CI can run it). `--all` also lists the drift held back
by `edits_freely`.

### `--prune`
Drops bindings in the `orphaned` class only — after an `/analyse` removed nodes. If git shows the
node's file was renamed, it follows the rename instead of dropping. Never use it to silence
`code` or `moved` drift.

### `--release`
Drops a file **the tree no longer holds** from every binding naming it. Refuses a file that still
exists (that one is reconciled, never released).

```sh
trace.py --release <target-root> src/legacy/old-handler.ts
```

### `--encodes`
Which nodes each file is bound to — the reverse question `--check` cannot answer for files that did
not drift.

```
$ trace.py --encodes backend src/troubleshooting/case.ts
backend/src/troubleshooting/case.ts: 2 binding(s)
  domain/troubleshooting/case — stale: the file changed without a rebind
  domain/troubleshooting/gone-from-the-base — matches
```

- `--encodes --changed <target-root> [<ref>]` — the same over what git says changed (against
  `HEAD`, or since `<ref>`).
- `--encodes --rank <target-root>` — the **accretion counts**: files by how many bindings they hold,
  nodes by how many files they are bound to. It is where an audit's file set usually comes from.

### `--untraced` and the four file states
Lists every tracked file under a target that no binding names. Each file is in exactly one state:

| State | Meaning |
|---|---|
| **bound** | A binding names it. |
| **holds-nothing** | An adoption judged it and bound none of its candidates to it. |
| **outside** | An adoption deliberately kept it out of the judgment (config, wiring). |
| **unsurveyed** | None of the above — nobody has looked at it yet. |

```
$ trace.py --untraced backend
3 tracked file(s) under backend: 2 bound, 1 no binding names
  0 holds-nothing: judged by an adoption, which bound none of its candidates to it
  0 outside: kept outside an adoption's judgment
  1 unsurveyed: no binding and no adoption names it
```

It refuses nothing: most files of a real system carry no business fact and are never bound.

### `--convergence` and the five node states
Every node of the specification in exactly one state, across the trace and every initiative:

| State | Meaning |
|---|---|
| `current` | Bound, and every digest still matches. |
| `stale` | Bound, and some binding drifted (see `--check`). |
| `planned-unbound` | A task implements it or an epic covers it, but nothing binds it. |
| `declared-uncovered` | An epic looked at it and wrote down why it is not being built. |
| `unreached` | No initiative names it and nothing binds it. |

```sh
trace.py --convergence <target-root> <spec-root> <work-root-parent>
```

A query: always exit `0`, no score.

---

## 8. Reconciliation (`/reconcile`)

This is where most of the unfamiliar words live. Read the entries in order the first time.

### What reconciliation is for
Every normal bind comes out of a delivery. But code also changes in other ways: a hot fix typed
during an incident, a merge conflict resolved by hand, a delivery that rewrote a file other nodes
also claim. The trace then keeps asserting digests that are no longer true. `/reconcile` takes a
**file set you name**, has independent judges read those files against every node the trace binds
to them, writes a **reconciliation record**, and **rebinds only what the judges cleared**.

It never writes source and never writes a specification node.

### Its three modes
| Mode | When | Flag on `--stage` |
|---|---|---|
| **ordinary** | Files changed without a rebind (hand edit, merge). | *(none)* |
| **audit** | Bindings that never drifted but may be wrong (over-broad from day one). | `--audit` |
| **adoption** | Code no delivery wrote — adopting Siegard on an existing project. | `--adopt --node … [--outside …]` |

(`--stage --review` is the same staging used from inside `/review-change`.)

### The order

```
situate → stage → judge → capture → fold → bind → report → stop
```

### Required inputs
1. **The file set** — every path, relative to the target source root. Named by the human, never
   discovered.
2. **The project root.**
3. **The target** (decided automatically when `siegard.json` declares only one).
4. **The slug** — the record's name under `siegard-reconcile/`. A taken slug is a stop.

Optional: **certifications** (tests the human offers as proof of a node). Mode words: **audit**,
**adoption** (with its **candidates** and optional **outside** files).

### Situate
Checks that the specification is valid (`spec.py`), that the trace is valid (`trace.py`), that
the record path is free, and that the named files are **committed** (a digest of an uncommitted
edit points at content the next checkout erases).

### `--stage` — preparing the workspace
**What it does.** Computes, mechanically, every node each named file is bound to, and prepares
everything the judges need, in a throw-away folder (the **workspace**, usually from `mktemp -d`).

```sh
trace.py --stage <target-root> <spec-root> <slug> <workspace> <file> [<file> ...] \
    [--audit | --review [--node <n> ...] [--demonstrated <proof-record> ...] \
     | --adopt --node <candidate> ... [--outside <file> ...]] \
    [--certify <certifications.yaml>]
```

**Inputs:** target root, specification root, slug, workspace folder, the file set, and the mode
flags.
**Output, in the workspace:**

| Item | What it is |
|---|---|
| `manifest.json` | The node set per file, plus `unbound`, `omitted`, `mechanical`, `certify`, `candidates` |
| `packs/<file with / as __>.md` | A **node pack** per file: the full text of every node that file's judge must read, each with its source path and digest |
| `packs/certify__<node>.md` | A **certification pack** per node being certified |
| `candidates.txt` | The **candidate index** for the whole batch |

It also creates `siegard-reconcile/<slug>.returns/` (empty) at the git toplevel, where the judges'
answers will be saved.

**Never** work out a node set by reading `siegard-trace.json` yourself; a node missed by hand is a
judge handed an incomplete set, and its answer looks exactly like a complete one.

### The four things staging separates
| What | What happens |
|---|---|
| A file with nodes in the manifest | Gets a judge. |
| A file the trace binds nothing to (**unbound**) | Reported only (except on an adoption, where candidates are read against it). |
| A file whose every pair was omitted | Nothing left to judge; recorded under `pairs_omitted`. |
| A node in the `orphaned` class | Stop for that node; the route is `--prune`. |

### `pairs_omitted` (the omission guard)
A pair is skipped when re-judging it would buy nothing: its binding still matches the file's
current bytes **and** no record in `siegard-reconcile/` holds an open finding against it. The bind
recomputes both conditions later; if either stopped being true, the whole record is refused.
`--audit` turns this off: every standing claim is judged.

### Mechanical tier (`mechanical`)
Pairs a **run** can decide are not given to a judge: a constraint a registry step `decides`, or a
node a **certified test** decides. Instead you capture the step once:

```sh
run.py siegard-reconcile/<slug>.returns --run <slug> --cwd <target-source-root> \
    --timeout-seconds <bound> --step test="npm test"
```

and pass it to the fold with `--run`. A red step is a result, not a stop.

### Candidate, candidate index, candidate tier
A **candidate** is a node a judge *may* open when its file states a fact its own nodes do not
settle — to say "this fact belongs to that node" instead of "no node holds this". The **candidate
index** lists every node the batch answers for, with its files. On an ordinary run, the human may
also name nodes **written since the last bind** (the ones `/analyse` just listed) as candidates.
On an audit, no candidate tier is passed.

On an **adoption**, "candidate" has a stronger meaning: the nodes `/analyse` wrote from the
source, named with `--node`, read by **every** file's judge — their reading decides whether they
get bound at all.

### `--certify` and the certifications file
Offers tests as proof of a node. A small YAML file in the workspace:

```yaml
- node: rules/sales/invoice-immutable
  proof:
    - tests/billing/raise.spec.ts
  step: test
```

Staging refuses a node the files do not encode, a proof file that is not there, or a step the
registry does not declare.

### Judge — the conformance judgment
One **`siegard:specification-conformance-reviewer`** agent **per file**, spawned together. Each
gets: its one file (absolute path), its node pack path, the candidate index path, the
specification root, and the path of `schemas/conformance-return.json`. One judge per file, because
one context reading everything at once "saturates" and claims clean over pairs it never weighed.

For each certification, one **`siegard:coverage-auditor`** agent gets the certification pack.

The orchestrating session **never reads the files and decides itself** — it accepted the human's
premise that the code is right, and would be judging from that premise.

### The return (conformance return)
What one judge answers: plain YAML, **only four keys allowed at any depth** — `findings`, `read`,
`looked_past`, `candidates_opened`. A fifth key refuses the return at fold time.

```yaml
findings:
  - where: the guard added to raise(), line 12
    evidence: |-
      if (order.invoices.length >= 1) return existing
    cost: |-
      the at-most-one-invoice rule lives only here, so the next reader looks
      for it in the specification and does not find it
    node: rules/sales/invoice-immutable
    kind: contradicts
read:
  - node: rules/sales/invoice-immutable
    held_at: nowhere
    evidence: |-
      the rule the file cites governs modification of a raised invoice;
      `if (order.invoices.length >= 1)` states a cap no node holds
candidates_opened:
  - rules/sales/invoice-immutable
```

The keys, one by one:

| Key | Meaning |
|---|---|
| **`findings`** | What the judge found against, each with `where`, `evidence`, `cost`, `kind`, and optionally `file`, `node`, `correction`. **The key absent means "nothing found" — a real result and a claim**: over this file and these nodes, the source states what the specification holds and nothing else. People often *say* "`findings: []`" for this, but in a saved return the empty list is refused by the contract (it needs at least one item): leave the key out. |
| **`read`** | **One entry per node of the judge's own set, in order — never a subset, never a candidate.** Says, per node, where its fact sits now. This is what a cleared node's `how` is written from. |
| `read[].node` | The node's identity. |
| `read[].held_at` | Where in the file the node's fact sits now (`the return statement of place(), line 41`), **or the word `nowhere`**. A fact is held by *code*, never by a comment about it. The answer is read by its first word: `nowhere. The file does no ranking.` still means nowhere. |
| `read[].evidence` | Quoted code that shows it. Where `held_at` is `nowhere`, it quotes what was looked at. |
| **`looked_past`** | One sentence naming what was seen and not reported because it belongs to another judgment (e.g. a style problem). |
| **`candidates_opened`** | Every candidate node the judge actually opened, whether or not a finding came of it. **`candidates_opened: []` (or the key absent) means it opened none.** It measures whether the candidate tier is worth offering. |

Free-text values are written as block scalars (`|-`) so a stray colon cannot break the YAML.

### `kind` — the three kinds of finding
A judgment answers different questions, and `kind` says which:

| `kind` | Means | Blocks the node's binding? | Route |
|---|---|---|---|
| **`contradicts`** | The source says what the node denies, or no longer carries the node's fact, or became a second home for it. | **Yes** — the node is not bound. | `/analyse` (specification behind) or `/plan-work` corrective (code wrong) |
| **`unstated`** | The source states a fact **no node holds at all**. | No — no rebind could ever close it. | `/analyse` |
| **`restates`** | A **comment** or a **docstring** — prose no running system emits — says a node's fact, **while code somewhere holds that fact too** (this file or another the finding names). | No — the pair conforms and binds where the code is. | Remove the prose (the comment route), then `/reconcile` over the file again |

If no code anywhere holds the fact, a comment that states it is `contradicts`, not `restates`.

**Text the running system emits is behaviour, never `restates`** — a tool's description, an
error message, a prompt sent to a model, a log line. It is what the system tells someone, so
removing it would change behaviour. Where it states a node's fact truly, it is **no finding** at
all; where it states the fact differently from the node, it is `contradicts`.

### Save the returns verbatim
Each return is saved the moment it arrives, as a copy and nothing else, at:

```
siegard-reconcile/<slug>.returns/<file path with every '/' as '__'>.yaml
siegard-reconcile/<slug>.returns/certify__<node with every '/' as '__'>.yaml
```

Never reshape, trim or repair one. The returns are the **evidence** the record is folded from, and
they outlive the session. A return that is unusable (missing field, a node not answered) means the
prompt was wrong: run a **fresh delegation** with the prompt fixed — never ask the same judge a
follow-up, never edit its answer. Two divergent answers from one judge void each other.

### Premise
The one part of the record that is the human's: a small YAML file in the workspace.

```yaml
title: Hand correction to invoicing
summary: The nightly run raised two invoices for one order; the guard was added by
  hand and the behavior is correct.
target: backend
files:
  - path: src/billing/raise.ts
    change: refuses a second invoice for an order that already has one
```

`summary` states **why the human says the code is correct** — as the human's assertion, never as
a finding. `change` says what the file now *does* differently, not what was typed.

### `--fold` — writing the record
**What it does.** Mechanically combines ("folds") all saved returns plus the premise into the
reconciliation record. No judgment happens here — only fixed rules.

```sh
trace.py --fold <target-root> <workspace> <premise.yaml> siegard-reconcile/<slug>.md \
    [--run siegard-reconcile/<slug>.returns/run/<slug>]
```

**Inputs:** the workspace (manifest, returns), the premise, the record path, and `--run` exactly
when there was a mechanical tier.
**Output:** `siegard-reconcile/<slug>.md`, validated before it lands.
**Rules it applies:** a node conforms only where every judge that read one of its files cleared
it; a finding naming a node lands on that node; a finding naming **no** node lands on every node
of that file (those are marked `collateral`); `unstated` and `restates` findings go to their own
lists; a certification is written only where the auditor answered `covered` **and** the node's
own reading cleared.

**Never edit what the fold wrote.** If the fold refuses: a refusal naming a delegation → fresh
delegation; a refusal about the premise → fix the premise.

### The reconciliation record (`siegard-reconcile/<slug>.md`)
Lives at the git toplevel, beside the trace, and is **never deleted** (not even by
`/siegard-archive`): it is the justification for bindings that are still in the trace.
Contract: `schemas/reconciliation.json` (current version `siegard-reconcile/8`).

```yaml
contract_version: siegard-reconcile/8
title: Hand correction to invoicing
summary: …                                   # the human's premise
target: backend
files:
  - path: src/billing/raise.ts
    change: refuses a second invoice for an order that already has one
nodes:
  - node: rules/sales/invoice-immutable
    conforms: false
    how: the source now states `if (order.invoices.length >= 1) return existing`, and
      no node holds that an order carries at most one invoice
    observed_at:
      - src/billing/raise.ts
notes: The behavior is right and the specification is behind it.
```

Fields:

| Field | Meaning |
|---|---|
| `files` | The file set the human named, each with its `change`. |
| `nodes[]` | Every node the trace binds to a named file, with the answer. |
| `conforms` | `true` = the judgment cleared the node; `false` = a finding stands. |
| `how` | Why — with what was read, quoted. |
| `encoded_at` | On a cleared node only: the files that hold its fact. **This is exactly what gets bound.** |
| `observed_at` | On an uncleared node only: files that were read, without claiming anything. |
| `collateral` | On an uncleared node: nothing was found against **its own** substance; it shares a file with a finding that named no node. Fix the finding and it clears with it. |
| `decided_by`, `step`, `proof` | A certification that held: the node is now decided by a test. |
| `remainder`, `remainder_why` | A certification that did not hold: whether a test *could* close the gap (`testable`) or not (`untestable`), and the assertion that would. |
| `unstated` | Facts the source states that no node holds, keyed by file. |
| `restates` | Places where a comment or docstring restates a node's fact the code already holds. |
| `unbound` | Named files the trace binds nothing to. |
| `adopted` | Present on an adoption record. |
| `unheld` | Adoption only: candidates **no file of the set holds** and nothing was found against — every judge answered `nowhere`. They claim no file. |
| `outside` | Adoption only: files the human kept out of the judgment. |
| `pairs_omitted` | Pairs not re-judged, each with its reason. |
| `notes` | Prose a later reader needs; never a decision. A note ending "owed a route of its own" must be carried into the report. |

### `--reconciliation` — validating the record

```sh
trace.py --reconciliation siegard-reconcile/<slug>.md
```

Writes nothing. Checks the record against its contract and the accounting (every path claimed is
in `files`; every named file is claimed or declared unbound).

### Bind (in reconciliation)

```sh
trace.py --bind-record <target-root> <spec-root> siegard-reconcile/<slug>.md --workspace <workspace>
```

Binds **only the nodes carrying `encoded_at`** — the cleared ones — and nothing else. The nodes
with findings stay exactly as they were. `--workspace` makes it refuse if any file or node moved
since staging. Run it once, whether everything cleared or not, and read its receipt.

### `--owed` — what is still open
**What it does.** Reads every record under `siegard-reconcile/` as a body of evidence (the
"corpus") and lists findings **no bind closed**. It writes nothing and decides nothing.

```sh
trace.py --owed <target-root> [--all]
```

It is needed because `--check` cannot see these: a node the judgment refused gets no new digest,
so there may be nothing for `--check` to compare. Each open finding is in one of three states:

| State | Meaning |
|---|---|
| `unseen` | Nothing binds the pair — `--check` can never report it. |
| `covered` | Bound at today's content — a later bind wrote over the only symptom; the finding still stands. |
| `reported` | The binding is stale, so `--check` already shows it; the record says what was found. |

It also lists the `unstated` facts, the `restates` text, pairs answered both ways by different
records, and the **testable remainders** (nodes a test could close). Exit `0` = nothing owed.
(Do not confuse this `covered` with the coverage state `covered` in §6.)

### Certification, `decided_by: test`
A **certification** is the judgment that the tests a human offered **would fail if the node's fact
stopped holding**. When it holds (auditor answers `covered`), the binding becomes **decided by a
test**: from then on, drift on its files is answered by running the step rather than by a new
reading, and no judge reads that pair again. The proof's digests are pinned in the trace; if the
test file changes, `--check` reports `proof` drift and the binding falls back to reading.

Default for every binding is `decided_by: reading`. A certification is offered by the human
(`--certify`) or composed from proof records during a review (`--demonstrated`); it is never
invented by the skill.

### Remainder: `testable` / `untestable`
When a certification is short of `covered`, the auditor says whether what is left could be closed
by a test:

- **`testable`** — one input against one expected result would close it. `remainder_why` names the
  assertion. `--owed` lists these; the report hands a **proof increment** to close them.
- **`untestable`** — no finite test closes it (an identity spanning files, a totality over a set
  nothing enumerates).

### Adoption
The route for **code written before Siegard**. Steps:

1. `trace.py --untraced <target>` — at the start, every file is `unsurveyed`.
2. Write the material **from the source alone** (observable behaviour, each fact beside its path).
3. `/analyse` over it → it lists the nodes it wrote.
4. `/reconcile` as an adoption over the context's files, with those nodes as `--node` candidates
   and config/wiring as `--outside`. The first adoption creates `siegard-trace.json`.
5. Read what comes back: `unheld` candidates, `contradicts`, `unstated` → back to `/analyse`;
   `restates` → remove the text, reconcile again.
6. Then the documentation, as an ordinary `/analyse` increment.

Adoption is **complete** when `--untraced` shows no `unsurveyed` file and `--convergence` no
`unreached` node. It is computed, never recorded, and nothing waits for it.

### The report and the next invocation
`/reconcile` ends by saying: the file set; what staging held per file; how many judges; the answer
per node with evidence; what was bound and what was not; certifications that held or not; and the
**next file set = the remainder** (only the files whose nodes are still owed). For every uncleared
node it hands **both** doors without choosing — `/analyse` (the specification is behind) or
`/plan-work` corrective (the code is wrong) — plus the comment route for `restates`.

---

## 9. The other skills and helper scripts

### `/analyse`
Turns material into specification nodes, validates them (`spec.py`), and derives projections.
Ends by listing the identities it wrote — the ones you may pass as candidates to `/reconcile`.

### `/siegard-config`
Writes or updates `siegard.json` from what you tell it. The only writer of that file.

### `/siegard-standard`
Drafts the project's standard from what its tooling already enforces (linter, compiler, secret
scanner) and what a person states. Never invents a rule.

### `/siegard-status`
A read-only, friendly status of the whole project: specification soundness, recent decisions,
each live initiative's outstanding tasks and `BLOCKING` notes, trace drift by class, uncommitted
work. It cites a command for every claim.

### `/siegard-progress`
A compact table of one initiative's tasks (status + why), made to be run repeatedly (e.g. with
`/loop`).

### `/siegard-archive`
Removes **closed** initiatives (work + delivery) from the working tree, after checking them
mechanically. It never touches the project file, the trace, the specification, the decision log
or the reconciliation records, and never commits — it hands you the git commands.

### `/siegard-telemetry` and `telemetry.py`
Writes a report of **how** a stretch of work happened (agents, cost in tokens and time, refusals,
runs, decisions, compactions), counted from disk and from the harness's session transcripts.

```sh
telemetry.py --probe <project-root> --since last        # can the transcripts be read?
telemetry.py <project-root> --since 2026-09-29T00:00:00Z [--until …]
```

Output: `<telemetry_root>/<stamp>.json` plus a Markdown report beside it.

### `project.py`

```sh
project.py <project-root>
```

Reads and validates `siegard.json` and prints each field it declares, one per line. Every skill
runs it first. If an old copy of the rules sits in the project's root `CLAUDE.md`, it prints a
`rules:` line asking you to remove it.

### Contract slices (`--contract`)
`plan.py --contract <branch>` and `deliver.py --contract <branch>` print one self-contained piece
of a schema, so an agent is handed exactly the fields it writes instead of the whole schema.

### Exit codes (all scripts)
| Code | Meaning |
|---|---|
| `0` | Sound / nothing found / done. |
| `1` | Problems found (invalid file, drift, a finding no bind closed, a refused record). |
| `2` | Cannot run (missing folder, broken input). |

A non-zero exit from a *status* command is not a failure of the skill: it **is** the status.

---

## 10. The agents

Skills delegate judgment and production to these agents, always by their plugin-scoped name
(`siegard:<name>`). No agent has a shell. Only the two producers can write files.

| Agent | Used by | Does | Writes files? |
|---|---|---|---|
| `codebase-surveyor` | `/plan-work` | Surveys the code; returns inventory nodes | No |
| `backlog-decomposer` | `/plan-work` | Cuts the scope into epics and task skeletons | No |
| `execution-contract-binder` | `/plan-work` | Decides each task's `implements`; returns classified notes | No |
| `unstated-fact-decider` | `/plan-work` | Decides one unstated fact, blind to the task; returns node edits + log entry | No |
| `task-implementer` | `/implement-task` | Writes the source for one task and its implementation record | **Yes** |
| `test-author` | `/implement-task` | Writes the tests and the proof record | **Yes** |
| `failure-diagnostician` | `/implement-task`, `/review-change` | Says why each failure in a captured run failed | No |
| `coverage-auditor` | `/review-change`, `/reconcile` | Pairs criteria with tests; certifies a node's tests | No |
| `specification-conformance-reviewer` | `/review-change`, `/reconcile` | Reads one file against its nodes; returns findings + `read` | No |
| `standard-conformance-reviewer` | `/review-change`, `/check-source` | Reads files against the standard's reading rules | No |

**Delegation** = spawning one of these in a clean context. **Inline** = the fallback when a
session cannot spawn agents: the session applies the agent's file itself, and the report must say
so. `/reconcile` refuses to run inline if the same session wrote any node being judged.

---

## 11. Informal words you may meet

These words show up in conversations, session notes or commit messages. They are **not** fields
or flags of the framework; here is the official term each one stands for.

| You may hear | It means | Official term |
|---|---|---|
| **fold** | Combining the saved judge returns + premise into the record. | `trace.py --fold` |
| **refold / re-fold** | Running `--fold` again over the **same saved returns** — typically after a framework fix changed a fold rule, and before the record is committed. Possible only because the returns are kept verbatim and the fold is mechanical. It is never a hand edit of the record, and never asks the judges again. | `trace.py --fold` (again) |
| **unfold / unfolded** | Appears only as an internal name in `deliver.py`: a review whose conformance pass ran over a traced target but **folded no reconciliation record**. `deliver.py` prints a receipt for it: the other nodes bound to the reviewed files still carry old digests, and a `/reconcile` over those files closes them. | the "unreconciled review" receipt |
| **certificate** | A certification that held. | `decided_by: test` (+ `step`, `proof`) |
| **comment findings** | `restates` findings where the text is a code **comment** or docstring. | `kind: restates` |
| **emitted-text findings** | Findings about text the **running system emits** — a tool/API description, an error message, a prompt, a log line. Since 4.21.3 such text is behaviour, never `restates`: agreeing with its node it is no finding, disagreeing it is `contradicts`. (Before 4.21.3 a description restating a fact code enforced was filed `restates`, so older records may still carry such entries.) | no finding, or `kind: contradicts` |
| **unheld** | *(this one is official)* an adoption candidate no file holds. | `unheld` in the record |
| **the corpus** | All records under `siegard-reconcile/`, read together. | read by `--owed` |
| **pair** | One node + one of its files. | node-file pair |
| **clear / cleared** | The judgment found nothing against a node: it conforms and gets bound. | `conforms: true` + `encoded_at` |
| **stamp / restamp** | Writing current digests into the trace. | bind / rebind |
| **judge** | An agent delegated a judgment. | a delegation |
| **door** | A ready-to-paste invocation a report hands you. | "the invocation ready to paste" |

---

## 12. One complete example: a hand fix

**The situation.** During an incident, someone added a guard to `src/billing/raise.ts` so an order
cannot get two invoices, and committed it. The behaviour is correct.

**1. Something notices.** A CI runs:

```
$ trace.py --check backend
backend/src/billing/raise.ts: the file changed without a rebind — 1 binding(s): rules/sales/invoice-immutable
...
1 code over 1 file(s): …
```

**2. You invoke the route**, naming the file set, project root and a new slug:

```
/siegard:reconcile  file set: src/billing/raise.ts   project root: .   slug: hand-fix-invoicing
```

**3. Stage.** The skill runs:

```sh
trace.py --stage backend specification hand-fix-invoicing /tmp/ws src/billing/raise.ts
```

The workspace now holds `manifest.json`, `packs/src__billing__raise.ts.md` (the text of
`rules/sales/invoice-immutable`), and `candidates.txt`; the empty folder
`siegard-reconcile/hand-fix-invoicing.returns/` exists.

**4. Judge.** One `siegard:specification-conformance-reviewer` reads the file against its pack. It
returns (saved verbatim as `siegard-reconcile/hand-fix-invoicing.returns/src__billing__raise.ts.yaml`):

```yaml
findings:
  - where: the guard added to raise(), line 12
    evidence: |-
      if (order.invoices.length >= 1) return existing
    cost: |-
      the at-most-one-invoice rule lives only here
    node: rules/sales/invoice-immutable
    kind: contradicts
read:
  - node: rules/sales/invoice-immutable
    held_at: nowhere
    evidence: |-
      the rule governs modification of a raised invoice; the guard states a cap no node holds
candidates_opened:
  - rules/sales/invoice-immutable
```

**5. Fold.** The skill writes the premise ("added by hand during an incident; correct") and runs
`trace.py --fold …`. The record says `conforms: false`, `observed_at: [src/billing/raise.ts]`.
`trace.py --reconciliation` passes.

**6. Bind.** `trace.py --bind-record … --workspace /tmp/ws` binds nothing (no node has
`encoded_at`) and its receipt says so.

**7. Report.** Two doors, and the skill chooses neither:
- **The code is right, the specification is behind** → `/analyse` with the finding as material,
  so a node gains "an order carries at most one invoice"; then `/reconcile` again over the same
  file under a new slug.
- **The specification is right, the code is wrong** → `/plan-work` corrective increment.

**8. Later.** `trace.py --owed backend` keeps listing the finding until a record clears the pair.

Had the only problem been a comment — say `// an order may only have one invoice` above code
that already enforces a rule node — the judge would have filed `kind: restates`, the node would
have bound, and the report would have handed the comment route: delete the comment, commit,
`/reconcile` that file under a new slug. Had it instead been the **error message** the system
returns, saying the same thing as the node, there would have been no finding at all: that is
behaviour agreeing with the node.

---

## 13. Alphabetical index

| Term | Section |
|---|---|
| `_context.md` | 3 |
| accretion counts (`--rank`) | 7 |
| adoption, `--adopt` | 8 |
| advisory (note) | 4 |
| aggregate-root | 3 |
| anchor | 4 |
| audit, `--audit` | 8 |
| bind, `--bind`, `--bind-record` | 7, 8 |
| binding | 7 |
| blocking, `BLOCKING` | 4 |
| bounded context | 3 |
| candidate, candidate index, candidate tier | 8 |
| `candidates_opened` | 8 |
| capability | 3 |
| captured run | 5 |
| certification, certification pack, `--certify` | 8 |
| certificate (informal) | 11 |
| `--changed` | 7 |
| `--check` | 7 |
| `/check-source`, `--check-record` | 6 |
| class (the five) | 3 |
| closure, `closure.md` | 4 |
| `code` (drift) | 7 |
| collateral | 8 |
| comment findings (informal) | 11 |
| comment rule | 2 |
| compound (note) | 4 |
| conformance pass | 6 |
| conformance return | 8 |
| `conforms` | 8 |
| `contested` | 5 |
| contract (class) | 3 |
| `--contract` (slices) | 9 |
| `contradicts` | 8 |
| `--convergence` | 7 |
| corrective increment | 4 |
| `covered` / `partial` / `uncovered` / `unauditable` | 6 |
| `covered` / `unseen` / `reported` (`--owed`) | 8 |
| `covers` / `uncovered` | 4 |
| coverage pass | 6 |
| criteria | 4 |
| `decided_by` (standard) | 2 |
| `decided_by: test` / `reading` (trace) | 8 |
| decide-and-disclose | 3 |
| decision log | 3 |
| `deferred` | 5 |
| `/deliver-scope`, `orchestration.md` | 5 |
| deliverable set | 5 |
| `delivery.json` | 5 |
| delivery root, delivery records | 5 |
| `demonstrates`, `--demonstrated` | 5, 8 |
| `depends_on` | 4 |
| digest | 3 |
| divergences | 5 |
| drift | 7 |
| `edits_freely` | 2 |
| emitted-text findings (informal) | 11 |
| `encoded_at` | 5, 8 |
| `--encodes` | 7 |
| epic | 4 |
| evidence | 6, 8 |
| failures pass, `cause` | 6 |
| finding | 6, 8 |
| finite test | 6 |
| floor / ceiling | 3 |
| `--fold` | 8 |
| git toplevel | 2 |
| `held_at` | 8 |
| `holds-nothing` / `outside` / `unsurveyed` | 7 |
| `how` | 5, 8 |
| identity | 3 |
| impact set, `--impact` | 3 |
| inferences | 5 |
| initiative | 2 |
| inline | 10 |
| intake | 3 |
| inventory | 4 |
| invariant / policy / state-machine | 3 |
| judge | 8 |
| `kind` | 8 |
| `looked_past` | 8 |
| manifest | 8 |
| material | 3 |
| mechanical tier | 8 |
| `moved` | 7 |
| node | 3 |
| node pack | 8 |
| node-file pair | 7 |
| `nowhere` | 8 |
| obligation | 6 |
| `observed_at` | 8 |
| `orphaned` | 7 |
| `--outstanding` | 5 |
| `--owed` | 8 |
| `pairs_omitted` | 8 |
| passes | 6 |
| pin | 3 |
| premise | 8 |
| `presupposes`, `produces`, substrate | 5 |
| `project.py` | 9 |
| projection | 3 |
| `proof` (drift) | 7 |
| proof increment | 4 |
| proof record | 5 |
| `--prune` | 7 |
| `read` | 8 |
| rebind | 7 |
| re-bind (planning) | 4 |
| receipt | 7 |
| reconciliation record | 8 |
| `--reconciliation` | 8 |
| refold (informal) | 11 |
| `--release` | 7 |
| remainder (note) | 4 |
| `remainder` `testable`/`untestable` | 8 |
| `--replace` | 7 |
| `restates` | 8 |
| returns, `.returns/` | 8 |
| review record | 5, 6 |
| routes | 2 |
| `run.py` | 5 |
| scenario | 3 |
| scope | 4 |
| `--shape`, `--of` | 3 |
| `siegard.json` | 2 |
| `siegard-check/` | 6 |
| `siegard-reconcile/` | 8 |
| `siegard-trace.json` | 7 |
| slug | 2 |
| `--stage` | 8 |
| standard (registry) | 2 |
| standard pass | 6 |
| `stands` | 4 |
| target, target source root | 2 |
| task | 4 |
| telemetry | 9 |
| trace | 7 |
| underdetermined (note) | 4 |
| `unbound` | 8 |
| unfold / unfolded (informal) | 11 |
| `unheld` | 8 |
| `unpaired` | 6 |
| `--unplanned` | 4 |
| `--unrecorded` | 5 |
| `unstated` (finding) | 8 |
| unstated (note), unstated-fact-decider | 4 |
| `--untraced` | 7 |
| workspace | 8 |
| worktree batch | 5 |
