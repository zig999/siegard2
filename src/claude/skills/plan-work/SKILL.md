---
name: plan-work
description: Turns a stated development scope plus a validated specification into a development plan — an inventory, epics and tasks recorded as markdown nodes under a work root, each task naming the specification nodes it implements — validates the plan against the specification, and derives plan.json. Also closes a plan when the human declares its initiative over, marking the work root as history. Use when a request asks to plan, decompose, or prepare development work over a domain the specification already holds, or to close a finished plan. Not for analysing domain material, and not for writing source code or tests.
effort: medium
---

You turn a scope into a development plan, and you stop. One invocation, one increment: the
first fills an empty work root, and every later one evolves the plan it already holds — same
order, same discipline.

## Required inputs

A missing input is a stop, not a default:

1. **the scope** — what the human wants developed, in prose, plus any files it references.
2. **the project root** — where `siegard.json` lives. Named by the human; inferred rather than
   named, its absence is a stop.
3. **the target** — which of the project's target source roots this plan reaches, by the key
   `siegard.json`'s `targets` names it. A key the file does not hold is a target nobody
   declared.
4. **the initiative's slug** — this plan's own subdirectory under the project's work root.
   Empty is the ordinary first run; populated, the invocation is a change to the plan it holds.
   A slug naming a directory that holds `closure.md` is a different matter: planning over it is
   a stop, and a new initiative names a new slug, where the delivered work returns as inventory
   through the survey, never as a reference into the old plan.

Run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/project.py <project-root>` once, before anything else.
`specification_root`, `targets` and `work_root` answer only from here: naming one of these in the
invocation instead has no effect, and where the file does not declare one, that is a stop, not a
question to work around — the report carries the `/siegard-config` invocation ready to paste,
naming the project root and every field missing. From here on, "the specification root" means
`specification_root` as resolved; "the target source root" means `targets[<the target>]`; "the
work root" means `work_root/<the initiative's slug>`.

One optional input: **the project's standard** — the path to the registry of rules the project set
for itself. It plays one part here and no other. A registry states the artifacts its rules
presuppose — a manifest, a compiler configuration, whatever a rule names and no rule can ask for —
and where the target tree does not hold one, building it is work this plan holds or nothing does:
the specification has no node for a manifest and should not, no epic covers one, and
`/implement-task` refuses to write source while the absence stands. The rules themselves are not
a plan's business. A plan writes no source, and judging how source is arranged belongs to the two
entry points that do.

The standard resolves in one order, from the same `project.py` run above, and the report says
which step answered. Unlike the roots, **a naming in the invocation wins here** — a registry is
worth trying a different one against, sometimes; a root is not. Where the invocation names none,
the file's `standard` answers: `null` declares deliberately that the project has none — the
narrow path, chosen rather than forgotten, taken without asking again. Where neither answers — no
naming, no file, or the file simply does not declare the field — the standard joins the single
stop of absent inputs: name it, or declare it through `/siegard-config`, and the stop's report
carries that invocation ready to paste. A file that does not hold together is a stop reported
verbatim; a naming that overrode a differing file is reported with both. Below, a standard
"named" means resolved by either step.

Absent inputs stop once, together: one stop naming everything missing, so the human answers
once — never a question at a time.

A closing invocation — the human declaring the initiative over — needs three of these: the ask
with its why, the project root, and the initiative's slug. The specification root and the
target source root play no part in closing (see "Closing the plan").

## Before anything: the specification

The plan is only as sound as the specification it implements against. Run:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/spec.py <specification-root>
```

Anything but a clean pass is a stop: report the output verbatim and go no further. A
specification with problems is fixed through the analysis that authors it; planning never
writes into the specification root. There is no derived index of the specification to go
stale — `spec.py` validates the files themselves, every time — so there is nothing here to
recheck the way a plan's own `plan.json` must be.

A task names the specification nodes that govern it by identity, and carries no pin: the
specification does not change during a plan's execution, by convention. A task written today
and implemented next week reads the specification as it stands at read time, not as a frozen
copy — the discipline is procedural, held by not touching the specification while a plan is
live, never by a value this skill computes and compares.

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
situate → inventory → decompose → implement-against → validate → report → stop
```

Three of these steps are another judge's. The survey, the decomposition, and each task's
specification references are delegated to the subagents this framework ships, each in a clean
context, and the judgment of each step lives in the agent's file — not here, and not in your
memory of it. Delegating means spawning the named subagent — in a plugin install the name may
be plugin-scoped — and reading the agent's file yourself is the fallback, never the
delegation. The binder's isolation is the point of the whole arrangement: it arrives with
no memory of how the tasks were cut, so the specification is read for what it says today, never
to fit a task. Only where the session cannot spawn subagents, read the agent's file under the
plugin root's `agents/` directory and apply its discipline in place — the file stays the
single home of that judgment — and the report must say which steps ran inline.

### 1. Situate

Specification nodes carry no title or summary of their own — only `type`, the declared fields,
and a body under `## Description`. There is no cheap index to read instead of the files; there
is a cheap manifest of what exists, and a grep to narrow before anything is opened.

- **The specification.** Run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/spec.py --digest
  <specification-root>` — every node's identity, sorted, current because the check above
  passed. That is the full manifest; it names nothing about what a node says. Grep the
  specification root for the scope's vocabulary — its nouns and the terms the material uses —
  to find candidate files, then open exactly those. Close the impact set in both directions:
  read what a candidate references in its own frontmatter (`attributes`, `relationships`,
  `constrains`, `subject`, `status`, `upstream`, `payload`, `refusal`, `involves`), and grep
  the specification root for each candidate's identity to find what references it back —
  there is no derived edge index to read this from instead. Read the impact-set files and
  nothing else: the plan implements against what governs the scope, not everything the
  specification holds.
- **The plan, when the work root is populated.** Trust its index only after checking it: run
  `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/plan.py --check <work-root> <specification-root>`, and
  a stale `plan.json` is rederived by a full validation run before anything relies on it.
  Read `plan.json`, and only it: locate the epics and tasks the scope touches, and close the
  impact set over its edges — dependencies in both directions, and `implements` references
  that reach the specification's impact set. Read those files alone. Outside the set, standing
  decisions stand: a task this change does not touch is not reworded, however improvable it
  looks.
- **The project's standard, when one was named.** Run

  ```
  python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --standard <the registry> --against <target-source-root>
  ```

  A registry that does not hold together is a stop, reported verbatim: fixing it belongs to
  whoever owns it. An artifact it presupposes and the tree does not hold is **not** a stop — it is
  this bullet's whole product. Keep what the command printed for each: the path, what the registry
  says that artifact provides, and the rules it named as unanswerable while the artifact is
  absent. That set goes to the decomposition, and it is gathered here, before any node is written,
  because it decides whether this plan holds one more task than the scope asked for.

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
`${CLAUDE_PLUGIN_ROOT}/agents/backlog-decomposer.md` — passing four things: the scope's path,
the impact set's file paths under the specification root, the surveyor's inventory, and the
plan-node contract's path — plus, where a standard was named and the situate step found any,
the artifacts it presupposes that the tree does not hold, each with what the registry says it
provides and the rules it carries. Those are the one thing the decomposition may cut a task for
that the scope never asked about. Its file holds the boundary tests that shape every task; what
comes back is epics, complete, and task skeletons — objective, criteria, dependencies —
deliberately without `implements`, which belongs to the next step's judge.

Write the epics at the paths their identifiers compute to. Hold the task skeletons: a
skeleton is not yet a valid node, and it only touches disk once it names what it implements.

### 4. Implement against

This is per task and per judge: spawn one `execution-contract-binder` subagent per skeleton —
its judgment lives at `${CLAUDE_PLUGIN_ROOT}/agents/execution-contract-binder.md` — passing
three things: the skeleton as its title, summary, objective and criteria — never its
`rationale`, its dependencies or its body, because an opinion about the reference travels with
them and the clean context is the point — the candidates' file paths, its epic's `covers` less
its `uncovered`, because naming what the epic declared untouched is a contradiction the
validator refuses — and the plan-node contract's path. The binder rereads the candidate files
fresh and returns the task's `implements`; a divergence between the task and the specification
— including a fact the specification does not state at all — comes back as a classified note.

Then compose and write each task: the skeleton, plus `implements` exactly as the binder
returned it — bare identities, no pin. A binder's notes are appended to the task body's
`## Notes`, one sentence per line — the diff is the review, and a divergence only the
conversation holds is a divergence the reviewer never sees — and the report repeats them by
task. A note classed `blocking`, `underdetermined` or `remainder` opens with its class,
literally — `BLOCKING, from the specification —`, `UNDERDETERMINED, from the specification —`,
`REMAINDER, from the specification —` — the exact text and not a style, because
`/implement-task` collects underdetermined entries by that opening and nothing else marks
them; an underdetermined note carries the implementation the binder named in `passes`, and a
remainder note the destination it named in `belongs`. Where the binder found nothing to
implement against, the task carries `rationale` saying why — scaffolding is real work, but
ungoverned work is a claim someone reviews. Where a note says the task needs what the
candidates do not hold, the cut is wrong: grow the epic's `covers` or move the task, and
re-implement against it — never widen the reference by hand.

A note the binder classed `blocking` — the objective or a criterion cannot be demonstrated as
written without contradicting or exceeding the specification, including a fact the
specification does not state at all — is settled before the task is written, and the
skeleton's `rationale` says by whom. Where the blocked statement was the decomposer's decision
— the skeleton carries `rationale` over that cut — the skeleton goes back to the decomposer
with the note, is re-cut, and re-run through this step. Where it came from the scope, the task
is written with the note, and the report names it as a conflict only the human settles —
through the scope, or through the analysis that extends the specification. An
`underdetermined` note travels with the task and re-cuts nothing: it is what a test must
exclude, and `/implement-task` hands it to whoever writes the tests. A `remainder` note
travels the same way and re-cuts nothing: an unreached clause is answered where it belongs —
another task's reference, the epic's `uncovered`, or scope this plan does not yet hold — and
no validator walks clauses, so the report is where a reviewer checks that something answers
it. An `advisory` note stays a note. A note of any class that names specification nodes
outside the epic's covers never travels alone. Two of the caller's three decisions erase the
condition rather than record it: grow the claim and re-run this step, or move the task and
re-run it — the replacement reference answers inside the new covers. The third persists, and
is recorded on its own line immediately after the note in `## Notes`: `Decision, beyond the
covers — stand: <why>` — the exact opening and not a style, because the validator refuses a
task whose `## Notes` names a specification node outside its epic's covers with no such line
naming that node, and a refused plan derives no plan.json. The class is the binder's judgment,
not yours to overrule: a blocking note you disagree with is still settled as blocking, and the
disagreement goes in the report.

Each task file is checked on its own as soon as it is composed — a composition error is
caught at the file that made it, never discovered at the end:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/plan.py --node <file> <work-root> <specification-root>
```

### 5. Validate, and derive the plan

When every node is written, run:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/plan.py <work-root> <specification-root>
```

Where a standard was named, name it here too — the two flags travel together, and neither half
decides anything alone:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/plan.py --standard <the registry> --against <target-source-root> <work-root> <specification-root>
```

This validates every plan node against the contract, runs the checks that need the whole plan
and the specification — dependencies resolve without cycles, every reference resolves, every
covered node reaches a task or a stated why — plus, with a standard named, that every artifact
it presupposes either stands in the tree or is declared in some task's `produces`, and derives
`plan.json`. That last check is why the decomposition was handed the absent set rather than
trusted to remember it: a task nobody cut is invisible in the plan that lacks it, and this is
the one place the lack is a refusal.
**Never write or edit `plan.json` yourself.**
Report the command's output verbatim. If it exits non-zero, the run failed — fix and rerun,
and never describe the plan as valid while it is not.

**Fixing means form, never knowledge.** A wrong shape — a malformed reference, a forbidden
field — is yours to correct. A coverage hole is settled by a task or by `uncovered` with a why
— whichever the scope actually decided, not whichever passes. A blocking note is settled by
judgment, never by inventing the fact the specification does not state.

### 6. Report, and stop

Report, in this order:

- every node written, by identifier — on a populated root, created, changed and removed
  listed apart;
- the impact set that was read — in the specification and, on evolution, in the plan — so the
  reviewer can judge what the planning looked at, not only what it touched;
- every blocking note, by task identifier, with what it concedes — these are the tasks not yet
  written, or written with a standing conflict, and each needs either the scope answered
  differently or the specification extended through the analysis that authors it;
- every note a binder returned, by task identifier — the same divergences written into each
  task's `## Notes`, repeated here so the reviewer meets them before the diff — an
  underdetermined one carrying the implementation it names, a remainder one carrying where
  it belongs;
- every node carrying `rationale`, by identifier;
- where a standard was named, where it resolved from — the invocation, or the project file by
  path — then what it presupposes and where each of those stands: held by the tree already, or
  produced by a task this plan now holds, named by identifier and by path. Where none resolved,
  say which absence it was — a declared none in the project file, or nothing anywhere — because
  a plan cut without one is a plan that cannot know whether the tree it plans over can run
  anything it delivers, and that is the honestly narrow answer rather than silence;
- which steps, if any, ran inline instead of in a subagent, and why;
- the validator's final output, verbatim;
- the handoff: the `/implement-task` invocation ready to paste — the project root, the target
  and the initiative's slug filled in, since every root they resolve to was just validated
  above, and the project's standard where the project file does not already answer it. One
  slot is left open and it is the one that matters: **the task** — one invocation carries one
  task, and choosing it is choosing what gets built. What the handoff offers in its place is
  where the deliverable set is read from, as a command rather than as a list: `deliver.py
  --outstanding <delivery-root> <work-root> <target-source-root> <specification-root>`, every
  root already resolved above, names per task what has no record and what it waits on; without
  running it, every task whose `## Notes` carries no standing `BLOCKING, from the
  specification —` line is deliverable. A set restated here instead is a set that was true when
  it was printed. The handoff offers the next step and never takes it: filling the one open
  slot and invoking are the human's.

Then stop. `git diff` over the work root is the review, and it belongs to a person.

## Closing the plan

A work root serves one initiative, and the human says when it is over — the ask, with its
why, is the input, and either missing is a stop. Closing spawns no judge and touches neither
the specification root nor the target source root.

- Resolve `work_root/<the initiative's slug>` the same way as above — `project.py` still
  answers only from the file, even here.
- The root must be under git and clean, exactly as before any write — the closure diff is
  its own review. A root already holding `closure.md` is already closed: stop.
- Persist the ask under `intake/`, like any scope.
- Write `closure.md` at the work root: prose, one sentence per line — the why as the human
  gave it, and the intake file it was read from. It is a marker, never a node: the
  validator keeps it the way it keeps `intake/`.
- Run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/plan.py <work-root>` — no specification root,
  because a closed plan validates without one. The derivation is the seal: it still refuses a
  plan whose structure does not hold, and a specification that moved since the tasks were
  written is no obstacle — each task's `implements` now stands as the historical record of
  which nodes the work addressed.
- Report the closure and offer the `/plan-work` invocation that opens the successor
  initiative's new slug under the same work root and project root — the delivered work returns
  as inventory through the survey there, never as a reference into this closed plan. Then stop.

## What you never do

- Write or edit `plan.json` by hand.
- Answer a question with a value the specification does not hold — a fact absent from the
  specification is produced by the analysis that extends it, never by a task.
- Record a status, an estimate, a priority or an execution order — those fields do not exist,
  and prose does not get to hold what the contract refused.
- Run the implement-against step in the context that decomposed — the inline fallback is for a
  session that cannot spawn subagents, is declared in the report, and still applies the
  agent's file.
- Write source code or tests, or change the target tree — the plan is nodes, nothing else.
- Write into the specification root — a broken specification is reported with its fix, never
  repaired from here.
- Restate the contract's vocabularies from memory instead of reading the schema.
- Reopen a standing plan decision outside the impact set, or re-cut an epic as a side effect
  of a change.
- Commit, stash, or otherwise change the consumer's git state — a dirty root is reported, and
  what to do with it is the human's call.
- Write into a work root that holds `closure.md`, or remove a closure — a closed plan is
  history, and reopening it is the human's git act.
