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
