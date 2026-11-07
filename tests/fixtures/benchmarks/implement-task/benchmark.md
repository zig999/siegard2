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
