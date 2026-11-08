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

# Iteration 3 — the pack over productcatalog's largest candidate sets (2026-11-08)

Six productcatalog tasks: four from the four largest epics of plan `dominio-inicial`
(`product-offering/patch`, `catalog-core/version-visibility`, `product-specification/create`,
`product-offering-price/patch`; packs of 1,563–2,112 lines, 116–125 KB) and two controls (packs of
321 and 666 lines). Two candidates the old epics name no longer exist and were skipped. Arm
`before-5.69.0` is `dist/.claude` at `1c6b8c7`, handed one path per node and log; arm
`pack-5.73.0` is the current tree, handed the pack. Same model (`claude-opus-5-5`), 3 repetitions,
arms interleaved by repetition, every Read captured from `stream-json` and the pack's coverage
counted from the line numbers each Read returned. 36 runs, 0 failures.

## Decision

| measure | before (A) | pack (B) |
|---|---|---|
| tasks identical across all 3 repetitions | 2 / 6 | 1 / 6 |
| mean pairwise Jaccard within the arm | 0.926 | 0.888 |
| minimum pairwise Jaccard within the arm | 0.667 | 0.50 |
| mean Jaccard against the recorded `implements` | 0.840 | 0.853 |
| mean Jaccard across arms | 0.903 | |

Five tasks diverge across arms within A's own divergence (0.87–1.00). The sixth,
`catalog-core/version-visibility`, implements 2–3 of 52 candidates, so one identity moves Jaccard
by a third: across arms 0.648, B naming 3, 6 and 3 nodes where A named 3, 2 and 2.

## Reading

- 17 of 18 pack runs read every line of the pack; 4 of them met the Read tool's 25,000-token
  refusal on a window and read it again smaller or with `allow_large`. None opened a node file or
  a log beside the pack.
- One run (`catalog-core/version-visibility`, repetition 3) read lines 1–1,598 and 2,040–2,113 and
  reached the rest by Grep: 1,671 of 2,112 lines, 79%.
- Arm A opened 34–49 node files per large task, 5 on `version-visibility`, where it narrowed by
  search instead of reading every candidate.

## Cost

| repetition | arm | cost (US$) | turns, median | seconds, median |
|---|---|---|---|---|
| 1 (cold) | A | 4.18 | 34.5 | 88 |
| 1 (cold) | B | 3.05 | 5 | 59 |
| 2 | A | 2.78 | 30.5 | 82 |
| 2 | B | 1.82 | 5 | 63 |
| 3 | A | 2.75 | 35 | 92 |
| 3 | B | 1.39 | 5 | 58 |

The cold repetition costs 27% less and takes 33% less time. The one task the pack made dearer is
`version-visibility` (A 0.39/0.08/0.14, B 0.62/0.39/0.39): a binder that implements a few nodes of a
large set pays the whole pack where it used to open a handful.

## Iteration 3b — reading the pack in windows (5.73.1)

The binder gains one sentence: a pack too large for one Read is read in consecutive windows until
its `logs:` line, skipping none and searching none. Arm `pack-5.73.1`, the two tasks whose packs
pass 1,800 lines, 3 repetitions each: 6 of 6 runs read every line of the pack (4 after a
25,000-token refusal), none opened a node file. `version-visibility` still varies as it did in both
arms before (3, 3 and 5 nodes; within-arm Jaccard 1.0, 0.6, 0.6; against the recorded `implements`
1.0, 1.0, 0.6); `product-offering/patch` across arms 0.966. US$ 3.89 for the six runs.
