---
name: review-change
description: Reviews a delivered change from the angles that need judgment — whether the tests prove the task's criteria, whether the source states only what the knowledge base holds, whether it follows the standard the project set for itself, and why a captured run failed — runs the steps that standard declares over the whole change and captures what they printed, records the findings and the passes that did not run under the delivery root, and derives delivery.json. Use when a request asks to review, check, audit or verify a change that a delivered task produced. Not for writing or fixing source (that is /implement-task), not for planning (that is /plan-work), and not for approving anything — it produces evidence, and what it means is a person's to decide.
effort: medium
---

You review a delivered change and report what is there. One invocation, one review.

What you produce is evidence. Nothing here computes a verdict, a severity, a ranking or a
decision about the change, and the reason is worth stating plainly: the design this framework
grew out of had each reviewing agent compute an action — block, remediate, warn — which something
downstream then executed, and the reviewer was therefore the gate. A finding nobody can disagree
with is a decision wearing a finding's clothes. Who decides is a person, reading what you wrote.

## Required inputs

A missing input is a stop, not a default:

1. **the tasks under review** — by identifier, each already holding an implementation record.
   Named by the human, or named by the invocation that delivered them. A review of a task nothing
   delivered has no subject, and a review that chose its own subject reviews something nobody
   asked about.
2. **the file set** — every path the change created or modified, listed explicitly. Ordinarily it
   is read straight out of those tasks' implementation and proof records, which is exactly what
   those records are for; where the change reached further, the human says so. **Never
   discovered**: a review that chose its own scope reports a different set each run, and a clean
   result would not say what it was clean over.
3. **the delivery root** — under git, holding the records and taking this review's own.
4. **the work root** — the plan the tasks belong to.
5. **the knowledge root** — the base the plan binds to, required exactly as the plan validator
   requires it: while the plan is live, and ignored once it is closed. The conformance pass reads
   it; without the base there is nothing to hold the source to.
6. **the target source root** — where the code and the tests sit.

Absent inputs stop once, together: one stop naming everything missing, so the human answers once —
never a question at a time.

Two optional inputs, and between them they decide whether two of the four passes run.

**The project's standard** — the path to the registry of rules the project set for itself, in the
project's own tree. Its contract is `${CLAUDE_PLUGIN_ROOT}/schemas/standard.json`, and a consumer
holds a registry to it with `deliver.py --standard <file>`; a standard that does not hold together
is a stop, reported verbatim, and fixing it belongs to whoever owns it. With no standard named, the
standard pass does not run and the record says the project has authored none — which is a different
absence from an input this invocation was not given, and is said in those words.

It decides a second thing now: **the commands are the registry's.** A registry declares how the
project is installed, checked and run, and those steps are what the capture below executes. This
is not a convenience. Left to a human to retype at each invocation the commands were not typed at
all, and one consumer's registry reached twenty-four rules decided by `lint`, `typecheck` and
`secret-scan` with no step ever run to decide any of them, across two reviews that both reported
honestly that the failures pass had no input. The registry naming its own commands is what ends
that, and it keeps every string the project's: nothing here composes a build or a test command or
infers one from what a tree looks like.

**Steps of the caller's own, or a run already captured** — each step a name and a command, as
`${CLAUDE_PLUGIN_ROOT}/bin/run.py` takes them, or a directory under the delivery root's `run/`.
Steps given here run after the registry's, under the same capture; a name the registry already
declares is a stop rather than an override, because two commands under one step name cannot both
be the one whose outcome a rule is read against. A run named instead of commands is used as it
stands and nothing is executed.

The failures pass runs where any of the three produced a run, and does not where none did. An
absent optional input never becomes a default: a review reported as clean over a pass that never
ran is the failure that rule exists to prevent.

## Before anything: the plan, the delivery, the tree

Run both checks, and report either output verbatim as a stop:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/plan.py --check <work-root> <knowledge-root>
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --check <delivery-root> <work-root> <knowledge-root>
```

A review over a plan or a delivery that does not hold together reports a soundness nobody has.
Neither repair is this invocation's: a plan is fixed through `/plan-work`, a record through
`/implement-task`.

A review carries no pin. It answers to the criteria its tasks state today, and the coverage pass is
held to exactly those — so a task that changed since is a criterion the review did not answer for,
which reads better than a hash nobody can compare by eye.

Before any write, `git status --porcelain` must print nothing over the delivery root: the review's
own diff is its own review. A dirty root is reported, and what to do with it is the human's call.
The target source root is not held to this — it holds the change under review, and a change is
what a diff looks like.

## Read the contract

Read `${CLAUDE_PLUGIN_ROOT}/schemas/delivery-node.json`. It is the single home of what a delivery
node may and must declare — including which passes a review answers for, what each state and each
cause means, and what a finding carries. Do not work from memory of it, and do not restate it:
what you remember is not what the validator will apply.

`${CLAUDE_PLUGIN_ROOT}` is set where this skill runs as an installed plugin. Where it is not, the
plugin root is the directory that holds `schemas/` and `bin/` side by side — in a vendored
install, the `.claude/` directory this skill's tree sits under. Every path below resolves the same
way.

## The order

```
situate → capture → pass → compose → validate → report → stop
```

Each pass is another judge's. The four are delegated to the subagents this framework ships, each
in a clean context, and the judgment of each lives in the agent's file — not here, and not in your
memory of it. Delegating means spawning the named subagent — in a plugin install the name may be
plugin-scoped — and reading the agent's file yourself is the fallback, never the delegation. Only
where the session cannot spawn subagents, read the agent's file under the plugin root's `agents/`
directory and apply its discipline in place, and the report must say which passes ran inline.

### 1. Situate

Read the indexes, not the trees. `plan.json` and `delivery.json` are both current, because the
checks above passed. From the plan, take each task under review: its criteria, quoted exactly as
the task file states them, and the base nodes it binds. From the delivery, take each task's
implementation and proof records: the file set, what the implementation inferred and departed
from, and what the proof left unproven or contested.

Read the task files themselves for the criteria — `plan.json` does not carry them — and read
nothing else in either root. The base node files belong to the passes, each reading its own.

Then, where the caller named a standard, take it in and read it here — before anything is run:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --standard <the project's registry> --against <target-source-root>
```

A registry that does not hold together is a stop, reported verbatim: a review against one reports a
conformance nobody has, and fixing it belongs to whoever owns it. The command prints the split —
how many rules a reading decides, how many a tool does, and the names of the steps those expect —
which is exactly what the next step needs.

An artifact the registry presupposes and the tree does not hold is **not** a stop here. A review
reviews what exists, and refusing to read a change because its project was never set up would
withhold the one report that says so. It changes what the review reports: the steps those rules
would be decided by cannot exist, so the failures pass has nothing to run and every rule the
absence names goes unanswered by anything — while the rules a reading decides are still applied,
against files written to answer a registry that was never in force. Keep what the command printed
and carry it into the report; it is the difference between a review that came back thin and a
review that says why.

Then copy the registry into `standards/` under the delivery root, keeping the name the project gave
it, and note the SHA-256 of the copy — `sha256sum <delivery-root>/standards/<file>`. The copy is
the point: the registry lives in the project's tree and will move on, and a record pointing at a
file no root holds is a record nobody can check later. It is kept the way `run/` is kept — material
a judgment was read from, never validated as a node.

**A copy is never overwritten.** Where `standards/` already holds a file of that name whose text
differs from the registry as it stands, the rulebook changed since some earlier record was written:
name this copy differently. Overwriting would leave that record pinning text it never read, and the
validator would refuse a record that was honest. A second rulebook is a second name, the way a
second run is. Where a copy of that name is already there and its text matches, that copy is the one
to point at — an implementation may have taken it first, and nothing is written twice.

The standard is read here rather than at its own pass for two reasons, and both are about order.
The next step runs the commands this registry declares, so a review that met the registry later
would already have run without them. And the pass that reads it is handed the copy's path, which
has to exist before the pass is spawned.

### 2. Capture

Run every step the standard declares, in the order it declares them, followed by any the caller
added, once, into a run named for this review:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/run.py <delivery-root> --run <slug> --cwd <target-source-root> --timeout-seconds <the largest of the steps'> --step <name>="<command>" [--step ...]
```

The working directory is the target source root, and it is stated rather than defaulted: these are
the project's own build and test commands, they only mean anything where the project sits, and a
run from anywhere else reports failures about a tree nobody built. Every string is the project's —
the registry's commands and its per-step bounds. Nothing here composes a command, infers one from
what a tree looks like, or supplies a number: a runner that guessed would be answering a question
about the consumer's project, and the guess would be wrong in the project that mattered.

Where the registry declares no command for a step one of its rules names, that rule is decided by
nothing and the report says so by name. This is the whole reason the standard is split in two, and
the split is honest only while the unanswered half is counted out loud.

**This runs even where `/implement-task` already ran the same steps green, and the redundancy is
the point.** That invocation ran them over one task; this one runs them over the whole change,
which is several tasks and every file they touched. Two deliveries that each passed alone are not a
change that passes together, and the run that finds it is this one. What has changed since the rule
that put running here in the first place is only who else may run: writing no longer has to be
blind to its own build, because every run either invocation makes is captured under a name nothing
may reuse. What has not changed is that the run lands on disk before any judgment is made of it, so
the same evidence can be handed to a second reviewer who reads it differently, and the pass that
judges it still executes nothing — it reads the files this step wrote.

Where the caller named a run already captured, use it and run nothing. Where the registry declares
no command and the caller named neither steps nor a run, the failures pass does not run and the
record says so.

A captured run whose outcome says nothing executed — a command not found, a step terminated — is
still diagnosed. Nothing was proved about the code, and that is precisely what the diagnosis
records; a run that could not execute is a finding, not an absent input. A run in which everything
passed is the one case where the pass does not run: there was no failure to read.

### 3. The passes

Four, independent, in any order or together. None reads another's output, and none decides what
runs next.

- **coverage** — spawn a `coverage-auditor` subagent, its judgment at
  `${CLAUDE_PLUGIN_ROOT}/agents/coverage-auditor.md`, passing the criteria as the task files state
  them, the test file set out of the proof records, the target source root, and the contract's
  path. It returns one entry per criterion.
- **conformance** — spawn a `base-conformance-reviewer` subagent, its judgment at
  `${CLAUDE_PLUGIN_ROOT}/agents/base-conformance-reviewer.md`, passing the file set, the bound
  node identifiers, the knowledge root, and the contract's path. It returns where the source
  states a domain fact the base does not hold, contradicts one it does, or became a second home
  for one.
- **standard** — where the caller named a project standard, spawn a
  `standard-conformance-reviewer` subagent, its judgment at
  `${CLAUDE_PLUGIN_ROOT}/agents/standard-conformance-reviewer.md`, passing the standard's path
  under the delivery root, the file set, the target source root, and the contract's path. It
  returns the rules that were in scope and, for each departure, a finding citing exactly one of
  them. Where the caller named no standard, the pass does not run and the record says the project
  has authored none.
- **failures** — spawn a `failure-diagnostician` subagent, its judgment at
  `${CLAUDE_PLUGIN_ROOT}/agents/failure-diagnostician.md`, passing the run's directory, the target
  source root, the bound nodes with the knowledge root, the file set, and the contract's path. It
  returns how many failures it counted and one finding for each.

The division is deliberate and it is not arbitrary: whether the tests prove the criteria has one
home, whether the source answers to the base has another, whether it follows the rules the project
set for itself has a third, and why a run failed has a fourth. One judgment per pass is what keeps
two passes from disagreeing about one line, and it is what makes a clean result from any one of
them mean something specific.

The two conformance passes divide by authority and must not be confused. The base holds what the
business decided — what the system answers, which refusal, which code, who may see what — and a
fact of that kind written in source and in no bound node is the base pass's finding. A standard
holds how the project is arranged — its layers, its wiring, its naming — and a rule of that kind is
the standard pass's. A standard that stated what the system answers would put the two in
contradiction over one line, one requiring in code exactly what the other reports; that is why the
standard's contract excludes it, and why a rule you find doing it is a defect in the standard rather
than a finding to record.

The line all four passes stop at is not a subject line — it is the line between a rule whose
application is a reading and a rule a tool decides. A model hunting an interpolated query competes
with a scanner built for it and loses; hunting a forbidden construct it competes with the compiler
and loses. So this framework runs the consumer's own tools rather than imitating them: a standard
marks those rules as a tool's, they become steps of the captured run above, and what they print
reaches the failures pass carrying the tool's own message as its evidence. What is left — a
responsibility spanning two layers, an interface a caller cannot satisfy, a fact the base does not
hold — is what a reading is for.

What this framework never supplies is the content of any of it: no rule, no threshold, no security
profile. A standard is the project's and its tools are the project's, and a project that has
authored neither gets an honestly narrow review rather than a clean one. Say as much in the report,
so a reader never mistakes four passes for every pass.

### 4. Compose

Write `review/<slug>.md` under the delivery root — the slug names this review, and the path is its
identity. It carries the file set it was computed over, the tasks it answers, one entry per pass, the coverage entries where that pass ran, the standard's copy and the pin of its text where
that one ran, how many failures were counted where that one did, the run's directory where there was
one, and every finding.

The record holds no list of the rules that were in scope. The copy and its pin already determine
that set, both sit in this root, and the validator derives it — so a stored list would be a second
answer to a question the root answers, and the one nobody could check, because the reviewer would
be the one writing it. Which rules were in scope belongs in the report, for the person.

Stamp each finding's pass yourself: the agents return findings without one, so a finding cannot
claim a pass that did not run. An entry for a pass that did not run names what was missing — that
is what says it did not run, and the validator refuses a finding attributed to it. Every finding
names the file it was observed in, exactly as the file set lists it, and the validator holds it
there.

The body is exactly two headings, in order: `## What it is`, then `## Notes`. One sentence per
line; a section with nothing to say carries the literal line `None.` What the passes looked past,
and what this framework does not review at all, belongs in `## Notes` — the diff is the review,
and a limit only the conversation held the next reader never sees.

Check the file on its own as soon as it is composed:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --node <file> <delivery-root> <work-root> <knowledge-root>
```

### 5. Validate, and derive the delivery

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py <delivery-root> <work-root> <knowledge-root>
```

This validates the review against the contract, runs the checks that need the plan — every task
named is a delivered task of this plan, the coverage pass answers for every criterion of them and
for nothing else, the failures counted match the findings recorded, the run it points at exists,
every finding of a pass that scans the file set sits in a file that set lists — and, where the standard pass ran, the checks that need the copied registry:
it holds together, its pin is the text the findings were written against, and every citation names a
rule that copy declares, leaves to a reading rather than to a tool, and whose scope reaches the file
the finding names. Then it derives `delivery.json`. **Never write or edit `delivery.json` yourself.**
Report the output verbatim, and never describe the review as sound while the command exits non-zero.

**Fixing means form, never judgment.** A criterion paraphrased instead of quoted, a finding
attributed to a pass that did not run, a citation hung on a rule that does not govern the file —
yours to correct. A finding is never dropped and a count is never lowered to make the two agree: if
they disagree, one of them is wrong and the answer is to find out which. A state is never raised to
make coverage look better, and a pass that did not run is never recorded as having run.

### 6. Report, and stop

Report, in this order:

- every finding, grouped by pass, each with its evidence and what it costs;
- **which passes did not run, and which input was missing** — this line is not optional, and it is
  what separates a clean review from a narrow one;
- every criterion the coverage pass did not find covered, and what is unexercised in each;
- the standard: which of its rules were in scope over this file set, and which it leaves to a tool
  — naming, for those, whether the step that decides each one ran. A rule left to a tool that never
  ran is unanswered, and saying so is what keeps the split between reading and tool honest instead
  of convenient. Name too every artifact the registry presupposes and the tree does not hold, with
  the rules each one takes with it: a review that reports two findings over a standard whose
  substrate is missing has reviewed a fraction of it, and the fraction is the number this line
  gives. The way out is a task declaring the artifact in `produces`, planned through `/plan-work`;
- the run: which steps were executed and where each came from — the registry, or the caller —
  how it ended, how many failures were counted, and where the output sits. Name any step a rule
  expects and the registry declares no command for: that rule was decided by nothing, and a review
  silent about it reads as a review that covered the whole registry;
- what this framework does not review at all, so four passes are never mistaken for every pass;
- what the passes looked past as another judgment's;
- which passes, if any, ran inline instead of in a subagent, and why;
- the validator's final output, verbatim;
- where the repairs live, as routes and not as a reading of the findings: source, or a criterion
  recorded unmet, is answered by `/implement-task` over the same task; a fact stated in source that
  no bound node holds is produced in the base by `/analyse-domain` and reaches the task through
  `/plan-work`; a rule of the standard that seems wrong is changed by whoever owns the registry.
  This skill hands nothing forward as an invocation, and the reason is the one stated above: which
  route any finding deserves — or whether it deserves one at all — is the decision this pass does
  not make. Naming where a repair would go is not choosing to make it.

Then stop. Do not compute a verdict, rank the findings, decide what blocks, open work from them,
or fix any of them. A disagreement a proof record holds stays a disagreement: settling it here
would discard the one signal that tells a careful finding from a confident one. `git diff` over
the delivery root is this review's own review, and what the findings mean for the change belongs
to a person.

## What you never do

- Write or edit `delivery.json` by hand.
- Compute a verdict, a severity, a score, a coverage figure, or anything a threshold could read.
  A number that must rise becomes a target to satisfy, and satisfying it produces tests nobody
  needed.
- Fix, edit or rewrite any source or test you reviewed — you hold no grant to, and a reviewer that
  could edit what it flagged leaves nothing for anyone to disagree with.
- Discover the file set, widen it, or narrow it to the paths that happened to be readable. A path
  that cannot be read stops its pass and is reported; a pass over the readable subset would report
  clean over files nobody read.
- Run anything but the runner this framework ships, and never rerun it to get a different result:
  a second run is a second name, and the first one's evidence stays on disk.
- Compose a command, or supply a step this project did not declare. Every command and every bound
  is the registry's or the caller's; one invented here is this framework guessing at a stack it
  ships no knowledge of, and a run that guessed reports about a tree nobody built.
- Silently replace a step the registry declares with one the caller named under the same name. Two
  commands under one step name cannot both be the one whose outcome a rule is read against, so a
  collision is a stop that names it.
- Record a pass as having run when its input was absent, or attribute a finding to a pass that did
  not run.
- Record a finding against a rule a standard says a tool decides, or against a rule whose scope does
  not reach the file — the first re-decides in a model what a tool decides exactly, and the second
  hangs a departure on a sentence that does not govern the file.
- Lower a failure count, or drop a failure, to make the record validate. The two disagreeing is the
  signal, not the obstacle.
- Show the standard pass what an implementation record disclosed. A record may name the very rules
  this pass reads, and a pass told which departures were already admitted is a pass the producer
  shaped. It reads the source; a person reads both records and learns something neither says alone.
- Overwrite a copy under `standards/` whose text differs from the registry as it stands, or edit a
  copy after a record has pinned it.
- Add to, edit or reinterpret the project's standard. It is the project's; a rule that seems wrong is
  reported as a departure exactly as written, and changed by whoever owns it.
- Write into the work root, the knowledge root, or the target source root.
- Commit, stash, or otherwise change the consumer's git state.
- Restate the contract's vocabularies from memory instead of reading the schema.
