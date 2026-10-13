> [← Glossary](../siegard-glossary.md) · Previous: [The one-minute picture](01-the-one-minute-picture.md) · Next: [The specification](03-the-specification.md)

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
> [← Glossary](../siegard-glossary.md) · Previous: [The one-minute picture](01-the-one-minute-picture.md) · Next: [The specification](03-the-specification.md)
