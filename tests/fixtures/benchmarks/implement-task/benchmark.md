# `/implement-task` over two cases — benchmark, iteration 1 (2026-11-07)

Every case delivers the one task of `project/`: `task/fees/compute-late-fee` of the `lending`
initiative, implementing `rules/lending/late-fee-per-overdue-day` into the Python target `app`,
whose standard declares a `build` step (`compileall`) and a `suite` step (`pytest`). The cases live
under `cases/<name>/case.json`; `tools/bench_implement_task.py` sets each one up, prints what the
running agent is handed and grades the record. `tests/test_benchmarks.py` recomputes every
`mechanical:` expectation from the record, so a grading is re-read, never trusted. A `reported:`
expectation rests on the agent's own `commands.txt` or on `facts.json`, written when the run was
recorded.

Each run is one `general-purpose` agent with a fresh context, on the session's model, told it
cannot spawn subagents — so both arms take the inline fallback the skill states, and the arms
differ only in the skill text. `before:` is `src/claude` at `d975730` (Siegard 5.60.0, the skill
at 1065 lines); `shipped:` is the working tree that became 5.61.0 (496 lines, a progress checklist,
eleven files under `references/`).

| run | case | arm | expectations | tokens | time |
|---|---|---|---|---|---|
| `compaction-resume` | resumed after step 4 | shipped | 15/15 | 98.7k | 2 m 27 s |
| `compaction-resume-2` | resumed after step 4 | shipped | 15/15 | 94.4k | 2 m 30 s |
| `compaction-resume--before-1` | resumed after step 4 | before | 13/15 | 74.9k | 1 m 52 s |
| `compaction-resume--before-2` | resumed after step 4 | before | 13/15 | 75.9k | 1 m 38 s |
| `first-delivery` | whole route, full skill | shipped | 16/16 | 111.7k | 3 m 20 s |
| `first-delivery--before-1` | whole route, full skill | before | 16/16 | 118.8k | 3 m 03 s |

## What the runs say

- **The compaction case separates the arms, and only at the handoff.** Holding the first 20,000
  characters of the old skill, both runs reached the route's end from the order line, the agent
  files and the scripts' `--help` — proof, suite, `--unrecorded`, the validator, the bind all
  passed — and both ended without `handoff.py --save-report` or `--render`, handing a report of
  their own form; one says it guessed the `/review-change` argument order. Both shipped runs read
  the checklist, read `SKILL.md` again, opened `references/delegation.md`, `records.md`,
  `finish.md` and `report.md` at their steps, and saved and rendered the handoff.
- **The full-context case does not separate them**, as expected of a change that moves text: both
  arms pass every expectation. The shipped run read `standard.md`, `delegation.md`, `records.md`,
  `finish.md` and `report.md` at the steps the checklist names them.
- **Cost.** Resumed, the shipped skill spends ~21k more tokens and ~45 s more per run: it reads
  the skill again and four references, which is the behaviour the checklist exists to cause. Over
  the full route the two arms sit within one run's variation.
- **Not attributable to the change:** in both arms a run read `schemas/handoff.json` after a
  `--render` refusal over the 600-character block limit, and a run said it guessed the
  `/review-change` argument form. Recorded, not graded.

Two runs per arm over the resumed case and one over the full route are a reading, not a
distribution. `test_the_checklist_is_what_carries_a_resumed_delivery_to_its_end` holds this
iteration's comparison; `test_the_latest_implement_task_iteration_passes_every_expectation_with_the_shipped_skill`
holds the newest iteration to the shipped skill passing every case.

## Re-running

    python3 tools/bench_implement_task.py setup  <case> <dir>/<run>/p [--skill <SKILL.md>]
    python3 tools/bench_implement_task.py prompt <case> <dir>/<run>/p <dir>/<run>/out [--skill <SKILL.md>] > prompt.txt
    # hand prompt.txt to a fresh general-purpose agent; then
    python3 tools/bench_implement_task.py record <case> <dir>/<run>/p <dir>/<run>/out \
        tests/fixtures/benchmarks/implement-task/iteration-<N>/<run> --arm "shipped: <version> (<commit>)" \
        --tokens <subagent tokens> --seconds <duration>

`--skill` points `setup` and `prompt` at another arm; `${CLAUDE_PLUGIN_ROOT}` is the directory three
levels above it, so an old arm is a whole plugin tree (`git archive <commit> src/claude`). A change
to the skill records a new iteration beside this one, never over it.

# Iteration 2 (2026-11-07): 5.62.0, the writing pass over the skill, its references and three agents

`before:` is `src/claude` at `96b7f59` (Siegard 5.61.0); `shipped:` is the working tree that became
5.62.0. The change rewrites `SKILL.md`, its eleven references and `task-implementer`,
`test-author` and `failure-diagnostician`: one term per concept (`the person`, `you`, `subagent`,
`producer`, `re-enter`, `stop`, `refusal`, `door`, defined once under `## Terms`), the passages an
audit named ambiguous rewritten, justification cut to at most one clause per rule, descriptions
that name the trigger first, and prose wrapped at 100 columns. Rules, commands, citations and the
order of steps are unchanged.

A third case joins the two: `reading-quiz`, eighteen multiple-choice questions over the points the
audit named ambiguous, each answered by an agent holding only the arm's fifteen files. Every wrong
option differs from the right one in one plausible detail; options are shuffled per question.

| run | case | arm | expectations | tokens | time |
|---|---|---|---|---|---|
| `reading-quiz` | quiz | shipped | 18/18 | 73.8k | 19 s |
| `reading-quiz-2` | quiz | shipped | 18/18 | 73.6k | 17 s |
| `reading-quiz--before-1` | quiz | before | 18/18 | 82.0k | 20 s |
| `reading-quiz--before-2` | quiz | before | 18/18 | 82.1k | 21 s |
| `first-delivery` | whole route | shipped | 16/16 | 115.5k | 3 m 31 s |
| `first-delivery--before-1` | whole route | before | 16/16 | 120.5k | 3 m 40 s |
| `compaction-resume` | resumed after step 4 | shipped | 15/15 | 89.1k | 2 m 48 s |
| `compaction-resume--before-1` | resumed after step 4 | before | 15/15 | 88.1k | 2 m 15 s |

## What the runs say

- **The quiz cannot show the old text misread, and says so.** A first version with easy
  distractors scored 18/18 on 5.61.0 twice and was discarded unrecorded; the recorded version,
  with one-detail distractors, scored 18/18 on both arms. A reader holding the whole text resolves
  the passages the audit called ambiguous. What the quiz holds is that the rewrite lost no meaning
  at any of those eighteen points.
- **Reading cost fell.** The fifteen files went from 133.6k to 102.6k characters; a whole read cost
  the quiz agents 73.7k tokens against 82.0k, a 10% fall with a spread of 0.2k inside each arm.
- **The text measures moved as claimed** (`text-metrics-5.61.0.json` against the shipped text,
  held by `tests/test_text_metrics.py`).
- **Behaviour held.** Both delivery cases pass every expectation on both arms; a whole delivery cost
  115.5k tokens against 120.5k, and a resumed one 89.1k against 88.1k — one run each, within one
  run's variation.

# Iteration 3 (2026-11-07): 5.69.0, wave B — the skill fits the compaction cut whole

`before:` is `src/claude` at `2a6ee49` (Siegard 5.68.0: `SKILL.md` 25,895 characters, the cut
falling inside step 5's spawn block and losing steps 6-9 and the never-list); `shipped:` is the
working tree that became 5.69.0 (`SKILL.md` 19,970 characters, 338 lines). The two spawn blocks
moved into `references/delegation.md`, the order diagram is dropped (the checklist states the
order), "Every run is captured" keeps its rules without their justification, and the task-pin
paragraph moved into `references/records.md`. The agents are untouched.

A fourth case joins: `compaction-resume-late`, resumed after step 6. `setup` writes the source,
the tests (`pre/test_fees.py`), the build and suite runs through `run.py`, and both records
through `deliver.py --write-implementation` and `--write-proof --from-text` over `pre/`; nothing
is committed. What remains is step 7 (`--unrecorded`, `deliver.py`), step 8 (`--bind-record`) and
step 9 (`--prepare`, `--save-report`, `--render`), which the 5.68.0 cut loses whole. The state is
held sound by `test_the_late_resumed_implement_task_case_starts_where_step_6_ends`: `deliver.py
--check` over it refuses as written (`delivery.json` has never been derived — deriving it is step
7), so the test derives it in a copy, which exits 0, and `--check` then accepts. A new check,
`delivery_derived`, holds that step 7 ran. Every resumed run's `facts.json` records
`skill_read_again`: whether its `files-read.txt` names the arm's `SKILL.md`, whole or in part.

| run | case | arm | expectations | read SKILL.md again | tokens | time |
|---|---|---|---|---|---|---|
| `compaction-resume-late` | resumed after step 6 | shipped | 15/15 | no | 66.4k | 1 m 30 s |
| `compaction-resume-late-2` | resumed after step 6 | shipped | 15/15 | no | 67.4k | 1 m 27 s |
| `compaction-resume-late--before-1` | resumed after step 6 | before | 15/15 | yes | 69.2k | 1 m 31 s |
| `compaction-resume-late--before-2` | resumed after step 6 | before | 15/15 | yes (lines 340-end) | 67.5k | 1 m 25 s |
| `compaction-resume` | resumed after step 4 | shipped | 15/15 | no | 83.1k | 2 m 21 s |
| `compaction-resume-2` | resumed after step 4 | shipped | 15/15 | no | 87.5k | 2 m 18 s |
| `compaction-resume--before-1` | resumed after step 4 | before | 15/15 | yes | 86.0k | 2 m 26 s |
| `compaction-resume--before-2` | resumed after step 4 | before | 15/15 | yes | 85.9k | 2 m 07 s |
| `first-delivery` | whole route | shipped | 16/16 | — | 107.5k | 3 m 28 s |
| `first-delivery--before-1` | whole route | before | 16/16 | — | 104.1k | 3 m 00 s |
| `reading-quiz` | quiz | shipped | 18/18 | — | 73.9k | 18 s |
| `reading-quiz-2` | quiz | shipped | 18/18 | — | 73.3k | 15 s |
| `reading-quiz--before-1` | quiz | before | 18/18 | — | 74.0k | 17 s |
| `reading-quiz--before-2` | quiz | before | 18/18 | — | 74.6k | 21 s |

## What the runs say

- **No expectation separates the arms.** As iteration 2 found, the 5.68.0 checklist already
  carries a resumed delivery to its end: it tells the session to read `SKILL.md` again, and every
  5.68.0 run did, after step 4 and after step 6 alike, and passed everything. 5.69.0 is held as
  non-regression, never as a better score.
- **What separates them is the read the cut forced.** Every 5.68.0 resumed run read `SKILL.md`
  again (one only from line 340, where step 6 began); no 5.69.0 run did, because the cut holds the
  whole skill. Each run still opened the references its steps name.
- **Tokens do not separate them.** The late case: 66.4k/67.4k against 69.2k/67.5k, 0.1k apart at
  the closest; the step-4 case: 83.1k/87.5k against 86.0k/85.9k, overlapping. The re-read of a
  25.9k-character file is a small share of a resumed run, and one run's variation is as large.
  Recorded, not claimed.
- **The quiz holds the move to losing no meaning**: 18/18 on both arms, twice each, at equal cost.

## Drafts

The first candidate dropped "you never type it" when it moved the task-pin paragraph into
`references/records.md`; both of its quiz runs answered question 2 right and named the sentence
as readable both ways. The candidate was corrected and every case run again; its seven runs stay
recorded under `draft:` (`*--draft-N`): 15/15, 15/15, 15/15, 15/15, 16/16 and 18/18, 18/18, none
reading `SKILL.md` again.

## Grader correction

`read_again` first matched only a line ending in `SKILL.md`; a run that annotated its line
(`SKILL.md (lines 340-end)`) read as not re-read. It now reads the path before a ` (` note. The
correction ran over every record that carries the fact, before any comparison;
`test_each_implement_task_run_grades_as_recomputed_from_its_record` recomputes it.

## Open

- Every run, both arms, found `/review-change` refusing while `delivery/<slug>` is uncommitted, and
  handed a commit first; several said they guessed the `/review-change` argument form.
- Every resumed run's first `--render` was refused (a block over 600 characters, a file name in
  prose) and passed on the second.
