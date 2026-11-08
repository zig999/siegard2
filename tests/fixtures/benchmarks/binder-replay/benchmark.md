# `execution-contract-binder` replay — noise floor, iteration 1 (2026-11-08)

A change to the specification's format is judged by whether the binder — the heaviest reader of
the specification in every consumer measured — still names what it named before. The binder's
own variance over identical inputs is the floor that judgment reads against: a format whose
divergence from the current format stays inside the current format's divergence from itself has
changed nothing the binder decides.

`tools/bench_binder_replay.py` freezes the four inputs `/plan-work` step 4 hands the binder —
skeleton, candidates (the epic's `covers` less its `uncovered`, each node followed by its
decision log), binding slice and prompt — from a consumer's delivered plan, spawns the binder
headless (`claude -p --agent siegard:execution-contract-binder --plugin-dir <dist>`, tools
`Read`, `Grep`, `Glob`), and grades pairwise Jaccard similarity of `implements` between
repetitions and against the delivered task's recorded `implements`.

The frozen inputs and the verbatim returns quote a consumer's specification and stay outside the
repository (`temp/binder-replay/`); this record keeps the measurement.

## Setup

- Consumer: the `configurator` module, plan `qualification-configuration-price`, 10 of its 38
  tasks across all five epics; candidate sets of 18–52 nodes (36–104 files with logs).
- Specification snapshot digest `138bf1a35db1…` (`tree_digest` over the copied specification).
- Arm `current-5.69.0`: `dist/.claude` at 5.69.0; the agent definition picked `claude-opus-5-5`.
- 3 repetitions per task, 5 in parallel; 30 runs, 0 failures.

## Results

| measure | value |
|---|---|
| tasks whose `implements` was identical across all 3 repetitions | 5 / 10 |
| mean pairwise Jaccard between repetitions | 0.944 |
| minimum pairwise Jaccard | 0.75 |
| mean Jaccard against the recorded `implements` | 0.931 |
| identities that varied between repetitions | 8 (5 constraints, 1 contract, 1 domain element, 1 scenario) |
| turns per run, median | 25 |
| tokens per run, median | 13.8k cache write, 164.6k cache read, 6.8k output |
| duration per run, median | 62 s |
| cost, 30 runs | US$ 10.37 (`total_cost_usd`) |

## What the runs say

- **The floor is about 6% divergence.** An arm is read against a mean pairwise Jaccard near 0.94
  and a minimum near 0.75; an arm below that has changed what the binder decides.
- **The variance sits on constraints.** Five of the eight identities that varied are
  `constraints/` nodes — the class every task's candidate set holds whole.
- **The first repetition of each task cost about 1.5× the later ones** (prompt cache). An A/B
  interleaves its arms, or its token comparison reads the cache rather than the format.
- **The historical binders ran on `claude-sonnet-5-5`** (subagent metadata); the agent definition
  at 5.69.0 picks Opus. Every arm compared against this floor runs on the same model.
