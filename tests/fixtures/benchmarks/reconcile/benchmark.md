# /reconcile benchmark

`tools/bench_reconcile.py` sets up, prompts and grades a model run of `/reconcile`;
`tests/test_benchmarks.py` recomputes every expectation from each record.

## Fixture

The review-change benchmark's seeded repository: the implement-task benchmark's fixture project
(`tests/fixtures/benchmarks/implement-task/project`) with that benchmark's recorded first delivery
(`iteration-2/first-delivery`) laid over it and committed. A second commit edits
`app/lending/fees.py` after the bind: the constant `LATE_FEE_CENTS_PER_DAY` is renamed
`FEE_CENTS_PER_OVERDUE_DAY`, and a comment restating the late fee rule is added. `trace.py --check
app` then reports one `code` drift on `app/lending/fees.py`, staling
`rules/lending/late-fee-per-overdue-day`. The reconciliation covers file set `lending/fees.py`,
target `app`, slug `fees-hand-edit`, and the person's words "renamed the late fee constant in
lending/fees.py by hand and added a comment; the behavior did not change and the code is correct".

## Cases

- `full-reconcile`: the ordinary route, with the full skill in context. 13 expectations:
  `trace.py --reconciliation` accepts `siegard-reconcile/fees-hand-edit.md`; the return for
  `lending/fees.py` is saved under `siegard-reconcile/fees-hand-edit.returns/`; the trace binds the
  node to `app/lending/fees.py` as `judged`; `trace.py --check` reports no drift on it; the report
  was saved through `handoff.py --save-report`; commands.txt shows `--stage`, `--fold`,
  `--reconciliation`, `--bind-record --workspace`, `--save-report` and `--render`; no commit;
  nothing written outside `siegard-reconcile/` and `siegard-trace.json`.
- `compaction-resume`: the session resumes holding the first 20,000 characters of the skill,
  after step 4. Setup builds that state with the framework's own writers: `--stage`, the
  conformance return in `cases/compaction-resume/pre/` (one `restates` finding on the comment, one
  `unstated` finding on the `overdue_days <= 0` branch, the node read as held) saved through
  `--save-return` from a one-message transcript, `--fold` over `pre/premise.yaml`, and
  `--reconciliation`. What is left is the bind over the staging's workspace and the report. 10
  expectations.
- `reading-quiz`: 18 multiple-choice questions on the densest points: what the staging omits, an
  audit and the candidate tier, the candidate index as a path, nodes written since the bind, waves
  and `--save-return`, a refused launch, how a return is saved, the five keys, `nowhere` against
  `read`, `collateral`, what the bind writes, `--replace` and the release, certification, the
  mechanical round of step 3b, a rewrite that reproduces nothing, adoption, the file set never
  discovered, and the doors the report hands without deciding. Each wrong option differs from the
  right one in one detail.

Every run is one `general-purpose` agent reading `prompt.txt`. No agent of the plugin is
registered, so every spawn fails and both arms take the inline route.

## Iteration 1 — 5.67.0 against 5.66.0 (dba563c)

| Case | before: 5.66.0 | shipped: 5.67.0 |
|---|---|---|
| full-reconcile | 13/13, 99.6k tokens, 138 s | 13/13, 102.8k tokens, 156 s |
| compaction-resume | 7/10, 7/10 (47.6k, 48.2k) | 10/10, 10/10 (66.4k, 67.7k) |
| reading-quiz | 18/18, 18/18 (63.7k, 63.7k) | 18/18, 18/18 (66.2k, 66.5k) |

- **The compaction separates the arms.** At 5.66.0 the cut falls inside step 2, before the
  candidates paragraph ends. Both runs found `--bind-record --workspace` through `trace.py --help`
  and bound the node, so the trace ended clean; neither ran `handoff.py --save-report` or
  `--render`, and the report was handed as free prose. At 5.67.0 the skill fits the cut whole
  (17,121 characters), and both runs saved and rendered the handoff. The resumed 5.67.0 runs cost
  more tokens because they did the report's work, including two refused renders each.
- **The full route does not separate the arms.** Both met 13 of 13. The 5.67.0 run cost about 3k
  tokens more.
- **The quiz does not separate the arms.** Both reached the ceiling. The 5.67.0 reader opens 11
  files instead of 3 and spends about 2.6k tokens more, so the quiz holds only that no meaning was
  lost.
- **No draft.** The first candidate ran as the shipped arm; no run is recorded under `draft:`.

## Open

- The inline route still states no way to save a return. In the 5.67.0 full run `--save-return`
  refused ("holds no assistant message"), and the session saved the return by hand, as the text
  allows only where a transcript cannot be read; the 5.66.0 run did the same. The fold's notes
  then say "Judged by 1 subagent(s)" over an inline judgment.
- `references/capture.md` (and the 5.66.0 text before it) reads each command and its bound from
  "what `deliver.py --standard` printed", but no step of `/reconcile` runs `deliver.py --standard`.
  The wording is carried unchanged; this benchmark has no mechanical tier and does not reach it.
