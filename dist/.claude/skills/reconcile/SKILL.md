---
name: reconcile
description: Reconciles source that changed outside any task with the specification the trace says it encodes — reads the trace for which specification nodes a named file set is bound to, holds that source to those nodes through the conformance judgment, records the answer per node, and rebinds only what the judgment cleared. Use when a human edited source by hand, resolved a file during a merge, or otherwise changed code no delivery wrote, and wants the trace to describe the tree as it now stands. Not for changing the specification (that is /analyse), not for routing a wrong behavior into a task (that is /plan-work), not for reviewing what a delivered task produced (that is /review-change), and never for writing source.
effort: medium
---

You reconcile source that no task wrote with the specification it is bound to, and you stop. One
invocation, one file set.

Every other bind this framework writes comes out of a delivery: an implementation record says which
nodes the source encodes and where, and the bind states exactly that and never a second judgment
about it. This entry point exists because source reaches a tree other ways — a correction typed in
during an incident, a file resolved by hand during a merge — and nothing outside a delivery binds.
The file changes, the trace keeps asserting a digest that is not there any more, and it asserts it
silently: `--check` is the only thing that ever says so, and nothing was going to run it.

What you produce is a rebind and the record that justifies it. **You never write source, and you
never write a specification node.** Where the reconciliation cannot be made — where the source now
states something no node holds — you bind nothing and hand back the two invocations that could
resolve it, without choosing between them.

## Required inputs

A missing input is a stop, not a default:

1. **the file set** — every path this reconciliation covers, listed explicitly, each relative to
   the target source root. Named by the human. **Never discovered**: a reconciliation that chose
   its own scope covers a different set each run, and what it writes is the one claim this
   framework keeps after every plan and delivery root is gone.
2. **the project root** — where `siegard.json` lives. Named by the human; inferred rather than
   named, its absence is a stop.
3. **the target** — which of the project's target source roots these files sit under, by the key
   `siegard.json`'s `targets` names it.
4. **the slug** — this reconciliation's own name, under `siegard-reconcile/` at the target's git
   toplevel. A slug already taken is a stop and not a suffix: the record it would overwrite is the
   justification for a binding that is still in the trace.

Run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/project.py <project-root>` once, before anything else.
`specification_root` and `targets` answer only from here: naming one of them in the invocation
instead has no effect, and where the file does not declare one, that is a stop — the report carries
the `/siegard-config` invocation ready to paste, naming the project root and every field missing.
From here on, "the target source root" means `targets[<the target>]`, and "the specification root"
means `specification_root` as resolved.

**No work root, no delivery root, no task, no plan.** This entry point deliberately asks for none
of them, and that is the whole of what it adds: the judgment it runs already existed and was
reachable only through a delivery that a hand edit does not have.

Absent inputs stop once, together: one stop naming everything missing, so the human answers once —
never a question at a time.

## Before anything: the tree

Here the usual rule inverts by half, and the half that inverts is the point. Everywhere else a
pending change is somebody's work in progress; here it is the subject.

**The named files must be committed.** `git status --porcelain -- <each named path>` must print
nothing. Not because a pending edit is hard to read, but because a bind records a digest: the digest
of an uncommitted edit points at content the next checkout erases, and the drift that would report
afterwards is drift nobody caused. Output is a stop that names what is pending — committing or
discarding is the human's decision, never this skill's.

`siegard-trace.json` must be clean for the same reason every other entry point wants its own output
clean: it is what this invocation writes, and a diff only says what this run did when it starts from
a committed state. A target source root not under git control is a stop as well — without git there
is no trace file's history, and the record you write points at a commit that has to exist.

The rest of the repository is not this skill's business. The pathspec is the scope.

## Read the contract

Read `${CLAUDE_PLUGIN_ROOT}/schemas/reconciliation.json`. It is the single home of what a
reconciliation record may and must declare — the fields, which of them a cleared node carries and
which a node the judgment refused carries instead, and one example per outcome. Do not work from
memory of it, and do not restate it: what you remember is not what the validator will apply.

`${CLAUDE_PLUGIN_ROOT}` is set where this skill runs as an installed plugin. Where it is not, the
plugin root is the directory that holds `schemas/` and `bin/` side by side — in a vendored install,
the `.claude/` directory this skill's tree sits under. Every path below resolves the same way.

## The order

```
situate → locate → judge → record → bind → report → stop
```

### 1. Situate

- **The specification must hold together before anything is read against it.** Run
  `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/spec.py <specification-root>`. Anything but a clean pass is
  a stop reported verbatim: this invocation does not repair a specification an earlier one left
  broken, and a judgment against a root that does not hold is a judgment about nothing.
- **The trace must hold together too.** Run
  `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py <target-source-root>`. A trace file that does not
  exist is a stop with a plain answer: nothing has ever been bound in this target, so there is no
  link to reconcile, and what the human wants is a delivery.
- **The record's own path must be free.** `siegard-reconcile/<slug>.md`, at the target source
  root's git toplevel — the directory `git -C <target-source-root> rev-parse --show-toplevel`
  prints, which is where `siegard.json` and `siegard-trace.json` already sit. A path that exists is
  the stop input 4 describes.

### 2. Locate

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --check <target-source-root>
```

This is the reverse lookup, and it is the only one there is: the trace is keyed by node, and what
makes a file findable in it is that the file drifted. Read the findings, and keep the ones whose
path is in the file set.

**Two anchors meet here, and only one of them belongs in what you write.** Findings are spelled from
the target's git toplevel, because that is where the trace file sits; everything you author — the
file set the human gave you, every path in the record — is spelled from the target source root, the
same anchor every other record in this framework uses. Copy a finding's path across unconverted and
the bind refuses it, which is the cheap failure; the expensive one is converting the human's paths
the other way to match the output you just read. **What you keep is every node those findings name, and never a subset** —
which nodes a file answers to is what the trace holds, and reconciling a file against the part of
the specification that happens to agree with it is the failure this whole route exists to prevent.

Four states, and they do not all continue:

- **A named file a finding of the code class names.** This is the subject. Its nodes go to the
  judgment.
- **A named file the trace binds nothing to.** Reported, never guessed. Deciding which node an
  untraced file answers to is a delivery's judgment or an analysis's, and inventing one here would
  write this framework's most durable claim out of its thinnest evidence. It goes into the record's
  `unbound` and no further.
- **A named file whose binding is intact.** It did not change, or it changed back. It stays in the
  file set and its nodes still go to the judgment — a file that did not move can be exactly where
  the fact another file's edit displaced has come to live twice, and dropping it here is dropping
  the reading that would find that.
- **A node reported under the orphaned class.** Stop for that node, and say so plainly: the
  specification no longer holds it, no bind can repair the entry, and the route is
  `trace.py --prune` followed by whatever put the fact somewhere else. Do not bind around it, and
  do not prune it from here — this invocation's writes are its own record and its own bindings.

Where a node also drifted on the specification side, the judgment below reads it as it now stands,
and the record says so in `notes`. Both sides having moved is not a special case; it is two facts,
and the bind restamps both.

### 3. Judge

Spawn a `specification-conformance-reviewer` subagent, its judgment at
`${CLAUDE_PLUGIN_ROOT}/agents/specification-conformance-reviewer.md`, passing the file set, the node
identifiers located above, the specification root, and the path to
`${CLAUDE_PLUGIN_ROOT}/schemas/delivery-node.json`, which is where the shape of what it returns
lives. One delegation, one pass.

The agent is unchanged and it is unchanged on purpose. Its file already says that what belongs in
the node set is the caller's rule and never its own; in a review that rule is the plan, and here it
is the trace. That one substitution is the whole of the difference, and duplicating the judgment
into a second agent that reads it differently is how two passes end up disagreeing about what
conformance means.

**Do not read the files yourself and decide.** The premise the human handed you is that the source
is correct; the question this step answers is a different one — whether the specification still
states what the source now says — and answering it from the same context that accepted the premise
is answering it from the premise.

Delegating means spawning the named subagent; in a plugin install the name may be plugin-scoped.
Only where the session cannot spawn subagents, read the agent's file under the plugin root's
`agents/` directory and apply its discipline in place — the file stays the single home of that
judgment — and the report must say the pass ran inline.

### 4. Record

Write `siegard-reconcile/<slug>.md`, against the contract you read, and write it whatever the
judgment returned. A reconciliation that stopped is the record worth keeping most: it says the
judgment ran, over which files, and what it found, and without it the next invocation rediscovers
the same divergence from scratch and calls it new.

- `summary` carries the human's premise — what changed and why they state it is correct — as
  theirs. Never restate it as a finding of yours.
- One entry per node, carrying the judgment's answer and why, with what was read quoted rather than
  summarised.
- **A node the judgment cleared carries the files it encodes; a node it did not carries the files it
  was read in.** The two field names are what makes the next step safe: the binding form reads only
  the first, so a node with a finding against it cannot be bound from this record however anyone
  invokes it. That is why the split is in the contract and not in a sentence here asking you not to.
- Every named file is accounted for — by a node, or under `unbound`. A file left out reads exactly
  like a file nobody had a question about.

Then hold it to its contract:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --reconciliation <the record>
```

Anything but a clean pass is a stop, reported verbatim and fixed here: everything it refuses is form
this invocation owns.

### 5. Bind

**Where the judgment cleared every node, and only then:**

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --bind-record <target-source-root> <specification-root> <the record>
```

The record is read the same way an implementation record is, and the whole of it is refused before
anything is written. What lands is the union: a file an earlier bind put on a node and this record
does not name stays bound, because two things landing one node in two files is not one of them
undoing the other's work.

**This skill never passes `--replace`.** Where the human says a fact moved out of a file rather than
into an additional one, the report hands that invocation ready to paste and stops: `--replace`
substitutes the whole entry, its receipt of what stopped being claimed is the only signal there is,
and a receipt nobody was there to read is the silent loss the union default exists to end.

**Where any node carries a finding, nothing is bound at all** — not even the nodes that cleared.
The file set is one act: a trace holding half of it says this source is reconciled when it is not,
and reads exactly like a trace that holds all of it.

### 6. Report

Say, in this order and in prose: the file set as given; what the trace held for each file, by class;
what the judgment answered per node, with its evidence; where the record was written; what was bound
and what was not; and the next invocation where there is one.

Where the judgment cleared everything, there is no next invocation. The trace now describes the tree
as it stands, and `trace.py --check` over the target is what a reader confirms that with.

Where it did not, there are two readings and **you choose neither.** The source may be right and the
specification behind it, or the node may be right and the source wrong — that is a person's to
settle, and a reviewer that settles it is a decision wearing a finding's clothes. Hand both, and say
which finding each one answers.

The first, where the fact the source now states belongs in the specification — the `/analyse`
invocation ready to paste, naming the material (the finding's evidence, the file it was read in, and
the nodes located above) and the project root. After it runs, this skill is invoked again over the
same file set under a new slug: the node has moved, the judgment reads it as it now stands, and the
bind stamps both sides.

The second, where the node is right and the behavior is not — the `/plan-work` invocation ready to
paste for a corrective increment, naming the scope (the one wrong behavior, as the finding states
it), the project root, the target, and the initiative's slug. That route ends in a delivery, which
binds on its own and leaves this reconciliation with nothing to do.

## What this never does

- **It never writes source and never writes a specification node.** Both have entry points, and a
  reconciliation that repaired what it found would be a third one nobody validated.
- **It never decides that a file is correct.** The human asserts that; this skill records the
  assertion as theirs and asks a different question.
- **It never binds a node the judgment did not clear**, and it never binds part of a file set.
- **It never prunes, and it never drops a binding.** A file that moved or vanished is drift with an
  owner; dropping its entry would destroy the one record of which node that code answers to while
  reporting the tree clean.
- **It is not a review.** It reads one file set against the nodes the trace already links to it. It
  says nothing about coverage, about the project's standard, or about whether anything was proven —
  those are `/review-change`'s, over a delivery, and a reconciliation that reported them would be
  reviewing a change nobody delivered.
