---
name: plan-work
description: Turns a stated development scope plus a validated specification into a development plan — an inventory, epics and tasks recorded as markdown nodes under a work root, each task naming the specification nodes it implements — validates the plan against the specification, and derives plan.json. A fact the specification does not state is decided on the way, blind to the task cut, and disclosed in the decision log. Also takes a corrective increment — one wrong behavior observed in code already delivered, answering to no task's criteria — as a single task on the same route, without the survey or the decomposition. Also closes a plan when the human declares its initiative over, marking the work root as history. Use when a request asks to plan, decompose, or prepare development work over a domain the specification already holds, to route a bug found by running the delivered system, or to close a finished plan. Not for analysing domain material, and not for writing source code or tests.
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
   declared. Where `targets` declares exactly one key and the invocation names none, that key
   is the target: a set of one holds no choice, so it is decided and disclosed in the report,
   never asked.
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
the file's `standard` answers **for the target**: a standard governs one target, so `project.py`
prints either one `standard:` line for a one-target project or one `standard <target>:` line per
target the file declares one for, and the line for the target this invocation names is the
answer — never another target's line. `null` there declares deliberately that the project has
none for this target — the narrow path, chosen rather than forgotten, taken without asking again.
Where neither answers — no naming, no file, the file not declaring the field, or the field
declaring no entry for this target — the standard joins the single stop of absent inputs: name
it, or declare it through `/siegard-config` for this target, and the stop's report carries that
invocation ready to paste. A file that does not hold together is a stop reported verbatim; a
naming that overrode a differing file is reported with both. Below, a standard "named" means
resolved by either step.

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
specification with problems is fixed through the analysis that authors it; planning writes
into the specification root only through step 4's decided-fact route, and repairs nothing
there. There is no derived index of the specification to go stale — `spec.py` validates the
files themselves, every time — so there is nothing here to recheck the way a plan's own
`plan.json` must be.

A task names the specification nodes that govern it by identity, and carries no pin: the
specification does not change during a plan's execution, by convention. A task written today
and implemented next week reads the specification as it stands at read time, not as a frozen
copy — the discipline is procedural, held by not touching the specification while a plan is
live, never by a value this skill computes and compares.

## Before anything: the tree

The review is `git diff` over the work root — and over the specification root, which step 4's
decided-fact route may write. A diff only says what this invocation did when the roots start
clean. Before any write, `git status --porcelain -- <work-root> <specification-root>` must
print nothing. Output is a stop: report what is pending and go no further — committing,
discarding, or overriding is the human's decision, never the plan's. A root not under git
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

Three of these steps are another judge's, and a fourth judge sits inside one of them. The
survey, the decomposition, and each task's specification references are delegated to the
subagents this framework ships, each in a clean context — and inside the implement-against
step, each fact the specification turns out not to state is delegated to its own judge, blind
to the cut that surfaced it. The judgment of each lives in the agent's file — not here, and
not in your memory of it. Delegating means spawning the named subagent — in a plugin install the name may
be plugin-scoped — and reading the agent's file yourself is the fallback, never the
delegation. The binder's isolation is the point of the whole arrangement: it arrives with
no memory of how the tasks were cut, so the specification is read for what it says today, never
to fit a task. Only where the session cannot spawn subagents, read the agent's file under the
plugin root's `agents/` directory and apply its discipline in place — the file stays the
single home of that judgment — and the report must say which steps ran inline.

## The corrective increment

One wrong behavior, observed in code this project already delivered, answering to no criterion any
task holds — because the task that wrote the file was delivered and reviewed before anybody saw
the behavior. Running the system for real is where these arrive, and they arrive after every
ceremony this framework has has already finished.

**The human names this in the invocation. It is never inferred from the tree**, exactly as the
narrow re-delivery in `/implement-task` is never inferred: a mode that decides for itself when to
run fewer steps is a mode that runs fewer steps.

It exists because of what happens without it. The whole path — survey, decomposition, a binder per
task — is sized for a scope, and a one-behavior correction is not a scope; so the correction gets
made by hand instead, and the hand that makes it writes the implementation and the test in one
context. That is precisely the guarantee the two producers exist to give, given up for a fix small
enough to feel like it did not need one — and an implementation and its tests written in one pass
agree by construction, including where both are wrong. The trace goes quiet the same way: nothing
outside `/implement-task` binds, so the file changes and `siegard-trace.json` keeps asserting a
digest that is no longer there. Neither of those is the correction being urgent. Both are the
correct route costing more than the incorrect one.

So the route is the ordinary one, at the size of the work:

```
situate → intake → the task, written here → implement-against → validate → report → stop
```

**The survey and the decomposition do not run.** There is no tree to discover — the human is
holding the file — and there is nothing to decompose: the increment is one task, and where it is
genuinely more than one, this is a scope and the ordinary path is what it gets.

**The binder runs, per task, exactly as it always does.** It is the step whose absence would make
this a second delivery machine instead of a smaller entrance to the one that exists: it is what
decides which specification nodes the correction answers to, and it is what returns a classified
note when the fix contradicts something the specification states or states nothing about — which
is the common shape here, because a behavior nobody specified is how the bug survived review. The
decided-fact route of step 4 runs here too, and settles that silence the same way, so the
correction stands still only on a genuine contradiction. The binder is also the cheapest of the
survey, decomposition and binding delegations, so the ceremony this path drops is the ceremony
that was buying nothing.

You write the task yourself, and it is held to every test a decomposer's task is held to. The
criteria are falsifiable, one condition each, and they are written from the observed behavior and
the node that governs it — never "the bug is fixed", which no test can fail. The task carries
`rationale` where it implements nothing, and `sources` pointing at the scope under `intake/`, the
same as any node here. It declares **no** `produces`: what a task produces is what the project's
own standard presupposes, and a correction to delivered source is not that.

Where it lands follows the rule the slug already states. A live work root takes the task as any
other increment does. A work root holding `closure.md` is closed and takes nothing — the
correction names a new slug, and the delivered code returns as what the specification says about
it, not as a reference into a plan that is history.

What this path does not do is end anywhere different. The task goes to `/implement-task` like
every other task: two producers, the standard applied, the run captured, and the trace bound at
step 8 — which is the whole reason the correction comes back through here rather than being typed
into the file. Say in the report that this was a corrective increment and which steps did not run,
so a reader never mistakes a plan of one task for a scope that decomposed to one.

### 1. Situate

Specification nodes carry no title or summary of their own — only `type`, the declared fields,
and a body under `## Description`. There is no cheap index to read instead of the files; there
is a cheap manifest of what exists, and a grep to narrow before anything is opened.

- **The specification.** Run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/spec.py --digest
  <specification-root>` — every node's identity, sorted, current because the check above
  passed. That is the full manifest; it names nothing about what a node says. Grep the
  specification root for the scope's vocabulary — its nouns and the terms the material uses —
  to find candidate files, then open exactly those. Close the impact set in both directions:
  read what a candidate references in its own frontmatter — every reference-bearing field the
  class schemas declare, read from the plugin root's `schemas/spec/` directory rather than from a
  list here, so a field a schema gains is a field this closure reaches — and grep
  the specification root for each candidate's identity to find what references it back —
  there is no derived edge index to read this from instead. Read the impact-set files and
  nothing else: the plan implements against what governs the scope, not everything the
  specification holds. Keep the trail this closure produced — which candidate's own fields
  were read for a reference outward, and the grep run for each to find a reference back — the
  report in step 6 carries it verbatim. A missing node found only after a binder relit it in
  step 4 is this closure skipped, discovered at the most expensive point to discover it: a
  binder that already ran once pays to run again over the grown set, per task the growth
  touches. The trail is what lets a reviewer tell the closure ran from one that was assumed.
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

**A layout the human supplied goes under `intake/layout/`, apart from the scope.** A mockup, a
rendering, a palette — anything that shows what a screen should look like rather than telling what
the system should do. The separation is a directory rather than a promise because of what reads
each: everything under `intake/` is material this skill's judges read, and only what a task names
in `reference` is read by the one thing that writes source. Two files in one directory, one of
them safe to hand an executor and one of them not, is a distinction nobody can keep by memory.

Every plan node this skill writes — this one and every one after it — carries a body of
exactly two headings, in order: `## What it is`, then `## Notes`. One sentence per line; a
section with nothing to say carries the literal line `None.`

Free prose — a title, a summary, a criterion — meets a colon often enough that a plain scalar
breaks the moment one appears in it. Emit every node's frontmatter with `python3 -c` calling
`yaml.safe_dump` rather than typing it by hand, so a sentence's own colon is never read as a
second mapping key; PyYAML is already a declared dependency of this framework's own tooling.

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

**Where a layout stands under `intake/layout/`, name it in the `reference` of each task that
builds what it shows** — yours to write, on the skeleton, before the next step. It is not the
decomposer's: what a screen should look like shapes no boundary between tasks, and a judge cut to
find those boundaries has no business deciding which mockup a task answers. Name only what the
task actually builds — a reference on every task of the epic is the executor reading a whole
design to write one component — and never point it at the scope. What the contract says of the
field is what makes the split matter: a reference decides form and never fact, so a screen's
statuses, its wording and its refusals still come from the specification, and the binder below is
still what discovers a fact nobody stated.

### 4. Implement against

This is per task and per judge: spawn one `execution-contract-binder` subagent per skeleton —
its judgment lives at `${CLAUDE_PLUGIN_ROOT}/agents/execution-contract-binder.md` — passing
four things: the skeleton as its title, summary, objective and criteria — never its
`rationale`, its dependencies or its body, because an opinion about the reference travels with
them and the clean context is the point — the candidates' file paths, its epic's `covers` less
its `uncovered`, because naming what the epic declared untouched is a contradiction the
validator refuses — the plan-node contract's path — and the decision log's path at the
specification root, the index that says which node a decided fact landed in, so a claim about
one rule replacing another is settled by the entry that records the replacement rather than by
which node reads closest. The binder rereads the candidate files
fresh and returns the task's `implements`; a divergence between the task and the specification
— including a fact the specification does not state at all — comes back as a classified note.

**Spawn them together, not one after another.** No binder reads another's return, none decides
what the next one is given, and each arrives with no memory of how the tasks were cut — that
isolation is the point of the whole arrangement, and it is exactly what makes the set independent.
This is the same independence `/review-change` states of its four passes, and it is the most
expensive judgment in this skill: a plan of ten tasks spawns ten of these, and running them in
sequence spends ten times the waiting for nothing. What they are not independent of is the epic's
claim: where a note below sends a skeleton back to be re-cut, or grows the claim it was judged
against, that skeleton runs through this step again.

A note classed `unstated` is settled here, before any task it touches is written, and it never
reaches a task file. First hold it to the cut: grep the specification root for the fact's
terms — a fact some node outside the candidates already states is a cut problem, not a
silence, and it takes the out-of-candidates answer below: grow the epic's `covers` or move the
task, and re-run this step. What survives is a genuine silence. Deduplicate the survivors by
fact — two skeletons resting on one fact are one decision, never two — then spawn one
`unstated-fact-decider` subagent per fact — its judgment lives at
`${CLAUDE_PLUGIN_ROOT}/agents/unstated-fact-decider.md` — passing four things: the fact
exactly as the note's `fact` carries it, the impact-set file paths under the specification
root plus the decision log's path, the scope's paths under `intake/`, and the specification
schema paths — the files under the plugin root's `schemas/spec/` directory, one per class, the
same seven `/analyse` reads. Never the skeleton, never the note's
own text, never a binder's reasoning: the decider is blind to the cut, and the blindness is
what keeps the specification from being bent to fit tasks already written.

What comes back is written, not judged. On `stated` or `decided`, write the edits verbatim at
the paths they name, append the returned log entry to the decision log where the outcome is
`decided`, then revalidate — `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/spec.py
<specification-root>`, and once it passes, `--project`, because the projections moved with the
nodes — and re-run this step's binder for every skeleton whose candidates include a touched
node: the note is gone, or what remains comes back reclassified. On `contradicted`, the note
was `blocking` wearing the wrong class: it takes the blocking route below, and the report says
the decider refused it and why. A `noticed` line in the return is a watch item for the report,
never a second decision made in passing. Every decided fact is a claim a reviewer can reject —
the log entry is what lets them, the diff over the specification root is where it sits, and
the report repeats it.

Each fact is decided once, and the loop is bounded by that: a fact already settled in this
invocation is never sent to a second decider, and a re-bind that returns an `unstated` note over
a fact this step already decided is a stop, not another round — the specification now states it,
so a binder still calling it silent is a disagreement a person settles. Two rounds that decide
nothing new end the step.

Then compose and write each task: the skeleton, plus `implements` exactly as the binder
returned it — bare identities, no pin. **Composing is transcription, never correction.** A
criterion whose wording must change at this point — a blocking note settled by rewording, a
decomposer's error caught late — changes the skeleton, and a changed skeleton runs through
this step again before it touches disk: a task composed with a criterion no binder read is a
plan whose judge saw a different plan, and a correction can make a neighboring criterion
jointly contradictory in a way only a fresh reading of the whole set finds. A binder's notes are appended to the task body's
`## Notes`, one sentence per line — the diff is the review, and a divergence only the
conversation holds is a divergence the reviewer never sees — and the report repeats them by
task. A note classed `blocking`, `underdetermined` or `remainder` opens with its class,
literally — `BLOCKING, from the specification —`, `UNDERDETERMINED, from the specification —`,
`REMAINDER, from the specification —` — the exact text and not a style. Two of the three are
read by something: `bin/plan.py` refuses a task persisting an `UNSTATED` opening and holds the
blocking and underdetermined openings as constants, and `/implement-task` collects
underdetermined entries by that opening and nothing else marks them. `REMAINDER` is read by no
validator today and is still written exactly, because the three classes are one vocabulary and a
note whose class a reader cannot see by its first words is a note nobody sorts; an underdetermined note carries the implementation the binder named in `passes`, and a
remainder note the destination it named in `belongs`. Where the binder found nothing to
implement against, the task carries `rationale` saying why — scaffolding is real work, but
ungoverned work is a claim someone reviews. Where a note says the task needs what the
candidates do not hold, the cut is wrong: grow the epic's `covers` or move the task, and
re-implement against it — never widen the reference by hand.

A note the binder classed `blocking` — the class its own file defines, and the one where the
specification is not silent but overruled — is settled before the task is written, and the skeleton's `rationale` says by whom. Where the blocked statement was the decomposer's decision
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
judgment, never here. An unstated fact is settled only through step 4's route — decided by the
context that never saw the cut and disclosed in the decision log — never filled in passing to
make a check go green.

### 6. Report, and stop

Report, in this order:

- every node written, by identifier — on a populated root, created, changed and removed
  listed apart;
- the impact set that was read — in the specification and, on evolution, in the plan — plus
  step 1's closure trail: which candidate's own fields were followed outward and the grep run
  for each to find a reference back, so the reviewer can judge not only what the planning
  looked at, but whether the set was closed before the decomposition ran rather than assumed
  closed;
- every fact the decided-fact route wrote into the specification: each `decided` outcome by its
  log entry — the file and the field it filled, what was unstated, the value, the why — and
  each `stated` outcome with where the material already held it. These are the claims a reviewer
  can reject, the diff over the specification root is where they sit, and every `noticed` watch item follows them;
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
  root already resolved above, names per task what has no record and everything it waits on —
  a dependency with no record, an artifact a task produces and the tree does not hold, a standing
  `BLOCKING, from the specification —` note — and then the set itself. Where that set holds more
  than one task, the distributed consumer rules describe delivering them in parallel — one
  worktree per task, integrated by merge — and taking that route is, like everything in this
  handoff, the human's choice. A set restated here instead is a set that was true when it was
  printed. The handoff offers the next step and never takes it: filling the one open slot and
  invoking are the human's — given per invocation, or given once for a whole route through the
  orchestrating entry point the consumer rules name, whose own file bounds what it may fill.

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
  specification is produced by the specification gaining the statement, through step 4's
  decided-fact route or the analysis that authors it, never by a task and never by prose.
- Decide an unstated fact in this context, or hand the decider the skeleton, the note's text or
  a binder's reasoning — the blindness is the route, and a decision made where the cut is
  visible is the specification bent to fit it.
- Record a status, an estimate, a priority or an execution order — those fields do not exist,
  and prose does not get to hold what the contract refused.
- Run the implement-against step in the context that decomposed — the inline fallback is for a
  session that cannot spawn subagents, is declared in the report, and still applies the
  agent's file.
- Write source code or tests, or change the target tree — the plan is nodes, nothing else.
- Write into the specification root beyond what step 4's decided-fact route returned — the
  route writes a decider's edits and its log entry, then revalidates; a specification that is
  otherwise wrong or broken is reported with its fix, never repaired from here.
- Restate the contract's vocabularies from memory instead of reading the schema.
- Reopen a standing plan decision outside the impact set, or re-cut an epic as a side effect
  of a change.
- Commit, stash, or otherwise change the consumer's git state — a dirty root is reported, and
  what to do with it is the human's call.
- Write into a work root that holds `closure.md`, or remove a closure — a closed plan is
  history, and reopening it is the human's git act.
