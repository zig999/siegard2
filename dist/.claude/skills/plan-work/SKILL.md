---
name: plan-work
description: Turns a stated development scope plus a validated specification into a development plan — inventory, epics and tasks as markdown nodes, each task naming the nodes it implements — validates the plan against the specification, and derives plan.json. A fact the specification does not state is decided on the way, blind to the task cut, and disclosed in the decision log. Also takes a corrective increment — one wrong behavior observed in code already delivered, answering to no task's criteria — as a single task, without the survey or the decomposition. Also takes a proof increment — facts a test decides, held by delivered code, proven by none — one task per fact. Also closes a plan whose initiative the human declares over. Use to plan or decompose work over a domain the specification holds, to route a bug found by running the delivered system, to owe a node its test, or to close a finished plan. Not for analysing domain material, and not for writing source code or tests.
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
target source root play no part in closing (see "Closing the plan"). A corrective increment
needs all four and one more the ordinary path never asks for: the file the wrong behavior lives
in (see "The corrective increment"). A proof increment needs all four, with the facts it names as
its scope (see "The proof increment"). A decided-fact increment needs all four and two more: the
fact a delivery stopped over, as its stop quoted it, and the task that delivery was for (see "The
decided-fact increment").

## Before anything: the specification

A planning invocation reads the specification and a closing one does not, so this section and
the next one's second root belong to planning alone: a closure stopped by a specification it
never opens would stop for a reason closing cannot act on.

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
print nothing; a closing invocation names the work root alone, because nothing it does reaches
the other. Output is a stop: report what is pending and go no further — committing,
discarding, or overriding is the human's decision, never the plan's. A root not under git
control is the same stop: without git there is no review.

## Read the contract

`${CLAUDE_PLUGIN_ROOT}/schemas/plan-node.json` is the single home of what a plan node may and
must declare — the kinds, the fields each kind requires, and one example per kind. Every
subagent below needs one or two of its three kinds, never the whole file, and
`python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/plan.py --contract <kind>` prints one self-contained
slice, every `$ref` already inlined.

**Each slice is printed by the step that hands it over, narrowed to what that judge writes** —
`--contract inventory` in step 2, `--contract epic` and `--contract task --without implements`
in step 3, `--contract task --fields implements` in step 4. Two things fall out of narrowing.
A judge stops reading a branch to write one field: the binder's slice is a sixth of the task
branch, and step 4 pastes it once per task. And a field a judge must not fill stops being
offered to it — the skeleton slice carries no `implements`, which is the binder's, and the
binder's carries nothing else. `plan.py` refuses a field name the branch does not declare, so a
typo cannot quietly widen a slice. A mode that skips a step never pays for the slice that step
would have used, and a closing invocation prints none. What a step prints, it hands to its
subagent verbatim, in place of the file's path. Do not work from memory of any of them, and do
not restate them: what you remember is not what the validator will apply.

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
not in your memory of it. Delegating means spawning the subagent by its plugin-scoped name —
`siegard:<agent-name>` — never the bare form, which a consumer's own `.claude/agents/` can shadow —
and reading the agent's file yourself is the fallback, never the
delegation. A spawned delegation runs in the background and the harness delivers a notification
when it answers; the session waits for that notification and nothing else — never a `sleep`, a
scheduled wakeup, an agent listing or a message to the delegation, each of which is a turn spent
reading nothing — and reads the return when the notification names it. The binder's isolation
is the point of the whole arrangement: it arrives with
no memory of how the tasks were cut, so the specification is read for what it says today, never
to fit a task. Only a spawn that was attempted and failed opens the inline route: read the
agent's file under the plugin root's `agents/` directory and apply its discipline in place —
the file stays the single home of that judgment — and the report carries the failure verbatim
beside the step's name. A session judged unable without an attempt is the isolation given up on
a guess, and nothing downstream can tell that apart from the isolation held.

## The corrective increment

One wrong behavior, observed in code this project already delivered, answering to no criterion any
task holds — because the task that wrote the file was delivered and reviewed before anybody saw
the behavior. Running the system for real is where these arrive, and they arrive after every
ceremony this framework has has already finished.

**The human names this in the invocation. It is never inferred from the tree**, exactly as the
narrow re-delivery in `/implement-task` is never inferred: a mode that decides for itself when to
run fewer steps is a mode that runs fewer steps. The invocation names two things: the wrong
behavior, and the file it lives in. Both are the human's — they ran the system and they are
holding the file — and the second is what the epic below is cut from.

It exists because the whole path is sized for a scope, and a one-behavior correction is not one;
priced that way, the correction gets made by hand instead, and two guarantees go with it. One
hand writes the implementation and the test, which then agree by construction including where
both are wrong — the exact thing two producers exist to prevent. And nothing outside
`/implement-task` binds, so the file changes while `siegard-trace.json` keeps asserting a digest
that is no longer there. Neither is the correction being urgent; both are the correct route
costing more than the incorrect one.

So the route is the ordinary one, at the size of the work:

```
situate → intake → the task, written here → implement-against → validate → report → stop
```

**The survey and the decomposition do not run.** `intake` above is step 2's first paragraph and
only it — the scope persists exactly as it always does, and the rest of that step is the survey.
There is no tree to discover — the human is
holding the file — and there is nothing to decompose: the increment is one task, and where it is
genuinely more than one, this is a scope and the ordinary path is what it gets.

**The scope under `intake/` is the human's and nothing else.** The behavior as they described
it, the reproduction, and the file by path. Where a goal's findings policy named the finding in
advance, the invocation carries it from the review's record, and the intake holds three things
from it: the node the finding names, as what the code must do; the file; and the record, by
path — never the finding's account of what the code does. Nothing you read in the source goes there — not the
line the defect lives on, not what the delivered code does around it, not why. The decider of
step 4 reads that directory as the one place a fact may already be stated, and a description of
the code there makes what the code does a stated fact, which is the direction this route exists
to reverse: the specification says what the code must do, and the code is held to it. The
source is read where it is read anyway — by the trace, which says what the file encodes.

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

The one condition a criterion carries is the observed behavior's, stated in the domain's terms.
How a target keeps an answer between surfaces — a client's cache, a marker it compares against,
whether the data was in hand before a surface was mounted or arrived after — is how the target
implements the domain, never a fact the domain states. A criterion conditioned on it rests on a
fact no node can state, so the binder returns the silence, correctly, and every act the criteria
name under that condition is a silence of its own: a set of criteria conditioned that way is
answered one cell at a time, each decision opening the next, and the specification gains rules
about a mechanism it never governed. The reproduction is the test's setup, not the criterion's
condition: the criterion says what the surface presents, and the path that reached it is how the
test gets there. Where a decided node says nothing turns on such a condition, the criterion that
carries it was the silence, and the criterion is what changes. You wrote the skeleton and you
rewrite it: a reworded skeleton runs through the binder again before it touches disk, exactly as
step 4 says of any changed skeleton. That is not the correction composing forbids — that rule
holds the file to what a binder read, never the skeleton to its first draft.

**The correction gets its own epic, never an existing one.** An epic's `covers` is the candidate
set of every task under it, so growing a delivered epic's claim for one correction re-opens every
task that epic already holds; a new epic claims exactly what this correction answers to and
re-judges nothing. What it answers to is the binder's to say, and the file seeds what the binder
reads — the human named the file, and the trace already knows what that file answers to:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --encodes <target-source-root> <file> [<file> ...]
```

A file the trace does not know is a stop, and the report names it: a correction to code no task
ever bound is not a corrective increment, because there is no claim to correct against. Close
what came back the way step 1 closes any impact set; that closed set is the binder's candidate set,
handed as the candidates' file paths exactly as step 4 hands them, and in place of the epic's
`covers` less its `uncovered`, because the epic is not written yet. Write the epic after the
binder returns: its `covers` is the `implements` the binder returned plus any node the human named
for this correction, and nothing else — a node the file encodes and the correction does not touch
is not claimed, so it owes no declaration. `uncovered` holds only a node the epic claims that the
human excluded from this correction, with the human's own why; a why composed to fill the field
says nothing the next reader can act on. The validator refuses an epic claiming a node its task
does not implement and `uncovered` does not declare.

Where it lands follows the rule the slug already states. A live work root takes the task as any
other increment does. A work root holding `closure.md` is closed and takes nothing — the
correction names a new slug, and the delivered code returns as what the specification says about
it, not as a reference into a plan that is history.

What this path does not do is end anywhere different. The task goes to `/implement-task` like
every other task: two producers, the standard applied, the run captured, and the trace bound at step
8 — which is the whole reason the correction comes back through here rather than being typed into
the file. Say in the report that this was a corrective increment and which steps did not run, and
carry the `--encodes` output the binder's candidates were seeded from verbatim, so a reader never
mistakes a plan of one task for a scope that decomposed to one.

## The decided-fact increment

A fact no node states, found by a delivery rather than by planning: `/implement-task`'s
implementer stopped over it, and the stop quoted it. It is the same silence step 4 settles, met
later — «a delivery finding that no node states a fact the work needs» (SPEC-001 R13) — and it
is settled the same way: decided by a context that never saw the task, disclosed in the node's
log, never left standing as a stop for a person whose only move is to trigger the decision.

**The invocation names it, and it is never inferred.** `/implement-task`'s report hands this
invocation beside the `/analyse` one, filled with the fact and the task: two doors, and the
choice between them is the person's — this one decides the fact blind and discloses it; the
other has the person's own material state it. Under a goal the person armed, `/deliver-scope`
takes this one.

```
situate → intake → step 4's settlement of the one fact → re-bind the task → validate → report → stop
```

**The scope under `intake/` is the fact as the stop quoted it, and the task's identity.** Nothing
read in the source goes there, for the reason the corrective increment states: the intake is the
one place the decider looks for a fact already stated, and a description of the code would make
what the code does a stated fact.

**The settlement is step 4's, for this fact alone.** Hold it to the cut — grep the specification
root for its terms; a node that already states it means the task's candidates missed it, and the
answer is the re-bind below, with no decider spawned. Otherwise spawn one
`siegard:unstated-fact-decider` subagent, handed exactly what step 4 hands it: the fact, the
impact set of the nodes the task implements, the intake paths and the specification schema
paths — never the task. Write its return as step 4 writes one. A return of `contradicted` is a
contradiction between the scope and the specification: write nothing, and stop with the node and
its statement quoted, because only a person settles it.

**Then the task is bound again,** by step 4's binder, so its `implements` and its notes see the
specification as it now stands, and the task file is rewritten from that return — a re-bind,
which `/implement-task` then delivers as a re-delivery. The survey and the decomposition do not
run: the task exists.

## The proof increment

One or more facts a finite test decides, held by code already delivered and proven by no test — a
certification the coverage auditor refused with `remainder: testable`, naming the assertion that
would close it. «A finite test is preferred to a reading, and to a registry step's decision,
wherever one exists» (SPEC-004 R10): a node left decided by a reading or a step where a test could
decide it is owed that test, and the implementation holding the fact may have been delivered long
before anyone could write it — by another task, in a plan already closed, or bound by a
reconciliation no task ever planned. This is the route that owes it a task.

**The human names this in the invocation, exactly as the corrective increment is named.** For each
fact the invocation names four things, all the human's: the node, by identity; the assertion,
verbatim, as the record's `remainder_why` states it; the record that stated it, by path under
`siegard-reconcile/`; and the file or files the node is bound to where its fact is held. `trace.py
--owed` prints the first three and the files beside every node it lists, and its closing line hands
this invocation ready to fill. Which facts are worth a test is the human's: this route takes the
ones named and proposes none.

Two stops, each reported with what answered it. Every named file must be one the trace binds the
node to:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --encodes <target-source-root> <file> [<file> ...]
```

A node the output does not list for a named file is a fact that does not stand there, and a proof
task over it would certify ground nothing claims — the route is `/reconcile` over that file, which
reads the node against it. And the record must carry the node with `remainder: testable`: an
`untestable` remainder is one no finite test closes, and a task over it would write the partial
test R12 forbids.

**The survey and the decomposition do not run**, and neither does anything that reads source: the
implementation stands, the trace says where, and what the task owes is stated in the assertion.
`intake/` holds the invocation and nothing else — per fact the node, the assertion verbatim, the
record's path and the files — because the decider of step 4 reads that directory as the one place a
fact may already be stated, and the assertion is a test's condition over a fact the node already
holds, never a new one. A decider return whose edit writes into a node a fact it found only in
an assertion under `intake/` is therefore not written: the task stays out of the plan, and the
report hands two doors — `/analyse` over the node, with the assertion as its material, or the
return written as it stands — and recommends the first, as «A recommendation names the door, the
criterion, the deciding fact and the reversing fact» (SPEC-006 R2) states: the criterion is
`rule violated`, the deciding fact the return's edit quoted beside the `intake/` path it cites,
and the reversing fact a node that already held the fact before this invocation — said to the
person as the reason in plain words, the name kept for the orchestration log.

**One task per fact, under one epic of their own.** The binder runs per task exactly as step 4 runs
it, handed as its candidate set the node **and every node that names it** — read, never
recalled, from:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/spec.py --impact <node> <specification-root>
```

A contract or a rule that answers the same case is where an assertion contradicts the
specification, and a binder handed the one node alone cannot see it: it confirms that the node
governs the criterion as the assertion states it, or it returns the note that says why not, and
every note routes the way step 4 routes it. A `BLOCKING, from the specification —` note here is
the standing stop for that fact: the assertion the auditor wrote contradicts a node, and that is
settled by a person before any test is written, never by the test going red. A binder that
returns no `implements` for the node is a stop for that fact alone, reported with the binder's
own reason — an assertion the node does not govern is not a proof of it. The task you write
carries:

- `implements`: the node, and nothing else;
- one criterion: the assertion, verbatim — it is falsifiable because an auditor wrote it as the
  one thing a test must fail over;
- `stands`: the files, exactly as the invocation named them and `--encodes` confirmed them;
- `sources`: the scope under `intake/`;
- no `produces` — a proof task builds no substrate, and the schema refuses the two together.

The epic's `covers` is the tasks' nodes. The landing follows the slug's rule, exactly as the
corrective increment's does: a closed work root takes nothing, so these facts name a new slug.

The tasks go to `/implement-task` like every other task, which reads `stands` and writes the proof
alone; the review that reads that proof is what certifies each node. Say in the report that this
was a proof increment, which steps did not run, and carry the `--encodes` and `--impact` outputs
verbatim.

### 1. Situate

Specification nodes carry no title or summary of their own — only `type`, the declared fields,
and a body under `## Description`. There is no cheap index to read instead of the files; there
is a cheap manifest of what exists, and a grep to narrow before anything is opened.

- **The specification.** Run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/spec.py --digest
  <specification-root>` — every node's identity, sorted, current because the check above
  passed. That is the full manifest; it names nothing about what a node says. Grep the
  specification root for the scope's vocabulary — its nouns and the terms the material uses —
  to find candidate files. **Every `constraints/` node is a candidate, whatever the grep
  returned.** An architecture constraint declares no reference and no class declares one at it,
  and its `scope` is the system or a whole context rather than anything a scope's nouns would
  name — so it reaches no grep and no closure, and it is precisely the thing that governs work
  nobody thought to bind to it. `spec.py --digest` lists them; there are few, and naming them all
  costs less than the one that arrives as a binder's note after the epic is cut.

  Beside the manifest, one reading narrows where a scope is open-ended rather than named:

  ```
  python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/plan.py --unplanned <work-root> <specification-root>
  ```

  over the directory the initiatives sit in — not one of them — which lists, by class, every node
  no initiative has ever named. It answers what no single plan can: closure inside a plan is
  total, so a node left out of every plan is invisible to each of them. A rule or a contract in
  that list is worth a look before the cut is fixed; an element in it usually is not, which is
  why the listing is by class. It is a query and decides nothing — a specification describes more
  than the work has reached, and a node nothing planned is an ordinary state, never a task this
  skill owes.

  **Naming the candidates is yours; closing over them is not.** Run

  ```
  python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/spec.py --impact <identity>[,<identity>...] <specification-root>
  ```

  over every candidate at once — it prints, per node, every reference it declares, every node
  that declares one at it, and every entry of the decision log beside it, plus the read set as
  paths with each node's own `<slug>.log.md` after it where one exists. One hop, both
  directions, read off the same walk that validated the specification above,
  so a field a schema gains is a field this closure reaches without anybody maintaining a list of
  which fields those are. Do not close a second hop by hand: the transitive closure of a
  connected specification is the specification, and the impact set is what governs the scope, not
  everything the specification holds. Read the files it names and nothing else.

  Two halves of this step, and only one of them is now mechanical. The command's output goes to
  the report in step 6 verbatim, and it settles that the closure ran. It settles nothing about
  the candidates: those came from a grep of the scope's vocabulary, which is judgment, so the
  report carries the terms that were grepped beside the output. A missing node found only after a
  binder relit it in step 4 is now almost always a candidate nobody nominated rather than a
  closure nobody ran — and it is still discovered at the most expensive point, a binder that
  already ran paying to run again per task the growth touches.
- **The plan, when the work root is populated.** Trust its index only after checking it: run
  `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/plan.py --check <work-root> <specification-root>`, and
  a `STALE` `plan.json` is rederived by a full validation run before anything relies on it. A
  `MOVED` line is never cleared by a derivation: the task it names joins the impact set and goes
  through step 4's binder, which reads the node as it stands. The anchor guards delivery, not
  derivation.
  Read `plan.json`, and only it: locate the epics and tasks the scope touches, and close the
  impact set over its edges — dependencies in both directions, and `implements` references
  that reach the specification's impact set. Read those files alone. Outside the set, standing
  decisions stand: a task this change does not touch is not reworded, however improvable it
  looks.
- **The project's standard, when one was named.** Run

  ```
  python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --standard <the registry> --against <target-source-root> --specification <specification-root>
  ```

  A registry that does not hold together is a stop, reported verbatim: fixing it belongs to
  whoever owns it — and a step deciding a constraint the specification does not hold is that
  stop, not a form problem of this plan's. An artifact it presupposes and the tree does not hold
  is **not** a stop — it is this bullet's whole product. Keep what the command printed for each:
  the path, what the registry says that artifact provides, and the rules it named as unanswerable
  while the artifact is absent. That set goes to the decomposition, and it is gathered here,
  before any node is written, because it decides whether this plan holds one more task than the
  scope asked for. Keep too what it printed against the specification: which constraints a step
  decides, and which no step decides — the latter are held by reading alone, and the report
  names them beside the tasks that implement them.

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

Then spawn a `siegard:codebase-surveyor` subagent — its judgment lives at
`${CLAUDE_PLUGIN_ROOT}/agents/codebase-surveyor.md` — passing three things: the target source
root, the scope's path under `intake/`, and the `inventory` slice — print it here, with
`plan.py --contract inventory`, and paste it whole. It returns
inventory nodes — modules, evidenced conventions, reuse points, consumer-named risks, and
the empty tree as a full answer where that is what it found. Write each returned node at the
path its identifier computes to, verbatim.

### 3. Decompose

Spawn a `siegard:backlog-decomposer` subagent — its judgment lives at
`${CLAUDE_PLUGIN_ROOT}/agents/backlog-decomposer.md` — passing four things: the scope's path,
the impact set's file paths under the specification root, the surveyor's inventory, and the
contract slices — print them here, `--contract epic` and `--contract task --without
implements`, and paste both whole — plus, where a standard was named and the situate step found
any, the artifacts it presupposes that the tree does not hold, each with what the registry says
it
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

This is per task and per judge: spawn one `siegard:execution-contract-binder` subagent per skeleton —
its judgment lives at `${CLAUDE_PLUGIN_ROOT}/agents/execution-contract-binder.md` — passing
four things: the skeleton as its title, summary, objective and criteria — never its
`rationale`, its dependencies or its body, because an opinion about the reference travels with
them and the clean context is the point — the candidates' file paths, its epic's `covers` less
its `uncovered`, because naming what the epic declared untouched is a contradiction the
validator refuses — the binding slice, `plan.py --contract task --fields implements`, printed
once and pasted whole into every spawn: it carries the one field a binder writes, and the
branch around it is what the decomposer and you write — and the decision
log's path at the
specification root, the index that says which node a decided fact landed in, so a claim about
one rule replacing another is settled by the entry that records the replacement rather than by
which node reads closest. The binder rereads the candidate files
fresh and returns the task's `implements`; a divergence between the task and the specification
— including a fact the specification does not state at all — comes back as a classified note,
and a criterion that states two conditions comes back as a `compound` note about the skeleton's
own form, asked before anything about the specification is asked of that criterion.

**Spawn them together, not one after another.** No binder reads another's return, none decides
what the next one is given, and each arrives with no memory of how the tasks were cut — that
isolation is the point of the whole arrangement, and it is exactly what makes the set independent.
This is the same independence `/review-change` states of its four passes, and it is the most
expensive judgment in this skill: a plan of ten tasks spawns ten of these, and running them in
sequence spends ten times the waiting for nothing. What they are not independent of is the epic's
claim: where a note below sends a skeleton back to be re-cut, that skeleton runs through this step
again — and where it grows the claim, **every skeleton under that epic does**. The candidate set
is the epic's and not the task's, so a binder that judged against the smaller set never saw what
the growth added, and a governing node invisible to one binder is exactly the miss step 1 pays to
prevent.

A note classed `unstated` is settled here, before any task it touches is written, and it never
reaches a task file. First hold it to the cut: grep the specification root for the fact's
terms — a fact some node outside the candidates already states is a cut problem, not a
silence, and it takes the out-of-candidates answer below: grow the epic's `covers` or move the
task, and re-run this step. What survives is a genuine silence. Deduplicate the survivors by
fact — two skeletons resting on one fact are one decision, never two — then spawn one
`siegard:unstated-fact-decider` subagent per fact — its judgment lives at
`${CLAUDE_PLUGIN_ROOT}/agents/unstated-fact-decider.md` — passing four things: the fact
exactly as the note's `fact` carries it, the impact-set file paths under the specification
root plus the decision log beside each of them where one exists (`<slug>.log.md`), the scope's
paths under `intake/`, and the specification
schema paths — the files under the plugin root's `schemas/spec/` directory, one per class, the
same seven `/analyse` reads. Never the skeleton, never the note's
own text, never a binder's reasoning: the decider is blind to the cut, and the blindness is
what keeps the specification from being bent to fit tasks already written.

What comes back is written, not judged, and read from where the delegation answered: its
transcript, or a return saved from it — never the text of the notification that relays it, which
renders the reply rather than holding it. On `stated` or `decided`, write the edits verbatim at
the paths they name, then append the returned log entry where the return carries one — every
`decided`, and a `stated` whose fact was read under `intake/`, recorded as read so the
specification root keeps the provenance of a node whose material lives in a work root —
through the writer and never by hand: `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/spec.py --decide
<the return's log.node> <specification-root>` with the rest of `log` as one JSON object on
stdin; it appends to the log beside that node and validates the root, and its first line is
what the report quotes. Once the root passes, `--project`, because the projections moved with
the nodes — and re-run this step's binder for every skeleton whose candidates include a touched
node: the note is gone, or what remains comes back reclassified. Where the edits landed in a
node no skeleton's candidates hold — the decider reads the whole impact set, and an epic claims
a slice of it — the fact is now stated and the candidate set that lacks it is the cut, not a
silence: grow the epic's `covers` to that node, or move the task, and re-run this step, exactly
as an out-of-candidates note is answered. On `contradicted`, the note
was `blocking` wearing the wrong class: it takes the blocking route below, and the report says
the decider refused it and why. A `noticed` line in the return is a watch item for the report,
never a second decision made in passing. Every decided fact is a claim a reviewer can reject —
the log entry is what lets them, the diff over the specification root is where it sits, and
the report repeats it.

Each fact is decided once, and the loop is bounded by that: a fact already settled in this
invocation is never sent to a second decider, and a re-bind that returns an `unstated` note over
a fact this step already decided is a stop, not another round — the specification now states it,
so a binder still calling it silent is a disagreement a person settles. That stop holds where the
node the decision filled already sits inside the candidates that returned the note; where it does
not, the answer is the growth above, and there is no disagreement to settle.

A binder classifies every divergence in one return, so a re-bind over an unchanged skeleton that
returns an `unstated` note over a fact this invocation has not seen is examined before anything
is spawned for it. First the tally: `git status --porcelain -- <specification-root>` lists
exactly what this invocation has written to the specification, because the root was clean before
the first write — print it, and say which re-bind of which skeleton this is. Then the fact
against the criteria: where it rests on a condition a criterion carries, and a node this
invocation wrote states that nothing turns on that condition, the silence is the skeleton's —
the criterion draws a distinction the domain does not make, and every act the criteria name
under that distinction is one more silence of the same kind. The criterion is reworded without
the condition and the skeleton re-runs this step; no decider is spawned for the fact. Otherwise
the fact is decided as above, and the report carries the sequence. Neither the count of re-binds
nor the count of facts is a stop on its own: the tally is what lets a reader see a skeleton being
answered one cell at a time while it happens, and the rewording is what ends it.

The decider is spawned, never offered: a fact a binder returns as unstated is not a question for
the person — not because the specification root is shared, and not because the person set the
area's route earlier. A node the person excluded from this scope is `uncovered` on the epic with
their why, and a fact that is not excluded is decided — «never left standing as a stop for a
person whose only move is to trigger the decision» (SPEC-001 R13). The disclosure is the log
entry and the report, after the write; a person who disagrees reverts the entry as an ordinary
change.

Then compose and write each task: the skeleton, plus `implements` exactly as the binder
returned it — bare identities, no pin. **Composing is transcription, never correction.** A
criterion whose wording must change at this point — a blocking note settled by rewording, a
decomposer's error caught late — changes the skeleton, and a changed skeleton runs through
this step again before it touches disk: a task composed with a criterion no binder read is a
plan whose judge saw a different plan, and a correction can make a neighboring criterion
jointly contradictory in a way only a fresh reading of the whole set finds.

A binder's notes are appended to the task body's `## Notes`, one sentence per line — the diff is
the review, and a divergence only the conversation holds is a divergence the reviewer never sees
— and the report repeats them by task. What each class means is the binder's file, decided there
and not reopened here; what it does here is this:

| class | the note opens | what it does to the task | what travels with it |
|---|---|---|---|
| `compound` | never written to a task | sends the skeleton back to the decomposer to be re-cut, once | the criterion and the conditions the binder named |
| `blocking` | `BLOCKING, from the specification —` | stops it being written until settled | the note, where the scope is what it blocks |
| `underdetermined` | `UNDERDETERMINED, from the specification —` | nothing; it re-cuts nothing | the note, and the implementation named in `passes` |
| `remainder` | `REMAINDER, from the specification —` | nothing; it re-cuts nothing | the note, and the destination named in `belongs` |
| `advisory` | `ADVISORY, from the specification —` | nothing | the note |

Every opening is exact text and not a style. Two of the four are read by something: `bin/plan.py`
holds the blocking and underdetermined openings as constants and refuses a task persisting an
`UNSTATED` one, `/implement-task` collects underdetermined entries by that opening and hands them
to whoever writes the tests, and `/siegard-telemetry` counts both. `REMAINDER` and `ADVISORY` are
read by no validator today and are still written exactly, because the four persisted classes
are one vocabulary and a note whose class a reader cannot see by its first words is a note
nobody sorts.

A `compound` note is never persisted, because it is answered before the task exists as a file.
The skeleton goes back to the decomposer with the note — the criterion verbatim and the
conditions the binder read in it — to be re-cut into criteria of one condition each, or into two
skeletons where the conditions are two outcomes; then it runs through this step again, and the
notes the binder returns on the re-cut criteria are the ones that land. Once: a `compound` note
returned over a skeleton this invocation already re-cut is written into the report with both
readings, and the skeleton proceeds as the decomposer last left it — this skill rewrites no
criterion itself, because the decomposer is the author of criteria and a criterion this skill
reworded would be one no judge cut. The decomposer already states the rule the note enforces;
the note exists because a rule a prompt states and nothing reads is a rule that is measured to
be skipped, and a compound criterion that reaches a delivery is read back later, by the coverage
audit, as a criterion only half proven.

Settling a blocking note takes one of two routes, and the skeleton's `rationale` says which.
Where the blocked statement was the decomposer's decision — the skeleton carries `rationale` over
that cut — the skeleton goes back to the decomposer with the note, is re-cut, and re-run through
this step. Where it came from the scope, the task is written with the note, and the report names
it as a conflict only the human settles: through the scope, or through the analysis that extends
the specification. A remainder's clause is answered where it belongs — another task's reference,
the epic's `uncovered`, or scope this plan does not yet hold — and no validator walks clauses, so
the report is where a reviewer checks that something answers it. The class itself is never yours
to overrule: a blocking note you disagree with is still settled as blocking, and the disagreement
goes in the report.

Where the binder found nothing to implement against, the task carries `rationale` saying why —
scaffolding is real work, but ungoverned work is a claim someone reviews. Where a note says the
task needs what the candidates do not hold, the cut is wrong: grow the epic's `covers` or move
the task, and re-implement against it — never widen the reference by hand.

A note of any class that names specification nodes outside the epic's covers never travels alone.
Two of the caller's three decisions erase the condition rather than record it: grow the claim and
re-run this step, or move the task and re-run it — the replacement reference answers inside the
new covers. The third persists, and is recorded on its own line immediately after the note in
`## Notes`: `Decision, beyond the covers — stand: <why>` — the exact opening and not a style,
because the validator refuses a task whose `## Notes` names a specification node outside its
epic's covers with no such line naming that node, and a refused plan derives no plan.json.

**A skeleton carrying `stands` is held to the trace before it is written**, once the binder has
returned its `implements` — «every file it names is bound in the trace, before the task is
written, to every node the task implements» (SPEC-004 R18):

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --encodes <target-source-root> <each file stands names>
```

A file the command cannot read — a path spelled from the repository rather than from the target
source root among them — or a node the task implements that the output does not list for those
files, sends the skeleton back to the decomposer once, with the output verbatim: where a task of
this plan writes the source that holds the fact, the proof becomes a criterion of that task, and
the skeleton goes; where the source already holds it and the trace does not bind it, no task is
cut for it — «The plan reports the reconciliation that would bind it, over the files that hold
it, and the proof waits for that binding.» (SPEC-004 R19) — and the report hands `/reconcile`
over those files as the person's door. A skeleton that comes back carrying the same unconfirmed
`stands` is not written; the report names it with the output. A task is refused at delivery for
exactly this, after the plan was committed, and a goal over the plan ends there.

Each task file is checked on its own as soon as it is composed — a composition error is
caught at the file that made it, never discovered at the end:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/plan.py --node <file> <work-root>
```

### 5. Validate, and derive the plan

When every node is written, run `plan.py --check <work-root> <specification-root>` once more: a
fact decided in step 4 writes into the specification, and a node it moved moves every task that
implements it. Each `MOVED` task not yet bound in this invocation goes through step 4's binder
first. Then run the derivation, which refreshes the anchors:

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
context that never saw the cut and disclosed in the node's decision log — never filled in
passing to make a check go green.

### 6. Report, and stop

Open as «A handoff opens with what needs the person, and explains after» (SPEC-006 R1)
states; what follows is the report that opening sits above.

Report, in this order:

- every node written, by identifier — on a populated root, created, changed and removed
  listed apart;
- the impact set that was read — in the specification and, on evolution, in the plan — as step
  1's `--impact` output verbatim, beside the vocabulary that was grepped to nominate the
  candidates it closed over. The output says the closure ran; the terms are what a reviewer
  argues with, because a set closed perfectly around the wrong candidates is still the wrong
  set, and nothing mechanical says otherwise;
- every fact the decided-fact route wrote into the specification: each `decided` outcome by its
  log entry — the node and the field it filled, what was unstated, the value, the why, as the
  writer's first line names it — and
  each `stated` outcome with where the material already held it and, where that was under
  `intake/`, its log entry recorded as read, in the order they surfaced,
  each with the skeleton and the re-bind that surfaced it, so a chain of facts under one skeleton
  reads as a chain; a criterion reworded on the way is named with the wording it lost. These are
  the claims a reviewer can reject, the diff over the specification root is where they sit, and
  every `noticed` watch item follows them;
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
  anything it delivers, and that is the honestly narrow answer rather than silence. Where one
  resolved, name too the constraints this plan's tasks implement that no step of it decides:
  those are held by reading alone, and a green suite settles nothing about them;
- which steps, if any, ran inline instead of in a subagent, each with the spawn failure that
  authorized it, verbatim;
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
  than one task, `bin/deliver.py --help` describes delivering them in parallel — one worktree
  per task, integrated by merge — and taking that route is, like everything in this
  handoff, the human's choice. A set restated here instead is a set that was true when it was
  printed. The handoff offers the next step and never takes it: filling the one open slot and
  invoking are the human's — given per invocation, or given once for a whole route through the
  orchestrating entry point, `/deliver-scope`, whose own file bounds what it may fill.

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
- Read what this closure leaves standing, from disk, before the marker is written — three
  commands, their output quoted whole in the report:

  ```
  python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --findings <delivery-root>/<slug>/review/<the newest review>.md
  python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --owed <target-source-root> --plan <work-root>
  python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/plan.py --notes <work-root>
  ```

  The newest review is the last name `ls` lists under `review/`; where the delivery root holds
  none, say "no review". None of the three is a stop, and none is a judgment: closing is the
  human's act, and these are the counts it closes over — findings nobody routed, nodes still
  owed a test, notes still standing — so that "complete" is a word read beside them rather than
  said instead of them.
- Write `closure.md` at the work root: prose, one sentence per line — the why as the human
  gave it, and the intake file it was read from. It is a marker, never a node: the
  validator keeps it the way it keeps `intake/`.
- Run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/plan.py <work-root>` — no specification root,
  because a closed plan validates without one. The derivation is the seal: it still refuses a
  plan whose structure does not hold, and a specification that moved since the tasks were
  written is no obstacle — each task's `implements` now stands as the historical record of
  which nodes the work addressed. Without a specification root the derivation drops each
  `implements` edge's anchor, and the closure diff shows it.
- Report the closure, opened as «A handoff opens with what needs the person» (SPEC-006 R1)
  states; right after the opening, **what this closure leaves standing** — the three counts
  above, each with the command that printed it, never a verdict on whether the work was
  complete — and then offer the `/plan-work` invocation that opens the successor
  initiative's new slug under the same work root and project root — the delivered work returns
  as inventory through the survey there, never as a reference into this closed plan. Then stop.

## What you never do

- Record a status, an estimate, a priority or an execution order — those fields do not exist,
  and prose does not get to hold what the contract refused.
- Commit, stash, or otherwise change the consumer's git state — a dirty root is reported, and
  what to do with it is the human's call.
- Remove a closure — a closed plan is history, and reopening it is the human's git act.
