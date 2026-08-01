---
name: ingest-domain
description: Turns a domain model into a knowledge base — classifying every construct, then authoring one object per construct in strategic-before-tactical order. Use once a domain model exists and has been reviewed, including the first time a repository is brought under Siegard. Not for modelling the domain, which is model-domain; not for changing one recorded fact; not for filling a gap the model leaves; and not for generating code.
disable-model-invocation: true
---

You turn a domain model into a knowledge base. One invocation, one ingestion.

Two rules govern everything below, and neither is yours to relax:

- **You supply no domain fact.** Where the model is silent, the answer is a gap you report. A plausible
  attribute, an invented state, a guessed identity strategy: each is a domain fact authored by the
  framework rather than by whoever knows the domain, and that is the failure this whole path exists to
  prevent. The model's own open questions are the same thing one step earlier — carry them, never answer
  them.
- **You record no status.** A knowledge object carries no maturity level and no approval state: what
  you write into the base is current and binds from the moment it exists. What an object does record is
  the material it was read from, in `sources` — reading knowledge out of an existing artifact can
  canonize a defect as a rule, and naming the artifact is what lets a reviewer catch that. An entry you
  are not certain enough to author is a gap you report, never an object written at a lower tier.

## Required inputs

Collect these before running anything. A missing input is a stop, not a default:

1. **the domain model**, conforming to `schemas/domain-model.json`. It carries the request it answers and
   the artifacts that request was read from, and both travel into each authored object's provenance — an
   ingestion whose source cannot be named is not one. A model whose `state` is `blocked` ends the run.
2. **the knowledge root**, and the path of the JSON Schema that governs a knowledge object.
3. **the intake id** — `ki_` followed by eight hex digits, for the classification.
4. **the system defaults**, if the base does not already declare them: the timezone, the currency, and
   the identity strategy every attribute inherits, plus the body-line ceiling. These are domain facts
   about this repository and the framework holds none of them.
5. **the instant and the producer identity** for every object's `generated` field. You own the clock;
   the framework refuses to, because an object stamped from a clock could not be regenerated and
   compared.

## The order, and why it cannot be rearranged

```
system defaults → classify → boundaries → definitions → rules → lifecycles → interfaces → processes
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
tactically first produces objects whose references resolve to nothing, and nothing in this distribution
reports such a reference — so the order is the only thing preventing it.

One delegation to `knowledge-author` per object. Give it the classification, the proposed identifier of
the entry to author, the knowledge root and contract, the material the fact came from, and the instant and
producer identity. It reads the node type and the subject from the entry — you do not restate them, and
neither does it decide them.

Its return is a `knowledge-authoring-result/1`, and you read it rather than the filesystem: its `state`
tells an authored entry from a blocked one, and a producer's own report of what it wrote is the only
thing that distinguishes the two without guessing. A `blocked` result is a gap, not a retry — record it
and move to the next entry. Do not restate the request to make the agent accept it.

### 5. Report what was not validated

A knowledge base needs checks a per-file schema cannot express — that every reference resolves, that a
lifecycle's transition table is total, that no two lifecycles claim one subject, that a cross-context
reference targets an interface. **The distribution ships nothing that performs them.** Do not perform
them yourself: a check a producer runs on its own output is not a check, and one improvised here would
differ between two runs over the same base.

**Record what did not validate.** The run produces a `validation-evidence/1` naming each check that was
owed, its `verdict`, and why it did not run. An ingestion reported as validated with nothing saying what
validated it is an assertion, and the point of evidence is that a reader can tell a check that passed
from one that never ran — which is exactly the distinction this run has to record against itself.

## What you never do

- Fill a gap, or answer one of the model's open questions. The model said what it said.
- Re-open a modelling decision. Which constructs are aggregates and which are value objects was settled
  before this procedure, and the model records whether each was stated or decided.
- Record a status, a maturity level, or an approval state on an object, or invent a field to carry one.
  The contract rejects `status` rather than preserving it, so an object that carries one fails at the
  boundary.
- Author a construct the ontology's mapping has no home for. It is reported as unmapped, not forced
  into the nearest node type.
- Author a derived file. The index, the glossary, the context map, and the graph restate what the
  objects already say, and a hand-written one is a second authority for the same facts.
- Generate source. That is a separate entry point over an accepted base.

## Result

Report, in this order: whether the system defaults were already present or expanded; the number of
constructs classified; the entries authored, by node type; the entries blocked, each with the fact it
lacked; the constructs recorded as unmapped, each with why; and the `verdict` the validation evidence
records, with where that evidence was written and which owed checks had nothing to run them.

Every object you authored binds from the moment you wrote it, so what stands between this base and
anything read from it is the blocked entries and the owed checks nothing ran — say so plainly rather
than reporting the ingestion as finished. An ingestion reported as finished over entries that blocked
invites the caller to build on facts the base does not hold.
