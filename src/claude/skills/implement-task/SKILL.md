---
name: implement-task
description: Writes the source one planned task requires and the tests that prove it, records both under a delivery root — what was written, every criterion answered, every bound base node accounted for, every inference and every departure — validates the delivery against the plan, and derives delivery.json. Use when a request asks to implement, build, code or deliver a task the plan already holds. Not for planning or decomposing work (that is /plan-work), not for analysing domain material (that is /analyse-domain), not for running the suite or reviewing what was written (that is /review-change), and never for more than one task.
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
clean. Before any write, `git status --porcelain` must print nothing over the delivery root and
nothing over the target source root. Output is a stop: report what is pending and go no further
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

## This invocation runs nothing

No build, no suite, no command of the target project's. Running is a script's work —
`${CLAUDE_PLUGIN_ROOT}/bin/run.py` — and it is invoked from `/review-change`, over a change
somebody else wrote. Whoever writes the source must not also be the one who witnesses whether
it passed: a session that could run the suite it just wrote would iterate quietly until the
suite went green, and what failed on the way would exist nowhere. What this invocation produces
is source, tests, and the record of both. What they are worth is decided elsewhere.

## The order

```
situate → implement → prove → validate → report → stop
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
  nobody will look for a decision. Report the entries; the answer is produced in the base,
  through `/analyse-domain`, and the task is re-bound through `/plan-work` afterwards. The
  validator refuses such a record too, but by then the source exists; the point of stopping here
  is that it does not.
- **A task this one builds on has no record.** Stop, and name it. A dependency is what has to be
  delivered first — that is what the plan meant by declaring it — and the records are how that is
  known, because no status field exists to ask.

A third refusal is not in that report, because the plan's index is not what holds it — the task file
does. So open the task file here, before the copying below writes anything, and read its `## Notes`:
**an entry opening `BLOCKING, from the binding —` is a stop.** Quote the entries whole. That class is
the binder's finding that the objective, or a criterion, cannot be demonstrated
as written without contradicting or exceeding the base, and a task that arrives here still carrying
one is the scope-origin kind — the other kind is re-cut and re-bound before the task is ever
written. What the plan said of it, in as many words, is that only the human settles it: through the
scope, re-planned in `/plan-work`, or through `/analyse-domain` producing the fact the base lacks,
after which the task re-binds and the note is gone. Writing source in the meantime encodes the
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

Where a standard was named, take it in before anything is written. Run:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --standard <the project's registry>
```

Anything but a clean pass is a stop, reported verbatim: source written against a registry that does
not hold together answers to nothing, and fixing the registry belongs to whoever owns it.

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

### 2. Implement

Spawn a `task-implementer` subagent — its judgment lives at
`${CLAUDE_PLUGIN_ROOT}/agents/task-implementer.md` — passing five things: the task file's path,
the knowledge root, the target source root, the paths of the plan's inventory nodes, and the
delivery-node contract's path — plus, where one was named, the path of **the copy** of the standard,
so what it read is exactly what the record pins. It reads the task and the nodes it binds, writes the source, and
returns the record: every path it created or modified and what each now does, every criterion of
the task answered, every bound node accounted for, and what it inferred, departed from,
preserved and deferred.

Compose and write `implementation/<epic>/<slug>.md` — the same epic and slug as the task, because
the path is the identity and nothing else names which task a record answers — from what the agent
returned plus the pin stamped on `task`, and — where a standard was named — where its copy sits and
the pin of its text. The body is exactly two headings, in order:
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

### 3. Prove

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
dismissed and why, what stays unproven, and where it disagrees with the implementation. Write
`proof/<epic>/<slug>.md`, same epic and slug again, and check it the same way.

Stamp on it the SHA-256 of the implementation record you just wrote — `sha256sum <that file>`. It
says which version of that record these tests were written against, and it is what makes a
re-delivery honest: rewrite the implementation later and leave the proof alone, and the validator
refuses the pair instead of letting tests stand that claim to prove criteria the source now
satisfies some other way.

A disagreement the author recorded is not settled here. It stays recorded: this invocation holds
two producers precisely so that one cannot overrule the other, and resolving it now would discard
the signal.

### 4. Validate, and derive the delivery

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

### 5. Report, and stop

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
- the standard this invocation followed, by the copy it took and that copy's pin, and every
  departure disclosed against it — or, where none was named, that the only project convention
  followed is what the inventory evidenced, which is the honestly narrow answer rather than a clean
  one;
- that nothing was run, and that `/review-change` is what runs the suite and judges the change,
  including holding the same source to the same standard;
- the handoff: the `/review-change` invocation ready to paste — this delivery root, this work
  root, this knowledge root and this target source root named by path as just validated; the
  tasks under review being the one task this invocation delivered, by identifier; and the file
  set being exactly the paths named above, because a review never discovers its own scope and
  this report is the only place that set exists. Two slots stay the human's: the commands to run,
  without which the failures pass does not run, and the project's standard where the project
  authored one. The handoff offers the next step and never takes it: filling the slots and
  invoking are the human's.

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
- Run a build, a suite, a linter or any command of the target project's — see "This invocation
  runs nothing".
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
