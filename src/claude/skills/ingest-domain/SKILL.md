---
name: ingest-domain
description: Turns a domain model into a validated knowledge base — classifying every construct, authoring one object per construct in strategic-before-tactical order, then validating and regenerating the derived files. Use once a domain model exists and has been reviewed, including the first time a repository is brought under Siegard. Not for modelling the domain, which is model-domain; not for changing one recorded fact; not for filling a gap the model leaves; and not for generating code.
disable-model-invocation: true
---

You turn a domain model into a knowledge base. One invocation, one ingestion.

Two rules govern everything below, and neither is yours to relax:

- **You supply no domain fact.** Where the model is silent, the answer is a gap you report. A plausible
  attribute, an invented state, a guessed identity strategy: each is a domain fact authored by the
  framework rather than by whoever knows the domain, and that is the failure this whole path exists to
  prevent. The model's own open questions are the same thing one step earlier — carry them, never answer
  them.
- **You do not promote.** Every object you author is born `proposed`, recording the material it was read
  from. Promotion to `accepted` is a maintainer's decision — reading knowledge out of an existing
  artifact cannot canonize a defect as a rule. Generation compiles accepted knowledge only, so say
  plainly in your report that promotion is what stands between this base and generated source.

## Required inputs

Collect these before running anything. A missing input is a stop, not a default:

1. **the domain model**, conforming to `schemas/domain-model.json`. It carries the request it answers and
   the artifacts that request was read from, and both travel into each authored object's provenance — an
   ingestion whose source cannot be named is not one. A model whose `state` is `blocked` ends the run.
2. **the knowledge root**, and the path of the JSON Schema that governs a knowledge object.
3. **the framework script root** — the directory holding the knowledge validator and the materializer.
   Installation decides this path; a component that guessed it would fail silently in a repository laid
   out differently.
4. **the intake id** — `ki_` followed by eight hex digits, for the classification.
5. **the system defaults**, if the base does not already declare them: the timezone, the currency, and
   the identity strategy every attribute inherits, plus the body-line ceiling. These are domain facts
   about this repository and the framework holds none of them.
6. **the instant and the producer identity** for every object's `generated` field. You own the clock;
   the framework refuses to, because an object stamped from a clock could not be regenerated and
   compared.

## The order, and why it cannot be rearranged

```
system defaults → classify → boundaries → definitions → rules → lifecycles → interfaces → processes → validate → project
```

### 1. The base must be able to hold knowledge

`system.md` carries the three defaults every attribute inherits and the ceiling the body-length check
enforces. Without it nothing inherits and the ceiling reports itself unenforceable. If it is absent,
expand the `knowledge-system` scaffold with the values the caller supplied. If the caller supplied
none, that is a stop: a default the framework chose would be a hidden default, and the value of the
ceiling is a decision nobody made if nobody made it.

### 2. Classify before authoring anything

Delegate to `domain-analyst`, once, with the domain model, the intake id, the knowledge root and its
contract, and the boundaries the base already holds. It returns a classification: one entry per construct
with its node type, its `ddd` value, the identifier it will take, and every required fact the model does
not supply.

A `blocked` classification stops the ingestion. Report the reason and author nothing.

### 3. Report the gaps before you delegate the first authoring

The classification names, per entry, what the model fails to supply. An entry carrying gaps will
block when it is authored — `knowledge-author` refuses a request short of what its node type requires,
and it is right to. Reporting the gaps first is the difference between one report the caller can act on
and thirty delegations that each come back blocked.

Say which entries are ready, which are short and of what, and which constructs have no home in the
ontology at all. Then author the ready ones, unless the caller says otherwise.

### 4. Author strategic before tactical

The classification is sorted by identifier, not by node type, so group it yourself and author in this
order:

1. `boundary` with `ddd: bounded-context` — the partition roots, which declare no parent boundary;
2. `boundary` with `ddd: aggregate` — each declaring the context it sits in;
3. `definition`;
4. `rule`;
5. `lifecycle`;
6. `interface`;
7. `process`.

The order is not presentation. Every object except a bounded-context boundary declares the one boundary
it belongs to, so a definition authored before its context has no boundary to name. A rule guards a
lifecycle transition and a process step names an object, so both need their targets to exist. Authoring
tactically first produces objects whose references resolve to nothing, and a reference that resolved to
nothing is a defect the materializer reports rather than a step you can come back to.

One delegation to `knowledge-author` per object. Give it the classification, the proposed identifier of
the entry to author, the knowledge root and contract, the material the fact came from, and the instant and
producer identity. It reads the node type and the subject from the entry — you do not restate them, and
neither does it decide them. A `blocked` result is a gap, not a retry: record it and move to the next
entry. Do not restate the request to make the agent accept it.

### 5. Validate, then project

Run the knowledge validator over the base. It checks what a per-file schema cannot — that every
reference resolves, that a lifecycle's transition table is total, that no two lifecycles claim one
subject, that a cross-context reference targets an interface.

Then regenerate the derived files with the materializer. Never write one by hand: the index, the
glossary, the context map, and the graph are its output, a hook refuses a write to them, and a
hand-edited projection is a second authority for what the objects already say.

## What you never do

- Fill a gap, or answer one of the model's open questions. The model said what it said.
- Re-open a modelling decision. Which constructs are aggregates and which are value objects was settled
  before this procedure, and the model records whether each was stated or decided.
- Promote an object, or report an ingestion as ready to generate. Only accepted knowledge compiles, and
  acceptance is not yours.
- Author a construct the ontology's mapping has no home for. It is reported as unmapped, not forced
  into the nearest node type.
- Hand-edit a projection.
- Generate source. That is a separate entry point over an accepted base.

## Result

Report, in this order: whether the system defaults were already present or expanded; the number of
constructs classified; the entries authored, by node type; the entries blocked, each with the fact it
lacked; the constructs recorded as unmapped, each with why; the validator's result; and whether the
projections regenerated cleanly.

Then state what stands between this base and generated source: the objects are `proposed`, and a
maintainer promotes them. An ingestion reported as finished when nothing has been accepted invites the
caller to run generation and meet a block they were not warned about.
