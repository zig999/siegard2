---
name: check-source
description: Holds source that no task delivered to the rules the project set for itself — takes a file set a human names, reads it against the standard's rules that a reading decides, and records every departure citing exactly one rule, beside the trace. Use when files were changed without a task and somebody wants them read — the paths a drift receipt counted as suppressed, a batch of direct edits, or a corner nobody has looked at. Not for reviewing what a delivered task produced (that is /review-change), not for the specification (that is /reconcile), not for running a suite, and never for writing source.
effort: medium
---

You hold a named file set to the project's own standard, and you stop. One invocation, one file
set, one reading.

This exists because of a gap with a precise shape. Every other reading of a standard this framework
performs happens inside `/review-change`, and a review's file set is read out of implementation and
proof records — so a change made without a task appears in no record, appears in no file set, and
is read by nothing. On a target the project declares freely edited that is not the exception, it is
the ordinary case: the trace's own receipt counts those files and says out loud that the rules a
reading decides went unread over them. This is the invocation that reads them.

**It reads, and it runs nothing.** The rules a tool decides are the project's own suite's, over its
whole tree, on every commit — a second runner here would duplicate that at a cost nobody asked for,
and would need a home for captured output that no initiative provides. What that costs is said in
the report rather than hidden: this invocation answers for one half of a registry, and names the
other half's owner.

## Required inputs

A missing input is a stop, not a default:

1. **the project root** — where `siegard.json` lives. Named by the human; inferred rather than
   named, its absence is a stop.
2. **the target** — which of the project's target source roots these files sit under, by the key
   `siegard.json`'s `targets` names it. Where `targets` declares exactly one key and the
   invocation names none, that key is the target: a set of one holds no choice, so it is decided
   and disclosed in the report, never asked.
3. **the file set** — every path to be read, listed explicitly, each relative to the target source
   root. **Never discovered**: a check that chose its own scope reads a different set each run, and
   a clean result would not say what it was clean over. Ordinarily this is what
   `trace.py --check --all` listed, or what a `/review-change` report offered; any list a human
   states is as good, and where they name none this invocation has no subject and stops. Where a
   human wants to see what a change touched before naming the set,
   `trace.py --encodes --changed <target-root> [<ref>]` prints the changed paths under the target
   and the nodes each is bound to — a reading they then name a set from, never a set this skill
   discovered for itself.

Run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/project.py <project-root>` once, before anything else.
`targets` answers only from here. From here on, "the target source root" means
`targets[<the target>]`, and every path below is spelled from it — a rule's scope is stated against
the same anchor, so a path spelled from the repository answers to no rule.

**The project's standard** resolves as it does everywhere: from `siegard.json`, unless the
invocation names a different one, and the report says which answered. A standard governs one
target, so the file's answer is the `project.py` line for the target this invocation names — the
one `standard:` line of a one-target project, or that target's `standard <target>:` line — never
another target's. Here it is required rather than optional — a check with no registry has nothing
to read the files against, and there is no narrower thing for it to do; `null` for this target is
the same stop, said in the file's own words. Where neither answers, that is the stop, and the
report carries the `/siegard-config` invocation ready to paste, naming this target.

Absent inputs stop once, together: one stop naming everything missing, so the human answers once.

## Before anything: the tree

Before any write, `git status --porcelain -- <the check directory>` must print nothing, where the
check directory is `siegard-check/` at the target's git toplevel. The pathspec is the point: a
pending change elsewhere is somebody else's work, not a reason this reading cannot leave a record.
A dirty check directory is reported, and what to do with it is the human's call.

The target source root is not held to this. It holds the very edits this invocation was called to
read, and an edit is what a diff looks like.

## Read the contract

Read `${CLAUDE_PLUGIN_ROOT}/schemas/check.json`. It is the single home of what this record may and
must declare. Do not work from memory of it, and do not restate it: what you remember is not what
the validator will apply.

`${CLAUDE_PLUGIN_ROOT}` is set where this skill runs as an installed plugin. Where it is not, the
plugin root is the directory that holds `schemas/` and `bin/` side by side.

## The order

```
situate → read → compose → validate → report → stop
```

### 1. Situate

Take the standard in, before anything is read:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --standard <the project's registry>
```

A registry that does not hold together is a stop, reported verbatim: a reading against one reports
a conformance nobody has, and fixing it belongs to whoever owns it. The command prints the split —
how many rules a reading decides, how many a tool does, and which steps those expect. Keep it: that
split is what the report says this invocation did and did not answer for.

`--against` is deliberately not passed. What a registry presupposes is a question about a tree
being set up to be built, and this invocation neither builds nor writes — files that exist are
read against rules that exist, and a missing `tsconfig.json` changes nothing about whether the
component in front of you composes a primitive it should have composed.

Then note the registry's own path, relative to the target source root, and the SHA-256 of its text
as read now — `sha256sum <target-source-root>/<path>`. Nothing is copied: the record points at the
project's own file. That pin is a citation of what this reading read, not a standing guarantee.

Do not open the registry's text yourself. Its rules are the judge's to read, and it is handed the
reading below.

### 2. Read

First print what the judge is handed:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --standard <the project's registry> --reading --for <every path of the file set, one --for each>
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --contract finding
```

The first prints the rules the registry marks as decided by reading whose scope reaches at least
one file of the set — the rules a tool decides, and a rule scoped away from every file, never
reach the judge. The second prints the delivery-node contract's `finding` slice, every `$ref`
already inlined. Keep both outputs.

Spawn a `siegard:standard-conformance-reviewer` subagent — its judgment lives at
`${CLAUDE_PLUGIN_ROOT}/agents/standard-conformance-reviewer.md` — passing the first output pasted
whole in place of the standard's path, the file set, the target source root, and the `finding`
slice pasted whole. It is the same judge `/review-change` spawns for its standard pass, unchanged
and handed the same four inputs, which is what makes a finding from here answerable to a finding
from there. It returns the rules that were in
scope and, for each departure, a finding citing exactly one of them.

Delegating means spawning the subagent by its plugin-scoped name — `siegard:<agent-name>` — never
the bare form, which a consumer's own `.claude/agents/` can shadow. Only where the session cannot
spawn subagents, read the agent's file under the plugin root's `agents/` directory and apply its
discipline in place, and the report must say so.

Tell the agent that a path it cannot read is recorded rather than stopped on: it names each in
`unread` and reviews the rest. That mode is stated per call and is this skill's alone — the same
agent stops the pass for `/review-change`, where a delivery under review has no field to record
the narrowing in. A path in the set that cannot be read is named in `unread` and reported — never
dropped. A reading silently narrowed to whatever happened to open reports clean over files nobody
read.

### 3. Compose

Write `siegard-check/<slug>.md` at the target's git toplevel — beside `siegard.json` and
`siegard-trace.json` — where the slug names this reading and the path is its identity. A slug
already taken is a stop and not an overwrite: the clean-tree gate above catches an uncommitted
record, and a committed one is a reading somebody acted on. Name this one differently and say so. It carries
the file set, the target, the standard's own path and the pin of its text, whatever could not be
read, and every finding.

The record holds no list of the rules that were in scope. That reference and its pin already
determine the set, both sit in this record, and the validator derives it — a stored list would be
a second answer to a question the record already answers, and the one nobody could check.

The body is exactly two headings, in order: `## What it is`, then `## Notes`. One sentence per
line; a section with nothing to say carries the literal line `None.`

A finding's own prose meets a colon often enough that a plain scalar breaks the moment one appears
in it. Emit the frontmatter with `python3 -c` calling `yaml.safe_dump` rather than typing it by
hand; PyYAML is already a declared dependency of this framework's own tooling.

### 4. Validate

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --check-record <the record> <target-source-root>
```

This holds the record to its contract and every citation to the registry read fresh from its own
path: the rule must be declared, must be one the standard leaves to a reading rather than to a
tool, and its scope must reach the file the finding names — the same three a review's citations are
held to. Report the output verbatim, and never describe the reading as sound while the command
exits non-zero.

**Fixing means form, never judgment.** A citation hung on a rule that does not govern the file, a
finding in a file the set does not list — yours to correct. A finding is never dropped to make the
record validate.

### 5. Report, and stop

Open as «A handoff opens with what needs the person, and explains after» (SPEC-006 R1)
states; what follows is the report that opening sits above.

Report, in this order:

- every finding, with its evidence and what it costs;
- **which rules of the registry were in scope over this file set, and which it leaves to a tool** —
  and say plainly that the second group was not answered here at all. They are decided by the
  project's own suite, over its whole tree, and this reading neither ran it nor read what it
  printed. A reader who takes a clean result here for a clean result against the registry has read
  half of one;
- the paths of the file set no rule reaches, from `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py
  --standard <the project's registry> --reach --for <every path of the file set, one --for each>`,
  apart from the rules that do — «A review reports the paths of its file set that no rule of the standard reaches, apart from the rules that do.» (SPEC-007 R2) — a fact about the registry and never a finding;
- every file that could not be read;
- what this invocation does not do at all: it does not judge the specification — whether the source
  states a fact no node holds is `/reconcile`'s question over a bound file set, and `/review-change`'s
  over a delivered one — and it does not judge whether tests prove anything, because a file set
  nobody delivered answers to no criteria;
- whether the judge ran inline instead of in a subagent, and why;
- the validator's final output, verbatim — the one check this reading proceeds past, listed with
  its output because «Where a handoff says a step may proceed, it lists the checks it ran and their output verbatim» (SPEC-006 R4); and «A finding stops nothing» (SPEC-006 R4): every stop
  this skill names is one its own steps above name, and a finding is never one;
- where the repairs live, as routes and not as a reading of the findings: source is changed by
  whoever owns it, or through a task where the change is more than superficial; a rule that seems
  wrong is changed by whoever owns the registry. This skill hands nothing forward as an invocation
  — which route a finding deserves, or whether it deserves one, is not this reading's to decide.

Then stop. `git diff` over the check directory is this reading's own review.

## What you never do

- Fix, edit or rewrite any source you read. You hold no grant to, and a reader that could edit what
  it flagged leaves nothing for anyone to disagree with.
- Compute a verdict, a severity, a score, or anything a threshold could read.
- Record a finding against a rule the standard says a tool decides, or against a rule whose scope
  does not reach the file.
- Bind, rebind or otherwise touch `siegard-trace.json`. A reading against a standard says nothing
  about which node a file encodes, and the trace records only that.
- Add to, edit or reinterpret the project's standard, or write into the specification root, a work
  root or a delivery root.
- Commit, stash, or otherwise change the consumer's git state.
