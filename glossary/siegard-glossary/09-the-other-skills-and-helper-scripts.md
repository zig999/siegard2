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

### Armed goal (`goal.py --arm`)
A goal is a condition the session keeps working toward until it holds. Armed through the
framework (since 5.43.0), it ends on a script's answer rather than on a model's reading: the
plugin's `Stop` hook runs `goal.py --state` at each stop. `state A` (done) or `state B` (stopped
for the person) ends the goal; `not yet` blocks the stop with the checks that failed, and the
session answers it with the route's next step; a fourth identical `not yet` pauses the goal.

```sh
goal.py --arm <project-root> --slug <slug> [--scope <id>]... | --objective <text>
goal.py --disarm <project-root>
```

Only `/siegard:siegard-goal` runs it, and only where your invocation opens with `--arm`: the skill
is closed to the model, so no session arms a goal on its reading of a message. The record is `siegard/goal.json` under the git
directory, never in the tree.

### Handoff record (`handoff.py`)
A handoff is the last message of a skill: what needs you, then the report. Since 5.43.0 a handoff
that hands you a decision is **rendered from a record** (`schemas/handoff.json`), never composed:

```sh
handoff.py --prepare --skill <skill> --project <project-root>   # skeleton: state + checked doors
handoff.py --save-report <path>                                 # full report, from stdin
handoff.py --render <record>                                    # the message you read
handoff.py --check <message>                                    # hold a written message to the limits
```

`--prepare` writes the state line from a script (the armed goal, else `progress.py`), and each
door already carries its `door.py` answer. The session fills only the empty fields. `--render`
refuses a record whose state moved, one that recommends a refused door, prose with framework
jargon, and text past the length limits. The full report lives under `siegard/handoff/` in the
git directory, outside every root `git status` checks.

### Door check (`door.py`)
A door is one action a handoff gives you, ready to paste. `door.py` says whether that action's
own skill would refuse its inputs as the tree stands now:

```sh
door.py --check <skill> --project <project-root> [inputs…]
door.py --check commit --project <project-root> --slug <slug> --file <path>...
```

The first line is `accepts` or `refuses`, then `refused:`, `checked:`, `decided:` and
`not decided:` lines. A refused door is shown as excluded, never recommended. The `commit` check
refuses a commit after a run whose log closed on a stop line, except for the measure.

### Recorded ask (`ask.py`)
A compaction keeps a summary of what you said, never your words. `ask.py --record` copies the
words that authorize a route to `ask-<stamp>.md` under the telemetry root, under a digest.
`ask.py --read` prints them back verbatim, so a resumed route reads its authorization from your
words and not from a summary.

### Relay (`relay.py`)
Text meant for another project's session. `relay.py --to <sibling-root> --from <project-root>`
writes it into this project's telemetry root, never into the sibling. It prints a `confirm:` line,
and the sibling's session runs that line first. The line refuses if that session is in the wrong
project or runs a different plugin version.

### Progress line (`progress.py`)
One line per live initiative, read from disk with no model involved:
`<slug> · task 3/7 delivered · phase delivery · last: <log line>`. It is drawn in Claude Code's
status line once `/siegard-config` runs `progress.py --install` on your request, which writes the
project's `.claude/settings.local.json`; `--uninstall` removes it.

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
