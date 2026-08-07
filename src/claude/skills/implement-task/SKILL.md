---
name: implement-task
description: Writes the source one planned task requires and the tests that prove it, installs what the project's own standard authorizes, runs the steps that standard declares until the project builds and its suite passes, records both nodes under a delivery root — what was written, every criterion answered, every bound base node accounted for, every inference, every departure, every run captured — validates the delivery against the plan, and derives delivery.json. Use when a request asks to implement, build, code or deliver a task the plan already holds. Not for planning or decomposing work (that is /plan-work), not for analysing domain material (that is /analyse-domain), not for reviewing or judging what was written (that is /review-change), and never for more than one task.
effort: medium
---

You carry one planned task from the plan into written source and the tests that prove it, and
you stop. One invocation, one task: two tasks in one invocation is two deliveries nobody can
review apart.

## Required inputs

A missing input is a stop, not a default:

1. **the task** — which one, by identifier. Named by the human, or named in a request that
   names exactly one; a request that names none, or several, is a stop, and the answer is to
   ask which. Choosing for the human is choosing what gets built.
2. **the work root** — the plan holding the task. Named by the human; inferred rather than
   named, its absence is a stop.
3. **the knowledge root** — the base the plan binds to, required exactly as the plan validator
   requires it: while the plan is live, and ignored once it is closed. A work root holding
   `closure.md` is a different matter: the plan is history, its initiative is over, and writing new
   source against it is a stop. Reviewing what it already delivered is not — that is
   `/review-change`'s, and it stays possible for as long as the records do.
4. **the target source root** — where the code lives or will live. An empty tree is an answer;
   which tree it is, the human says.
5. **the delivery root** — the directory the records are written into, under git, beside neither
   of the other two roots. Named by the human and absent, it is created empty; inferred rather
   than named, its absence is a stop. Records are not written into the work root: a plan that
   held what was delivered would be recording progress, and that is the orchestrator's state
   file this framework refuses to have.

Absent inputs stop once, together: one stop naming everything missing — the task among them, where
the request named none — so the human answers once, never a question at a time.

One optional input: **the project's standard** — the path to the registry of rules the project set
for itself, in the project's own tree. Named, the source is written to follow it; not named, the
only convention this invocation follows is what the inventory evidenced, and the report says so.
The framework ships no rule and never owns the registry: `${CLAUDE_PLUGIN_ROOT}/schemas/standard.json`
is the contract a project's own file answers to.

## Before anything: the plan

Nothing is written over a plan that does not hold together. Run:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/plan.py --check <work-root> <knowledge-root>
```

Anything but a clean pass is a stop: report the output verbatim and go no further. A plan with
problems is fixed through `/plan-work`; a stale index is rederived by whoever owns the plan.
Neither repair is this invocation's to make — delivering never writes into the work root, and
never into the knowledge root either.

The pin the implementation record carries is the SHA-256 of the task's own file:
`sha256:<hexdigest>`, computable as `sha256sum <work-root>/task/<epic>/<slug>.md`. It pins the task
and not the plan's index, because a record answers one task and that is what it should be held to —
and because pinning the index made every record in the root stale the moment any unrelated task was
added, which no entry point here is allowed to go and fix. The proof carries no task pin: what it
pins is the implementation record itself, and step 3 says why.

## Before anything: the tree

The review is `git diff`, and a diff only says what this invocation did when the tree starts
clean. Before any write, `git status --porcelain -- <delivery-root> <target-source-root>` must
print nothing — the pathspec is the point: the stop's scope is the roots this invocation writes,
and a pending change elsewhere in the repository is somebody else's work in progress, not a reason
this delivery cannot be reviewed. Output is a stop: report what is pending and go no further
— committing, discarding or overriding is the human's decision, never this skill's. A root not
under git control is the same stop: without git there is no review, and source is the one thing
here nobody can review any other way.

## Read the contract

Read `${CLAUDE_PLUGIN_ROOT}/schemas/delivery-node.json`. It is the single home of what a
delivery node may and must declare — the kinds, the fields each kind requires, and one example
per kind inside that kind's branch. Do not work from memory of it, and do not restate it: what
you remember is not what the validator will apply.

`${CLAUDE_PLUGIN_ROOT}` is set where this skill runs as an installed plugin. Where it is not,
the plugin root is the directory that holds `schemas/` and `bin/` side by side — in a vendored
install, the `.claude/` directory this skill's tree sits under. Every path below resolves the
same way.

## This invocation runs, and every run it makes is captured

What it hands over is a project that installs and builds, not source alone. Source nobody executed
is source whose every rule a tool decides went unanswered, and a rule a project's own registry
names Zod for cannot be followed by a session that never saw Zod's types.

**Nothing here is run by narration.** Every execution goes through
`${CLAUDE_PLUGIN_ROOT}/bin/run.py`, with the commands the project's registry declares, into a
directory under the delivery root's `run/`. A command run any other way did not happen: what it
printed exists in a conversation, which is not state, and the record would rest on it.

That capture is what replaced the older rule that this invocation ran nothing at all. The rule
existed because a session that could run the suite it just wrote would iterate quietly until the
suite went green, and what failed on the way would exist nowhere. The second half is what has
changed, and only the second half: `run.py` refuses to write a run under a name that already
exists, so a session that tried four times leaves four directories with four verbatim logs, and
the record points at the one that passed while the three that did not keep their names. Iterating
is not forbidden here. It is recorded, and recorded is stronger — the old rule could only stop the
producer from looking, and this one makes everything the producer saw readable by somebody else.

**The skill runs; the agents do not.** No agent this framework ships holds a shell, and none gains
one here. Writing source stays the `task-implementer`'s even when a run comes back red: a failure
goes back to the agent with what the run printed, and the source is written again. A skill that
patched a file to make a build pass would be the writer that nobody separated from the witness.

## The order

```
situate → set up → implement → build → prove → suite → validate → report → stop
```

Two of these steps are another judge's. Writing the source and writing what proves it are
delegated to the subagents this framework ships, each in a clean context, and the judgment of
each step lives in the agent's file — not here, and not in your memory of it. Delegating means
spawning the named subagent — in a plugin install the name may be plugin-scoped — and reading
the agent's file yourself is the fallback, never the delegation. The separation between the two
is the point of the arrangement: an implementation and its tests written in one pass agree by
construction, including where both are wrong. Only where the session cannot spawn subagents,
read the agent's file under the plugin root's `agents/` directory and apply its discipline in
place — the file stays the single home of that judgment — and the report must say which steps
ran inline.

The three steps that execute — set up, build, suite — run only where the standard names commands.
Where none was named, or the registry declares none, they do not run, the report says so, and what
this invocation hands over is source alone, which is the older and narrower answer rather than a
clean one.

### 1. Situate

One command answers where the task stands, and it validates the delivery on the way:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --outstanding <delivery-root> <work-root> <knowledge-root>
```

On an empty delivery root it reports every task without a record; on a populated one it also
reports, per task, what the base leaves unresolved and which dependencies have no record yet.
Anything but a clean run is a stop, reported verbatim: a delivery that does not hold together is
not added to.

Two of its lines are refusals, and each is settled before anything is written:

- **The task carries unresolved entries.** Stop. An unresolved entry is a fact the base does not
  hold that bears on the objective or a criterion, and there is no honest way to write source
  over one — what gets written reads exactly like a decision the business made, in the one place
  nobody will look for a decision. Report the entries quoted whole, and hand over the door, not
  just the wall: the report ends with the `/analyse-domain` invocation ready to paste — this
  knowledge root named by path, the entries listed as the asks the material must answer, and,
  where a cited gap carries a proposal, the ask being to ratify or reject it. The answer is
  produced in the base, never here, and the task is re-bound through `/plan-work` afterwards.
  The validator refuses such a record too, but by then the source exists; the point of stopping
  here is that it does not.
- **A task this one builds on has no record.** Stop, and name it. A dependency is what has to be
  delivered first — that is what the plan meant by declaring it — and the records are how that is
  known, because no status field exists to ask.
- **The named task is not in the plan.** Stop — and hand over the door, not just the wall: the
  report ends with a `/plan-work` invocation filled with everything this invocation already knows
  (the work root, the knowledge root, the target source root, the standard where one was named),
  leaving only the scope for the human to state. A task the plan does not hold is planned into
  it, never improvised past.

A third refusal is not in that report, because the plan's index is not what holds it — the task file
does. So open the task file here, before the copying below writes anything, and read its `## Notes`:
**an entry opening `BLOCKING, from the binding —` is a stop.** Quote the entries whole. That class is
the binder's finding that the objective, or a criterion, cannot be demonstrated
as written without contradicting or exceeding the base, and a task that arrives here still carrying
one is the scope-origin kind — the other kind is re-cut and re-bound before the task is ever
written. What the plan said of it, in as many words, is that only the human settles it: through the
scope, re-planned in `/plan-work`, or through `/analyse-domain` producing the fact the base lacks,
after which the task re-binds and the note is gone. Both doors leave here ready to open: the
report ends with the `/plan-work` invocation and the `/analyse-domain` invocation, each filled
with everything this invocation already knows — the roots by path, the note quoted as the
conflict the scope must settle or as the ask the material must answer — leaving to the human
only the choice of door and what only the human holds. Writing source in the meantime encodes the
contradiction as though the business had decided it — the same failure an unresolved entry names,
and the worse half of it, because here the base is not silent but overruled. The class is the
binder's judgment and not yours to overrule: a note you disagree with is still a stop, and the
disagreement goes in what you report.

This stop is the skill's and not the validator's. `deliver.py` refuses a record over an unresolved
entry and says nothing about notes, deliberately: a blocking note is cleared by amending the scope
or the base, and by the time either lands the task has re-bound and the note is gone — so a second
gate in the validator would only ever fire on a state this stop already refuses. What the plan
records, the code cannot embody; those are different acts and they get different answers.

A fourth fact the report does not carry, because you can see it directly: **a record already at the
path this task computes to.** That is a re-delivery, not a stop, and the report says so. Both
records are rewritten whole rather than amended — a record amended across two acts of writing
describes neither, and the proof's pin on the implementation refuses the pair if you rewrite one
and leave the other. `git diff` over the two is then the history of the delivery.

Where a standard was named, take it in before anything is written. Which command depends on one
field of the task file — already open from the note check above — read as a yes or a no:
**does the task declare `produces`?**

Where it does not, the tree is held to what the registry presupposes on the way in:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --standard <the project's registry> --against <target-source-root> --delivery <delivery-root>
```

Where it does, drop `--against` and run the registry check alone, keeping `--delivery`:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --standard <the project's registry> --delivery <delivery-root>
```

Either way, anything but a clean pass is a stop, reported verbatim. A line opening
`AUTHORIZATIONS LOST` is not a stop but travels into the report whole: it says a pinned copy under
the delivery root authorizes packages the registry no longer does, which is what a registry
updated by pasting a template over it looks like — and whether that was deliberate is the
consumer's to say, in their own file, before a delivery needs the missing entry.

The first form carries two refusals. A registry that does not hold together answers to nothing, and
fixing it belongs to whoever owns it. An artifact the registry presupposes and the tree does not
hold is the same refusal one step earlier: a rule is a condition over a file that exists and can
never ask for one, so a registry whose substrate is absent is a registry nothing can be held to —
its tool-decided rules have no step to run as, and its read-decided rules are read against files
written to answer a set of rules that was never in force. Written anyway, the absence is found once
per file in a review, after the files exist, instead of once here, before the first of them. The
way out is named in the output: a task declaring the artifact in `produces`, planned through
`/plan-work` and delivered first.

**`produces` is what drops that half of the check, and it drops nothing else.** A task producing an
artifact is the one building the substrate, and holding it to the substrate's presence is circular:
with no exemption the artifact could never be written by anything, and the plan would stop on a
condition only the plan could end. The exemption is one field, read once, and the record is held to
it afterwards — the validator refuses an implementation whose `files` does not list what the task
said it would produce, so a task that claimed the artifact and did not write it is a refusal rather
than a delivery.

Then copy the registry into `standards/` under the delivery root, keeping the name the project gave
it, and note the SHA-256 of the copy — `sha256sum <delivery-root>/standards/<file>`. The copy is
what makes a disclosure checkable afterwards: the registry lives in the project's tree and will move
on, and a record pointing at a file no root holds is a record nobody can check later. It is kept the
way `run/` is kept — material a judgment was read from, never validated as a node.

**A copy is never overwritten.** Where `standards/` already holds a file of that name whose text
differs from the registry as it stands, the rulebook changed since some earlier record was written:
name this copy differently. Overwriting would leave that record pinning text it never read, and the
validator would refuse a record that was honest. A second rulebook is a second name, the way a
second run is.

Then read the rest of the task file — the notes were read above — and the plan's inventory nodes. `plan.json` lists every node the
plan holds with its kind and its file, so the inventory is found there rather than by walking the
root; pass on the ones whose `area` reaches where this task lands, and leave the rest — an
inventory surveyed for another territory carries conventions this task has no business following.
Read the epic only for what it covers. Read no other task: this invocation delivers one.

### 2. Set up

Where the standard declares a command whose role is `install`, run it before anything is written,
so the implementer reads the types of what this project already declares instead of guessing at
them — which is the whole difference between following a rule that names a library and writing
what a rule that names a library sounds like:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/run.py <delivery-root> --run <epic>-<slug>-setup --cwd <target-source-root> --timeout-seconds <the step's own> --step <its step>="<its command>"
```

Three cases skip it, and each is said in the report rather than worked around. The task
`produces` the manifest: nothing is declared yet, and this project's first install is the build
below. The registry declares no install: a project may hold several registries, and the one whose
rules govern this task need not be the one that owns the manifest. No standard was named at all:
then nothing here runs, and what this invocation hands over is source alone.

A red setup is a stop, before a line is written. The run holds what the installer printed, and
what it names — a registry nobody can reach, a lockfile that does not resolve against the manifest
— is not this invocation's to guess at or to route around.

### 3. Implement

Spawn a `task-implementer` subagent — its judgment lives at
`${CLAUDE_PLUGIN_ROOT}/agents/task-implementer.md` — passing five things: the task file's path,
the knowledge root, the target source root, the paths of the plan's inventory nodes, and the
delivery-node contract's path — plus, where one was named, the path of **the copy** of the standard,
so what it read is exactly what the record pins. Where the task declares `produces`, pass those
paths too: they are artifacts this delivery has to create rather than conventions it has to follow,
and the record is refused if `files` does not list every one of them. Where the standard authorizes
dependencies, pass that list too, by name: it is what the agent may add to the manifest and the
whole of it — a package outside it is the agent's refusal, not its judgment call, because the list
is where a human's approval of a package survives the session it was given in. It reads the task and the nodes it binds, writes the source, and
returns the record: every path it created or modified and what each now does, every criterion of
the task answered, every bound node accounted for, which authorized dependencies it added, and
what it inferred, departed from, preserved and deferred.

**Every path in the record is relative to the target source root** — the directory the registry's
commands run from — never to the repository around it. The target root may be the repository root
and may just as well be `backend/` inside it: `produces` is held to `files` by spelling, and a
registry scope reaches a file only under the same anchor, so a record that spelled paths from the
repository while the registry spelled them from the target would answer to no rule and satisfy no
`produces`. Spell the software's paths from the software's own root, always.

### 4. Build

Everything the registry declares except the step whose role is `suite`, in the order it declares
them, with the install first so that whatever the implementer added to the manifest is real before
anything reads it:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/run.py <delivery-root> --run <epic>-<slug>-build --cwd <target-source-root> --timeout-seconds <the largest of those steps'> --step <name>="<command>" [--step ...]
```

`run.py` stops at the first step that does not pass, so a tree that did not install is never
type-checked and the log says which one it was.

**One task runs less than that, and it is the same task and the same field as at the situate step:
one declaring `produces`.** It runs the step whose role is `install`, and no other. What every other
step decides is a rule over a file; a delivery that wrote the substrate wrote no such file, so a
check run here decides nothing — and whether it says so by failing or by exiting 0 is the stack's
accident rather than this delivery's evidence. That is the sharper half: a green step over an empty
tree would be recorded as a project that builds, and nothing here could tell it from one that does.
The install is not an accident. It says the manifest is well formed and the dependencies it names
resolve, which is the whole of what can be decided about a substrate before there is source. Where
the registry declares no install, nothing runs here at all.

Either way the report names the steps that did not run and why, and `## Notes` on the record carries
the same sentence: a reader meeting a substrate record must not read it as a project that builds,
and what holds the substrate up is the first delivery that writes source over it, whose build is
full.

The claim is held afterwards, exactly as `produces` is held against `files`: the validator refuses a
record whose run covered fewer steps than its registry declares, and the one exemption is a task
that declares `produces` and wrote nothing any rule's scope reaches. A task that declared `produces`
and also wrote source owes every step, and the refusal says so.

**A red build is not the end of the invocation and it is not a stop.** Send what the run printed
back to the `task-implementer` — the source is its to write, and a skill that patched a file to
turn a build green would be the writer nobody separated from the witness — and run again under
`<epic>-<slug>-build-2`, then `-3`. Every attempt keeps its directory and its log, because the
runner refuses a name that already exists. That refusal is the whole reason this invocation is
allowed to iterate at all: what failed on the way is readable afterwards by somebody who was not
here.

Giving up is the stop. Report every run by path, what the last one printed, and write no record:
a record over a red run is refused by the validator anyway, and the point of stopping here is that
it was never composed.

Compose and write `implementation/<epic>/<slug>.md` — the same epic and slug as the task, because
the path is the identity and nothing else names which task a record answers — from what the agent
returned plus the pin stamped on `task`, and — where a standard was named — where its copy sits,
the pin of its text, the build run that passed, and every dependency the agent added. The body is exactly two headings, in order:
`## What it is`, then `## Notes`. One sentence per line; a section with nothing to say carries the
literal line `None.` An inference or a departure worth a reader's eye goes in `## Notes` as well
as in its field — the diff is the review, and what only the conversation held the reviewer never
sees.

Check the file on its own as soon as it is composed, so a composition error is caught at the file
that made it:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --node <file> <delivery-root> <work-root> <knowledge-root>
```

Where the agent stopped instead of writing — an input absent, a bound node missing, the base
silent on a fact the work needs — that is a successful stop and not a failure of this invocation:
report what it said and write no record. Where it wrote files and then stopped, the run failed:
say which files exist, and leave them for a person to look at rather than tidying them away.

### 5. Prove

**A task that produced the substrate has nothing to prove, and no proof record is written.** There
is no source for a test to reach, and a proof requires at least one test precisely because a test
that cannot be said to fail for a stated reason is one nobody can evaluate — over an empty tree
every entry would be that. So this step and the next do not run, and `deliver.py --outstanding`
reports the task as implemented with no proof holding it up, which is exactly true. Say so in the
report and go to step 7. Composing a proof anyway would be the one thing worse than the absence: a
record asserting that tests hold up a task, written where no test could exist.

Spawn a `test-author` subagent — its judgment lives at
`${CLAUDE_PLUGIN_ROOT}/agents/test-author.md` — passing four things: the task file's path, the
implementation record's path, the target source root, and the delivery-node contract's path — plus
the copy of the standard where one was named, because a project's rules about how its tests are
written are the test author's to follow, and plus every `UNDERDETERMINED, from the binding —`
entry of the task's `## Notes`, quoted whole: each names an implementation that satisfies every
criterion as written and that the base refuses, and excluding it is the test author's work.
Where the task's criteria name a failure that must stop happening, pass the reproduction too;
without it the tests prove the fix rather than the defect, and afterwards nobody can tell the
difference.

It writes the tests and returns what each proves, what would make each fail, which edge cases it
dismissed and why, what stays unproven, where it disagrees with the implementation, and every rule
of the standard its tests depart from.

### 6. Suite

Every step the registry declares, in order, ending with the one whose role is `suite`:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/run.py <delivery-root> --run <epic>-<slug>-suite --cwd <target-source-root> --timeout-seconds <the largest of them> --step <name>="<command>" [--step ...]
```

The checks run again here rather than only at the build, and the repetition is deliberate: a rule
about where a test file sits or how it is named reaches files that did not exist when the build
ran, so a build-only pass would leave every rule about tests decided by nothing. Each step that
already passed passes again in seconds; the runner stops at the first that does not.

**A red suite is a stop, and it has exactly two ways out.** Nothing further is written — the
implementation record stands, because its own run passed, and no proof record is composed, so
`deliver.py --outstanding` reports the task as implemented with no proof holding it up, which is
true and is the state a person should meet. Report the run by path and the tests that failed. Then
either the source is wrong, and the fix goes back to the `task-implementer` and the suite runs
again under `<epic>-<slug>-suite-2`, with the first run keeping its name; or the two producers
disagree and that disagreement is what the red is — the proof asserts what the criterion requires
and the implementation does not satisfy it — and only a person settles that.

**The third way is forbidden and it is the one that is easy.** A test is never weakened, deleted,
narrowed or rewritten to make the suite green. This invocation holds two producers precisely so
that one cannot overrule the other, and a test edited until it passes is exactly that overruling,
performed where nobody would see it. What makes the rule enforceable rather than pious is that the
runs are on disk: four attempts leave four logs, and a test that changed between them is in the
diff beside them.

Where the registry declares no command at all, this step does not run, the tests stand unexecuted,
and the report says so — the narrow answer rather than a clean one. A task that produced the
substrate reaches neither this step nor the one before it, for the reason step 5 gives.

Write `proof/<epic>/<slug>.md`, same epic and slug again, and check it the same way. Where a
standard was named, stamp where its copy sits, the pin of its text and the suite run that passed on
this record too, exactly as the implementation carries its own — the rules about how a project
writes its tests reach files no implementation ever lists, so a departure from one is the proof's
to disclose and resolves against the copy the proof itself pins.

Stamp on it the SHA-256 of the implementation record you just wrote — `sha256sum <that file>`. It
says which version of that record these tests were written against, and it is what makes a
re-delivery honest: rewrite the implementation later and leave the proof alone, and the validator
refuses the pair instead of letting tests stand that claim to prove criteria the source now
satisfies some other way.

A disagreement the author recorded is not settled here. It stays recorded: this invocation holds
two producers precisely so that one cannot overrule the other, and resolving it now would discard
the signal.

### 7. Validate, and derive the delivery

When both records are written, run:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py <delivery-root> <work-root> <knowledge-root>
```

This validates every delivery node against the contract, runs the checks that need the plan — the
task exists, a proof sits beside an implementation, every criterion of the task is answered
exactly once and nothing else is, every base node the task binds is accounted for, no task the
base leaves unresolved is delivered, no task is delivered before what it builds on, every record's
pin matches its own task as it stands, each proof's pin matches the implementation beside it, and
every departure disclosed against a standard rule cites one that standard declares and sits in a
file this record says it wrote — and derives `delivery.json`. **Never write or edit
`delivery.json` yourself.** Report the command's output verbatim. If it exits non-zero, the run
failed — fix and rerun, and never describe the delivery as sound while it is not.

**Fixing means form, never knowledge.** A wrong shape — a malformed pin, a criterion paraphrased
instead of quoted, a missing entry for a bound node — is yours to correct. A criterion the source
does not satisfy is recorded as unmet, not talked into met. A fact the base does not hold is not
supplied to make a check pass: it is a stop, and it was one before the source was written.

### 8. Report, and stop

Report, in this order:

- the two nodes written, by identifier, and whether this was a re-delivery;
- every path the delivery created or modified — this is the file set `/review-change` needs, and
  the one thing it must never discover for itself;
- every criterion recorded unmet, with what the record says about it;
- every inference recorded, and every departure — these are the decisions nobody asked for, and
  they are what a reviewer reads first;
- everything the proof left unproven, every edge case it dismissed, and every disagreement it
  recorded;
- what the implementation deferred, and what it says must keep working;
- which steps, if any, ran inline instead of in a subagent, and why;
- the validator's final output, verbatim;
- the standard this invocation followed, by the copy it took and that copy's pin, every departure
  disclosed against it by either record, and what it presupposes — that the tree holds it, or, for a
  task that produced it, that this delivery is what made it hold. Where none was named, say that
  the only project convention followed is what the inventory evidenced, which is the honestly narrow
  answer rather than a clean one — and where `--outstanding` named a standard this root's earlier
  records pin, say that too: an invocation naming none over a root that remembers one is writing
  source the review will still read against those rules;
- every run this invocation captured, by path and by outcome, including the ones that failed —
  those are not noise and they are not a draft: they are the only record of what it took, and a
  report naming only the run that passed describes a delivery that went right the first time
  whether or not it did — and every step of the registry that did not run, with why. Where this
  delivery built the substrate, that is most of them, and saying which rules they own is what keeps
  a substrate record from reading as a project that builds;
- every dependency this delivery installed, and that what those pulled in transitively is nobody's
  approval — the lockfile is what says what actually arrived, and it is in the diff;
- what `/review-change` still does that this invocation did not: it runs the same steps again over
  the whole change rather than one task's, and it judges — whether the tests prove the criteria,
  whether the source states only what the base holds, whether it follows the same standard, and
  why anything failed. A green suite here is a green suite over one task, and two tasks that each
  passed alone are not a change that passes together;
- the handoff: the `/review-change` invocation ready to paste — this delivery root, this work
  root, this knowledge root and this target source root named by path as just validated; the
  tasks under review being the one task this invocation delivered, by identifier; the file
  set being exactly the paths named above, because a review never discovers its own scope and
  this report is the only place that set exists; and the project's standard where one was named,
  which is also where the review reads its commands from. The handoff offers the next step and
  never takes it: filling any empty slot and invoking are the human's.

Then stop. `git diff` over the target source root and the delivery root is the review, and it
belongs to a person.

## What you never do

- Write or edit `delivery.json` by hand.
- Take a second task, or widen the one you were given — code that should change and that this
  task does not reach is deferred in the record, never changed.
- Write source over a task the base leaves unresolved, or supply the fact yourself. A fact is
  produced in the base, through `/analyse-domain`, never in code, a comment, a test or a record.
- Write source over a task whose `## Notes` still carries a `BLOCKING, from the binding —` entry,
  or settle the conflict it names. The class is the binder's, the settlement is the human's, and
  both ways out of it run through another entry point.
- Record a status, a readiness, an approval or a progress figure — those fields do not exist, and
  prose does not get to hold what the contract refused.
- Judge whether the work is correct, done well enough, or fit to merge. Nothing here carries a
  ready flag: a producer that certified its own output would be the validator of its own work.
- Run a command this project's registry does not declare, or compose one. Every step is the
  registry's string, run through `bin/run.py`; a command invented here is this framework guessing
  at a stack it ships no knowledge of, and the guess would be wrong in the project that mattered.
- Install a package the registry does not authorize. The stop names it, and what ends the stop is
  the registry gaining an entry — a human editing their own file, not an answer given here that
  the next invocation would not have.
- Weaken, narrow, delete or rewrite a test to turn a red suite green. Two producers exist so that
  one cannot overrule the other, and that is the overruling, done where nobody would look.
- Edit source yourself to make a run pass. Writing is the `task-implementer`'s; a failed run goes
  back to it with what the run printed.
- Run anything outside `bin/run.py`, or report an outcome the runner did not capture. A command
  whose output lives only in this conversation did not happen.
- Read `produces` as leave to skip a check over source. It exempts the delivery that wrote the
  substrate and nothing else; a task that declared it and also wrote source owes every step the
  registry declares, and the validator refuses the record whose run did not cover them.
- Write into the work root or the knowledge root; a plan or a base that is wrong is reported with
  its fix.
- Write the tests in the context that wrote the source — the inline fallback is for a session that
  cannot spawn subagents, is declared in the report, and still applies each agent's file.
- Settle a disagreement the proof recorded, or delete an inference to make a record read cleanly.
- Commit, stash, branch, or otherwise change the consumer's git state — a dirty tree is reported,
  and what to do with it is the human's call.
- Record which rules of the standard were in scope. That set derives from the copy and the files
  written, both of which this root holds, so a stored list would be a second answer to a question
  the root already answers — and the one nobody could check, because the producer would be writing
  it.
- Overwrite a copy under `standards/` whose text differs from the registry as it stands, or edit a
  copy after a record has pinned it.
- Treat a disclosed departure as leave to depart. It says the departure was known and reasoned, and
  it settles nothing: the review holds the same source to the same rules and is not shown what was
  disclosed.
- Restate the contract's vocabularies from memory instead of reading the schema.
