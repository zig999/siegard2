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

# Iteration 2 — the candidate pack (2026-11-08)

Arm `pack-p2`: the 5.70.0 working tree. `/plan-work` hands the binder the path of one file
`spec.py --pack` printed over the candidates — every node verbatim under its identity and digest,
each decision log listed by path and not carried — instead of one path per node and log. Same
frozen inputs, same snapshot, same model (`claude-opus-5-5`), 3 repetitions per task, 30 runs,
0 failures.

## Decision

| measure | current (A) | pack (B) |
|---|---|---|
| tasks identical across all 3 repetitions | 5 / 10 | 3 / 10 |
| mean pairwise Jaccard within the arm | 0.944 | 0.929 |
| minimum pairwise Jaccard within the arm | 0.75 | 0.80 |
| mean Jaccard against the recorded `implements` | 0.931 | 0.924 |
| mean Jaccard across arms (every A run × every B run) | 0.928 | |
| minimum Jaccard across arms | 0.75 | |

Every identity on which B diverged is one A already oscillated on, or one the recorded
`implements` holds, save one domain element named once in one B run of one task — an element A
also named and dropped between repetitions of another task. The divergence across arms equals B's
divergence from itself and sits within 0.016 of A's: the pack changed no decision outside the
floor iteration 1 measured.

## Cost

| repetition | arm | cost (US$) | turns, median | cache read, median | cache write, median | seconds, median |
|---|---|---|---|---|---|---|
| 1 (cold) | A | 4.63 | 25 | 150.6k | 33.1k | 69 |
| 1 (cold) | B | 3.84 | 4 | 24.2k | 35.7k | 45 |
| 2 | A | 2.99 | 27.5 | 177.4k | 12.6k | 62 |
| 2 | B | 1.34 | 4 | 58.9k | 0 | 38 |
| 3 | A | 2.75 | 24 | 164.6k | 10.6k | 59 |
| 3 | B | 1.55 | 4 | 56.9k | 0 | 48 |

- **Repetition 1 is the production-like reading**: each binder in a plan reads a different
  skeleton before its pack, so the pack enters the cache cold, as here. Against it the pack costs
  17% less, takes 35% less time and 84% fewer turns. The cache write is the same — the pack is
  written once instead of across 25 turns — and the saving is the cache re-read every turn pays.
- **Repetitions 2 and 3 cost about half** of A's, but their inputs are byte-identical to
  repetition 1's, so the pack is read from cache; a plan does not repeat a task, and these rows
  bound the saving from above.
