---
name: siegard-telemetry
description: Writes a telemetry report over one window of work with this framework — not what was delivered but how the work happened. Which agents ran, how often, at what effort, and what each cost in tokens and wall-clock; which framework commands refused and how often; what the captured runs took; what stopped for a person; what was decided on their behalf; which classified notes stood. Every figure is counted by bin/telemetry.py from disk — the delivery roots' runs, the plan's notes, the decision log, git, and the harness's own session transcripts, read only after a probe and an announcement — and lands as a JSON record and a Markdown report side by side under the project's telemetry_root, in English, self-sufficient enough for the framework's maintainer to rule on without a second conversation. Use when a human asks for a retrospective, a friction report, a cost breakdown, or a consumer report to send back to the framework's maintainer. Not for the project's status — that is /siegard-status.
effort: medium
---

You answer one question — how did the work in this window happen, in figures somebody else can
recompute — and you stop. The product is two files that travel together: a JSON record written by
`${CLAUDE_PLUGIN_ROOT}/bin/telemetry.py` and held to
`${CLAUDE_PLUGIN_ROOT}/schemas/telemetry.json`, and beside it the Markdown report you write from
that record and from nothing else numeric. The report exists so the framework's maintainer can
decide what to change without asking a follow-up question: it names the framework version it
measured, the effort every agent was configured at, the window it covers, and the source of every
claim.

The discipline is the one this framework holds over its own state, applied to the account of the
work: **a number you cannot point at a file for is not in the report.** Conversation history is
non-authoritative here in the strongest sense. The token totals the previous shape of this report
carried were recalled from tool results; after one context compression they were guesses that
read as counts. That is what `telemetry.py` replaces.

## Required inputs

A missing input is a stop, not a default:

1. **the project root** — where `siegard.json` lives. Named by the human; inferred rather than
   named, its absence is a stop.
2. **the window** — the instant the report opens at, and optionally the instant it closes at
   (default: now). Named by the human as an ISO-8601 instant, as a commit (`git show -s
   --format=%aI <commit>` turns it into one — say which commit), or as `last`, which continues
   from the moment the previous report closed. A window is never inferred from memory of when a
   session began: where the human names none and no previous report exists under
   `telemetry_root`, that is a stop — say what `last` would have needed, and ask.

Run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/project.py <project-root>` once, before anything
else — the one reader of `siegard.json`, held to `${CLAUDE_PLUGIN_ROOT}/schemas/project.json`.
`telemetry_root` answers only from here; where it is absent, that absence *is* the answer:
`telemetry.py` prints the `/siegard-config` invocation ready to paste, and you stop.

`${CLAUDE_PLUGIN_ROOT}` is set where this skill runs as an installed plugin. Where it is not,
the plugin root is the directory that holds `schemas/` and `bin/` side by side — in a vendored
install, the `.claude/` directory this skill's tree sits under.

## Before anything: the probe, and the announcement

The script reads one directory outside the project: the harness's session transcripts under its
own projects directory — every conversation held in this working directory, including this one.
That read is permitted on two conditions, and both are yours to meet before it happens:

1. **Probe first.** Run
   `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/telemetry.py --probe <project-root> --since <since> [--until <until>]`.
   It writes nothing. It prints the transcript directory it would read, whether it is readable,
   which sessions overlap the window and how many human turns each holds — naming the sibling
   directory where a session was opened in a subdirectory of the project — what leaves those files
   (agent types, descriptions, token counts, timestamps, and the command lines that invoked this
   framework's scripts — no message text), and where the report would land — including whether
   that stamp is already taken.
2. **Announce, verbatim.** Quote the probe's output to the human before the full run, so the read
   is stated rather than discovered. Where the probe reports the directory unavailable, say so
   and continue: the report is still written, with the agent and command sections absent and the
   reason recorded in its `provenance`. Where the human, on seeing the probe, asks you not to read
   the transcripts, pass `--transcripts` a directory that does not exist — the report says why
   those sections are empty rather than pretending they were counted.

## The order

```
project.py → telemetry.py --probe → announce → telemetry.py → read the JSON → write the .md → stop
```

1. **Resolve the roots** with `project.py`, as above.
2. **Probe and announce**, as above.
3. **Count.** `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/telemetry.py <project-root> --since <since> [--until <until>]`.
   It writes `<telemetry_root>/<stamp>.json` — the stamp being `until` in UTC — and prints a
   receipt. A stamp that already exists is a refusal: close the window at a later `--until`, never
   overwrite. A non-zero exit is reported verbatim and ends the run.
4. **Read the record whole.** Open the JSON it wrote. Every number in the report below comes from
   a field in this file; the field is the citation.
5. **Write the report** at `<telemetry_root>/<stamp>.md` — the same stem, beside the record.
6. **Report, and stop.** Print both paths, the receipt, and the completeness verdict.

## The report

English, whatever language the conversation is in: this file is an artifact that travels to the
framework's maintainer, not an answer to the person in the session. Fixed headings, in this order,
numbered as written — a reader comparing two reports compares two of one shape:

```
---
contract_version: siegard-telemetry/1
project_root: <from the record>
window: { since, until, since_resolved_from }
framework_version: <framework.version, or "unknown">
record: <stamp>.json
complete: true | false
---
## 0. Scope and window
## 1. Framework identity
## 2. Timeline
## 3. Agents
## 4. Commands and captured runs
## 5. Refusals and re-runs
## 6. Human stops
## 7. Decisions disclosed
## 8. Standing notes
## 9. Aggregate cost
## 10. Friction and anomalies
## 11. Evidence
## 12. Completeness
```

What each section holds:

- **0.** The window, both bounds and where `since` came from; the project root; which sessions
  overlapped the window (id, entries, human turns, working directories, harness versions). Where
  the transcripts were unavailable, say so here first.
- **1.** `framework.version` and `framework.plugin_root`; every contract version in
  `framework.contracts`; a table of every shipped agent and skill with its configured effort and
  model, from `framework.agents` and `framework.skills`. A report that cannot name the framework
  version it measured says `unknown` and says why that hollows the rest.
- **2.** Phases in wall-clock order, built from what has a clock: the first and last agent of each
  type, the runs' `started_at`/`ended_at`, the commits' timestamps, the human turns. A phase is
  named by the skill its agents belong to (`/plan-work` spawns surveyors, decomposers, binders,
  deciders; `/implement-task` spawns implementers, authors, diagnosticians; `/review-change` and
  `/reconcile` spawn reviewers and auditors). Where nothing carries a clock for a stretch, write
  "duration not recorded" — never a figure.
- **3.** One table over `agents`: invoked at, type, description, model, duration, tokens (input,
  cache creation, cache read, output), tool calls, `repeats_earlier`. Then one row per type from
  `agent_totals.by_type` with invocations, how many carried a transcript, summed duration and
  tokens. Where `with_transcript` is below `invocations`, say the totals are a floor and list the
  invocations without a transcript by their `unavailable` reason. For every repeat, judge from
  the two descriptions and their timing whether it was rework (same input set, same reason) or
  deliberate (the input set changed) — and mark that judgment as yours.
- **4.** Every entry of `commands`: issued at, scripts, the command line, exit code where the
  harness marked one, `problems` where a validator counted, interrupted. Then every entry of
  `runs`: initiative, run, outcome, failed step, timeout, one line per step with its outcome, exit
  code and duration.
- **5.** The subset of §4 that refused or failed — every non-zero exit, every `problems` count,
  every failed run — each followed by what happened next in the record: the next command invoking
  the same script, the next run under the same initiative, the agents spawned in between. Cost of
  the repeat is the tokens and seconds of those agents where they carried a transcript, and
  "not recorded" where they did not.
- **6.** Where the work waited for a person. Sources, in order of strength: standing `BLOCKING`
  notes from `notes`; the human turns in `harness.sessions`, each placed against the commands and
  agents around it; commits whose subject names a decision. What was asked and how the human
  answered is not in the record — where you were present for it in this conversation, quote it
  and tag it `[recall]`; where you were not, say "not recorded" rather than reconstructing it.
- **7.** Every entry of `decisions.added`, whole — location, field, unstated, decided, why — and
  the baseline it was diffed against. Where the baseline was unavailable, the section says every
  current entry is listed and why.
- **8.** Every entry of `notes`, verbatim, keyed by initiative and node, grouped by class.
- **9.** Totals: `agent_totals.overall`; the same per type; the same per skill phase from §2;
  and per unit of work — divide by `scope`'s task counts and by the records landed in the window,
  naming the denominator each time. A total over fewer transcripts than invocations is a floor,
  said as one.
- **10.** Judgment, and only here: a step whose cost is out of proportion to what it decided, a
  repeat an earlier check would have spared, a stop that was unnecessary or one that was missing,
  two files disagreeing. Every item carries its evidence beside it — the field, the row, the
  path — and is tagged `[judgment]`. An item without evidence in the record is not an item.
- **11.** Every command you ran in this invocation and what it printed, so the checks reproduce
  without trusting the summary: the `project.py` line, the probe, the full run's receipt, and any
  `git` command you used to turn a commit into an instant.
- **12.** Computed from `provenance`, never from impression: `complete: true` where no entry
  carries a reason; otherwise `false`, with every section and reason listed and what a complete
  report would need (a readable transcript root, a declared root, a decision log in git). Then
  one line: whether this report is ready to send to the framework's maintainer as a consumer
  report, which is exactly the same question.

### Provenance tags

Every claim in §§2–10 carries one tag, and the tag is the claim's source:

- `[record: <field>]` — read from the JSON record, by field path (`agents[3].usage.output_tokens`,
  `runs[0].steps[1].duration_seconds`).
- `[disk: <path>]` — read from a file the record points at, by path (a run's log, a note's node).
- `[recall]` — this conversation, and only in §6 and §10, and never a number.
- `[judgment]` — yours, and only in §3's rework column and §10.
- `[unavailable: <reason>]` — the reason from `provenance`, in place of the figure.

## What you never do

- Write a number the record does not hold — a token total from memory of a tool result, a
  duration from a sense of how long something took, a count of stops from impression. The
  phrase for that field is "not recorded", with the tag that says why.
- Read the transcripts without the probe, or without quoting the probe to the human first.
- Quote a prompt, a reply, or a tool's result out of a transcript. The record carries none, and
  the report carries none: what leaves that directory is counts, names, timestamps, and the
  command lines that invoked this framework's scripts.
- Overwrite a report. A stamp that exists is a window that was already closed; close this one
  later.
- Write the report in the session's language. The framework's artifacts are English, and this
  one is an artifact that travels.
- Judge outside §10 and §3's rework column, or judge without a field beside the judgment.
- Alter, bind, prune, derive, or commit anything in the project. The two files under
  `telemetry_root` are the only writes, and `git diff` over them is the review, which belongs to
  a person.
