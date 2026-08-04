---
name: plan-work
description: Turns a stated development scope plus a validated knowledge base into a development plan — an inventory, epics and tasks recorded as markdown nodes under a work root, each task bound to the base nodes that govern it — validates the plan against the base, and derives plan.json. Also closes a plan when the human declares its initiative over, marking the work root as history. Use when a request asks to plan, decompose, or prepare development work over a domain the base already holds, or to close a finished plan. Not for analysing domain material (that is /analyse-domain), and not for writing source code or tests.
---

You turn a scope into a development plan, and you stop. One invocation, one increment: the
first fills an empty work root, and every later one evolves the plan it already holds — same
order, same discipline.

## Required inputs

A missing input is a stop, not a default:

1. **the scope** — what the human wants developed, in prose, plus any files it references.
2. **the knowledge root** — the base the plan binds to. Named by the human; inferred rather
   than named, its absence is a stop. A plan bound to a base nobody named answers a question
   nobody asked.
3. **the work root** — the directory the plan nodes are written into. Empty is the ordinary
   first run; populated, the invocation is a change to the plan it holds. Named by the human
   and absent, it is created empty; inferred rather than named, its absence is a stop. A root
   serves one initiative: holding `closure.md`, it is history — planning over it is a stop,
   and a new initiative names a new root, where the delivered work returns as inventory
   through the survey, never as a reference into the old plan.
4. **the target source root** — where the code lives or will live. An empty tree is an answer
   — a greenfield target — not a stop; but which tree it is, the human says.

A closing invocation — the human declaring the initiative over — needs two of these: the ask
with its why, and the work root. The knowledge root and the target source root play no part
in closing (see "Closing the plan").

## Before anything: the base

The plan is only as sound as the base it binds. Run:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/graph.py --check <knowledge-root>
```

Anything but a clean pass is a stop: report the output verbatim and go no further. A base with
problems is fixed through `/analyse-domain`; a stale `graph.json` is rederived by whoever owns
the base. Neither repair is this invocation's to make — planning never writes into the
knowledge root.

The pin every task carries is the SHA-256 of the base's `graph.json` as just checked:
`sha256:<hexdigest>`, computable as `sha256sum <knowledge-root>/graph.json`. Compute it once,
after the check passes, and stamp it on every task this invocation binds or re-binds.

## Before anything: the tree

The review is `git diff` over the work root, and a diff only says what this invocation did
when the root starts clean. Before any write, `git status --porcelain -- <work-root>` must
print nothing. Output is a stop: report what is pending and go no further — committing,
discarding, or overriding is the human's decision, never the plan's. A work root not under git
control is the same stop: without git there is no review.

## Read the contract

Read `${CLAUDE_PLUGIN_ROOT}/schemas/plan-node.json`. It is the single home of what a plan node
may and must declare — the kinds, the fields each kind requires, and one example per kind
inside that kind's branch. Do not work from memory of it, and do not restate it: what you
remember is not what the validator will apply.

`${CLAUDE_PLUGIN_ROOT}` is set where this skill runs as an installed plugin. Where it is not,
the plugin root is the directory that holds `schemas/` and `bin/` side by side — in a vendored
install, the `.claude/` directory this skill's tree sits under. Every path below resolves the
same way.

## The order

```
situate → inventory → decompose → bind → validate → report → stop
```

Three of these steps are another judge's. The survey, the decomposition, and each task's
binding are delegated to the subagents this framework ships, each in a clean context, and
the judgment of each step lives in the agent's file — not here, and not in your memory of
it. Delegating means spawning the named subagent — in a plugin install the name may be
plugin-scoped — and reading the agent's file yourself is the fallback, never the
delegation. The binder's isolation is the point of the whole arrangement: it arrives with
no memory of how the tasks were cut, so the base is read for what it says today, never to
fit a task. Only where the session cannot spawn subagents, read the agent's file under the
plugin root's `agents/` directory and apply its discipline in place — the file stays the
single home of that judgment — and the report must say which steps ran inline.

### 1. Situate

Two indexes, one rule: read the index, never the whole tree.

- **The base.** Read `<knowledge-root>/graph.json` — current, because the check above passed:
  identifiers, titles, summaries, each node's open gap fields, and every edge. Locate the
  nodes the scope speaks to, and close the impact set over the edges in both directions —
  what those nodes reference, and what references them. Where the scope's vocabulary does not
  surface in the index, grep the base for its terms. Read the impact-set nodes and nothing
  else: the plan binds to what governs the scope, not to everything the base holds. When the
  impact set is the whole base, the index is all this step reads — the node files belong to
  the binders, each reading its own candidates fresh.
- **The plan, when the work root is populated.** Trust its index only after checking it: run
  `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/plan.py --check <work-root> <knowledge-root>`, and a
  stale `plan.json` is rederived by a full validation run before anything relies on it.
  Read `plan.json`, and only it: locate the
  epics and tasks the scope touches, and close the impact set over its edges — dependencies
  in both directions, and bindings that reach the base's impact set. Read those files alone.
  Outside the set, standing decisions stand: a task this change does not touch is not
  reworded, however improvable it looks.

### 2. Inventory

Before any node, persist the scope: the prose as supplied, plus any files it references, go
under `intake/` in the work root. Point every `sources` entry at a file under it. A change
persists the same way — a new file under `intake/`, never an edit to what intake already
holds.

Every plan node this skill writes — this one and every one after it — carries a body of
exactly two headings, in order: `## What it is`, then `## Notes`. One sentence per line; a
section with nothing to say carries the literal line `None.`

Then spawn a `codebase-surveyor` subagent — its judgment lives at
`${CLAUDE_PLUGIN_ROOT}/agents/codebase-surveyor.md` — passing three things: the target source
root, the scope's path under `intake/`, and the plan-node contract's path. It returns
inventory nodes — modules, evidenced conventions, reuse points, consumer-named risks, and
the empty tree as a full answer where that is what it found. Write each returned node at the
path its identifier computes to, verbatim.

### 3. Decompose

Spawn a `backlog-decomposer` subagent — its judgment lives at
`${CLAUDE_PLUGIN_ROOT}/agents/backlog-decomposer.md` — passing four things: the scope's path, the impact set as you read it from the base's index —
identifiers, titles, summaries, and each node's open gap fields — the surveyor's inventory,
and the plan-node contract's path. Its file holds the boundary tests that shape every task;
what comes back is epics, complete, and task skeletons — objective, criteria, dependencies —
deliberately without the binding fields, which belong to the next step's judge.

Write the epics at the paths their identifiers compute to. Hold the task skeletons: a
skeleton is not yet a valid node, and it only touches disk bound and pinned.

### 4. Bind

Binding is per task and per judge: spawn one `execution-contract-binder` subagent per
skeleton — its judgment lives at `${CLAUDE_PLUGIN_ROOT}/agents/execution-contract-binder.md`
— passing four things: the skeleton as its title, summary, objective and criteria — never
its `rationale`, its dependencies or its body, because an opinion about the binding travels
with them and the clean context is the point — the candidates — its epic's `covers` less its
`uncovered`, because binding what the epic declared untouched is a contradiction the
validator refuses — the knowledge root, and the plan-node contract's path. The binder rereads the node files fresh and returns the task's `nodes`, its
full gap triage — `unresolved` and `waived`, with whys — and the questions the base cannot
answer; a divergence between the task and the nodes comes back as notes.

Then compose and write each task: the skeleton, plus what its binder returned, plus the pin
from the base check stamped on `base`. A binder's notes are appended to the task body's
`## Notes`, one sentence per line, a blocking one saying so — the diff is the review, and a
divergence only the conversation holds is a divergence the reviewer never sees — and the
report repeats them by task. Where the binder bound nothing, the task carries `rationale` saying why —
scaffolding is real work, but ungoverned work is a claim someone reviews. Where a note says
the task needs what the candidates do not hold, the cut is wrong: grow the epic's `covers`
or move the task, and re-bind — never widen a binding by hand.

A note the binder classed `blocking` — the objective or a criterion cannot be demonstrated
as written without contradicting or exceeding the base — is settled before the task is
written, and the skeleton's `rationale` says by whom. Where the blocked statement was the
decomposer's decision — the skeleton carries `rationale` over that cut — the skeleton goes
back to the decomposer with the note, is re-cut, and re-bound. Where it came from the scope,
the task is written with the note, and the report names it as a conflict only the human
settles — through the scope, or through `/analyse-domain`. An `advisory` note stays a note —
except one naming nodes outside the epic's covers, which never travels alone: the caller's
decision is recorded beside it in `## Notes` — grow the claim and re-bind, move the task and
re-bind, or stand with the why. The class is the binder's judgment, not yours to overrule: a
blocking note you disagree with is still settled as blocking, and the disagreement goes in
the report.

Each task file is checked on its own as soon as it is composed — a composition error is
caught at the file that made it, never discovered at the end:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/plan.py --node <file> <work-root> <knowledge-root>
```

### 5. Validate, and derive the plan

When every node is written, run:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/plan.py <work-root> <knowledge-root>
```

This validates every plan node against the contract, runs the checks that need the whole plan
and the base — dependencies resolve without cycles, bindings resolve, every open gap on a
bound node is triaged, every covered node reaches a task or a stated why, every pin matches
the base as it stands — and derives `plan.json`. **Never write or edit `plan.json` yourself.**
Report the command's output verbatim. If it exits non-zero, the run failed — fix and rerun,
and never describe the plan as valid while it is not.

**Fixing means form, never knowledge.** A wrong shape — a malformed pin, a bad reference, a
forbidden field — is yours to correct. An untriaged gap is settled by judgment — unresolved
or waived — never by inventing the fact it names. A question is never answered by the plan. A
coverage hole is settled by a task or by `uncovered` with a why — whichever the scope actually
decided, not whichever passes.

### 6. Report, and stop

Report, in this order:

- every node written, by identifier — on a populated root, created, changed and removed
  listed apart;
- the impact set that was read — in the base and, on evolution, in the plan — so the reviewer
  can judge what the planning looked at, not only what it touched;
- every unresolved entry, by task identifier — the gaps that block and the questions that
  outran the base, the latter with the pointer back to `/analyse-domain`;
- every waiver, by task identifier — these are the claims a reviewer can reject;
- every note a binder returned, by task identifier — the same divergences written into each
  task's `## Notes`, repeated here so the reviewer meets them before the diff;
- every node carrying `rationale`, by identifier;
- which steps, if any, ran inline instead of in a subagent, and why;
- the validator's final output, verbatim.

Then stop. `git diff` over the work root is the review, and it belongs to a person.

## Closing the plan

A work root serves one initiative, and the human says when it is over — the ask, with its
why, is the input, and either missing is a stop. Closing spawns no judge, runs no base
check, and computes no pin: it never touches the knowledge root.

- The root must be under git and clean, exactly as before any write — the closure diff is
  its own review. A root already holding `closure.md` is already closed: stop.
- Persist the ask under `intake/`, like any scope.
- Write `closure.md` at the work root: prose, one sentence per line — the why as the human
  gave it, and the intake file it was read from. It is a marker, never a node: the
  validator keeps it the way it keeps `intake/`.
- Run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/plan.py <work-root>` — no knowledge root,
  because a closed plan validates without one. The derivation is the seal: it still
  refuses a plan whose structure does not hold, and a base that moved since the bindings
  is no obstacle — each pin now stands as history, naming the base its binding read.
- Report the closure and the legacy the plan carries out — its unresolved gaps, citations
  and unique, and its open questions: the agenda `/analyse-domain` inherits. Then stop.

## What you never do

- Write or edit `plan.json` by hand.
- Close a gap, or answer a question, with a value the base does not hold — a fact is produced
  in the base, through `/analyse-domain`, never in a task.
- Waive a gap without a why, or triage by silence.
- Record a status, an estimate, a priority or an execution order — those fields do not exist,
  and prose does not get to hold what the contract refused.
- Bind a task in the context that decomposed it — the inline fallback is for a session that
  cannot spawn subagents, is declared in the report, and still applies the agent's file.
- Write source code or tests, or change the target tree — the plan is nodes, nothing else.
- Write into the knowledge root — a broken or stale base is reported with its fix, never
  repaired from here.
- Restate the contract's vocabularies from memory instead of reading the schema.
- Reopen a standing plan decision outside the impact set, or re-cut an epic as a side effect
  of a change.
- Commit, stash, or otherwise change the consumer's git state — a dirty root is reported, and
  what to do with it is the human's call.
- Write into a work root that holds `closure.md`, or remove a closure — a closed plan is
  history, and reopening it is the human's git act, after which the live checks and the
  stale pins force the re-binding themselves.
