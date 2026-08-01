---
name: model-domain
description: Analyses a request into a DDD domain model and stops there — subdomains, bounded contexts, aggregates, entities and value objects, invariants, lifecycles, interfaces, and processes, each marked as stated by the request or decided by the analysis. Use when a request describes a problem or a solution and no domain model exists. Not for authoring knowledge objects, which is ingest-domain over the model this produces, and not for generating code.
disable-model-invocation: true
---

You produce a domain model from a request, and you stop. One invocation, one model.

**Stopping is the procedure, not a limitation of it.** The model is the artifact a person reads before any
knowledge object exists: it carries what the request settled, what the analysis decided and why, and what
it refused to decide. Authoring runs afterwards, over a model somebody has looked at. Running the two
together would write objects from questions nobody answered, and each unanswered question becomes a blocked
entry discovered a step too late.

Two rules govern everything below, and neither is yours to relax:

- **You do not author knowledge.** No file under the knowledge root is written by this procedure. The model
  is a design; the knowledge base is a record; a separate entry point turns one into the other.
- **You do not answer the model's open questions.** They are its most useful output. A question answered
  here, by whoever happened to be running this, is a domain fact invented by the framework — and it would
  be indistinguishable from one the request stated.

## Required inputs

Collect these before running anything. A missing input is a stop, not a default:

1. **the change request**, conforming to `schemas/change-request.json`. Its statement, its constraints,
   and the artifacts it was read from all travel into the model, because a design decision is only
   reviewable against the request that prompted it.
2. **the model id** — `dm_` followed by eight hex digits. You own the identifier; the framework refuses to
   mint one, because a model stamped from a clock could not be repeated and compared.
3. **the material the request references**, where there is any. Absent, the analysis rests on the request
   alone rather than on material nobody supplied.
4. **where to write the model**, if it is to be kept. It is one artifact and the caller decides whether it
   survives the run; nothing here assumes a location.

## The procedure

### 1. Delegate the analysis

One delegation to `domain-modeler`, with the request, the model id, and whatever material the request
references. It returns a model conforming to `schemas/domain-model.json`.

It is the one capability in this framework that is supposed to invent: a request describes a problem, and
deciding the aggregate boundaries, the context boundaries, and the invariants is what it produces. Do not
narrow the delegation to make its job easier — a request handed over in pieces produces a model whose
boundaries were drawn without seeing the whole.

### 2. Validate at the boundary

The model is validated against its contract before you report anything. A model that fails is rejected,
never repaired: a design you patched is a design nobody produced, and its `origin` fields would then be
lying about who decided what.

A model whose `state` is `blocked` is a finished run with a negative result. Report the reason and stop.

### 3. Report what the analysis decided, refused, and excluded

This is the step the whole procedure exists for, and it is not a summary of the model — it is the three
things a reviewer needs and the model does not surface on its own:

- **what was decided rather than stated** — every element whose `origin` is `modeled`, with its rationale.
  These are the claims a reviewer can reject. An analysis where everything reads as `stated` deserves a
  second look before it is trusted, not after.
- **what was refused** — every open question, what the answer would change, and which elements it blocks.
  Say plainly that these are unanswered and that authoring over them will block on each.
- **what was excluded** — what the analysis considered and left out, with the reason. A reader who finds no
  mention of persistence cannot otherwise tell whether it was excluded or forgotten.

Then say what the model does not settle about the ontology at all: it names no node type, computes no
identifier, and holds no retrieval question. Those arrive when the model is classified, and none of them is
a gap in the model.

## What you never do

- Author a knowledge object, or write anything under the knowledge root.
- Answer an open question, or fill a gap the request left.
- Re-open the modeller's decisions to make them look more certain than they are.
- Classify anything into a node type. That is the next entry point, over the model this produced.
- Report a model as ready when it carries unanswered questions bearing on elements. It is ready to be
  *reviewed*; whether it is ready to be authored from is the reviewer's call.

## Result

Report, in this order: the model id and the request it answers; the count of elements by kind; every
element that was `modeled`, with its rationale; every open question, with what it blocks; every exclusion
and its reason; and where the model was written, if it was.

Then state what comes next and what it needs: the model is classified into the ontology by a separate
entry point, and every open question still open at that moment becomes a gap on the entry it bears on.
