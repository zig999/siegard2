---
name: model-domain
description: Turns a request into a reviewable set of domain objects — analyses it in DDD, writes one object per construct into the knowledge base, maps what that touched, and seals what was written — then stops for a person to read the diff. Use when a request describes a problem or a solution and the base does not yet hold what it asks for. Not for writing the four fields only judgment supplies, which is ingest-domain over what this produces, and not for generating code.
disable-model-invocation: true
---

You turn a request into domain objects, and you stop. One invocation, one analysis.

**Stopping is the procedure, not a limitation of it.** What was written is what a person reads before
it is enriched, and `git diff` is the surface: it shows exactly what this run added. That review is why
there are two entry points and not one. A procedure that said "stop here" in the middle would be asking
the model to hold a place in a sequence; a procedure that *ends* has stopped whether anyone honours
anything.

There is no staging tree and no promotion. An object is written where it is read, and what says a pass
has not run is the object's own open `kind: authoring` gap rather than which directory it sits in — a
schema cannot see a directory, and a second tree was a second staging area on top of the one version
control already gives you.

Two rules govern everything below, and neither is yours to relax:

- **You do not write the four fields only judgment supplies.** The retrieval question, the summary,
  the declared out-of-scope and the body belong to the next entry point, and each is recorded here as
  a gap rather than guessed at.
- **You do not answer the analysis's open questions.** They are its most useful output. A question
  answered here, by whoever happened to be running this, is a domain fact invented by the framework —
  and it would be indistinguishable from one the request stated.

## Required inputs

Collect these before running anything. A missing input is a stop, not a default:

1. **the request** — what a person asked for, in prose, plus its `rq_` identifier. It is not a
   contracted artifact and no capability produces one. Its statement, any bound the requester set,
   and the paths it was read from all travel into the model, because a design decision is only
   reviewable against the request that prompted it.
2. **the record id** — `ar_` followed by eight hex digits — and **the analysis id**, `ia_` and eight
   hex digits. You own both; the framework refuses to mint either, because a run stamped from a clock
   could not be repeated and compared.
3. **the material the request references**, where there is any. Absent, the analysis rests on the
   request alone rather than on material nobody supplied.
4. **the knowledge root**, which is both what this writes into and what it reads. A reference stated
   by name resolves against what is already there, so a request that changes one rule about a
   definition already recorded names it instead of restating it. It must exist; empty is the ordinary
   first run.
5. **the seal path**, where the record of what was written goes.
6. **the instant and the producer identity** for every object's `generated` field. You own the
   clock; the framework refuses to, because an object stamped from one could not be regenerated and
   compared.

## The order

```
analyse and write → impact → check → seal → stop
```

### 1. Delegate the analysis, which writes the objects

One delegation to `domain-modeler`, with the request, the record id, the knowledge root, the stamp,
and whatever material the request references. It writes one object per construct and returns an
`analysis-record/1` naming what it wrote and what it refused to decide.

It is the one capability in this framework that is supposed to invent: a request describes a problem,
and deciding the aggregate boundaries, the context boundaries and the invariants is what it produces.
Do not narrow the delegation to make its job easier — a request handed over in pieces produces
boundaries drawn without seeing the whole.

The record is validated at the boundary before anything reads it. One that fails is rejected, never
repaired: a design you patched is a design nobody produced, and its `origin` fields would then be
lying about who decided what. A record whose `state` is `blocked` is a finished run with a negative
result and an empty `written` — report the reason and stop.

### 2. Learn what the analysis touched

One delegation to `impact-analyst`, with the record, the analysis id, and the knowledge root. It
returns an `impact-analysis/5`: a verdict of `none`, `update`, or `create`, one entry per implicated
artifact, and `base_state` recording whether anything existed to implicate.

**It runs for every request, including the first one against an empty base.** A `create` over nothing
implicates nothing that exists and is a full answer rather than a degenerate one — which is why
`base_state` exists, and why an empty base is not a reason to skip this.

**It runs after the writing rather than before it, and that is a change with a consequence.** While a
conversion stood between the analysis and the base, this ran first and a verdict of `none` prevented
the write. Now the objects exist by the time you have the verdict, so `none` asks for a discard rather
than preventing anything — say so plainly, and let the reviewer drop the change through version
control. Nothing is lost, and nothing was written anywhere a reader could mistake for settled.

- **`none`** — the base already held what the analysis describes. Report it and say the run should be
  discarded rather than reviewed;
- **`update`** — name the objects that were already there and are now implicated;
- **`create`** — name what is new, which over a populated base is what a reviewer looks for first.

### 3. Check that gaps and absences agree

Run `bin/check_knowledge.py <knowledge-root>`. It holds the two directions to each other: every gap
names a fact the kind requires and the object lacks, and every fact it lacks is named by a gap. The
schema enforces neither — its per-kind alternation reads "everything this kind requires, or `gaps`",
and `gaps` there is any gap over any field, so a gap about one fact would otherwise excuse the absence
of another.

**This is where the identifiers are held to their arithmetic too.** A path is computable from an
identifier and an identifier from a path, and nothing allocates either — so a mismatch is a defect the
check reports rather than a convention the writer is trusted to have followed.

### 4. Seal what was written

Run `bin/seal_analysis.py <knowledge-root> <seal-path>`. It records, per object, a digest of every
field on the analysis's side of the line, the `kind: domain` gaps verbatim, and the body headings.

**The next entry point cannot check its own boundary without this.** What the enrichment may touch is
four fields and a body, and a tool grant cannot express that — so the check compares the object against
what was written before, and this is what records it. Seal before anything edits the tree: a seal taken
afterwards records the edit as though the analysis had made it.

Hand the seal path to `/ingest-domain` with the knowledge root.

### 5. Stop

The objects are the artifact. Do not enrich them, and do not run the checks that belong to the next
entry point.

## What you never do

- Answer an open question, or fill a gap the request left.
- Re-open the analysis's decisions to make them look more certain than they are.
- Write the retrieval question, the summary, the declared out-of-scope, or a body section. Those are
  the four the next pass owns, and each is recorded here as a gap rather than guessed at.
- Record a status, a maturity level, or an approval state. An open `kind: authoring` gap is what says
  the enrichment has not run, and a field saying it too would be a second home for one fact.
- Report a run as ready when it carries unanswered questions. It is ready to be *reviewed*; whether it
  is ready to be enriched is the reviewer's call.

## Result

Report, in this order: the record id and the request it answers; the count of objects by kind; then
the three things a reviewer needs and the artifacts do not surface on their own —

- **what was decided rather than stated** — every object whose `origin` is `modeled`, with its
  rationale. These are the claims a reviewer can reject. An analysis where everything reads as
  `stated` deserves a second look before it is trusted, not after;
- **what was refused** — every open question, what the answer would change, and which objects it
  blocks. Say plainly that these are unanswered and that each becomes a gap the object carries;
- **what was excluded** — what the analysis considered and left out, with the reason. A reader who
  finds no mention of persistence cannot otherwise tell whether it was excluded or forgotten.

Then the run's own outcomes: the impact verdict, its `base_state`, and every implicated artifact; the
objects written, by identifier; the `kind: domain` gaps by object, which is what the domain owes; and
where the seal was left.

Then say what comes next and what it needs: a person reads `git diff` over the knowledge root, and
`/ingest-domain` enriches what survives that reading. Every open question still open at that moment is
a gap the enrichment carries rather than closes.
