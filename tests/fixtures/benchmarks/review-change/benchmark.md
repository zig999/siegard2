# /review-change benchmark

`tools/bench_review_change.py` sets up, prompts and grades a model run of `/review-change`;
`tests/test_benchmarks.py` recomputes every expectation from each record.

## Fixture

The implement-task benchmark's fixture project (`tests/fixtures/benchmarks/implement-task/project`)
with that benchmark's recorded first delivery (`iteration-2/first-delivery`: `delivery/`, `app/`,
`work/`, `siegard-trace.json`) laid over it and committed. The review covers
`task/fees/compute-late-fee`, file set `lending/fees.py` and `tests/test_fees.py`, target `app`,
slug `lending`, review name `fees-review`. The project's standard comes from `siegard.json`.

## Cases

- `full-review`: the ordinary route, with the full skill in context. 14 expectations:
  `deliver.py --review` exits 0 over the recorded tree; the review record exists and names
  `siegard-reconcile/fees-review.md`; `trace.py --reconciliation` accepts it; the trace binds the
  node to `app/lending/fees.py` as `judged`; the run captured the registry's build and test steps;
  the report was saved through `handoff.py --save-report`; commands.txt shows `--stage --review`,
  `--fold`, `--bind-record --workspace`, `--review` and `--render`; no commit; nothing written
  outside the delivery root, `siegard-reconcile/` and `siegard-trace.json`.
- `compaction-resume`: the session resumes holding the first 20,000 characters of the skill,
  after step 3b. Setup builds that state with the framework's own writers: `--stage --review`,
  `run.py`, the two conformance returns in `cases/compaction-resume/pre/` saved through
  `--save-return` from a one-message transcript, `--fold`, `--reconciliation` and
  `--bind-record --workspace`. The coverage and standard returns come in the compaction summary.
  What is left is compose, validate and report. 11 expectations.
- `reading-quiz`: 18 multiple-choice questions on the densest points: staging and omissions,
  waves and `--save-return`, what the bind writes, when the failures pass runs, certification
  against coverage, what the report groups and never decides, the file set never discovered, and
  the review that carries no pin. Each wrong option differs from the right one in one detail.

Every run is one `general-purpose` agent reading `prompt.txt`. No agent of the plugin is
registered, so every spawn fails and both arms take the inline route.

## Iteration 1 — 5.66.0 against 5.65.0 (e98711f)

| Case | before: 5.65.0 | shipped: 5.66.0 |
|---|---|---|
| full-review | 14/14, 119.7k tokens | 14/14, 121.8k tokens |
| compaction-resume | 9/11, 9/11 (72.5k, 77.4k) | 11/11, 11/11 (81.9k, 83.8k) |
| reading-quiz | 18/18, 18/18 (70.7k, 70.7k) | 18/18, 18/18 (71.8k, 71.7k) |

- **The compaction separates the arms.** At 5.65.0 the cut falls inside step 1. Both runs wrote
  a review the validator accepted, working from `deliver.py --help` and `--contract review`, but
  neither saved the report through `handoff.py --save-report` nor ran `--render`. At 5.66.0 the
  skill fits the cut whole (19,820 characters), and both runs reached the handoff. The resumed
  5.66.0 runs cost more tokens because they did the report's work.
- **The quiz does not separate the arms.** Both reached the ceiling. The 5.66.0 reader opens 12
  files instead of 5 and spends about 1k tokens more, so the quiz holds only that no meaning was
  lost.
- **full-review--draft-1** ran the first candidate and is kept as a draft record, not a shipped
  one. That text said every return is saved "through `--save-return`". On the inline route there
  is no subagent transcript, so the save refused both returns, the fold never ran, and the
  review met 10 of 14 expectations. The shipped text restores 5.65.0's wording: each return is
  saved verbatim at its path, and `--save-return` is how a spawned subagent's transcript gets
  there. The rerun met 14 of 14. The compaction runs resume after step 3b and never save a
  return, so the change does not reach them.

## Open

The inline route has no transcript for `--save-return` to read. Every run of both arms, before
and shipped, wrote its returns straight to the returns directory, and the fold's notes then say
"Judged by 2 subagent(s)". Neither the skill nor `trace.py` states what an inline return is saved
through.
