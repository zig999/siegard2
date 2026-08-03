---
name: ingest-domain
description: Enriches the objects an analysis wrote — writes the four fields no analysis carries into each, checks that nothing else moved, and derives the graph and its projections. Use once an analysis has written its objects and a person has read the diff. Not for producing those objects, which is model-domain; not for filling a gap only the domain can close; and not for generating code.
disable-model-invocation: true
---

You finish the objects an analysis wrote. One invocation, one ingestion.

**You start where the review ended.** `/model-domain` wrote the objects and stopped so a person could
read `git diff` over them. That reading is the reason there are two entry points: a procedure that ends
has stopped, where one that says "stop here" in the middle is asking the model to hold a place in a
sequence. If nobody has read the diff, this is the wrong moment to run this.

There is no promotion. The objects are already where they are read, and what says the enrichment has
not reached one is its own open `kind: authoring` gap. Closing that gap is what records the field was
filled — there is no state to advance and none to forget.

Two rules govern everything below, and neither is yours to relax:

- **You supply no domain fact.** An object carries `kind: domain` gaps naming what the domain
  has not stated. Carry them; never close one. A plausible attribute, an invented state, a guessed
  identity strategy: each is a domain fact authored by the framework rather than by whoever knows
  the domain, and that is the failure this whole path exists to prevent.
- **You record no status.** An object carries no maturity level and no approval state: what the base
  holds is current and binds from the moment it is written. What an object does record is the material
  it was read from, in `sources`, and whether the analysis decided the fact or the material stated it,
  in `origin`.

## Required inputs

Collect these before running anything. A missing input is a stop, not a default:

1. **the knowledge root** `/model-domain` wrote into, and **the seal** it left over it — the field
   ownership check compares each object against what the analysis wrote, and the seal is that record.
   Neither substitutes for the other.
2. **a result id** — `er_` followed by eight hex digits — for each enrichment. You own them; a report
   stamped by whoever wrote it could not be traced back to the run that asked for it.
3. **the material** the request was read from, so each enrichment can be checked against it rather
   than composed from the object alone.
4. **the system defaults**, if the base does not already declare them: the timezone, the currency,
   and the identity strategy every attribute inherits, plus the body-line ceiling. These are domain
   facts about this repository and the framework holds none of them.

## The order, and why it cannot be rearranged

```
system defaults → enrich in parallel → check ownership → check knowledge → materialize
```

Every object already exists, which is what makes the enrichments independent: none is ordered behind
another, and nothing has to be serialized to let one reference the next. That is also what makes
`out_of_scope` writable at all — it is a claim about the objects around one, and it was being
written while half of them did not exist yet.

### 1. The base must be able to hold knowledge

`system.md` carries the three defaults every attribute inherits and the ceiling the body-length check
enforces, and `knowledge-system/1` governs it. Without it nothing inherits and the ceiling reports
itself unenforceable. If it is absent, expand the `knowledge-system` scaffold with the values the
caller supplied. If the caller supplied none, that is a stop: a default the framework chose would be
a hidden default, and the value of the ceiling is a decision nobody made if nobody made it.

### 2. Report what the base still owes, before delegating anything

Read the record `/model-domain` returned and the gaps on the objects it names. Say which constructs
the analysis excluded and which questions it refused, each with why, and then the gaps split by who
closes them — a `kind: domain` gap waits on whoever knows the domain, and a `kind: authoring` gap
waits on the next step.

The split is the point. A report of thirty gaps with no way to see what is waiting on the reader is
a report the reader stops reading.

### 3. Enrich, in parallel, one delegation per object

One delegation to `knowledge-enricher` per object. They are independent: every object already
exists, so no ordering constrains them and nothing has to be serialized to let one reference another.

Give each the object's path, the material, the knowledge root, and a result id. Its return is a
`knowledge-enrichment-result/1`, and you read it rather than the filesystem — a `blocked` result is
recorded and not retried, and a `findings` array is reported to the reviewer rather than acted on
here. You are the consumer the contract names, and reporting the findings is what that means.

### 4. Check that the enrichment stayed inside its fields

Run `bin/check_field_ownership.py <seal> <knowledge-root>`, with the seal `/model-domain` left. It
recomputes each digest and reports any difference outside the four fields and the body.

A seal rather than a re-derivation, and the difference is what it costs you: nothing. The check needs
neither the analysis nor a way to run it again, which matters because there is no way — an analysis
writes by judgment, and two runs over one request agree in meaning rather than in bytes. What it does
need is a seal taken before anything edited the objects; one taken afterwards records the edit as
though the analysis had made it.

This is not defence in depth — it is the only enforcement there is. A tool grant names tools, not the
keys of a file, so "edit these four fields" is prose until this runs.

### 5. Check the base, not just each object

Run `bin/check_knowledge.py <knowledge-root>`. It holds both directions of the gap alternation, and
the three rules no per-file schema can express: a lifecycle's table is total, no two lifecycles claim
one subject, and a reference crossing a bounded context targets an interface.

The gap alternation first: a gap excuses an object from a field its kind requires, so the excuse is
only as good as the field name — and a fact the kind requires and nothing names is an absence nobody
declared.

Without the first, `{kind: domain, field: colour}` excuses an object from declaring `attributes`.
Without the second, an object short of one fact while declaring a gap about another passes as one
whose incompleteness is justified.

### 6. Materialize

Run `bin/materialize.py <knowledge-root>`. It derives `graph.json` and the three projections the
ontology admits — an index, a glossary, a context map — from the objects, and reports any edge naming
an id the base does not hold.

**It is where cross-object validation happens, and the only place it can.** A per-file schema cannot
see whether a reference resolves; the graph is what makes that decidable. A defect it reports is
reported and never repaired: the graph is still written, so a reader sees the shape the defect sits
in rather than only the pair that failed.

Every file it writes is derived. Hand-editing one is editing a view of facts that live elsewhere, and
`--check` is how a later run tells a stale view from a current one.

### 7. Report what was not validated

A knowledge base needs checks a per-file schema cannot express, and the distribution now ships all
four. Step 5 performs three — a lifecycle's transition table is total, no two lifecycles claim one
subject, and a reference crossing a bounded context targets an interface — and step 6 performs the
fourth, that every reference resolves and an orphan is named.

They were declared owed and unshipped for as long as this procedure existed, which is why the
evidence still records what ran rather than asserting that everything did. Do not improvise a fifth:
a check a producer runs on its own output is not a check, and one written here would differ between
two runs over the same base.

**Record what validated and what did not.** The run produces a `validation-evidence/3` naming each
check that was owed, its `verdict`, and where a check did not run, why. An ingestion reported as
validated with nothing saying what validated it is an assertion, and the point of evidence is that a
reader can tell a check that passed from one that never ran.

## What you never do

- Fill a gap, or answer one of the model's open questions. The model said what it said.
- Re-open a modelling decision. Which constructs are aggregates and which are value objects was settled
  before this procedure, and the model records whether each was stated or decided.
- Record a status, a maturity level, or an approval state on an object, or invent a field to carry one.
  The contract rejects `status` rather than preserving it, so an object that carries one fails at the
  boundary — and an open `kind: authoring` gap already says which pass has not run.
- Edit an object yourself. The analysis writes the design and the enricher writes the four fields; a
  third hand in the file is what the ownership check exists to find.
- Author a derived file. The index, the glossary, the context map, and the graph restate what the
  objects already say, and a hand-written one is a second authority for the same facts.
- Generate source. That is a separate entry point over an accepted base.

## Result

Report, in this order: whether the system defaults were already present or expanded; the objects
enriched and the ones blocked, each with what was missing; every finding an enricher reported, which
is what the reviewer acts on; the `kind: domain` gaps still open, by object, which is what the base
now holds and says it lacks; and the `verdict` the validation evidence records, with where it was
written and which owed checks had nothing to run them.

Every object you authored binds from the moment you wrote it, so what stands between this base and
anything read from it is the blocked entries and the owed checks nothing ran — say so plainly rather
than reporting the ingestion as finished. An ingestion reported as finished over entries that blocked
invites the caller to build on facts the base does not hold.
