# Replaying real stops

`tools/replay_stops.py` answers one question about a change before it ships: **had this plugin
been running, what would the sessions of a consumer have done at the stops they really made?**
It replays stops taken from a consumer's own session transcripts, under a plugin tree you choose,
and reads what the grant answered and what the session did next. It is how 5.134.0, 5.135.0 and
5.136.0 were measured; their commit messages and the readings of `specs/grant.md` and
`specs/handoff.md` dated 2026-11-21 carry the numbers.

This document explains; it governs nothing. The tool's docstring is its usage, and its tests are
`tests/test_replay_stops.py`.

## What a replay is

For one stop — the last assistant message before a person's turn — the tool:

1. clones the consumer repository at the last commit before the stop's second, with no `origin`;
2. copies the consumer's `.git/siegard/` state as it stood at the stop (files stamped later, the
   `.jsonl` logs and `goal.json`, are left out), and writes the grant that was armed at that time,
   re-versioned to the arm's plugin version so it is live. `goal.json` is left out because the file
   on disk is the goal armed now, not the one armed at the stop: a session that read it would
   answer a goal another session armed;
3. cuts the session transcript and rewrites every path in it — the consumer, its parent directory,
   the plugin cache, the session id, and each `/tmp/` path the real session wrote, which moves
   under the run's `scratch/` — to the clone, and writes it where Claude Code finds a session for
   the clone;
4. resumes that session with `claude -p --resume`, the arm's tree loaded by `--plugin-dir`,
   prompted by a background-task notification and nothing else, so the session continues on its
   own as it would after a tool finished;
5. grades the run from what it printed and called, never from what it says it did.

Two bench hooks run beside the plugin's own, through `--settings`:

- `tests/fixtures/benchmarks/grant-gate/intercept.py` records every `Skill` and `Agent` call to
  `calls.jsonl` and **denies** it. A run shows the session's first act after the grant answered,
  and never runs a delivery.
- the tool's own `guard` denies a `Bash`, `Write` or `Edit` whose input names the real consumer,
  or a path under `/tmp` outside the run's directory and the arm's own tree. It tells the session
  to use `<run>/scratch`, which is also the run's `TMPDIR`, so that parallel runs never read each
  other's scratch files. `guarded` in `grade.json` counts the denials: a run with denials replays
  a session that was kept from a command, so read what it was denied before counting its
  outcome.

### The cut

- `--cut final` (the default, and what `batch` uses): the transcript ends at the last tool result
  before the stop's last message. The session writes its closing message again, so a Stop hook —
  and any change to what the hooks do at a stop — meets it.
- `--cut render`: the transcript ends at the tool result of a render that printed a grant's
  `judge`, at the minute the point's `at` names. Use it to measure what a session does with an
  answer it already received; the point's `at` must then be the render's time, not the stop's.

## Prerequisites

- This repository, with PyYAML and jsonschema installed, and the `claude` CLI logged in.
- The consumer repositories on disk, and their transcripts under
  `~/.claude/projects/-<path-with-dashes>/`. The tool derives that directory from the consumer path.
- Disk: each run holds a full clone. A clone of the sales consumers was 100–250 MB, so 100 runs
  need 10–25 GB under the root you choose.
- Account spend room. A run costs about $0.40–$1.20 at `claude-sonnet-5-5`, and 4 parallel jobs
  finish about 100 runs in 1.5–2 hours.

## The workflow

### 1. Choose the stops

```bash
S=/home/<you>/projects/sales
python3 tools/replay_stops.py points \
    --consumer $S/configurator $S/inventory $S/productorder \
    --since 2026-11-19T13:37 --out /tmp/points.json --live-grant --doors
```

`points` keeps a stop only where the person's next turn was a go-ahead or a "what now?", and
classifies that turn by fixed words (`GO`, `STATUS` and `PERSON` in the tool; Portuguese and
English). `--live-grant` keeps only stops where a grant was armed **and** its version was the
plugin version the session ran, read from the plugin-cache paths in the transcripts.
`--doors` keeps only stops whose message named a route door (`/plan-work`, `/implement-task`,
`/review-change`, `/reconcile`, `/deliver-scope`, `/analyse`). Drop either flag to widen the set.

Each point carries `project`, `consumer`, `session`, `at` (the stop's last message),
`skills` (the skills the turn invoked), `ask` (the person's turn before), `reply`
(the turn after) with its `reply_class`, `doors`, `rendered`, and the `grant` armed then.
Read a few before spending: the selection is regular-expression work and errs both ways.

### 2. Build the arms

An arm is a plugin tree: a directory holding `.claude-plugin/plugin.json`. The arm under test is
usually `src/claude` itself. A baseline or a variant is a copy:

```bash
cp -r src/claude /tmp/arms/B && find /tmp/arms/B -name __pycache__ -prune -exec rm -rf {} +
# then edit /tmp/arms/B — e.g. a released version from `git worktree`, or one line patched
```

The arm's `plugin.json` version is what the replayed grant is stamped with, so every arm's grant
is live under that arm.

A mode a project sets in its harness `env` — `SIEGARD_HANDOFF_STOP`, `SIEGARD_GRANT_STOP` — is
set in the arm by prefixing the `Stop` hook's command in the copy's `hooks/hooks.json`, for
example `SIEGARD_HANDOFF_STOP=enforce python3 "${CLAUDE_PLUGIN_ROOT}/hooks/goal_stop.py"`: the
replayed session reads no project settings of its own.

### 3. Run

```bash
python3 tools/replay_stops.py batch /tmp/points.json /tmp/replay \
    --arm A=$PWD/src/claude --arm B=/tmp/arms/B --reps 2 --jobs 4
```

Runs land in `/tmp/replay/<arm>/<point-index>-<rep>/`. Run `batch` again over the same root to
redo only the runs that are missing or `invalid`. `--only 3,17,30` limits the run to those
points. Smoke-test one point first (`--only 30 --reps 1 --jobs 1`): if the account hit its spend
limit, every run comes back `invalid` in seconds.

A single run can also be built and run by hand:

```bash
python3 tools/replay_stops.py build /tmp/points.json 30 $PWD/src/claude /tmp/replay/A/30-1
python3 tools/replay_stops.py run /tmp/replay/A/30-1 $PWD/src/claude
```

### 4. Read

```bash
python3 tools/replay_stops.py table /tmp/replay
```

One row per arm: runs, and how many came to each outcome, with the mean cost. The outcome of a
run (`grade.json`, field `outcome`):

| outcome | meaning |
|---|---|
| `took` | a render printed `take` or `judge`, and the session invoked the door or spawned the door decider |
| `took-not-carried` | the grant answered `take` or `judge`, and the session did not act on it |
| `stop` | the grant answered `stop` (the reason is in `answers`) |
| `rendered-silent` | the session rendered, and no grant line was printed (a `report`, or no grant asked) |
| `blocked-no-render` | a Stop hook blocked the stop, and the session still did not render |
| `no-block-no-render` | the session ended without rendering, and nothing blocked it |
| `invalid` | the run never ran (spend limit) |

Every run also keeps `stream.jsonl` (the whole session), `calls.jsonl` (intercepted calls and
guard denials), `stderr.txt`, `meta.json`, and the clone with its `.git/siegard/` — the kept
handoff records, `grant-checks.jsonl` and `handoff-checks.jsonl` included. `blocks` in
`grade.json` lists the grant gate's lines and the handoff check's blocks alike, so a run the
handoff check blocked under `SIEGARD_HANDOFF_STOP=enforce` comes to `blocked-no-render` when the
session still did not render. Read the `stop` reasons in `grade.json`'s
`answers` before drawing a conclusion. The first question for each one is whether the stop is
the person's by rule (SPEC-006 R3), or a gap the change could close.

### 5. Measure a render-time change without a model

When a change acts only inside `bin/handoff.py --render` or `bin/grant.py`, the runs already made
can be read again under the new code at no cost:

```bash
python3 tools/replay_stops.py static /tmp/replay --bin $PWD/src/claude/bin
```

For each run's newest kept decision record, `static` asks the grant again (`handoff.completed`
then `handoff.grant_answer`) and counts the decisions whose answer moved between `stop` and
`take`/`judge`, naming each one that moved. It does not show whether a session would carry the new
answer out. That was measured at 13 of 14 under the gate of SPEC-011 R12. This is how 5.136.0
was validated: 13 → 21 of 55 decisions.

### 6. Clean

```bash
python3 tools/replay_stops.py clean /tmp/replay
```

`clean` removes each run's clone and the cut transcript the tool wrote under
`~/.claude/projects/`. It keeps the run directories with their grades and streams. Delete the
root itself when the numbers are recorded.

## What to record

A change grounded in a replay states, in its commit message and in the reading of the
specification it changes:

- the window and the consumers;
- the selection flags and the number of points;
- the arms, runs per point and cost;
- the outcome counts per arm;
- for every stop the change must never take, that none was taken — the stops read as the
  person's by SPEC-006 R3, checked by hand;
- the estimator: "the grant's lines in each run's stream and the intercept log";
- and what a reversal would look like.

## Limits

- **One run per point is noisy.** The same point can come to `took` in one run and
  `no-block-no-render` in the next, and about one point in five ends differently from the real
  stop on any run. Use `--reps 2` or more for a decision.
- **The selection is by fixed words.** The reply classes and the door count are regular
  expressions. `PERSON` wins over `GO`, so "pode comitar" is never a go-ahead, and "o que falta"
  reads as a status question.
- **A clone is not the consumer.** Uncommitted files, environment variables, running services
  and anything outside the repository are absent. A stop that depended on them, such as a
  conformance kit against a live server, replays differently.
- **Grants are rebuilt, not replayed.** The grant armed at the stop is written with the arm's
  version, so its budget state is what the copied `.git/siegard/` held at the stop. A grant that
  had ended by a version change in the real session is live in the replay.
- **Denied calls end the run early.** The session never sees what the door would have done, so
  a replay measures the decision at one stop, never a route carried through.
