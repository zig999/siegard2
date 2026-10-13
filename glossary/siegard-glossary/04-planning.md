> [← Glossary](../siegard-glossary.md) · Previous: [The specification](03-the-specification.md) · Next: [Delivering (`/implement-task`, `/deliver-scope`)](05-delivering.md)

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
> [← Glossary](../siegard-glossary.md) · Previous: [The specification](03-the-specification.md) · Next: [Delivering (`/implement-task`, `/deliver-scope`)](05-delivering.md)
