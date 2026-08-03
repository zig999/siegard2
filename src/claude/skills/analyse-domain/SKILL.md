---
name: analyse-domain
description: Turns material a human supplies into a DDD analysis recorded as markdown nodes under a knowledge root, validates them, and derives graph.json. Use when a request describes a problem or a system and the base does not yet hold it. Not for generating code.
disable-model-invocation: true
---

You turn material into domain nodes, and you stop. One invocation, one analysis.

## Required inputs

A missing input is a stop, not a default:

1. **the material** — what the human supplied, in prose, plus any files it references.
2. **the knowledge root** — the directory the nodes are written into. It must exist; empty is the
   ordinary first run.

## Before anything: read the contract

Read `${CLAUDE_PLUGIN_ROOT}/schemas/node.json`. It is the single home of what a node may and must
declare — the kinds, the fields each kind requires, the closed vocabularies, and one example per
kind inside that kind's branch. Do not work from memory of it, and do not restate it: what you
remember is not what the validator will apply.

## The order

```
analyse → write → validate → report → stop
```

### 1. Analyse

Decide the contexts, the aggregates inside each, the definitions with their typed attributes, the
rules, the lifecycles, the interfaces between contexts, and the processes that cross them. Two
rules bind the analysis:

- **A fact the material does not state is not invented.** It is recorded as a `gaps` entry naming
  the absent field, with `why` saying what was missing. An invented value reads exactly like one
  the business stated, and that is the failure this framework exists to prevent.
- **A fact the analysis decided — rather than read — carries `rationale`.** That is what lets a
  reviewer accept what the material stated and argue with what you concluded.

### 2. Write

The path is the identity. A context sits at `context/<slug>.md`; every other node sits at
`<kind>/<context>/<slug>.md`. There is no id field, no type field and no boundary field — the
path already says all three, so there is nothing to keep in step.

Write contexts first, then aggregates and definitions, then the rest. The body of every file
carries exactly two headings, in order: `## What it is`, then `## Rules`. One sentence per line;
a section with nothing to say carries the literal line `None.`

While writing, a single file can be checked on its own:

```
python3 ${CLAUDE_PLUGIN_ROOT}/bin/graph.py --node <file> <knowledge-root>
```

### 3. Validate, and derive the graph

When every node is written, run:

```
python3 ${CLAUDE_PLUGIN_ROOT}/bin/graph.py <knowledge-root>
```

This validates every node against the contract, runs the checks that need the whole base — every
reference resolves, one lifecycle per subject, one root per aggregate, transition tables are
total — and derives `graph.json`. **Never write or edit `graph.json` yourself**: it is derived,
and an edit to it is a fact with no node behind it.

Report the command's output verbatim. If it exits non-zero, the run failed — fix and rerun, and
never describe the base as valid while it is not.

**Fixing means form, never knowledge.** A wrong shape — a value outside a vocabulary, a list
where a mapping belongs, a malformed slug — is yours to correct. An absent fact — attributes
nobody stated, an unnamed upstream contract, a consistency nobody decided — is a `gaps` entry,
never a value you supply. If the validator names a missing field and the material does not answer
it, the correction is a gap naming that field, not an answer.

### 4. Report, and stop

Report, in this order:

- every node written, by identifier;
- every node carrying `rationale` — these are the claims a reviewer can reject;
- every question the material left open, and the gap that records it;
- the validator's final output, verbatim.

Then stop. `git diff` over the knowledge root is the review, and it belongs to a person.

## What you never do

- Write or edit `graph.json` by hand.
- Invent a value to make validation pass, or close a gap with a guess.
- Answer an open question the material refused to answer.
- Record a status, a maturity level or an approval state — an absent fact is a gap, and nothing
  else says how "done" a node is.
- Restate the contract's vocabularies from memory instead of reading the schema.
