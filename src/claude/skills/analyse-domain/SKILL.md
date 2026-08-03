---
name: analyse-domain
description: Turns material a human supplies into a DDD analysis recorded as markdown nodes under a knowledge root, validates them, and derives graph.json. Use when a request describes a problem or a system and the base does not yet hold it. Not for generating code.
disable-model-invocation: true
---

You turn material into domain nodes, and you stop. One invocation, one analysis.

## Required inputs

A missing input is a stop, not a default:

1. **the material** — what the human supplied, in prose, plus any files it references.
2. **the knowledge root** — the directory the nodes are written into. Empty is the ordinary
   first run. Named by the human and absent, it is created empty; inferred rather than named,
   its absence is a stop.

## Before anything: read the contract

Read `${CLAUDE_PLUGIN_ROOT}/schemas/node.json`. It is the single home of what a node may and must
declare — the kinds, the fields each kind requires, the closed vocabularies, and one example per
kind inside that kind's branch. Do not work from memory of it, and do not restate it: what you
remember is not what the validator will apply.

`${CLAUDE_PLUGIN_ROOT}` is set where this skill runs as an installed plugin. Where it is not,
the plugin root is the directory that holds `schemas/` and `bin/` side by side — in a vendored
install, the `.claude/` directory this skill's tree sits under. Every path below resolves the
same way.

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

How to decide, kind by kind. The schema says what each kind may declare; this is the judgment
that decides what goes in it:

- **Language first.** The material's recurring nouns, with the meanings the material gives them,
  are the candidate definitions — the set of definitions is the ubiquitous language. A term that
  keeps one meaning everywhere is one definition. A term whose meaning shifts between departments
  is the strongest boundary signal you will get: two meanings, two contexts, one definition in
  each.
- **A context is a linguistic boundary.** Not a team, not a deployment unit, not a module. Draw
  one where the language changes or where somebody else's model gets translated at the edge.
  In a first pass, fewer and larger contexts beat many thin ones.
- **Identity decides a definition.** Ask whether the domain cares *which one* it is or only
  *what it holds*. Most things a first pass calls entities are value objects: where two
  instances with equal attributes are interchangeable, the thing is replaced, not modified.
- **An aggregate is a consistency boundary, not an object graph.** Group only what must change
  together in one transaction; the default size is small. A reference that leaves the boundary
  goes by identity, never by containment. When an invariant seems to demand a bigger aggregate,
  first ask whether it truly needs to hold immediately — most such rules converge, and that is a
  rule declaring eventual consistency, not a wider boundary.
- **One rule, one falsifiable condition.** "Orders are validated" is prose; "an order total MUST
  be greater than zero" is a rule. Where the material states a policy vaguely, record the part
  that is falsifiable and gap the rest.
- **A lifecycle only where the domain tracks states.** It needs transitions whose triggers the
  business names. A flag, or a value computed from other facts, is an attribute. Record
  rejections deliberately: refusing a trigger is a business decision worth keeping.
- **An interface is what crosses a boundary.** An event records a fact that already happened and
  is named in the past tense; a command requests something that may still be refused. What a
  context consumes from another is recorded on the consuming side, pointing at the published
  contract that owes it compatibility.
- **A process only for a flow that crosses nodes.** A saga exists because of its compensations;
  a flow with no failure path worth recording is rarely worth a process node.
- **A relationship records power, not plumbing.** It says who owes compatibility to whom. Two
  contexts that do not need each other stay unconnected — going separate ways is a real answer,
  and a map that connects everything says nothing.
- **What never enters the base:** persistence, UI, stack, performance — implementation knowledge
  is not domain knowledge. And no fact enters because it is plausible. Plausible is the failure
  mode this framework exists to catch.

### 2. Write

The path is the identity. A context sits at `context/<slug>.md`; every other node sits at
`<kind>/<context>/<slug>.md`. There is no id field, no type field and no boundary field — the
path already says all three, so there is nothing to keep in step.

Before any node, persist the material: the prose as supplied, plus any files it references, go
under `intake/` in the knowledge root. The validator ignores that directory the way it ignores
`graph.json`. Point every `sources` entry at a file under it — what a node was read from should
be something a reviewer can open, not a conversation nobody can reread.

Write contexts first, then aggregates and definitions, then the rest. The body of every file
carries exactly two headings, in order: `## What it is`, then `## Rules`. One sentence per line;
a section with nothing to say carries the literal line `None.`

While writing, a single file can be checked on its own:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/graph.py --node <file> <knowledge-root>
```

### 3. Validate, and derive the graph

When every node is written, run:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/graph.py <knowledge-root>
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
