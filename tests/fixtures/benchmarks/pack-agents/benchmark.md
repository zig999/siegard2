# The candidate pack for `backlog-decomposer` and `unstated-fact-decider` (2026-11-08)

The binder reads its candidate set in one pack since 5.70.0 (`tests/fixtures/benchmarks/binder-replay`).
This measures the same pack for the two other agents `/plan-work` hands the impact set to.
`tools/bench_pack_agents.py` freezes a case from a consumer's git history — the specification as it
stood before the plan or the decision, the scope, intake and inventory the plan recorded, and the
impact set as the union of the plan's epic claims that the snapshot holds — and replays the agent
headless over it, every Read captured from `stream-json`. Frozen inputs and returns quote the
consumer's specification and stay outside the repository (`temp/pack-agents/`).

## Setup

- Consumer `configurator`: specification at `55e2b9f`, plan `qualification-configuration-price`
  at `a40c146`; impact set 107 nodes (40 claimed nodes absent at the snapshot), pack 1,680 lines,
  paths arm 214 files with logs.
- Decider cases: three facts the plan's decisions later recorded (`unstated` of the entry), over
  the specification before them.
- Arm `before` is `dist/.claude` at `6e7c6cd` (5.73.1), handed paths; arm `pack` the working tree,
  handed the pack. Model `claude-opus-5-5`, arms interleaved.

## Decomposer — 4 repetitions per arm

| arm | cost (US$) per run | turns | node files opened | nodes covered | epics | tasks |
|---|---|---|---|---|---|---|
| before | 1.69, 1.54, 1.41, 1.55 (6.19) | 115, 115, 116, 21 | 107 each | 107 | 5 | 29, 27, 33, 32 |
| pack | 1.46, 0.84, 1.18, 0.98 (4.46) | 7 each | 0 | 107 | 5–6 | 32, 33, 29, 35 |

Cost falls 28% over the four runs, 14% on the cold first; every pack run read all 1,680 lines; the
task counts overlap (27–33 against 29–35), so the cut does not move outside what the paths arm
already varies by.

## Decider — 3 facts, 2 repetitions per arm

| arm | cost (US$), 6 runs | read | where the fact landed |
|---|---|---|---|
| before | 2.84 | 6–13 of 107 nodes, found by search | as recorded in 2 of 3 facts |
| pack | 3.68 (+30%) | all 107, every run | differently in 2 of 3 facts, both repetitions |

With the whole impact set read, the decider created a new rule where it had edited the domain
element, and dropped the contract edit it had made beside a new constraint. The decider keeps its
paths: it reads the few nodes a fact needs, and the pack makes it dearer and moves its decisions.

Cost of the 20 runs: US$ 16.07.
