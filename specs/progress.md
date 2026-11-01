---
id: "SPEC-009"
title: The progress line
status: proposed
contract_version: spec/1
---

# The progress line

## Scope

This specification fixes what the one line a status line setting redraws says about a project's
live initiatives, where each of its parts is read from, what it costs, and how the setting that
runs it is written. It binds `bin/progress.py`, the one script that prints it and writes that
setting, and `/siegard-config`, the one skill that runs the write.

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
- **R4** — Outside a project that declares `siegard.json`, the line is empty, and it is empty wherever nothing can be read — no `work_root`, no live initiative, a project file that does not parse; printing it exits 0 on every path, because a status line command that fails is drawn as an error on every redraw.
- **R5** — The status line is set only where the person asks for it, in the project's `.claude/settings.local.json`, as the command `python3 -B` over the absolute path of the `bin/progress.py` that wrote it. The entry is merged into what the file holds and every other key stands; a `statusLine` the script did not write is refused, never replaced, and the script removes only an entry it wrote.
- **R6** — Where the plugin version loaded for the project is not the one the line runs from, the line says so, naming both, and names the re-run that moves it. The loaded version is read from the harness's own record of installed plugins, the entry installed for the project before the one installed for the user; a record that is absent, does not parse or names no entry adds nothing, and a line otherwise empty stays empty.

## Validation required before acceptance

1. Tests hold `progress.py` to R1, R3 and R4 over fixture repositories: one per phase, a log's
   last line shown, two live initiatives on one line, a closed initiative left out, and an empty
   line outside a project and over a project with no live initiative.
2. Its time over a plan of 100 tasks is measured and recorded below, with the machine it ran on.
3. A consumer session run with the line set is read for the person's questions about where a run
   stands — "status?" and its kin — against the grounds; fewer is the reading that holds R1, and
   no fewer is the reading that reopens what the line names.
4. For R5: `--install` writes the entry into a project with no settings file and the command it
   writes, run by a shell from another directory over the harness's record, prints the line; it
   merges into a file holding other keys and leaves each standing; it replaces an entry it wrote
   from another version's path and refuses a foreign one, leaving the file byte-identical; it
   never rewrites a file that does not parse, nor writes into a directory holding no
   `siegard.json`; `--uninstall` removes only its own entry; and the write says when git does not
   ignore the file — `tests/test_progress.py` proves each
   (`test_install_writes_the_entry_whose_command_prints_the_line`,
   `test_install_merges_and_every_other_key_stands`,
   `test_install_replaces_its_own_entry_from_another_version_and_refuses_a_foreign_one`,
   `test_install_never_rewrites_a_file_that_does_not_parse_or_a_project_without_siegard`,
   `test_uninstall_removes_only_its_own_entry`,
   `test_install_says_when_git_does_not_ignore_the_settings_file`).
5. For R6: a project-scoped entry naming another install path puts both versions on the line
   ahead of a user-scoped entry naming this one; an entry naming this one, an entry for another
   project and a record that does not parse each add nothing; and a line otherwise empty stays
   empty — `tests/test_progress.py` proves each
   (`test_the_line_names_both_versions_where_the_project_loads_another`,
   `test_the_line_names_no_version_where_the_loaded_one_is_its_own_or_none_is_recorded`,
   `test_a_line_otherwise_empty_stays_empty_whatever_version_is_loaded`).

## Readings

- 2026-10-31 — `progress.py` over a synthetic plan of 100 tasks (one epic, a chain of
  `depends_on`), on the generator maintainer's WSL2 machine, Python 3, wall time of the whole
  process over 20 runs each: 7 of 100 delivered and no review record, median 0.048 s, max
  0.067 s; 100 of 100 delivered and proven with one review record naming every task, median
  0.070 s, max 0.120 s — the difference is the PyYAML import, made only where a review record
  exists. `deliver.py --outstanding` over the same plan with 7 delivered took 0.56 s by `time`, and
  importing `deliver.py` alone 0.46 s: R2 is what keeps the line out of that cost.
- 2026-10-31 — R5, R6 and R4's last clause. The line shipped with no way to set it short of a
  person writing `statusLine` by hand, and whether `${CLAUDE_PLUGIN_ROOT}` expands inside a status
  line command is unverified, so the entry names an absolute path resolved when it is written.
  Claude Code's plugin cache is one directory per version
  (`~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`), and on the maintainer's machine
  every earlier version's directory was still present — 20 of them, back to 4.6.0 — so a stale
  entry keeps running the earlier script rather than failing; that is what R6 names. The loaded
  version is read from `~/.claude/plugins/installed_plugins.json`, a harness record no Claude
  Code document fixes: its shape (`plugins` → `<name>@<marketplace>` → entries carrying `scope`,
  `projectPath`, `installPath`, `version`) was read from the maintainer's own copy (4,925 bytes),
  and R6's silence on a record it cannot read is what keeps a change of that shape from becoming a
  wrong line. The local settings file was chosen over `.claude/settings.json` because the path is
  one machine's; on the maintainer's machine the global git excludes file already ignores
  `**/.claude/settings.local.json`. The cost of the version read, 30 runs each over a fixture with
  one live initiative on the same WSL2 machine: median 0.123 s with no plugin record, 0.111 s with
  a 4.9 kB record and the note shown — inside the run-to-run spread, which on this reading put
  the plain line's median at twice the 0.048 s of the reading above. R4's "the script exits 0 on
  every path" became "printing it exits 0 on every path": `--install` and `--uninstall` refuse
  with 1 and cannot run with 2, and the command a status line runs invokes neither.
