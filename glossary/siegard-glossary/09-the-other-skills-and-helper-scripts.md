> [← Glossary](../siegard-glossary.md) · Previous: [Reconciliation (`/reconcile`)](08-reconciliation.md) · Next: [The agents](10-the-agents.md)

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
> [← Glossary](../siegard-glossary.md) · Previous: [Reconciliation (`/reconcile`)](08-reconciliation.md) · Next: [The agents](10-the-agents.md)
