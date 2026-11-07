# `/plan-work` over three cases — benchmark, iteration 1 (2026-11-07)

Every planning case plans the renewal scope (`scope.md`) over the implement-task benchmark's fixture
project, its plan removed: the lending specification, the Python target `app` and its standard.
`tools/bench_plan_work.py` sets each case up, prints what the running agent is handed and grades
the record; `tests/test_benchmarks.py` recomputes every expectation from the record. Each run is one
`general-purpose` agent with a fresh context, on the session's model, in a session where no agent of
the plugin is registered, so every spawn fails and both arms take the inline route the skill states.

`before:` is `src/claude` at `5a4317a` (Siegard 5.64.0, the skill at 871 lines); `shipped:` is the
working tree that became 5.65.0 (327 lines, a progress checklist, `## Terms`, eight references, the
four agents rewritten).

| run | case | arm | expectations | tokens | time |
|---|---|---|---|---|---|
| `first-plan` | whole route, full skill | shipped | 14/14 | 95.9k | 3 m 30 s |
| `first-plan--before-1` | whole route, full skill | before | 14/14 | 106.4k | 3 m 28 s |
| `compaction-resume` | resumed after step 4 | shipped | 8/8 | 66.2k | 1 m 43 s |
| `compaction-resume-2` | resumed after step 4 | shipped | 8/8 | 65.4k | 1 m 49 s |
| `compaction-resume--before-1` | resumed after step 4 | before | 5/8 | 49.4k | 1 m 02 s |
| `compaction-resume--before-2` | resumed after step 4 | before | 5/8 | 47.2k | 0 m 43 s |
| `reading-quiz` | quiz | shipped | 18/18 | 63.3k | 16 s |
| `reading-quiz-2` | quiz | shipped | 18/18 | 63.3k | 16 s |
| `reading-quiz--before-1` | quiz | before | 18/18 | 67.1k | 14 s |
| `reading-quiz--before-2` | quiz | before | 18/18 | 67.2k | 13 s |

## What the runs say

- **The compaction case separates the arms.** Holding the first 20,000 characters of 5.64.0, which
  end inside the corrective increment before any numbered step, both runs derived the plan from the
  order line and `plan.py --help` and ended without `handoff.py --save-report` or `--render`, filling
  the task slot with a task of their own choosing instead of offering `deliver.py --outstanding`.
  The 5.65.0 `SKILL.md` is 19,470 characters, inside the cut whole: both runs read
  `references/report.md` at step 6 and handed the record. They spent ~17k tokens more doing it.
- **The full route does not separate them**, as expected of a change that moves and trims text;
  the rewrite's run spent 10% fewer tokens, one run each.
- **The quiz cannot show the old text misread** — both arms answer every point, as in the
  implement-task benchmark — and holds that the rewrite lost no meaning there. Reading the files
  whole cost 63.3k tokens against 67.2k.
