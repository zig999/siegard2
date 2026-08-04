---
name: review-change
description: Reviews a delivered change from the angles that need judgment — whether the tests prove the task's criteria, whether the source states only what the knowledge base holds, and why a captured run failed — captures the run itself when given the commands, records the findings and the passes that did not run under the delivery root, and derives delivery.json. Use when a request asks to review, check, audit or verify a change that a delivered task produced. Not for writing or fixing source (that is /implement-task), not for planning (that is /plan-work), and not for approving anything — it produces evidence, and what it means is a person's to decide.
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

Optionally, and this is what decides whether the third pass runs: **the commands to run** — each a
name and a command, as `${CLAUDE_PLUGIN_ROOT}/bin/run.py` takes them — or **a run already
captured**, by its directory under the delivery root's `run/`. With neither, the failures pass
does not run, and the record says which input was missing. An absent optional input never becomes
a default: a review reported as clean over a pass that never ran is the failure that rule exists
to prevent.

## Before anything: the plan, the delivery, the tree

Run both checks, and report either output verbatim as a stop:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/plan.py --check <work-root> <knowledge-root>
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --check <delivery-root> <work-root> <knowledge-root>
```

A review over a plan or a delivery that does not hold together reports a soundness nobody has.
Neither repair is this invocation's: a plan is fixed through `/plan-work`, a record through
`/implement-task`.

The pin this review carries is the SHA-256 of `plan.json` as just checked, computable as
`sha256sum <work-root>/plan.json`.

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

Each pass is another judge's. The three are delegated to the subagents this framework ships, each
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

### 2. Capture

Where the caller named commands, run them, once, into a run named for this review:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/run.py <delivery-root> --run <slug> --timeout-seconds <n> --step <name>="<command>" [--step ...]
```

The timeout is the caller's; there is no default, because a bound this framework shipped would be
one nobody calibrated. The commands are the caller's too: nothing here composes a build or a test
command, or infers one from what the tree looks like.

Running belongs here rather than in `/implement-task` for one reason: whoever wrote the source
must not be the one who witnesses whether it passed, or the writing quietly iterates until the
suite goes green and what failed on the way exists nowhere. Running it here is safe in a way it is
not there — this invocation has no work to protect — and the run lands on disk before any judgment
is made of it, so the same evidence can be handed to a second reviewer who reads it differently.
The pass that judges it still never executes anything: it reads the files this step wrote.

Where the caller named a run already captured, use it and run nothing. Where they named neither,
the failures pass does not run and the record says so.

A captured run whose outcome says nothing executed — a command not found, a step terminated — is
still diagnosed. Nothing was proved about the code, and that is precisely what the diagnosis
records; a run that could not execute is a finding, not an absent input. A run in which everything
passed is the one case where the pass does not run: there was no failure to read.

### 3. The passes

Three, independent, in any order or together. None reads another's output, and none decides what
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
- **failures** — spawn a `failure-diagnostician` subagent, its judgment at
  `${CLAUDE_PLUGIN_ROOT}/agents/failure-diagnostician.md`, passing the run's directory, the target
  source root, the bound nodes with the knowledge root, the file set, and the contract's path. It
  returns how many failures it counted and one finding for each.

The division is deliberate and it is not arbitrary: whether the tests prove the criteria has one
home, whether the source answers to the base has another, and why a run failed has a third. One
judgment per pass is what keeps two passes from disagreeing about one line, and it is what makes a
clean result from any one of them mean something specific.

What none of these passes covers, this framework does not ship: no security scan, no structural or
duplication scan, no analysis of what the change exposes to its consumers. Those are real
judgments and this is not their home — the ecosystem the consumer already works in has tools for
them, and a pass here would compete with tools this framework does not own while pretending the
question was answered. Say as much in the report, so a reader never mistakes three passes for
every pass.

### 4. Compose

Write `review/<slug>.md` under the delivery root — the slug names this review, and the path is its
identity. It carries the file set it was computed over, the tasks it answers, the pin, one entry
per pass, the coverage entries where that pass ran, how many failures were counted where that one
did, the run's directory where there was one, and every finding.

Stamp each finding's pass yourself: the agents return findings without one, so a finding cannot
claim a pass that did not run. An entry for a pass that did not run names what was missing — that
is what says it did not run, and the validator refuses a finding attributed to it.

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
and the pin matches the plan as it stands — and derives `delivery.json`. **Never write or edit
`delivery.json` yourself.** Report the output verbatim, and never describe the review as sound
while the command exits non-zero.

**Fixing means form, never judgment.** A criterion paraphrased instead of quoted, a finding
attributed to a pass that did not run, a count that does not match — yours to correct. A finding
is never dropped to make the record read cleanly, a state is never raised to make coverage look
better, and a pass that did not run is never recorded as having run.

### 6. Report, and stop

Report, in this order:

- every finding, grouped by pass, each with its evidence and what it costs;
- **which passes did not run, and which input was missing** — this line is not optional, and it is
  what separates a clean review from a narrow one;
- every criterion the coverage pass did not find covered, and what is unexercised in each;
- the run: what was executed, how it ended, how many failures were counted, and where the output
  sits;
- what this framework does not review at all, so three passes are never mistaken for every pass;
- what the passes looked past as another judgment's;
- which passes, if any, ran inline instead of in a subagent, and why;
- the validator's final output, verbatim.

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
- Record a pass as having run when its input was absent, or attribute a finding to a pass that did
  not run.
- Write into the work root, the knowledge root, or the target source root.
- Commit, stash, or otherwise change the consumer's git state.
- Restate the contract's vocabularies from memory instead of reading the schema.
