---
id: "SPEC-009"
title: The progress line
status: proposed
contract_version: spec/1
---

# The progress line

## Scope

This specification fixes what the one line a status line setting redraws says about a project's
live initiatives, where each of its parts is read from, and what it costs. It binds
`bin/progress.py`, the one script that prints it.

The line answers the question a person asks of a long run — where it is — without a model and
without a turn of the session. It is a reading of disk, never a report: it hands no door and
states no decision, so SPEC-006 does not bind it.

Grounds: a four-day read of four consumers' transcripts (2026-10-27..30, Siegard 5.36.0–5.41.0),
over 251 handoffs. During long `/deliver-scope` runs the person asked "status?", "qual fase está
em exec?" and "pq está demorando tanto?" dozens of times; the lines the harness showed never named
the phase or how many tasks were delivered, and a stub reading "waiting for the binder" drew
"Status?". Every fact those questions asked for was already on disk: the plan's index, the records
at their paths, the orchestration log's last line.

### Decided elsewhere, deliberately not restated here

- What a task's state is — delivered, proven, waiting, blocked — and what is deliverable now:
  `deliver.py --outstanding`, which `/siegard-progress` reads.
- Whether the records hold together: `deliver.py --check`.
- What the orchestration log holds, and its stop line: `/deliver-scope`'s own file and
  `specs/goal.md` (SPEC-008 R4).
- What a goal ends on: `goal.py --state` (SPEC-008 R1).

## Definitions

- **Progress line** — the line `bin/progress.py` prints: one segment per live initiative.
- **Live initiative** — a directory under the project's `work_root` that holds no `closure.md`.
- **Phase** — the first of `plan`, `delivery`, `proof`, `review`, `reviewed` that R3 finds
  holding over one initiative.

## Requirements

- **R1** — The progress line is one line, printed by a script from disk and git alone, with no model in it: per live initiative, its slug, how many of the plan's tasks hold an implementation record out of how many the plan's index names, its phase, and the last line of its orchestration log where one exists.
- **R2** — A count on the line is a count of records present at the paths their tasks compute to, and never a statement that they hold together; the line validates nothing, so its cost does not grow with what a validation reads, and whether the records hold together is answered where a person asks for it, by `/siegard-progress` and `/siegard-status`.
- **R3** — An initiative's phase is `plan` where the work root holds no `plan.json` or the index names no task; otherwise `delivery` while a task holds no implementation record; otherwise `proof` while a task holds no proof record; otherwise `review` while a task is named by no record under the delivery root's `review/`; otherwise `reviewed`. A phase names which records are present and never what is owed: a task delivered as the substrate alone holds no proof record, and the line reads `proof` over it.
- **R4** — Outside a project that declares `siegard.json`, the line is empty, and it is empty wherever nothing can be read — no `work_root`, no live initiative, a project file that does not parse; the script exits 0 on every path, because a status line command that fails is drawn as an error on every redraw.

## Validation required before acceptance

1. Tests hold `progress.py` to R1, R3 and R4 over fixture repositories: one per phase, a log's
   last line shown, two live initiatives on one line, a closed initiative left out, and an empty
   line outside a project and over a project with no live initiative.
2. Its time over a plan of 100 tasks is measured and recorded below, with the machine it ran on.
3. A consumer session run with the line set is read for the person's questions about where a run
   stands — "status?" and its kin — against the grounds; fewer is the reading that holds R1, and
   no fewer is the reading that reopens what the line names.

## Readings

- 2026-10-31 — `progress.py` over a synthetic plan of 100 tasks (one epic, a chain of
  `depends_on`), on the generator maintainer's WSL2 machine, Python 3, wall time of the whole
  process over 20 runs each: 7 of 100 delivered and no review record, median 0.048 s, max
  0.067 s; 100 of 100 delivered and proven with one review record naming every task, median
  0.070 s, max 0.120 s — the difference is the PyYAML import, made only where a review record
  exists. `deliver.py --outstanding` over the same plan with 7 delivered took 0.56 s by `time`, and
  importing `deliver.py` alone 0.46 s: R2 is what keeps the line out of that cost.
