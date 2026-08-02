---
name: ingest-domain
description: Enriches a reviewed staging tree into a knowledge base — writes the four fields no analysis carries into each staged object, checks that nothing else moved, promotes what conforms, and derives the graph and its projections. Use once a staging tree exists and a person has read its diff. Not for producing that tree, which is model-domain; not for filling a gap only the domain can close; and not for generating code.
disable-model-invocation: true
---

You turn a reviewed staging tree into a knowledge base. One invocation, one ingestion.

**You start where the review ended.** `/model-domain` produced the tree and stopped so a person
could read `git diff` over it. That reading is the reason there are two entry points: a procedure
that ends has stopped, where one that says "stop here" in the middle is asking the model to hold a
place in a sequence. If nobody has read the diff, this is the wrong moment to run this.

Two rules govern everything below, and neither is yours to relax:

- **You supply no domain fact.** A staged object carries `kind: domain` gaps naming what the domain
  has not stated. Carry them; never close one. A plausible attribute, an invented state, a guessed
  identity strategy: each is a domain fact authored by the framework rather than by whoever knows
  the domain, and that is the failure this whole path exists to prevent.
- **You record no status.** A knowledge object carries no maturity level and no approval state: what
  reaches the base is current and binds from the moment it is promoted. What an object does record
  is the material it was read from, in `sources`, and whether the analysis decided the fact or the
  material stated it, in `origin`.

## Required inputs

Collect these before running anything. A missing input is a stop, not a default:

1. **the staging root** `/model-domain` wrote, and **the domain model** it was expanded from — the
   enrichment check re-derives the expansion from the model rather than trusting a stored copy, so
   both are needed and neither substitutes for the other.
2. **the knowledge root**, and the path of the JSON Schema that governs a knowledge object.
3. **the intake id** the expansion used, and **a result id** — `er_` followed by eight hex digits —
   for each enrichment. You own them; a report stamped by whoever wrote it could not be traced back
   to the run that asked for it.
4. **the material** the request was read from, so each enrichment can be checked against it rather
   than composed from the object alone.
5. **the system defaults**, if the base does not already declare them: the timezone, the currency,
   and the identity strategy every attribute inherits, plus the body-line ceiling. These are domain
   facts about this repository and the framework holds none of them.

## The order, and why it cannot be rearranged

```
system defaults → enrich in parallel → check → check gaps → promote → materialize
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

### 2. Report what the tree still owes, before delegating anything

Read the plan `/model-domain` returned. Say which constructs were `unmapped` and which `refused`,
each with why, and then the gaps split by who closes them — a `kind: domain` gap waits on whoever
knows the domain, and a `kind: authoring` gap waits on the next step.

The split is the point. A report of thirty gaps with no way to see what is waiting on the reader is
a report the reader stops reading.

### 3. Enrich, in parallel, one delegation per object

One delegation to `knowledge-enricher` per staged object. They are independent: every object already
exists, so no ordering constrains them and nothing has to be serialized to let one reference another.

Give each the object's path, the material, the staging root, and a result id. Its return is a
`knowledge-enrichment-result/1`, and you read it rather than the filesystem — a `blocked` result is
recorded and not retried, and a `findings` array is reported to the reviewer rather than acted on
here. You are the consumer the contract names, and reporting the findings is what that means.

### 4. Check that the enrichment stayed inside its fields

Run `bin/check_enrichment.py <model> <staging-root> <intake-id> <by> <at>`. It re-derives what the
expansion wrote and reports any difference outside the four fields and the body.

This is not defence in depth — it is the only enforcement there is. A tool grant names tools, not the
keys of a file, so "edit these four fields" is prose until this runs.

### 5. Check that every gap names something real

Run `bin/check_gap_fields.py <staging-root>`. A gap excuses an object from a field the contract
requires, so the excuse is only as good as the field name — and the schema cannot check it, because
the requirement a gap excuses is a conditional elsewhere in the same document.

Without this, `{kind: domain, field: colour}` excuses an object from declaring `attributes`, and an
object incomplete in a way nobody named passes as one whose incompleteness is justified.

### 6. Promote

Run `bin/promote_staged.py <staging-root> <knowledge-root>`. It validates each object against
`knowledge-object/5` with its version line substituted, and writes only where every object passes.

An object whose `kind: domain` gaps are open is refused by default. Promote it anyway only if the
caller asks — `--with-open-domain-gaps` — and report that they did: the base then holds an object
that says which fact it lacks, which is a decision somebody took rather than one that happened.

### 7. Materialize

Run `bin/materialize.py <knowledge-root>`. It derives `graph.json` and the three projections the
ontology admits — an index, a glossary, a context map — from the objects, and reports any edge naming
an id the base does not hold.

**It is where cross-object validation happens, and the only place it can.** A per-file schema cannot
see whether a reference resolves; the graph is what makes that decidable. A defect it reports is
reported and never repaired: the graph is still written, so a reader sees the shape the defect sits
in rather than only the pair that failed.

Every file it writes is derived. Hand-editing one is editing a view of facts that live elsewhere, and
`--check` is how a later run tells a stale view from a current one.

### 8. Report what was not validated

A knowledge base needs checks a per-file schema cannot express. Step 7 performs one of them —
every reference resolves, and an orphan is named — and the rest are still owed: that a lifecycle's
transition table is total, that no two lifecycles claim one subject, that a cross-context reference
targets an interface. **The distribution ships nothing that performs those three.** Do not perform
them yourself: a check a producer runs on its own output is not a check, and one improvised here
would differ between two runs over the same base.

**Record what did not validate.** The run produces a `validation-evidence/3` naming each check that
was owed, its `verdict`, and why it did not run. An ingestion reported as validated with nothing
saying what validated it is an assertion, and the point of evidence is that a reader can tell a check
that passed from one that never ran.

## What you never do

- Fill a gap, or answer one of the model's open questions. The model said what it said.
- Re-open a modelling decision. Which constructs are aggregates and which are value objects was settled
  before this procedure, and the model records whether each was stated or decided.
- Record a status, a maturity level, or an approval state on an object, or invent a field to carry one.
  The contract rejects `status` rather than preserving it, so an object that carries one fails at the
  boundary.
- Promote a construct whose entry is not `classified`. One the mapping has no home for is `unmapped`
  and one the model states wrongly is `refused`; neither is forced into the nearest node type.
- Edit a staged object yourself. The expansion writes the design and the enricher writes the four
  fields; a third hand in the file is what the boundary check exists to find.
- Author a derived file. The index, the glossary, the context map, and the graph restate what the
  objects already say, and a hand-written one is a second authority for the same facts.
- Generate source. That is a separate entry point over an accepted base.

## Result

Report, in this order: whether the system defaults were already present or expanded; the objects
enriched and the ones
blocked, each with what was missing; every finding an enricher reported, which is what the reviewer
acts on; the objects promoted and any promoted with open domain gaps at the caller's request; the
`kind: domain` gaps still open, by object; and the `verdict` the validation evidence records, with
where it was written and which owed checks had nothing to run them.

Every object you authored binds from the moment you wrote it, so what stands between this base and
anything read from it is the blocked entries and the owed checks nothing ran — say so plainly rather
than reporting the ingestion as finished. An ingestion reported as finished over entries that blocked
invites the caller to build on facts the base does not hold.
