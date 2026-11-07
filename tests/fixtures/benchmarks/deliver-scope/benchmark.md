# /deliver-scope benchmark

`tools/bench_deliver_scope.py` sets up, prompts and grades a model run of `/deliver-scope`;
`tests/test_benchmarks.py` recomputes every expectation from each record.

## Fixture

The implement-task benchmark's fixture project (`tests/fixtures/benchmarks/implement-task/project`):
plan `lending`, epic `epic/fees`, its one task `task/fees/compute-late-fee` undelivered. The seed
declares `telemetry_root: telemetry` beside the fixture's roots — without it `project.py` answers
no telemetry root and the skill stops at its inputs — and is committed on `main` with a git
identity. The ask is the person's own words, verbatim, naming the reach `epic/fees`, so step 1
plans nothing:

> Quero o épico epic/fees do plano lending entregue de ponta a ponta: implementa a tarefa que
> falta, revisa e comita cada passo, sem parar no meio pra me perguntar.

The skill commits, so a record carries every commit the run added above the seed (`facts.json`:
subject and paths), the branches and the remotes. The checks read them: one commit per step under
`deliver-scope lending: <step>`, each path inside the roots that step names, every path inside the
declared roots, no branch beside `main`, no remote.

## Cases

- `full-deliver`: the whole route with the full skill in context. `/implement-task` and
  `/review-change` run inline from their own SKILL.md. 16 expectations: `deliver.py --check` and
  `--review lending` accept the recorded tree; the review is named `lending` by step 4's rule; one
  `deliver task/fees/compute-late-fee` and one `review` commit, each inside its roots; the measure
  committed where the probe wrote and only there; every commit named for the run and inside the
  declared roots; no branch, no remote; the log names both entry points; the handoff saved;
  commands.txt shows `--outstanding`, `--probe`, `--save-report` and `--render`; nothing written
  outside the declared roots.
- `compaction-resume`: the session resumes holding the first 20,000 characters of the skill,
  after step 4. Setup commits the implement-task benchmark's recorded delivery
  (`iteration-2/first-delivery`) as `deliver-scope lending: deliver task/fees/compute-late-fee`
  and the review-change benchmark's recorded review (`iteration-1/full-review`, its name
  `fees-review` renamed `lending`, as step 4 names a review) with its reconciliation as
  `deliver-scope lending: review`, each with the log's lines; the review's line is left
  uncommitted. From iteration 2 the ask is recorded with `ask.py --record` before the delivery, as
  the session rules have it recorded in the turn it is given, and the summary carries its `read:`
  line. Both validate (`deliver.py --check`, `--review lending`). No certification was
  staged, so step 5 has nothing to prove. What is left is the measure, the log's line for it and
  the report through the handoff — what the 5.67.0 cut, falling inside "Under a goal", leaves out:
  "What ends the run" and "Report, and stop". 13 expectations.
- `reading-quiz`: 18 multiple-choice questions on the densest points: the ask quoted verbatim and
  never inferred, the ask after a compaction, paste never compose, `--outstanding` as the only
  routing, what the deliver commit takes, the review's name, findings never acted on, step 5 and
  its second refusal, the measure after a stop, a probe that cannot read, the log, `decided:`
  lines, `/analyse` only under a goal and before the plan, what the door decider is handed, the
  findings policy, a stop class, and what the report hands without deciding. Each wrong option
  differs from the right one in one detail.

Every run is one `general-purpose` agent reading `prompt.txt`. No agent of the plugin is
registered, so every spawn fails and both arms take the inline route.

## Iterations 1 and 2 — 5.68.0 against 5.67.0 (f013ce2)

| Case | before: 5.67.0 | shipped: 5.68.0 |
|---|---|---|
| full-deliver (it. 1) | 16/16, 182.0k tokens, 375 s | 16/16, 175.3k tokens, 342 s |
| compaction-resume (it. 1, no ask recorded) | 9/13, 9/13 (56.2k, 49.8k) | 13/13, 12/13 (67.0k, 76.2k) |
| compaction-resume (it. 2, ask recorded) | 9/13, 9/13 (50.7k, 54.0k) | 13/13, 13/13 (66.3k, 63.0k) |
| reading-quiz (it. 1) | 18/18, 18/18 (47.3k, 47.2k) | 18/18, 18/18 (48.6k, 48.8k) |

- **The compaction separates the arms.** At 5.67.0 the cut falls inside "Under a goal"; every
  5.67.0 run measured and committed, and none ran `handoff.py --prepare`, `--save-report` or
  `--render`: the report was handed as free prose, and no run recommended any of the doors it named. At 5.68.0 the skill fits the cut whole (16,661 characters), and all four
  runs saved and rendered the handoff. The resumed 5.68.0 runs cost about 12k tokens more,
  spent on the report's work, including refused renders rewritten.
- **The full route does not separate the arms.** Both met 16 of 16; the 5.68.0 run cost about
  7k tokens less. Neither ran the conformance pass of the review inline (the session wrote the
  files it would judge), so neither wrote a reconciliation.
- **The quiz does not separate the arms.** Both reached the ceiling; the 5.68.0 reader opens 6
  files instead of 2 and spends about 1.5k tokens more, so the quiz holds only that no meaning
  was lost.
- **Iteration 1's resumed case was unsound.** It recorded no ask, so the summary was the only
  authorization a resumed run held. One 5.68.0 run read the skill's SPEC-010 R3 rule, found
  `ask.py --read` refusing, and committed nothing after the compaction (12/13: the telemetry it
  wrote left uncommitted). Iteration 2 records the ask in setup and re-runs both arms ×2; the
  iteration 1 records stay as they ran.
- **Grader fixes, applied to every record alike.** `review_named` first required the review to
  name a reconciliation, which an inline review whose conformance pass did not run never does;
  it now reads the review's file name. `measure_committed` first refused a `measure` commit when
  the probe wrote nothing; it now refuses only one that carries telemetry the probe did not
  write. No candidate text was corrected after a run: no run is recorded under `draft:`.

## Open

- **The log and the clean-tree checks contradict.** `/deliver-scope` appends each step's line to
  `<delivery_root>/<slug>/orchestration.md` after the step's commit (the line names that commit's
  hash), so the line is pending when the next entry point opens; `/implement-task` and
  `/review-change` both stop on `git status --porcelain -- <delivery-root>` printing anything.
  Both full runs worked around it by holding the line back. A plan with two tasks would stop at
  the second delivery as written. After the measure, nothing commits the measure's own line.
- **`--outstanding` refuses a delivery root that does not exist.** Where the ask names a reach
  and step 1 plans nothing, the first `deliver.py --outstanding` over `delivery/<slug>` exits 2
  ("is not a directory"); both full runs created the directory. The skill's `<delivery-root>
  <work-root>` reads as the project's roots, which `--outstanding` refuses; the initiative's are
  meant.
- The inline route still states no way to save a return, and no inline run of the review's
  conformance pass ran here.
