---
name: model-domain
description: Turns a request into a reviewable staging tree — analyses it into a DDD domain model, maps what that touches in the base, and expands it into one staged knowledge object per construct — then stops for a person to read the diff. Use when a request describes a problem or a solution and no staging tree exists for it. Not for enriching or promoting those objects, which is ingest-domain over the tree this produces, and not for generating code.
disable-model-invocation: true
---

You turn a request into a staging tree, and you stop. One invocation, one tree.

**Stopping is the procedure, not a limitation of it.** The staged objects are what a person reads
before anything enters the base, and `git diff` is the surface: it shows exactly what would enter.
That review is why there are two entry points and not one. A procedure that said "stop here" in the
middle would be asking the model to hold a place in a sequence; a procedure that *ends* has stopped
whether anyone honours anything.

Two rules govern everything below, and neither is yours to relax:

- **You do not author knowledge.** No file under the knowledge root is written by this
  procedure — everything lands in the staging root the caller names. A staged object declares a different contract from the base's, so a file that leaked into
  the base would be refused there rather than silently accepted.
- **You do not answer the model's open questions.** They are its most useful output. A question
  answered here, by whoever happened to be running this, is a domain fact invented by the framework —
  and it would be indistinguishable from one the request stated.

## Required inputs

Collect these before running anything. A missing input is a stop, not a default:

1. **the request** — what a person asked for, in prose, plus its `rq_` identifier. It is not a
   contracted artifact and no capability produces one. Its statement, any bound the requester set,
   and the paths it was read from all travel into the model, because a design decision is only
   reviewable against the request that prompted it.
2. **the model id** — `dm_` followed by eight hex digits — **the analysis id**, `ia_` and eight hex
   digits, and **the intake id**, `ki_` and eight hex digits. You own all three; the framework
   refuses to mint any, because a run stamped from a clock could not be repeated and compared.
3. **the material the request references**, where there is any. Absent, the analysis rests on the
   request alone rather than on material nobody supplied.
4. **the staging root** and **the knowledge root**. The first is where this writes; the second is
   what the impact analysis reads and this never touches.
5. **the instant and the producer identity** for every object's `generated` field. You own the
   clock; the framework refuses to, because an object stamped from one could not be regenerated and
   compared.

## The order

```
model → impact → expand → stop
```

### 1. Delegate the analysis

One delegation to `domain-modeler`, with the request, the model id, and whatever material the
request references. It returns a model conforming to `schemas/domain-model.json`.

It is the one capability in this framework that is supposed to invent: a request describes a
problem, and deciding the aggregate boundaries, the context boundaries and the invariants is what it
produces. Do not narrow the delegation to make its job easier — a request handed over in pieces
produces a model whose boundaries were drawn without seeing the whole.

The model is validated at the boundary before anything reads it. A model that fails is rejected,
never repaired: a design you patched is a design nobody produced, and its `origin` fields would then
be lying about who decided what. A model whose `state` is `blocked` is a finished run with a
negative result — report the reason and stop.

### 2. Learn what the model touches, before it touches anything

One delegation to `impact-analyst`, with the model, the analysis id, and the knowledge root. It
returns an `impact-analysis/4`: a verdict of `none`, `update`, or `create`, one entry per implicated
artifact, and `base_state` recording whether anything existed to implicate.

**It runs for every request, including the first one against an empty base.** A `create` over
nothing implicates nothing that exists and is a full answer rather than a degenerate one — which is
why `base_state` exists, and why an empty base is not a reason to skip this.

- **`none`** — the base already holds what the model describes. Stop and say so. Expanding would
  stage objects the base already answers, and the diff a reviewer reads would be noise around
  nothing;
- **`update`** — name the stored objects the expansion will stage over, before it stages them;
- **`create`** — name what is new, which over a populated base is what a reviewer looks for first.

### 3. Expand the model into staging

Run `bin/expand_model.py <model> <staging-root> <intake-id> <by> <at>`. It writes one staged object
per classified construct and returns a `knowledge-intake-plan/6` recording what became of every
construct — `classified`, `unmapped`, or `refused`.

**Delegate nothing here.** The mapping from a DDD construct to a node type is a closed table and the
identifiers are arithmetic; a measured run put the cost of doing it by judgment at 75,329 tokens for
a result that matched the table in every one of 24 entries. The script decides nothing, so two runs
over one model produce the same tree byte for byte.

A staged object carries everything the model settled — its identifier, node type, `ddd`, boundary,
statement, attributes — and none of the four things only judgment supplies. Those are recorded as
`kind: authoring` gaps, and the next entry point writes them.

### 4. Check that every gap names something real

Run `bin/check_gap_fields.py <staging-root>`. A gap excuses an object from a field the contract
requires, so the excuse is only as good as the field name — and the schema cannot check it, because
the requirement a gap excuses is a conditional elsewhere in the same document.

### 5. Stop

The staging tree is the artifact. Do not enrich it, do not promote it, and do not run the checks
that belong to the next entry point.

## What you never do

- Write under the knowledge root. Everything this produces lands in staging.
- Answer an open question, or fill a gap the request left.
- Re-open the modeller's decisions to make them look more certain than they are.
- Write the retrieval question, the summary, the declared out-of-scope, or a body section. Those are
  the four the next pass owns, and each is recorded here as a gap rather than guessed at.
- Report a tree as ready when it carries unanswered questions. It is ready to be *reviewed*; whether
  it is ready to be enriched is the reviewer's call.

## Result

Report, in this order: the model id and the request it answers; the count of elements by kind; then
the three things a reviewer needs and the artifacts do not surface on their own —

- **what was decided rather than stated** — every element whose `origin` is `modeled`, with its
  rationale. These are the claims a reviewer can reject. An analysis where everything reads as
  `stated` deserves a second look before it is trusted, not after;
- **what was refused** — every open question, what the answer would change, and which elements it
  blocks. Say plainly that these are unanswered and that each becomes a gap the staged object
  carries;
- **what was excluded** — what the analysis considered and left out, with the reason. A reader who
  finds no mention of persistence cannot otherwise tell whether it was excluded or forgotten.

Then the run's own outcomes: the impact verdict, its `base_state`, and every implicated artifact;
the constructs classified, unmapped and refused, each of the last two with why; the `kind: domain`
gaps by object, which is what the domain owes; and where the staging tree was written.

Then say what comes next and what it needs: a person reads `git diff` over the staging tree, and
`/ingest-domain` enriches and promotes what survives that reading. Every open question still open at
that moment is a gap the enrichment carries rather than closes.
