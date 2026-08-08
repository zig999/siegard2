---
name: siegard-config
description: Writes or updates siegard.json — the project's own declaration of its specification root, its target source roots, its work and delivery root containers, and its standard — so every other skill reads them from one place instead of retyping them per invocation. Use when a human wants to declare, add or change what a project's siegard.json holds, including at the start of a new initiative when work_root or delivery_root's meaning changes. Not for anything the file itself governs — it never authors a specification, a plan, a delivery, or a standard's content.
disable-model-invocation: true
effort: low
---

You write one file — `siegard.json` — from what the human tells you, and you stop. One
invocation, one write: it may create the file or update the fields the human names, and it never
touches a field the human did not name.

## Required inputs

A missing input is a stop, not a default:

1. **the project root** — where `siegard.json` lives, or will. Named by the human; inferred
   rather than named, its absence is a stop.
2. **at least one field to declare** — any of `specification_root`, one or more `targets`
   entries (a name and a path each), `work_root`, `delivery_root`, or `standard` (a path, or
   `null` to declare deliberately that the project authors none). An invocation naming none has
   nothing to write, and is a stop.

## Before anything: the tree

The review is `git diff` over the project root, and a diff only says what this invocation did
when it starts clean. Before any write, `git status --porcelain -- <project-root>/siegard.json`
must print nothing. Output is a stop: report what is pending and go no further — committing,
discarding, or overriding is the human's decision, never this skill's. A project root not under
git control is the same stop: without git there is no review.

## Read the contract

Read `${CLAUDE_PLUGIN_ROOT}/schemas/project.json`. It is the single home of what this file may
declare — every field, its shape, and which of them an invocation may override versus which
answer only from the file once declared. Do not work from memory of it, and do not restate it:
what you remember is not what `bin/project.py` will apply.

`${CLAUDE_PLUGIN_ROOT}` is set where this skill runs as an installed plugin. Where it is not,
the plugin root is the directory that holds `schemas/` and `bin/` side by side.

## The order

```
read → merge → write → validate → report → stop
```

### 1. Read

Where `<project-root>/siegard.json` already exists, read it whole — every field it declares,
touched or not by this invocation. Where it does not exist, start from an empty declaration:
this invocation may be the one that creates the file.

### 2. Merge

Overlay only the fields the human named onto what was read. A field the human did not name is
left exactly as the existing file held it — this is an update, never a replacement — and where
the file did not exist, only the named fields exist in the result. Never infer a value for a
field the human did not name: a guessed `work_root`, an invented target, or a `standard` carried
over from a different project would all be answers this invocation was not given.

A `targets` entry the human names is added under its own key, or overwrites the existing value
at that key; a key the human does not name is left standing. There is no way to remove a key, or
any other field, through this step — a deliberate removal is a fresh declaration of the whole
file, named as such in the report, never a silent side effect of naming other fields.

### 3. Write

Write the merged document to `<project-root>/siegard.json`, its properties sorted by name, so an
unrelated reordering never shows up in the diff.

### 4. Validate

Run:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/project.py <project-root>
```

This is the same resolution every other skill will now perform, so a human reading this report
is reading exactly what they will get. Anything but a clean pass is a stop: report the output
verbatim. **Fixing means form, never invention** — a malformed path or an unreduced `targets` key
is yours to correct; a `standard` path that does not resolve to a file, or any field's value, is
never supplied by guessing what the human meant. Where the merged document does not hold
together and the fix is not a form correction, undo the write — restore what step 1 read, or
remove the file if step 1 found none — and report the problem instead of leaving a broken
declaration on disk.

### 5. Report, and stop

Report, in this order:

- whether this created the file or updated an existing one;
- every field this invocation declared or changed, by name, with its new value;
- every field the file already held that this invocation left untouched;
- the validator's final output, verbatim.

Then stop. `git diff` over `siegard.json` is the review, and it belongs to a person.

## What you never do

- Guess a value for a field the human did not name — an absent field stays absent, an existing
  one stays as it was.
- Remove a field the human did not ask to change.
- Write anything other than `siegard.json` — no specification, no plan, no delivery, no
  standard's content.
- Require a `targets` entry, `work_root` or `delivery_root` to already exist on disk — a
  container or a target may legitimately not exist yet; only `standard`, named as a path, must
  resolve to a file that does.
- Commit, stash, or otherwise change the consumer's git state — a dirty tree is reported, and
  what to do with it is the human's call.
- Restate the contract's vocabularies from memory instead of reading the schema.
