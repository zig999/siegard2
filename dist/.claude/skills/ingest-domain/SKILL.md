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
system defaults → expand → review the diff → enrich in parallel → check → check gaps → promote
```

Two passes with a human between them, and the ordering is not preference. The expansion decides what
exists, and every object exists before any is enriched — which is what makes `out_of_scope`
writable, because it is a claim about the objects around one and cannot be written while half of
them do not exist yet.

### 1. The base must be able to hold knowledge

`system.md` carries the three defaults every attribute inherits and the ceiling the body-length check
enforces. Without it nothing inherits and the ceiling reports itself unenforceable. If it is absent,
expand the `knowledge-system` scaffold with the values the caller supplied. If the caller supplied
none, that is a stop: a default the framework chose would be a hidden default, and the value of the
ceiling is a decision nobody made if nobody made it.

### 2. Expand the model into staging

Run `bin/expand_model.py <model> <staging-root> <intake-id> <by> <at>`. It writes one staged object
per classified construct and returns a `knowledge-intake-plan/4` recording what became of every
construct — `classified`, `unmapped`, or `refused`.

**Delegate nothing here.** The mapping from a DDD construct to a node type is a closed table and the
identifiers are arithmetic; a measured run put the cost of doing it by judgment at 75,329 tokens for
a result that matched the table in every one of 24 entries. The script decides nothing, so two runs
over one model produce the same tree byte for byte.

Nothing is written under the knowledge root by this step. A staged object declares
`staged-knowledge-object/1`, which is a different contract from the base's — it does not require the
three fields the next pass supplies.

### 3. Report the three outcomes before delegating anything

Say, from the plan: how many constructs were classified; which were `unmapped` and why; which were
`refused` and why. Then the gaps, split by who closes them — a `kind: domain` gap waits on whoever
knows the domain, and a `kind: authoring` gap waits on the next step.

The split is the point. A report of thirty gaps with no way to see what is waiting on the reader is
a report the reader stops reading.

**A refusal is not a gap.** A construct is `refused` because the model states something the ontology
rejects — an attribute typed outside the closed vocabulary, a reference resolving to no element or
to two. That is a defect in the model, fixed by re-running the analysis, not a fact the domain owes.

### 4. Stop, and let somebody read the diff

The staging tree is the artifact a person reviews, and `git diff` is the surface: it shows exactly
what would enter the base. This is the review the two-pass shape exists for, and running past it
turns every unanswered question into an object nobody looked at.

### 5. Enrich, in parallel, one delegation per object

One delegation to `knowledge-enricher` per staged object. They are independent: every object already
exists, so no ordering constrains them and nothing has to be serialized to let one reference another.

Give each the object's path, the material, the staging root, and a result id. Its return is a
`knowledge-enrichment-result/1`, and you read it rather than the filesystem — a `blocked` result is
recorded and not retried, and a `findings` array is reported to the reviewer rather than acted on
here. You are the consumer the contract names, and reporting the findings is what that means.

### 6. Check that the enrichment stayed inside its fields

Run `bin/check_enrichment.py <model> <staging-root> <intake-id> <by> <at>`. It re-derives what the
expansion wrote and reports any difference outside the four fields and the body.

This is not defence in depth — it is the only enforcement there is. A tool grant names tools, not the
keys of a file, so "edit these four fields" is prose until this runs.

### 7. Check that every gap names something real

Run `bin/check_gap_fields.py <staging-root>`. A gap excuses an object from a field the contract
requires, so the excuse is only as good as the field name — and the schema cannot check it, because
the requirement a gap excuses is a conditional elsewhere in the same document.

Without this, `{kind: domain, field: colour}` excuses an object from declaring `attributes`, and an
object incomplete in a way nobody named passes as one whose incompleteness is justified.

### 8. Promote

Run `bin/promote_staged.py <staging-root> <knowledge-root>`. It validates each object against
`knowledge-object/4` with its version line substituted, and writes only where every object passes.

An object whose `kind: domain` gaps are open is refused by default. Promote it anyway only if the
caller asks — `--with-open-domain-gaps` — and report that they did: the base then holds an object
that says which fact it lacks, which is a decision somebody took rather than one that happened.

### 9. Report what was not validated

A knowledge base needs checks a per-file schema cannot express — that every reference resolves, that
a lifecycle's transition table is total, that no two lifecycles claim one subject, that a
cross-context reference targets an interface. **The distribution ships nothing that performs them.**
Do not perform them yourself: a check a producer runs on its own output is not a check, and one
improvised here would differ between two runs over the same base.

**Record what did not validate.** The run produces a `validation-evidence/2` naming each check that
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

Report, in this order: whether the system defaults were already present or expanded; the constructs
classified, unmapped, and refused, each of the last two with why; the objects enriched and the ones
blocked, each with what was missing; every finding an enricher reported, which is what the reviewer
acts on; the objects promoted and any promoted with open domain gaps at the caller's request; the
`kind: domain` gaps still open, by object; and the `verdict` the validation evidence records, with
where it was written and which owed checks had nothing to run them.

Every object you authored binds from the moment you wrote it, so what stands between this base and
anything read from it is the blocked entries and the owed checks nothing ran — say so plainly rather
than reporting the ingestion as finished. An ingestion reported as finished over entries that blocked
invites the caller to build on facts the base does not hold.
