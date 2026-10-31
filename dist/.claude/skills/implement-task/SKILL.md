---
name: implement-task
description: Writes the source one planned task requires and the tests that prove it, installs what the project's own standard authorizes, runs the steps that standard declares until the project builds and its suite passes, records both nodes under a delivery root — what was written, every criterion answered, every specification node the task implements accounted for, every inference, every departure, every run captured — validates the delivery against the plan, binds every node it encoded into the target's trace, and derives delivery.json. Use when a request asks to implement, build, code or deliver a task the plan already holds. Not for planning or decomposing work (that is /plan-work), not for analysing domain material (that is /analyse), not for reviewing or judging what was written (that is /review-change), and never for more than one task.
effort: medium
---

You carry one planned task from the plan into written source and the tests that prove it, and
you stop. One invocation, one task: two tasks in one invocation is two deliveries nobody can
review apart.

## Required inputs

A missing input is a stop, not a default:

1. **the task** — which one, by identifier. Named by the human, or named in a request that
   names exactly one; a request that names several is a stop, and the answer is to ask which.
   Choosing for the human is choosing what gets built — but a set of one holds no choice: a
   request that names none is a stop unless the deliverable set the situate step computes holds
   exactly one task, which is then decided and disclosed in the report, never asked.
2. **the project root** — where `siegard.json` lives. Named by the human; inferred rather than
   named, its absence is a stop.
3. **the target** — which of the project's target source roots this task delivers into, by the
   key `siegard.json`'s `targets` names it. Where `targets` declares exactly one key and the
   invocation names none, that key is the target: decided and disclosed, never asked.
4. **the initiative's slug** — the plan holding the task, and the delivery root its records are
   written into: both are `<slug>` under the project's `work_root` and `delivery_root`
   respectively. Absent, it is created empty for the delivery side; the work side must already
   hold the task. Where the invocation names none and the project's `work_root` holds exactly
   one initiative without `closure.md`, that is the slug: decided and disclosed, never asked. A work root holding `closure.md` is a different matter: the plan is history,
   its initiative is over, and writing new source against it is a stop. Reviewing what it
   already delivered is not — that is `/review-change`'s, and it stays possible for as long as
   the records do.

Run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/project.py <project-root>` once, before anything else.
`specification_root`, `targets`, `work_root` and `delivery_root` answer only from here: naming
one of these in the invocation instead has no effect, and where the file does not declare one,
that is a stop, not a question to work around — the report carries the `/siegard-config`
invocation ready to paste, naming the project root and every field missing. From here on, "the
work root" means `work_root/<the initiative's slug>`; "the delivery root" means
`delivery_root/<the initiative's slug>`; "the target source root" means `targets[<the target>]`;
"the specification root" means `specification_root` as resolved, required exactly as the plan
validator requires it — while the plan is live, and ignored once it is closed.

Absent inputs stop once, together: one stop naming everything missing — the task among them, where
the request named none and the situate step's deliverable set holds more than one — so the human
answers once, never a question at a time. An input a singleton decided is not missing; the report
disclosing it is what replaces the question.

One optional input: **the project's standard** — the path to the registry of rules the project set
for itself, in the project's own tree. Named, the source is written to follow it; not named, the
only convention this invocation follows is what the inventory evidenced, and the report says so.
The framework ships no rule and never owns the registry: `${CLAUDE_PLUGIN_ROOT}/schemas/standard.json`
is the contract a project's own file answers to.

The standard resolves in one order, from the same `project.py` run above, and the report says
which step answered. Unlike the roots, **a naming in the invocation wins here**. Where the
invocation names none, the file's `standard` answers **for the target**: a standard governs one
target, so `project.py` prints either one `standard:` line for a one-target project or one
`standard <target>:` line per target the file declares one for, and the line for the target this
invocation names is the answer — never another target's line. `null` there declares deliberately
that it has none for this target — the narrow path, chosen rather than forgotten, taken without
asking again. Where neither answers — no naming, no file, the file not declaring the field, or
the field declaring no entry for this target — the standard joins the single stop of absent
inputs: name it, or declare it through `/siegard-config` for this target, and the stop's report
carries that invocation ready to paste. A file that does not hold together is a stop reported
verbatim; a naming that overrode a differing file is reported with both. Below, a standard
"named" means resolved by either step.

## Before anything: the plan

Nothing is written over a plan that does not hold together. Run:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/plan.py --check <work-root> <specification-root>
```

Anything but a clean pass is a stop: report the output verbatim and go no further. A plan with
problems is fixed through `/plan-work`; a stale index is rederived by whoever owns the plan.
Neither repair is this invocation's to make — delivering never writes into the work root, and
never into the specification root either.

The pin the implementation record carries is the SHA-256 of the task's own file:
`sha256:<hexdigest>`, computable as `sha256sum <work-root>/task/<epic>/<slug>.md`, and stamped by
the writer step 4 runs rather than typed. It pins the task
and not the plan's index, because a record answers one task and that is what it should be held to —
and because pinning the index would make every record in the root stale whenever any unrelated task
is added, which no entry point here is allowed to go and fix. The proof carries no task pin: what it
pins is the implementation record itself, and step 6 says why.

## Before anything: the tree

The review is `git diff`, and a diff only says what this invocation did when the tree starts
clean. Before any write, `git status --porcelain -- <delivery-root> <target-source-root>
<work-root>/task/<epic>/<slug>.md` must print nothing — the pathspec is the point: the stop's
scope is the roots this invocation writes, plus the one file it reads and pins. A pending change
elsewhere in the work root — a sibling task still being drafted, an epic for a later increment —
is somebody else's work in progress, not a reason this delivery cannot be reviewed; the task file
this invocation is about to build against and hash into the implementation record is different in
kind, because `/plan-work` already told a person to review that diff and stop there, and a pin
taken before that review happened is a hash of something nobody looked at. Output is a stop:
report what is pending and go no further — committing, discarding or overriding is the human's
decision, never this skill's. A root not under git control is the same stop: without git there is
no review, and source is the one thing here nobody can review any other way.

## Read the contract

`${CLAUDE_PLUGIN_ROOT}/schemas/delivery-node.json` is the single home of what a delivery node may
and must declare — the kinds, the fields each kind requires, and one example per kind. Most of it
belongs to kinds nobody you spawn this run will write, so none of them is handed the file. Run:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --contract implementation
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --contract proof
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --contract finding
```

Each prints one self-contained slice — the fields that kind admits, or that `$defs` entry, with
every `$ref` already inlined — and that is what step 3, step 5 and the diagnosis below hand to
their subagent, verbatim, in place of the file's path. Do not work from memory of any of them,
and do not restate them: what you remember is not what the validator will apply.

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

`--excerpt 40` on each of those runs is what a red one hands you: the last forty lines of the
step that failed, printed before the record and bounded by the runner rather than by you. Take
that and go — never a command of your own over the log. A whole failing log is unbounded, and
cutting one down by a pattern that looks like a failure is this framework guessing at a
reporter's format, which it refuses everywhere else and which the runner's own `--help` declines
by name. The excerpt is what goes back to a producer and what the report quotes. It is never a
diagnosis's input: the `failure-diagnostician` is handed the run's directory and reads the whole
of what it holds, which is why the record names the log rather than carrying it.

That capture is why this invocation may run at all: a session that could run the suite it just
wrote would otherwise iterate quietly until the suite went green, and what failed on the way would
exist nowhere. `run.py` refuses to write a run under a name that already
exists, so a session that tried four times leaves four directories with four verbatim logs, and
the record points at the one that passed while the three that did not keep their names. Iterating
is not forbidden here. It is recorded, and recorded is stronger than forbidden: everything the
producer saw is readable by somebody else.

**The skill runs; the agents do not.** No agent this framework ships holds a shell, and none gains
one here. Writing source stays the `task-implementer`'s even when a run comes back red: a failure
goes back to the agent with what the run printed, and the source is written again. A skill that
patched a file to make a build pass would be the writer that nobody separated from the witness.

## The order

```
situate → set up → implement → build → prove → suite → validate → bind → report → stop
```

Two of these steps are another judge's. Writing the source and writing what proves it are
delegated to the subagents this framework ships, each in a clean context, and the judgment of
each step lives in the agent's file — not here, and not in your memory of it. Delegating means
spawning the subagent by its plugin-scoped name — `siegard:<agent-name>` — never the bare form,
which a consumer's own `.claude/agents/` can shadow — and reading
the agent's file yourself is the fallback, never the delegation. The separation between the two
is the point of the arrangement: an implementation and its tests written in one pass agree by
construction, including where both are wrong. Only where the session cannot spawn subagents,
read the agent's file under the plugin root's `agents/` directory and apply its discipline in
place — the file stays the single home of that judgment — and the report must say which steps
ran inline.

A spawned delegation runs in the background and the harness delivers a notification when it
answers; the session waits for that notification and nothing else — never a `sleep`, a scheduled
wakeup, an agent listing or a message to the delegation, each of which is a turn spent reading
nothing — and reads the return when the notification names it.

A spawned subagent that stalls is never resumed. Its partial work already stands on disk — a
draft implementation, a run directory, a half-written record — and resuming a stalled context
asks it to continue from a state it may no longer hold, where a fresh one asks it to continue
from the one thing that is actually still true: what the tree now shows. Spawn again under the
same task, naming what the prior attempt already left in place and what remains, and let the new
attempt read the tree rather than inherit the old context. Nothing here is lost by this: the
record this step writes is judged against the tree at the end, never against how many attempts it
took to get there.

**A delegation that returned is the opposite case, and a red run is where it comes up.** It holds
the task, the contract slice, the standard and every file it read, all of it consistent with the
tree it just wrote — the state a stalled context is doubted for holding is exactly the state this
one has. So what the run printed goes back to that delegation where the session can reach one
that has returned, rather than to a fresh spawn of the same agent: a fresh spawn is handed the
same block again and reads its way back to where the first one already stood. **What it returns
is the whole mapping, revised — never the part that changed.** Both records are rewritten whole,
so a delta would leave a record assembled out of two answers, which is what an amended record is
refused for.

Where the session cannot reach a delegation that has returned, spawn again, and hand the same
filled block as the first time plus what the run printed and what remains. Either way the runs
keep their own names on disk and the record is judged against the tree at the end, so which of
the two happened changes nothing about the delivery — only what it cost.

The three steps that execute — set up, build, suite — run only where the standard names commands.
Where none was named, or the registry declares none, they do not run, the report says so, and what
this invocation hands over is source alone — a narrower answer, and never presented as a
clean one.

### 1. Situate

One command answers where the task stands, and it validates the delivery on the way:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --outstanding <delivery-root> <work-root> <target-source-root> <specification-root>
```

On an empty delivery root it reports every task without a record; on a populated one it also
reports, per task, what each one waits on — the dependencies with no record yet, an artifact a task
of this plan produces and the tree does not hold, and a standing blocking note — and then the set
deliverable now. Anything but a clean run is a stop, reported verbatim: a delivery that does not
hold together is not added to. Where the invocation named no task and the deliverable set holds
exactly one, that one is the task — decided here and disclosed in the report; a set of more than
one is the stop that asks which.

One of its lines is a refusal, and it is settled before anything is written:

- **A task this one builds on has no record.** Stop, and name it. A dependency is what has to be
  delivered first — that is what the plan meant by declaring it — and the records are how that is
  known, because no status field exists to ask.
- **The named task is not in the plan.** Stop — and hand over the door, not just the wall: the
  report ends with a `/plan-work` invocation filled with everything this invocation already knows
  in the terms that skill actually takes — the project root, the target by its key, and the
  initiative's slug — leaving only the scope for the human to state. Do not fill it with roots:
  `/plan-work` reads `specification_root`, `targets` and `work_root` from the project file, and
  naming one in the invocation has no effect there. A task the plan does not hold is planned into
  it, never improvised past.

A second refusal the report names and does not make. Open the task file here, before anything below
is written, and read its `## Notes`: **an entry opening `BLOCKING, from the specification —` is a
stop.** Quote the entries whole — from the file, which is what holds them, rather than from the
report, which read the same file. What that class means is the binder's, defined in
`agents/execution-contract-binder.md` and never re-derived here — what matters at this step is
that it is a stop and whose settlement it waits on. A task that arrives here still carrying one is
the scope-origin kind — the cut-origin kind is re-cut and re-implemented against before the
task is ever written. What the plan said of it, in as many words, is that only the human
settles it: through the scope, re-planned in `/plan-work`, or through `/analyse` amending the
specification, after which the task is re-run through the implement-against step and the note
is gone. Both doors leave here ready to open: the report ends with the `/plan-work` invocation
and the `/analyse` invocation, each filled with everything this invocation already knows — the
roots by path, the note quoted as the conflict the scope must settle or as the statement the
specification must amend — leaving to the human only the choice of door and what only the human
holds. Writing source in the meantime encodes the contradiction as though the business had
decided it: here the specification is not silent but overruled — the failure this whole
discipline exists to prevent. The class is the binder's judgment and not yours to overrule: a note you
disagree with is still a stop, and the disagreement goes in what you report.

**This stop is the skill's and the validator's, and each holds what only it can.** Here, the
stop is made before a file is written, and both doors leave ready to paste — the two invocations
that settle it are composed from what this invocation already knows, which no validator holds. In
`deliver.py`, a record over a task whose `## Notes` still carries the entry is refused, quoting it
and naming both doors, so a delivery that wrote past this stop does not derive; and `--outstanding`
says which tasks carry one, because a caller choosing which task to deliver learns it there rather
than by opening every task file. A blocking note is cleared by amending the scope or the
specification, never by the record: by the time either lands the task has re-run through
implement-against and the note is gone, and the record is written then.

A third fact the report does not carry, because you can see it directly: **a record already at the
path this task computes to.** That is a re-delivery, not a stop, and the report says so. Every run
name below is deterministic per task, and `bin/run.py` refuses a name that already exists — so a
re-delivery names each of its runs with the next free `-N` suffix the delivery root's `run/`
directory does not yet hold, exactly as a retry within one invocation does. `ls <delivery-root>/run`
is how that is read; a name is never improvised past the refusal, and a phase is never retyped from
prose to avoid it. Both records are rewritten whole rather than amended — a record amended across two acts of writing
describes neither, and the proof's pin on the implementation refuses the pair if you rewrite one
and leave the other. `git diff` over the two is then the history of the delivery.

One narrower re-delivery exists, and only the human names it — stated in the invocation, never
inferred from the tree: **the implementation stands, and only the proof must answer a tree that
moved.** Two plain cases. A sibling task's legitimate delivery falsifying an assertion that
claimed more than this task's criteria establish — totality over ground the two tasks share. And
a certification an auditor refused while naming what would close it: a reconciliation or a
review judged a node this task encodes as decided by reading, with `remainder: testable` and the
assertion in `remainder_why`, and `trace.py --owed` lists it as the work a test closes. For that
case the invocation states three things the record holds — the node's identity, the assertion
verbatim, and the proof file(s) the record named — and they reach the test author as its
`remainder` line below: the assertion is the obligation the new test fails for, and the test
names the node under `demonstrates`, so the next review's staging carries the claim to
certification without anyone composing it. The proof's `## Notes` names the record that left the
remainder. Nothing here decides that a remainder is worth a test — `--owed` prints the count of
bindings a reading still decides on the file, and whether closing this one frees a judge is what
a person weighs.
Steps 3 and 4 do not run: the implementation record is not touched, and the proof is rewritten
whole — never amended — by a fresh test author reading the tree as it stands now, with the suite
running and captured as ever, and written through `--write-proof --replace` as step 6 states,
every `--note` line it carries given again. The pin the writer restamps is valid precisely
because the implementation record did not move; what the validator refuses is the opposite
direction, an implementation rewritten under a proof left behind. Two things hold the mode
honest. Before anything is written, run

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --check --all <target-source-root>
```

over the target: the implementation's files are
bound with digests, and one that moved since the bind is exactly what makes "the implementation
stands" false — that drift is a stop. Where what moved it is a later task's own delivery over
that file, the answer is not this task's at all: the test is that delivery's to rewrite, under
step 7's second `test` exit; anywhere else, the answer is a full re-delivery. **`--all` is what
makes this mode's premise checkable at all**, and it is the one place in this framework that
needs it: a project may declare a target freely edited, and an ordinary check then holds that
class back as noise a reader cannot act on — but here it is the whole question, so this call asks
for the findings rather than the report. And the reason the proof had to move goes in the record's
`## Notes`, naming the task whose delivery falsified it, so the diff carries what only the
conversation would otherwise hold.

**A task carrying `stands` is delivered the same way from its first delivery, because its plan
says so** — the one case where the narrower route is read from the task rather than from the
invocation: `/plan-work` writes `stands` only over files the trace already binds to every node
the task implements, in the proof increment the human names or in an ordinary decomposition
alike. The implementation stands at the files `stands` lists,
and nothing in this delivery writes source. Before anything is written, the same `trace.py
--check --all` holds every one of those files current — a moved one makes "stands" false, and the task is
not delivered: the door is `/reconcile` over the files that moved, which the person asks for,
and the report hands it with those files named — and `trace.py --encodes <target-source-root>
<each file>` must still list every node the task implements for them. Step 3 does not run. Step
4 does, over the tree as it stands: the build is what shows the standing implementation still
builds, and the record points at that run as any implementation record does. No producer is
spawned for the record: you compose the return yourself, from the plan and from the record the
task's `sources` name, never from a reading of the source — the same mapping the
`task-implementer` would return, as plain YAML in a file — and write the record through
`--write-implementation --from-text <that file>`, stamps and all, exactly as step 4 states.
What the mapping holds: `stands` exactly as the task lists it, `files` empty, one
criteria entry per criterion — `met: true`, its `how` saying that the implementation stands at
those files and the proof below decides it — and one node answer per node the task implements,
`how` quoting where the fact is held as the named record's reading states it, never
`encoded_at`: this delivery binds nothing, and step 8 prints that and moves on. The test author
receives each criterion's assertion as its `remainder` line and the task's `stands` as the files
under test; the proof names the node under `demonstrates`, and the review that reads it — with
the `stands` files in its file set, which the validator holds — certifies it.

Where a standard was named, take it in before anything is written. Which command depends on one
field of the task file — already open from the note check above — read as a yes or a no:
**does the task declare `produces`?**

Where it does not, the tree is held to what the registry presupposes on the way in:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --standard <the project's registry> --against <target-source-root> --specification <specification-root>
```

Where it does, drop `--against` and run the registry check alone:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --standard <the project's registry> --specification <specification-root>
```

Either way, anything but a clean pass is a stop, reported verbatim. A clean pass prints each
delivery phase — setup, build, suite — composed for `bin/run.py`, timeout included: **keep those
three lines; they are the step lists the runs below paste in**, and the validator holds each
captured run to exactly that selection, so a phase retyped from prose is a transcription error
waiting for the refusal.

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

Then note the registry's own path, relative to the target source root, and its absolute path:
the writer each record goes through stamps the SHA-256 of its text as read when the record is
written, `sha256sum <target-source-root>/<path>` by hand. Nothing is copied: the record points at the
project's own file, the same way `files[].path` already points at code without a second copy of
it. That pin is a citation of what this record read when it was written, not a standing guarantee
— the project's registry is free to keep evolving, and this record stays held to the text it
actually read rather than to whatever the file says later.

What the command printed is also everything this invocation reads *from* the registry: each step
with its command and its bound, which step installs and which proves, and the packages it
authorizes, by name. Do not open the registry's text here — the rules it declares are its two
producers' to read, each is handed the path below, and a registry read twice is the same registry
at twice the cost.

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
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/run.py <delivery-root> --run <epic>-<slug>-setup --cwd <target-source-root> --excerpt 40 <the setup phase the situate step's registry check printed>
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

Spawn a `siegard:task-implementer` subagent — its judgment lives at
`${CLAUDE_PLUGIN_ROOT}/agents/task-implementer.md` — and hand it this, filled:

```
task file:             <absolute path of work-root/task/<epic>/<slug>.md>
specification root:    <absolute path>
target source root:    <absolute path>
inventory:             <absolute path of each inventory node whose area reaches where this
                        task lands, one per line>
implementation slice:  <the --contract implementation output above, pasted whole>
standard:              <absolute path — omit this line where none was named>
authorized packages:   <each package the registry authorizes, by name — omit where it
                        authorizes none, or where no standard was named>
produces:              <each path the task's `produces` declares — omit where it declares none>
reference:             <each path the task's `reference` declares, resolved against the work
                        root — omit where it declares none>
earlier record:        <absolute path of the implementation record this re-delivery replaces —
                        omit on a first delivery>

You write no file under the delivery root: return the record's content as text.
```

Every path is absolute, and the contract slice is pasted rather than cited: a path resolves only
where the delegation's own read scope reaches it, and a slice named instead of pasted is a
delegation composing the record from memory of a shape the validator does not apply.

Two of those lines carry a rule of their own. **Pass no reference the task did not name** — a
delegation sent looking through `intake/` for something helpful is reading the scope, which is
the one document this route exists to keep out of the writing — and a `reference` path that
resolves to nothing is a stop, named, because guessing which file was meant is the guess the
field exists to remove. **`authorized packages` is a whole list or an absent line**, never a
selection: what it admits is what a human approved, and narrowing it here is this invocation
deciding a manifest.

**A return that writes nothing because the work already stands is a stop with its door, never an
improvisation.** The tree is as it was found and the delivery root gains nothing: the record
writer admits a task that writes no source only with `stands`, and `stands` is `/plan-work`'s.
«A delivery whose implementer finds every criterion of the task already met by source the tree
holds writes no record and stops, naming the files that hold the fact.» (SPEC-004 R20) Over the
files the return names:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --encodes <target-source-root> <each file named>
```

The output decides the door: «Where the trace binds every node the task implements to those
files, the door is the plan over this slug carrying `stands` over them; where it does not, the
door is the reconciliation over them, and the plan waits for that binding.» (SPEC-004 R20) The
first is `/plan-work` over this slug naming the task and those files, which writes `stands` only
where `--encodes` confirms them — «every file it names is bound in the trace, before the task is
written, to every node the task implements» (SPEC-004 R18); the second is `/reconcile` over those
files, and the plan would refuse them. Report the stop with the output verbatim and both doors
ready to paste, the one the output decides as the recommended and its kind derived, as step 9's
bullet on a stop that hands more than one door says. Taking either is the person's. The
orchestrating skill logs this stop as `already-met` wherever it does not take the door itself.

**A re-delivery whose task's own files already hold the fact is not that stop.** «A re-delivery
of a task whose own earlier implementation record names every file that holds the fact is not
the stop R20 states: the record is written again over those files, answering the task as it
stands.» (SPEC-004 R21) That is the re-delivery a re-plan leaves owed — a re-bind that widened
what the task implements, a criterion that reads differently and is already met — and the
`earlier record` line is what lets the implementer see it: a return naming those files, each
with what it does now and every node answered as it stands, is written through
`--write-implementation --replace` like any re-delivery, and the proof follows it whole. A
return that finds the fact in a file the earlier record does not name is the stop above, and
step 7 refuses the record that names one anyway.

**Every path the returned record names is relative to the target source root** — the directory
the registry's commands run from — never to the repository around it. `produces` is held to
`files` by spelling, and a registry scope reaches a file only under the same anchor, so a record
spelling paths from the repository while the registry spells them from the target answers to no
rule and satisfies no `produces`.

### 4. Build

Everything the registry declares except the step whose role is `suite`, in the order it declares
them, with the install first so that whatever the implementer added to the manifest is real before
anything reads it:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/run.py <delivery-root> --run <epic>-<slug>-build --cwd <target-source-root> --excerpt 40 <the build phase the situate step's registry check printed>
```

The timeout and the step list are the registry check's `build:` line, verbatim — composed by the
same function that will hold the captured run to them, never re-derived from this paragraph.
`run.py` stops at the first step that does not pass, so a tree that did not install is never
type-checked and the log says which one it was. Where the step that failed is one the registry
check listed as deciding a constraint, the red is that constraint's: name it beside the step when
the run goes back to the producer and again in the report, so a reader meets the node the tree
broke and not only the file.

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
back to the `task-implementer`, re-entered as *The order* says — the source is its to write, and
a skill that patched a file to turn a build green would be the writer nobody separated from the
witness — and run again under `<epic>-<slug>-build-2`, then `-3`. Every attempt keeps its directory and its log, because the
runner refuses a name that already exists. That refusal is the whole reason this invocation is
allowed to iterate at all: what failed on the way is readable afterwards by somebody who was not
here.

Giving up is the stop. Report every run by path, what the last one printed, and write no record:
a record over a red run is refused by the validator anyway, and the point of stopping here is that
it was never composed.

**A red only a test can answer is the test author's, and it is answered before the record.** The
implementer writes no test, so where the fix a red names lies in a test — one the registry
requires beside a file this delivery wrote, or an existing one this delivery's source no longer
compiles under — no return of the implementer turns the build green. «A build red whose fix lies
only in files the project declares as its tests is answered by the delivery's test author, before
the implementation record is written» (SPEC-004 R24). Which files the fix lies in is the
implementer's to say, re-entered with what the run printed; which of them are tests is a script's:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/project.py <project-root> --declared-tests <the target's key> <each path the implementer named>
```

Where it calls every path a declared test, the implementer keeps its source, and re-entered once
more it returns the whole mapping over that source; that final reply is what the record will be
written from. Step 5 runs now, ahead of the record: the test author is handed the implementer's
transcript in the record's place, and the run and those paths under `red build`, and it writes
the proof whole, those files with it. A path the proof of another task names is answered here only as step 6 answers a
test an earlier task owns, read from that task's implementation record and this delivery's return:
«A test the proof of another task names is answered here only where this delivery's files include
one that task's implementation record names; otherwise the red is a stop» (SPEC-004 R24) — the stop
below, naming the test and the task whose proof names it. Then the build runs again under the next
name. A red that now names source goes back to the implementer and one that names a test to the
test author, each re-entered; green, the record is written over that run, and step 5 has run —
go on to step 6 with the proof's return in hand. Where some named paths are declared tests and
some are not, the implementer answers its own first and the build runs again: what is left of the
red decides whose it is.

**A red no change to this task's own files can answer is a stop of its own, and never a retry.**
Two shapes, and the first is read from the tree rather than from anyone's account of it: after the
implementer returns, `git status --porcelain -- <target-source-root>` printing nothing means this
delivery changed nothing under the target, so a red build is the tree's own — it was red before
this invocation began, and no return of this task's producer can turn it green. The second is
read from the producer: the fix a diagnosis or the run names lies only in files no record of this
task names — another task's, or no task's, and not a test the target declares, which the shape
above hands the test author — and the implementer says so rather than writing there. Either way, write no record, report the run by path with the files the fix would touch,
and hand `/plan-work` over this slug as the door — a corrective increment or an ordinary one, the
person's to choose. The orchestrating skill logs it as `outside-task`; trying the same delivery
again pays the run again and answers nothing.

Write `implementation/<epic>/<slug>.md` through the writer, never by hand — the same epic and
slug as the task, because the path is the identity and nothing else names which task a record
answers:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --write-implementation <delivery-root> task/<epic>/<slug> --target <the target's key> --task-file <absolute path of work-root/task/<epic>/<slug>.md> --run run/<epic>-<slug>-build --standard <the registry's path relative to the target source root> --standard-file <absolute path of the registry> --from <the delegation's transcript> [--what "…"]... [--note "…"]...
```

`<the delegation's transcript>` is the output file the harness names for the spawned agent: the
return is read from its final reply — or from the `message` of a hand-back the harness confirmed
delivered — verbatim, never retyped from the notification that relays it. Where the step ran inline, the mapping is in a file and `--from-text <file>` names it. The
record is a function of that return, the task file, the standard and the run: the writer stamps
`target` — input 3's key, the root every path in the record is spelled from, which the
validator resolves the record at and never the one an invocation happened to name — the pin of
the task file on `task`, the registry's own path and the pin of its text as read now, and the
build run that passed. Omit `--standard` and `--standard-file` where no standard was named, and
`--run` where nothing ran. A return carrying any of those keys is refused naming the key: the
producer answers for what it decided, and what the invocation knows is stamped here. Every
dependency the agent added is in its return under `installed`, and the writer carries it
through as returned.

The body is the writer's as well, exactly two headings in order: `## What it is` from each
`--what` line, defaulting to the return's `summary`; `## Notes` from each `--note` line,
defaulting to the literal line `None.` One sentence per line. `--note` carries what a reader
meeting the record is owed and no field holds: where this delivery built the substrate, the
sentence the substrate paragraph above names — which steps did not run and why — so the record
does not read as a project that builds. The writer validates the record as `--node` validates
one before writing it and writes nothing while it finds a problem; a refusal is a composition
error at the file that made it, corrected in the invocation or sent back to the producer, never
worked around. It prints the path written and the pin of the file.

Where the agent stopped instead of writing — an input absent, a node it implements missing, the
specification silent on a fact the work needs — that is a successful stop and not a failure of
this invocation: report what it said and write no record. A stop over a silence does not end with
a bare report: the fact the agent named is an implementation-level silence the planning route
never saw, and the report ends with two invocations filled with everything this invocation
already knows: `/analyse`, with the project root and the missing fact quoted whole as the
question the material must answer; and `/plan-work`'s decided-fact increment, with the project
root, the target, the slug, the task and the same fact. The first has the person's material
state the fact; the second has it decided blind and disclosed in the node's log. Which is the
person's — and under a goal the person armed, `/deliver-scope` takes the second. After the specification gains
the statement, the task re-runs through the implement-against step, exactly as a settled blocking
note does: the decided value can newly contradict a criterion as written, classing that is the
binder's, and the re-bind is also what repairs the case where the fact lands in a node this
task's `implements` does not yet name. Where it wrote files and then stopped, the run failed: say
which files exist, and leave them for a person to look at rather than tidying them away.

### 5. Prove

**A task delivered as the substrate alone has nothing to prove, and no proof record is written.**
«A task delivered as the substrate alone — it declares `produces`, and nothing it wrote is a file a
rule of its standard reaches — owes no proof.» (SPEC-004 R23) There is no source for a test to
reach, and a proof requires at least one test precisely because a test that cannot be said to fail
for a stated reason is one nobody can evaluate — over an empty tree every entry would be that.
Whether this task is that one is the validator's answer, never this invocation's reading of what
the task built:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --outstanding <delivery-root> <work-root> <target-source-root> <specification-root> --scope task/<epic>/<slug>
```

Where it names the task `implemented as the substrate alone, which owes no proof`, this step and
the next do not run: say so in the report and go to step 8. Composing a proof anyway would be the
one thing worse than the absence — a record asserting that tests hold up a task, written where no
test could exist. Anywhere else the task proves like any other, a task that built the substrate and
also wrote a file a rule reaches included: «Every other task owes one, a task that built the
substrate and also wrote a file a rule reaches included.» (SPEC-004 R23) Its tests are files the
suite runs, and a record with no proof beside them is a task nobody can hold up.

Spawn a `siegard:test-author` subagent — its judgment lives at
`${CLAUDE_PLUGIN_ROOT}/agents/test-author.md` — and hand it this, filled:

```
task file:             <absolute path of work-root/task/<epic>/<slug>.md>
implementation record: <absolute path of the record step 3 wrote — or, where step 4 runs this
                        step ahead of the record, the implementer's transcript, whose final
                        reply the record will be written from>
red build:             <the build run's absolute path and each path its fix lies in — omit
                        unless step 4 runs this step ahead of the record>
target source root:    <absolute path>
proof slice:           <the --contract proof output above, pasted whole>
nodes:                 <the identity of each specification node the task implements, with the
                        absolute path of the specification root — omit where the task implements none>
standard:              <absolute path — omit this line where none was named>
underdetermined:       <every `UNDERDETERMINED, from the specification —` entry of the task's
                        `## Notes`, quoted whole — omit where the task carries none>
remainder:             <the node's identity, the assertion an auditor named as what would close
                        its certification, verbatim, and the proof file(s) the record named —
                        omit unless this is the proof-only re-delivery over a refused
                        certification, or a task carrying `stands`, where each criterion is
                        the assertion and the files are the task's `stands`>
reproduction:          <how the failure is observed — omit unless the task's criteria name a
                        failure that must stop happening>

You write no file under the delivery root: return the record's content as text.
```

The same two rules hold as at step 3: every path absolute, the slice pasted rather than cited.

The nodes are handed over because each is an obligation of the proof, not a reference: «Where a
node the task implements states a fact a finite test decides, the proof carries a test that fails if
that fact stops holding, whole, and names the node on that test» (SPEC-004 R10). The author reads
the fact and decides whether a finite test decides it; a node it leaves without a test it names
under `untested` with why, and a node under neither is what the report below says is open.

The `underdetermined` set was already read for you — the situate report quotes these entries per
task, by their opening, so what you hand over is what a script found, and an entry the report
carries and your collection lacks is your collection wrong rather than the report's. Quote them
from the task file all the same, which is what holds them.

### 6. Suite

Every step the registry declares, in order, ending with the one whose role is `suite`:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/run.py <delivery-root> --run <epic>-<slug>-suite --cwd <target-source-root> --excerpt 40 <the suite phase the situate step's registry check printed>
```

The timeout and the step list are the registry check's `suite:` line, verbatim, for the same
reason the build's are.
The checks run again here rather than only at the build, and the repetition is deliberate: a rule
about where a test file sits or how it is named reaches files that did not exist when the build
ran, so a build-only pass would leave every rule about tests decided by nothing. Each step that
already passed passes again in seconds; the runner stops at the first that does not.

**A red suite is a stop, and which way out applies is diagnosed, never guessed.** Nothing further
is written — the implementation record stands, because its own run passed, and no proof record is
composed, so `deliver.py --outstanding` reports the task as implemented with no proof holding it
up, which is true and is the state a person should meet. Report the run by path and the tests
that failed.

Where the step that failed is the one whose role is `suite`, spawn a `siegard:failure-diagnostician`
subagent — its judgment lives at `${CLAUDE_PLUGIN_ROOT}/agents/failure-diagnostician.md` — and
hand it this, filled:

```
run:                   <absolute path of the run's directory under the delivery root>
target source root:    <absolute path>
nodes:                 <the identity of each specification node the task implements, with the
                        absolute path of the specification root>
finding slice:         <the --contract finding output above, pasted whole>
file set:              <every path the implementation record's `files` and the tests just
                        written name>
```

Always, on every red of that step, and never your own reading of the log in its place: a session
probing flakiness with commands of its own is composing commands the registry never declared,
which this skill forbids below, and the diagnosis is the licit form of the same question. Where
an earlier step of this run failed instead — a typecheck or a lint reaching the files just
written — no diagnosis is owed: the log names the file, and that red goes back to the producer
whose file it is, exactly as a red build does.

**The `cause` the diagnosis returns is one of the contract's four, and it opens five ways out.**
Four of the five it settles on its own. The fifth it does not: where the cause is `test`, which
of that cause's two exits applies turns on who owns the failing test, and the diagnosis returns
the file the run named without being told what this delivery wrote. This invocation knows —
the tests step 5 just wrote are in the proof it is about to compose, and everything else is
somebody else's. A file in that set takes the first `test` exit; any other file takes the second.

`code` — the source is wrong: the fix goes back to the `task-implementer` with the findings, that
delegation re-entered rather than respawned, and the suite runs again under
`<epic>-<slug>-suite-2`, with the first run keeping its name. Where the implementer returns that
the fix lies only in files no record of this task names, the red is the stop step 4 names for a
red no change to this task's own files can answer. `build` — nothing ran, because a
compile the suite step performed itself failed, and every failure the output lists after it
describes a binary nobody built. No registry owes a step that compiles
before the suite, so this is the same red as a typecheck step's, arriving one step later instead
of never: it goes back to the producer whose file the compiler named — the `task-implementer` for
source and the `test-author` for a test, that delegation re-entered too — and the suite runs
again under the next name. Nothing here waits on a person. `test`, on a test this delivery
wrote — the two producers disagree and that disagreement is what the red is: the proof asserts
what the criterion requires and the implementation does not satisfy it, and only a person
settles that. The report quotes the diagnosis's evidence and correction in full, whole findings
and not a summary of them — a diagnosis obvious enough to look mechanical is still a person's
call to make, and the report's business is to make that call fast, not to make it for them.
`test`, on a test an earlier task owns — what broke it is not a regression but
this delivery's own legitimate files, and which of two shapes it took is read from the two
implementation records, never from the assertion's wording: whether a path this delivery's
`files` names is one the owning task's `files` names too. **Where none is**, the old assertion
claimed more than its task's criteria establish, totality over ground the two tasks share, and
this delivery falsified the excess beside it. That test is not edited from here, whatever the
temptation: the way out is the proof-only re-delivery the re-delivery paragraph names, over the
task that owns the test, and it is the human's to invoke. The report hands that invocation ready
to paste — the owning task by identifier, the assertion the run named, the file this delivery
added — and says plainly that it runs only after the human commits this delivery's pending
state, because that invocation's own clean-tree stop refuses a tree still carrying it. **Where
one is**, this delivery rewrote a file the owning task bound — the shape a corrective increment
takes, cut over that very file — and the assertion states what the file did before the
specification moved. The owning task's implementation no longer stands as its record describes,
so the proof-only re-delivery is not open to it: its own `--check --all` would refuse before a
line was written, and an invocation handed toward that refusal costs a round trip and answers
nothing. The test is this delivery's to answer. The `test-author` is re-entered and rewrites it
whole — never trimmed, never narrowed — against the nodes as they stand now; it joins this
proof's `tests`; the record's `## Notes` names the owning task, the assertion the run named and
the file this delivery moved; and the suite runs again under the next name. The owning task's
own records are left as they are: each describes the tree it was written against, which is what
a record is, and what the file asserts now is this proof's to say. And `setup` — neither the code nor the test
was reached, because the harness or the environment it needs did not stand up: that is not this
delivery's defect and not its to fix, so nothing is sent to any producer. Run the suite again,
once, under the next name. A second consecutive red the diagnosis reads the same way is a stop:
infrastructure failing twice is a fact for a person, and the report quotes both diagnoses and
hands the rerun invocation ready. That exit licenses exactly one thing — the same suite,
again — and the run is what decides; a fix routed through it would be a fix nobody diagnosed.

**One more way out exists, it is forbidden, and it is the one that is easy.** A test is never
weakened, deleted, narrowed or rewritten to make the suite green. This invocation holds two
producers precisely so that one cannot overrule the other, and a test edited until it passes is
exactly that overruling, performed where nobody would see it. The `test` exits over a test an
earlier task owns exist precisely so this one never looks necessary: whichever shape applies, the
assertion is rewritten whole by the producer class that owns proofs — in its own invocation where
the owning implementation stands, in this one where this delivery moved what that task bound —
and never trimmed to unblock a run. What makes the rule enforceable
rather than pious is that the runs are on disk: four attempts leave four logs, and a test that
changed between them is in the diff beside them.

Where the registry declares no command at all, this step does not run, the tests stand unexecuted,
and the report says so — the narrow answer rather than a clean one. A task delivered as the
substrate alone reaches neither this step nor the one before it, for the reason step 5 gives.

Write `proof/<epic>/<slug>.md`, same epic and slug again, through the writer the same way:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --write-proof <delivery-root> task/<epic>/<slug> --target <the target's key> --run run/<epic>-<slug>-suite --standard <the registry's path relative to the target source root> --standard-file <absolute path of the registry> --from <the delegation's transcript> [--what "…"]... [--note "…"]...
```

The same `target`, and — where a standard was named — the same stamps: the registry's own path,
the pin of its text as read now, and the suite run that passed on this record too, exactly as
the implementation carries its own — the rules about how a project writes its tests reach files
no implementation ever lists, so a departure from one is the proof's to disclose and resolves
against the pin the proof itself carries. The writer reads `implementation/<epic>/<slug>.md`
from disk and stamps its SHA-256 on `implementation` — `sha256sum <that file>` by hand — which
says which version of that record these tests were written against, and is what makes a
re-delivery honest: rewrite the implementation later and leave the proof alone, and the
validator refuses the pair instead of letting tests stand that claim to prove criteria the
source now satisfies some other way.

A disagreement the author recorded is not settled here. It stays recorded: this invocation holds
two producers precisely so that one cannot overrule the other, and resolving it now would discard
the signal.

What `--note` carries on a proof is every sentence an earlier paragraph says its `## Notes`
names — the task whose delivery falsified an assertion, the record that left a remainder, the
owning task, the assertion and the file this delivery moved — and, where earlier suite attempts
failed before this one passed, each red run by path with the cause its diagnosis returned, one
sentence per run. The diagnosis otherwise lives only in the conversation, and a reader meeting
three run directories beside one proof deserves the sentence that says why; the writer refuses a
proof whose notes name none of them, naming the runs, so a red attempt is never left unnamed by
oversight. A proof rewritten whole — the proof-only re-delivery, or the restamp step 7 names —
goes through `--write-proof --replace`, with every `--note` line given again.

### 7. Validate, and derive the delivery

When both records are written, hold the tree to them first — every record this invocation
wrote, and on a proof-only re-delivery the standing implementation record beside the new proof:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --unrecorded <target-source-root> <implementation record> [<proof record>]
```

«Every path a delivery created, modified or deleted under its target source root is named by one
of the delivery's records» (SPEC-004 R16). The tree started clean under this invocation's
pathspec, so what git shows changed under the target is what this delivery did, and the file set
the report hands `/review-change` is the records' — a path they leave out is one no review reads.
Each path it prints is named where it belongs: a source path in the implementation's `files`, a
test file in the proof's `tests`, or in its `files` where the path holds no test `tests` names —
with the effect the producer that changed it states, that delegation re-entered to say it where
its return did not. A path neither producer claims is reported as such and never reverted: what
to do with a change nobody explains is a person's. On a re-delivery it prints `uncarried:`
beside an unchanged path the implementation names that the record it replaces did not — «A
re-delivery names a file the tree did not change only where the record it replaces named it»
(SPEC-004 R21) — and that path is source the task never wrote: the return goes back to the
implementer, and where the fact holds only there, the stop above is the answer. Rerun until it
exits 0. A record rewritten
here goes through its writer again under `--replace`, from the producer's revised return. An
implementation rewritten changes the pin the proof carries, and the writer prints a receipt
saying so: the proof is then rewritten whole through `--write-proof --replace`, with the same
`--note` lines, so its `implementation` is stamped again from the record as it now stands.

Then run:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py <delivery-root> <work-root> <target-source-root> <specification-root>
```

This validates every delivery node against the contract, runs the checks that need the plan — the
task exists, a proof sits beside an implementation, every criterion of the task is answered
exactly once and nothing else is, every specification node the task implements is accounted for,
no task is delivered before what it builds on, every record's
pin matches its own task as it stands, each proof's pin matches the implementation beside it, and
every departure disclosed against a standard rule cites one that standard declares and sits in a
file this record says it wrote — and derives `delivery.json`. **Never write or edit
`delivery.json` yourself.** Report the command's output verbatim. If it exits non-zero, the run
failed — fix and rerun, and never describe the delivery as sound while it is not.

**Fixing means form, never knowledge.** A wrong shape — a malformed pin, a criterion paraphrased
instead of quoted, a missing entry for a node the task implements — is yours to correct. A criterion the source
does not satisfy is recorded as unmet, not talked into met. A fact the specification does not hold is not
supplied to make a check pass: it is a stop, and it was one before the source was written.

### 8. Bind the trace

The delivery's own records are disposable — the plan and the delivery root exist to get this code
written, and nothing requires either to survive the code landing. What has to survive is the link
between the specification and the files that now encode it, so a later `/plan-work` or `/analyse`
invocation can ask, without either root, whether this code and the specification it followed have
since moved apart.

Name the record you just wrote, once:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --bind-record <target-source-root> <specification-root> <the implementation record>
```

It reads that record's `nodes` and binds every entry carrying `encoded_at`, at exactly the paths
that entry lists — so nothing here is retyped, and the rule that the trace states what the record
already says rather than a second judgment about it is held by the reading rather than by you. A
node the record answers only by `how` — constrained but encoded nowhere — is not bound: there is no
file to name, and a bind with none is refused; a record naming no such node binds nothing and that
is not a failure. Where a proof exists, its criteria stay with the implementation record; the trace
binds what the source encodes, not what the tests prove.

The whole record is one act: a node or a file it names that does not resolve refuses all of it and
writes nothing, because a trace holding half a delivery's bindings reads exactly like one holding
all of them.

This is the one place in the whole invocation that touches a file outside the delivery root, the
work root and the target source root — `siegard-trace.json`, beside `siegard.json` at the
target's git toplevel — and it is not this skill's to design around: `trace.py` is the one writer,
and what it refuses (a node the specification no longer holds, a trace already bound to a
different specification root) is reported here, plainly, rather than worked around. A refusal at
this step does not unwrite the delivery: the records already validated stand on their own, and
what is missing is exactly the fact that this delivery's files and the specification it followed
are not yet linked for anyone who looks later.

One more thing the bind may print, and it is a receipt, never a refusal: **the bindings this act
left stale** — another node's binding over a file this delivery rewrote (a bind restamps only this
task's own nodes), or a file this task's nodes carried forward from an earlier bind that has since
changed. Keep the receipt whole for the report. The `/review-change` that follows this delivery is
what answers it: its conformance pass reads every file of the change against every node the trace
binds to it and restamps what cleared. Where no review will follow, the receipt is the one moment
those bindings are in the hands of whoever changed the files, and dropped here it survives only as
a `--check` finding nobody was going to run.

### 9. Report, and stop

Open as «A handoff opens with what needs the person, and explains after» (SPEC-006 R1)
states; what follows is the report that opening sits above.

Report, in this order:

- the two nodes written, by identifier, and whether this was a re-delivery;
- every path the delivery created, modified or deleted — the records' `files` and `tests`
  together, which `--unrecorded` held to the tree — this is the file set `/review-change` needs,
  and the one thing it must never discover for itself;
- every criterion recorded unmet, with what the record says about it;
- every inference recorded, and every departure — these are the decisions nobody asked for, and
  they are what a reviewer reads first;
- every node the task implements that no test demonstrates, with what the proof's `untested`
  says of it — and, where it says nothing, that the proof leaves the node open;
- everything the proof left unproven, every edge case it dismissed, and every disagreement it
  recorded;
- what the implementation deferred, and what it says must keep working;
- every node bound into the target's trace, and any binding `trace.py` refused — the trace is
  what lets a future invocation ask whether this code and the specification have since moved
  apart, and a refused binding left unreported is a delivery that looks synced when it is not;
- where the bind printed a stale-bindings receipt, the receipt verbatim, and after it one
  `/reconcile` invocation ready to paste **for the case where no `/review-change` follows this
  delivery** — the review's conformance pass judges and restamps these same bindings over the
  files it reads, so the door is taken only where that review will not run — the project root and
  the target filled in, the file set being every path the receipt names, converted to the target
  source root's own anchor (the receipt spells paths from the git toplevel, and `/reconcile` reads
  them relative to the target source root), and a slug slot left for the human to name, since
  `/reconcile` requires one and refuses a slug already taken — with the one sentence that makes
  the door real rather than decorative: it runs only after the human commits this delivery's
  pending state, because `/reconcile` refuses a named file the tree holds uncommitted. Never a
  stop, and never per file: one invocation, one file set, and taking it is the human's;
- which steps, if any, ran inline instead of in a subagent, and why;
- where this invocation stopped and hands more than one door, the door a fact on disk decides,
  as «A recommendation names the door, the criterion, the deciding fact and the reversing fact»
  (SPEC-006 R2) states. A door whose entry point would refuse its inputs as the tree stands — a
  proof increment over a node no record under `siegard-reconcile/` carries with `remainder:
  testable`, a task `deliver.py --outstanding` does not list as deliverable — is `precondition
  unmet`, and the door left is the one recommended; a door whose work the producer's own return
  says the delivered tree already holds is `already done`. The name classifies the reason for
  the log; what the person reads is the reason in plain words, with the fact quoted and what
  would change it. A stop over a BLOCKING note, a contradiction, or a suite whose diagnosis
  two producers read apart is «the person's own decision» (SPEC-006 R3): the report says so,
  what each door assumes is true, and what would settle it, and names no door;
- the validator's final output, verbatim;
- the standard this invocation followed — where it resolved from, the invocation or the project
  file by path — by its own path and the pin taken of it, every departure
  disclosed against it by either record, and what it presupposes — that the tree holds it, or, for a
  task that produced it, that this delivery is what made it hold. Where none was named, say that
  the only project convention followed is what the inventory evidenced, which is the honestly narrow
  answer rather than a clean one — and where `--outstanding` named a standard this root's earlier
  records pin, say that too: an invocation naming none over a root that remembers one is writing
  source the review will still read against those rules. Say too every line the report prints of
  records that pin no standard, or another than the one `siegard.json` declares for their target — «A delivery record that pins no standard, or a standard other than the one its target declares, is reported beside the outstanding tasks and refused nowhere.» (SPEC-007 R1) — or an earlier version of it — «a step declared after a record was written is owed by the records written after it» (SPEC-007 R3) — a statement and never a stop: an invocation may name another registry on purpose;
- every run this invocation captured, by path and by outcome, including the ones that failed —
  those are not noise and they are not a draft: they are the only record of what it took, and a
  report naming only the run that passed describes a delivery that went right the first time
  whether or not it did — with, for each red suite that was diagnosed, the `cause` the diagnosis
  returned — and every step of the registry that did not run, with why. Where this
  delivery built the substrate, that is most of them, and saying which rules they own is what keeps
  a substrate record from reading as a project that builds;
- every dependency this delivery installed, and that what those pulled in transitively is nobody's
  approval — the lockfile is what says what actually arrived, and it is in the diff;
- what `/review-change` still does that this invocation did not: it runs the same steps again over
  the whole change rather than one task's, and it judges — whether the tests prove the criteria,
  whether the source states only what the specification holds, whether it follows the same standard, and
  why anything failed. A green suite here is a green suite over one task, and two tasks that each
  passed alone are not a change that passes together;
- the handoff: the `/review-change` invocation ready to paste — the project root, the target and
  the initiative's slug filled in, since every root they resolve to was just validated above; the
  tasks under review being the one task this invocation delivered, by identifier; the file
  set being exactly the paths named above, because a review never discovers its own scope and
  this report is the only place that set exists; and the project's standard as it resolved,
  which is also where the review reads its commands from — a slot only where neither the
  invocation nor the project file answered it. The handoff offers the next step and
  never takes it: filling any empty slot and invoking are the human's — given per invocation, or
  given once for a whole route through the orchestrating entry point, `/deliver-scope`, whose
  own file bounds what it may fill.

Then stop. `git diff` over the target source root and the delivery root is the review, and it
belongs to a person.

## What you never do

- Write or edit `delivery.json` by hand.
- Record a status, a readiness, an approval or a progress figure — those fields do not exist, and
  prose does not get to hold what the contract refused.
- Judge whether the work is correct, done well enough, or fit to merge. Nothing here carries a
  ready flag: a producer that certified its own output would be the validator of its own work.
- Run a command this project's registry does not declare, or compose one. Every step is the
  registry's string, run through `bin/run.py`; a command invented here is this framework guessing
  at a stack it ships no knowledge of, and the guess would be wrong in the project that mattered.
- Write the tests in the context that wrote the source — the inline fallback is for a session that
  cannot spawn subagents, is declared in the report, and still applies each agent's file.
- Commit, stash, branch, or otherwise change the consumer's git state — a dirty tree is reported,
  and what to do with it is the human's call.
- Record which rules of the standard were in scope. That set derives from the pin and the files
  written, both of which this root holds, so a stored list would be a second answer to a question
  the root already answers — and the one nobody could check, because the producer would be writing
  it.
- Treat a disclosed departure as leave to depart. It says the departure was known and reasoned, and
  it settles nothing: the review holds the same source to the same rules and is not shown what was
  disclosed.
