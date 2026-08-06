---
name: analyse-domain
description: Turns material a human supplies into a DDD analysis recorded as markdown nodes under a knowledge root, validates them, and derives graph.json. Use when a request describes a problem, a system, or a change to one the base already holds. Not for planning development work (that is /plan-work), and not for generating code.
disable-model-invocation: true
effort: xhigh
---

You turn material into domain nodes, and you stop. One invocation, one increment: the first
fills an empty root, and every later one evolves what the root already holds — same order,
same discipline.

## Required inputs

A missing input is a stop, not a default:

1. **the material** — what the human supplied, in prose, plus any files it references.
2. **the knowledge root** — the directory the nodes are written into. Empty is the ordinary
   first run; populated, the invocation is a change to the base it holds. Named by the human
   and absent, it is created empty; inferred rather than named, its absence is a stop.

Naming can go by reference when the reference carries the path: "the base we just validated
at `knowledge/`" names `knowledge/`, and the handoff a `/plan-work` report or closure ends
with names roots the same way. A reference without a path resolves only through the
conversation's memory, which is not state — it is an absent input, and a stop. However named,
the root is taken as disk holds it — the checks below are that verification — never as the
conversation remembers it.

Absent inputs stop once, together: one stop naming everything missing, so the human answers
once — never a question at a time.

## Before anything: the tree

The review is `git diff` over the knowledge root, and a diff only says what this invocation
did when the root starts clean. Before any write, `git status --porcelain -- <knowledge-root>`
must print nothing. Output is a stop: report what is pending and go no further — committing,
discarding, or overriding is the human's decision, never the analysis's. A root not under git
control is the same stop: without git there is no review.

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
situate → analyse → write → validate → report → stop
```

### 1. Situate

An empty root has nothing to situate: skip to the analysis. A populated root is a standing
decision set, and this invocation is a change to it — located, not re-derived:

- **Trust the index only after checking it.** Run the validator with `--check`; a stale
  `graph.json` is rederived by a full validation run before anything relies on it.
- **Read `graph.json`, and only it**: identifiers, titles, summaries, each node's open gap
  fields, and every edge, at a fraction of the cost of opening the base. Locate the nodes the
  material speaks to. Where the material's vocabulary does not surface in the index, grep the
  root for its terms — aliases and bodies answer by filename, costing nothing to read.
- **Close the impact set over the edges, in both directions**: what the entry nodes reference,
  and what references them. The whole-base checks the validator runs are what propagation
  means — the impact set is every node that must still satisfy them after the change.
- **Read the impact set and nothing else.** Outside it, standing decisions stand: this
  invocation does not reopen them, however improvable they look. Material that invalidates a
  context boundary is a finding for the report, never a change this invocation makes.

### 2. Analyse

Decide the contexts, the aggregates inside each, the definitions with their typed attributes, the
rules, the lifecycles, the interfaces between contexts, and the processes that cross them. Two
rules bind the analysis:

- **A fact the material does not state is not invented.** It is recorded as a `gaps` entry naming
  the absent field, with `why` saying what was missing. An invented value reads exactly like one
  the business stated, and that is the failure this framework exists to prevent.
- **A fact the analysis decided — rather than read — carries `rationale`.** That is what lets a
  reviewer accept what the material stated and argue with what you concluded. The line between
  the two is what the material gives you to read: `rationale` covers a reading of stated
  material — where a boundary falls, which construct a stated thing is — never a value the
  material is silent on. A plausible value is a gap, not a decision; a lifecycle's initial
  state nobody stated is the canonical case.
- **An operative claim is recorded where something can hold the base to it.** A sentence that
  constrains the domain — a MUST, a never, an exactly-one, an at-least — is a rule node's
  `statement`, a declared constraint on an attribute, or a `gaps` entry, before it is a line
  of prose. Body and summary prose explains; it is not addressable: no criterion can cite it,
  no validator holds the base to it, no binding reaches it, so a claim living only in prose
  is one everything downstream silently drops. Catching yourself writing one into a body or
  a summary is the signal that you owe a node, a constraint, or a gap.

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
  that is falsifiable and gap the rest. A concept the material names and a rule must bind is a
  definition, however thin — a node whose gaps say what the material left unsaid, not a gap
  label coined on the rule.
- **A lifecycle only where the domain tracks states.** It needs transitions whose triggers the
  business names. A flag, or a value computed from other facts, is an attribute. Record
  rejections deliberately: refusing a trigger is a business decision worth keeping.
- **An interface is what crosses a boundary.** An event records a fact that already happened and
  is named in the past tense; a command requests something that may still be refused. What a
  context consumes from another is recorded on the consuming side, pointing at the published
  contract that owes it compatibility. A third-party system is an upstream context like any
  other: name it by the capability it supplies, record its interface there as published, and
  leave the concrete vendor in the intake. A gap on `upstream` says the contract is unknown —
  never that it is external.
- **A process only for a flow that crosses nodes.** A saga exists because of its compensations;
  a flow with no failure path worth recording is rarely worth a process node.
- **A relationship records power, not plumbing.** It says who owes compatibility to whom. Two
  contexts that do not need each other stay unconnected — going separate ways is a real answer,
  and a map that connects everything says nothing.
- **What never enters the base:** persistence, UI, stack, performance — implementation knowledge
  is not domain knowledge. And no fact enters because it is plausible. Plausible is the failure
  mode this framework exists to catch.

### 3. Write

The path is the identity. A context sits at `context/<slug>.md`; every other node sits at
`<kind>/<context>/<slug>.md`. There is no id field, no type field and no boundary field — the
path already says all three, so there is nothing to keep in step.

Before any node, persist the material: the prose as supplied, plus any files it references, go
under `intake/` in the knowledge root. The validator ignores that directory the way it ignores
`graph.json`. Point every `sources` entry at a file under it — what a node was read from should
be something a reviewer can open, not a conversation nobody can reread.

A change persists the same way: a new file under `intake/`, never an edit to what intake
already holds — it is the record of what was read, and records do not move. A touched node
appends the new source. Where the new material contradicts a standing fact, the newer material
wins and the diff shows the cost; closing a gap takes exactly that — material stating the
fact, cited from the new intake — and nothing else closes one. Removing a node decides every
node that references it, in the same invocation: the validator refuses a base with the
reference left hanging.

Write contexts first, then aggregates and definitions, then the rest. The body of every file
carries exactly two headings, in order: `## What it is`, then `## Rules`. One sentence per line;
a section with nothing to say carries the literal line `None.`

`## Rules` points at what governs the node — the rule nodes that constrain it, the declared
constraints its own attributes carry — and holds no rule of its own. A line there that restates
no rule node and no declared field is the analysis telling you it still owes one: author the
rule node, declare the constraint, or record the gap, and then point at it.

While writing, a single file can be checked on its own:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/graph.py --node <file> <knowledge-root>
```

The single-file check cannot see across files. The checks that need the whole base — one
root per aggregate, a rule's `constrains` reaching outside its aggregate without
`consistency`, transition totality — only fire on a full run, so run the full validation of
step 4 as each context's nodes close rather than once at the end: an error surfaces at the
batch that made it, not under everything stacked on top of it.

### 4. Validate, and derive the graph

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

### 5. Report, and stop

Report, in this order:

- every node written, by identifier — on a populated root, created, changed and removed
  listed apart;
- the impact set that was read, so the reviewer can judge what the analysis looked at, not
  only what it touched;
- every node carrying `rationale`, each by identifier — these are the claims a reviewer can
  reject, and a claim without an identifier cannot be rejected in place;
- every gap closed, with the material that closed it, and every question the material left
  open with the gap that records it;
- the validator's final output, verbatim;
- the handoff: the `/plan-work` invocation ready to paste — this knowledge root named as just
  validated, one named slot for each input only the human decides — the scope, the work root,
  the target source root — and the base's open agenda, as `--gaps` prints it, pointed at as
  candidate scope material. The handoff offers the next step, never takes it: filling the
  slots and invoking are the human's.

Then stop. `git diff` over the knowledge root is the review, and it belongs to a person.

## What you never do

- Write or edit `graph.json` by hand.
- Invent a value to make validation pass, or close a gap with a guess.
- Answer an open question the material refused to answer.
- Record a status, a maturity level or an approval state — an absent fact is a gap, and nothing
  else says how "done" a node is.
- Restate the contract's vocabularies from memory instead of reading the schema.
- Reopen a decision outside the impact set, or redraw a context boundary as a side effect of a
  change — a boundary the material invalidates is reported, and the decision belongs to a
  person.
- Commit, stash, or otherwise change the consumer's git state — a dirty root is reported, and
  what to do with it is the human's call.
