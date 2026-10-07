# `/analyse` under thin and rich material — benchmark, iteration 1 (2026-10-07)

Two arms, two materials, four runs, one `general-purpose` agent per run with a fresh context, each
handed the arm's `SKILL.md`, `hooks/rules.md`, the material and a git-initialised project under
`runs/<arm>-<material>/`. The arm is the plugin root: `arms/baseline/` is `src/claude` at `4d2d8d5`
(Siegard 5.12.0); `arms/candidate/` links to the working tree after A1–A3 (5.13.0 candidate).
Returns are saved verbatim under `iteration-1/<run>/report.md`, the written root under
`iteration-1/<run>/spec/`, the measurement under `shape-decided.txt`, the grading under
`grading.json`. SPEC-001 validation 2 names this kind of run; this is the first one recorded.

| run | ended − started | tokens | nodes | decisions | result |
|---|---|---|---|---|---|
| baseline × minimal | 1 m 55 s | 69k | 3 | 2 | wrote a context (`supporting`), `customer` AR with one required `name` and a `register` operation, a capability contract; `type` and `operations` decided and not logged |
| candidate × minimal | 1 m 00 s | 52k | 0 | 0 | **stopped before any write** citing SPEC-001 R15; named per class what the material would have to state; no question, nothing decided |
| baseline × rich | 3 m 30 s | 84k | 9 | 13 | AR, 2 VOs, 2 enumerations, state machine, uniqueness policy, capability; three nodes the material does not name carry no existence entry; report lists nodes without counts |
| candidate × rich | 4 m 14 s | 91k | 8 | 18 | same model minus the capability; **3 existence entries** (`type` on both enumerations and the state machine); **report opens with `N decided / M declared` per node** and names the two barely described; one watch item surfaced |

`candidate × minimal` ran with the arm symlink broken (one `..` too many); the agent read the skill
from the evident target, which is the candidate, and wrote nothing. The link was repaired before
`candidate × rich`.

## What the four runs say about the three changes

- **A3 (R15 stop).** The one thing the audit predicted — a floor produced from one sentence — is
  what the baseline did, with restraint (one attribute, no CPF, no e-mail), and what the candidate
  refused to do. The stop named the five classes in the session's plain words and asked nothing.
- **A2 (existence disclosure).** Over rich material both arms introduced the same three nodes the
  material never names (two enumerations, the state machine). Baseline: zero entries say so; the
  enumerations have no log at all. Candidate: one `type` entry each, `unstated` saying what the
  material named instead. Over the minimal material the baseline's `aggregate-root` and `register`
  were likewise decided and invisible.
- **A1 (counts).** The candidate's report put `18 decided / 56 declared` and the per-node lines at
  the top of its body and said which two logs to open first; `--shape` over the root prints the same
  eight lines. The baseline's reader finds the same thing only by reading all 13 entries.
- **Not attributable to the change:** the candidate wrote no capability contract where the baseline
  wrote one, and surfaced a watch item (inactive customer's document still blocks registration) the
  baseline's cross-check passed over. Both are model variance over an unchanged part of the skill;
  recorded, not graded.
- **Cost:** the candidate's rich run spent 8% more tokens and 44 s more than the baseline's; its
  minimal run spent 25% fewer and a minute less. Four runs are a reading, not a distribution.

## Companion readings

- `w3-decisions-reading.md` — what became of 714 decisions in two consumers: eternal 62/309 revised,
  54 within a day, almost all by `/analyse` increments aligning to code; servicedeskn1 0/405.
- `s2-conflict-reading.md` — decisions born of a contradiction inside the material: 19 in eternal,
  all over code-derived material, 7 revised (37%, twice the base rate), 5 by a person vs 12 standing;
  0 in servicedeskn1. The stop proposal is declined there with the criterion that reopens it.
