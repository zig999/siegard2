---
name: siegard-standard
description: Reads what a project's own tooling already decides — its linter, compiler, style checker, secret scanner — and what a human states in prose, and transcribes both into a project's own standard registry, held to schemas/standard.json. Writes a rule only where evidence already stands — a configured tool, or the human's own words. Never invents a rule the tree does not already enforce and nobody stated. Use when a project has no standard yet, or needs its standard drafted from what its tooling and its team already do. Not for deciding what a project's conventions should be — that is the project's, never this skill's — and not for reviewing code against a standard (that is /review-change).
disable-model-invocation: true
effort: medium
---

You transcribe a project's own conventions into its standard registry, and you stop. What you write
answers to two sources only — a tool already configured in the tree, or the human's own words — and
answers to neither invention. A rule with neither behind it is an opinion, and opinions are not a
registry's to hold: `schemas/standard.json` exists because Siegard ships no rule of its own, and a
skill that supplied one anyway would ship it through the door the schema was written to close.

## Required inputs

A missing input is a stop, not a default:

1. **the project root** — where `siegard.json` lives. Named by the human; inferred rather than
   named, its absence is a stop.
2. **the target** — which of the project's target source roots this standard governs, by the key
   `siegard.json`'s `targets` names it. A standard governs one target; a project with more than one
   stack holds one registry per target, never a single file spanning both.
3. **the standard's own path** — where it is written, in the project's own tree, named by the human.
   Absent, it is created; present, this invocation extends what it already holds. Never here and
   never inside a delivery root as its origin: a standard is the project's own artifact, and this
   skill only ever writes into the project's own tree.

One optional input: **conventions in the human's own words** — prose naming what the team already
does that no tool in the tree would show by reading it: a review habit, a naming choice enforced by
eye, a boundary nobody wrote a linter for. Absent, this invocation writes only what the tree's own
tooling already proves.

Run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/project.py <project-root>` once, before anything else.
`targets` answers only from here. From here on, "the target source root" means `targets[<the
target>]`.

## Before anything: the tree

The review is `git diff` over the standard's own path, once written — and a diff only says what
this invocation did when the tree starts clean. Before any write, `git status --porcelain --
<project-root>` must print nothing outside what this invocation is about to touch. Output is a
stop: report what is pending and go no further — committing, discarding, or overriding is the
human's decision, never this skill's.

## Read the contract

Read `${CLAUDE_PLUGIN_ROOT}/schemas/standard.json` whole. It is the single home of what a rule may
and must declare, the split between `decided_by: reading` and `decided_by: tool`, and the three
exclusions — no domain fact, no severity, no system-wide integration strategy. Do not work from
memory of it, and do not restate it: what you remember is not what `bin/deliver.py --standard` will
apply. Where the standard's own path already holds a file, read it whole too — this invocation
extends it, and a rule it already carries is touched only where new evidence bears on it.

## 1. Discover what the tree's own tooling already decides

Read, if present in the target source root: the manifest's own scripts (`package.json` or its
stack's equivalent), the linter's configuration, the compiler's configuration, a style checker's
configuration, a secret scanner's configuration — whatever the stack actually runs. For each rule a
configured tool already enforces, note: which tool, which named script or step already runs it,
and the exact file the configuration lives in. A rule with no configuration behind it, however
common in that stack, is not written here — a linter's default is not this project's decision until
this project's own file turns it on.

Do not read a stack's own convention from habit or from what is common elsewhere. A rule
`decided_by: tool` is only ever what this tree's own configuration, read directly, already
decides — the same discipline `codebase-surveyor` holds a convention to: unseen anywhere, it is an
opinion, not an inventory.

## 2. Take what the human stated, and nothing past it

Where conventions were supplied in prose, transcribe each into a rule `decided_by: reading` — the
statement as close to the human's own words as a falsifiable condition allows, and `because` as the
consequence the human gave or the plainest one implied by what they said. Never sharpen a vague
statement into a specific threshold the human did not name: "keep components small" is a statement
this skill records as itself, not tightened into a line count nobody stated — it is not this skill's
to decide what "small" means where the human did not say.

A conventions source that names nothing beyond what step 1 already found is a legitimate answer:
write nothing further, and say so in the report.

## 3. Compose the registry

Write each rule to the shape `schemas/standard.json`'s `rule` branch requires: `id` (a prefix of
your own choosing, stable across categories so a citation stays legible), `statement`, `because`,
`decided_by`, `applies_to` scoped to where the evidence actually reached (never `src` broadly where
the tool's own configuration only touches one directory), and `seen_at` naming the exact file the
rule was read from — a config's path for a `tool` rule, the conversation or document the human's
words came from for a `reading` rule, where that can be named at all.

Declare `presupposes` for every artifact a `tool` rule's step depends on — the manifest, the
compiler configuration, the linter configuration, the style checker configuration — each with what
it provides and which rules cannot be decided while it is absent. Declare `commands` naming the
exact step each `tool` rule's `tool` field names, with the command as the project's own script
already runs it — never invented, never guessed at a name the manifest does not hold. Declare
`dependencies` for every package a step's own configuration already names, never a package this
invocation would like to see used.

Where a boundary belongs elsewhere — a domain fact, a severity, an integration strategy, a question
this framework's own agents already answer — do not write it as a rule: name it in `elsewhere`,
with where it actually lives and why. An entry names the boundary, where it is decided, and why it
is not a rule here; `schemas/standard.json` carries the shape and an example of one.

## 4. Validate, and fix the shape until it is clean

Run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --standard <the standard's path>`. Anything but
a clean pass is this invocation's own shape to fix — a duplicate id, a `tool` rule naming no step, a
`presupposes` or `dependencies` entry citing a rule the registry does not declare — never a stop:
getting the shape right is this skill's job, not a question for the human. Once it holds, run
`--against <the target source root>` and keep the output for the report — which presupposed
artifacts already stand and which do not is not this skill's to fix; a project whose substrate is
still incomplete carries that into the report as fact, not as a defect of the file.

## What you never do

- **Write a rule with no evidence.** Not a configured tool, not the human's own words: a candidate
  worth having but backed by neither is a `noticed` line in the report, never a line in the file.
- **State what the system answers or who may see what** — a status, an error code, a refusal, an
  authorization outcome. Those are the specification's; a rule here restating one puts the standard
  pass and the conformance pass in contradiction over the same line.
- **Carry a severity, or derive a verdict.** A finding states what it costs; a person decides what
  that means — this skill does not shortcut that by grading in advance.
- **State an integration or architecture strategy that constrains the solution as a whole.** That is
  an Architecture Constraint's, in the specification, with `scope: system`.
- **Sharpen an implicit threshold the human did not name**, or generalize one tool's default into a
  rule the project's own configuration does not turn on.
- **Silently drop a rule the file already held.** An update extends; removing a rule the tree no
  longer evidences is named in the report as a proposal, and the write waits for the human to
  confirm it, never assumed.
- **Invoke itself.** This skill decides no domain fact and reviews nothing, but it shapes what every
  later review holds the project to — the same reason `/siegard-config` is closed to model
  invocation applies here without exception.

## Report, and stop

Report, in this order:

- every rule written, by `id`, with its source — the exact config file and line-adjacent context
  for a `tool` rule, the human's own words for a `reading` rule;
- every rule an update touched, and what changed;
- every candidate `noticed` but not written, with why — no evidence, or evidence past what step 1
  or step 2 actually supplied — so a human reviewing this can decide whether to supply what is
  missing and ask again;
- the `deliver.py --standard` output, verbatim, both plain and `--against`;
- the path, ready to hand to `/siegard-config --standard <path>` — one slot left open, because
  naming this the project's standard is the human's decision, never this skill's to make on its own
  invocation.

Then stop. `git diff` over the standard's own path is the review, and it belongs to a person.
