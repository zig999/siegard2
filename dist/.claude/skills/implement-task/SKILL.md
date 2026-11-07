---
name: implement-task
description: Writes the source one planned task requires and the tests that prove it, installs what the project's own standard authorizes, runs the steps that standard declares until the project builds and its suite passes, records both nodes under a delivery root — what was written, every criterion answered, every specification node the task implements accounted for, every inference, every departure, every run captured — validates the delivery against the plan, binds every node it encoded into the target's trace, and derives delivery.json. Use when a request asks to implement, build, code or deliver a task the plan already holds. Not for planning or decomposing work (that is /plan-work), not for analysing domain material (that is /analyse), not for reviewing or judging what was written (that is /review-change), and never for more than one task.
effort: medium
---

You carry one planned task from the plan into written source and the tests that prove it, and
you stop. One invocation, one task: two tasks in one invocation is two deliveries nobody can
review apart.

## Progress checklist

Copy this checklist into your working notes and tick each step as it closes. Where a step's
section is no longer in your context, read `${CLAUDE_PLUGIN_ROOT}/skills/implement-task/SKILL.md`
again before acting on it. `references/` is the directory beside that file: read a reference when
its step is reached, before acting on it.

```
- [ ] Inputs: task, project root, target, slug, else one stop naming all; standard: references/standard.md
- [ ] Root: bin/project.py <project-root>, or --here where none is named
- [ ] Plan: plan.py --check clean, else stop
- [ ] Tree: git status --porcelain over delivery root, target, task file prints nothing, else stop
- [ ] Contract: deliver.py --contract implementation, proof, finding
- [ ] 1 Situate: deliver.py --outstanding; BLOCKING note: references/blocking.md; re-delivery or
      stands: references/redelivery.md; deliver.py --standard, keep its three phase lines
- [ ] 2 Set up: run.py --run <epic>-<slug>-setup where the registry declares an install
- [ ] 3 Implement: read references/delegation.md; spawn siegard:task-implementer; a return that
      writes nothing: references/implementer-returns.md
- [ ] 4 Build: run.py --run <epic>-<slug>-build; red: references/red-build.md; produces:
      references/substrate.md; read references/records.md; deliver.py --write-implementation
- [ ] 5 Prove: spawn siegard:test-author
- [ ] 6 Suite: run.py --run <epic>-<slug>-suite; red: references/red-suite.md; deliver.py --write-proof
- [ ] 7 Validate: deliver.py --unrecorded, then deliver.py; read references/finish.md
- [ ] 8 Bind: trace.py --bind-record; keep any stale-bindings receipt
- [ ] 9 Report: handoff.py --prepare; read references/report.md; --save-report, --render; stop
```

## Required inputs

A missing input is a stop, not a default:

1. **the task** — which one, by identifier. Named by the human, or named in a request that
   names exactly one; a request that names several is a stop, and the answer is to ask which.
   Choosing for the human is choosing what gets built — but a set of one holds no choice: a
   request that names none is a stop unless the deliverable set the situate step computes holds
   exactly one task, which is then decided and disclosed in the report, never asked.
2. **the project root** — where `siegard.json` lives, named by the human. «Where the invocation
   names none, the project root is the git toplevel of the session's working directory, as
   `bin/project.py --here` resolves it, and only where that toplevel holds `siegard.json`»
   (SPEC-010 R6): there, `project.py --here` runs in place of the `project.py <project-root>` run
   below, and its `project_root:` line is the root. Its refusal is a stop.
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
disclosing it is what replaces the question. One optional input, **the project's standard**,
resolves as `references/standard.md` states; read it before that stop, which the standard can join.

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
printed exists in a conversation, which is not state, and the record would rest on it. `--excerpt
40` on each of those runs bounds what a red one hands you; `references/red-build.md` says what is
done with it.

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

Two of these steps are another judge's. Writing the source and writing what proves it are delegated
to the subagents this framework ships, each in a clean context, and the judgment of each step lives
in the agent's file — not here, and not in your memory of it. Delegating means spawning the subagent
by its plugin-scoped name — `siegard:<agent-name>` — never the bare form, which a consumer's own
`.claude/agents/` can shadow — and reading the agent's file yourself is the fallback, never the
delegation. The separation between the two is the point of the arrangement: an implementation and
its tests written in one pass agree by construction, including where both are wrong. Only where the
session cannot spawn subagents, read the agent's file under the plugin root's `agents/` directory
and apply its discipline in place — the file stays the single home of that judgment — and the report
must say which steps ran inline. Before the first spawn, read `references/delegation.md`: how to
wait for a spawned subagent, what to do when one stalls, and how a red run goes back to one that
returned.

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
stop.** `references/blocking.md` says what the stop quotes and the two doors it hands.

A record already at the path this task computes to is a re-delivery, a task carrying `stands`
delivers without writing source, and only the person names a proof-only re-delivery: for any of the
three, read `references/redelivery.md` before anything is written.

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

What the first form refuses, and the registry's pin both records carry, are in
`references/standard.md`; what `produces` drops is in `references/substrate.md`.

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

A return that writes nothing because the work already stands is a stop with its doors, never an
improvisation: read `references/implementer-returns.md`.

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

A task declaring `produces` runs less than that: read `references/substrate.md` before the run. A
red build: read `references/red-build.md` and follow it — the retries, a red only a test answers,
and a red no change to this task's own files answers.

Write `implementation/<epic>/<slug>.md` through the writer, never by hand — the same epic and
slug as the task, because the path is the identity and nothing else names which task a record
answers:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --write-implementation <delivery-root> task/<epic>/<slug> --target <the target's key> --task-file <absolute path of work-root/task/<epic>/<slug>.md> --run run/<the build run that passed> --standard <the registry's path relative to the target source root> --standard-file <absolute path of the registry> --from <the delegation's transcript> [--what "…"]... [--note "…"]...
```

What the writer reads, stamps and writes in the body is in `references/records.md`; read it before
the first write. Where the agent stopped instead of writing, `references/implementer-returns.md`
says what the report hands.

### 5. Prove

Where the task declares `produces`, read `references/substrate.md` first: a task delivered as the
substrate alone writes no proof.

Spawn a `siegard:test-author` subagent — its judgment lives at
`${CLAUDE_PLUGIN_ROOT}/agents/test-author.md` — and hand it this, filled:

```
task file:             <absolute path of work-root/task/<epic>/<slug>.md>
implementation record: <absolute path of the record step 4 wrote — or, where step 4 runs this
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
under `untested` with why, and a node under neither is what the report says is open.

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

A red suite: read `references/red-suite.md` and follow it — the diagnosis owed, the five ways out,
and the one that is forbidden. Where the registry declares no command at all, this step does not
run, the tests stand unexecuted, and the report says so — the narrow answer rather than a clean one.
A task delivered as the substrate alone reaches neither this step nor the one before it, for the
reason step 5 gives.

Write `proof/<epic>/<slug>.md`, same epic and slug again, through the writer the same way:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --write-proof <delivery-root> task/<epic>/<slug> --target <the target's key> --run run/<the suite run that passed> --standard <the registry's path relative to the target source root> --standard-file <absolute path of the registry> --from <the delegation's transcript> [--what "…"]... [--note "…"]...
```

The proof's stamps and its `--note` lines are in `references/records.md`.

### 7. Validate, and derive the delivery

When both records are written, hold the tree to them first — every record this invocation
wrote, and on a proof-only re-delivery the standing implementation record beside the new proof:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --unrecorded <target-source-root> <implementation record> [<proof record>]
```

How each printed path is named, and what `uncarried:` means, is in `references/finish.md`. Then run:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py <delivery-root> <work-root> <target-source-root> <specification-root>
```

What it validates, and why fixing means form and never knowledge, is in `references/finish.md`.

### 8. Bind the trace

Name the record you just wrote, once:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --bind-record <target-source-root> <specification-root> <the implementation record>
```

What the bind binds, refuses and may print — a stale-bindings receipt the report keeps whole — is in
`references/finish.md`.

### 9. Report, and stop

«The state a handoff opens with is a script's line, never the session's» (SPEC-006 R10). Run
`python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/handoff.py --prepare --skill implement-task --project
<project-root> --slug <slug> --target <target> --language <en or pt-BR, the session's>`. Write the
full report — every item `references/report.md` lists, in its order — through `bin/handoff.py
--save-report <path>`, to the path its `report` names, and fill only the fields the skeleton left
empty. Hand the person exactly what `handoff.py --render` prints over the record; it opens with
what needs the person — «A handoff opens with what needs the person, and explains after»
(SPEC-006 R1). The doors it marks are the `/review-change` and `/reconcile` ones this report
hands, each with what its entry point answered: a `refuses` is said excluded beside its
`refused:` fact, never recommended. A refusal is answered by rewriting the field it names; a state
it says has moved, by running `--prepare` again and carrying its `state` and `state_from` whole.

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
