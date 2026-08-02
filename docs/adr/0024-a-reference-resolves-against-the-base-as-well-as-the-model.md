---
id: "0024"
title: Resolve a reference against the base as well as the model, so a model stays the size of its request
status: accepted
contract_version: adr/1
---

# Resolve a reference against the base as well as the model, so a model stays the size of its request

## Context

A domain model answers one request. Its identifier is minted per run, it carries the request it
answers, and nothing accumulates in it — the knowledge base is what accumulates. So a request that
changes one rule should produce a model holding roughly that one rule.

It could not. Four fields of a model point at another construct by the name the model gives it — a
process step, a transition guard, and the `target` or `of` of a `ref` or `list` attribute — and the
object the expansion writes requires an identifier in all four. `bin/expand_model.py` built its index
from the model alone and refused a name it did not find there, so a rule about a definition already
promoted named something unresolvable. The only way to expand it was to restate the definition in the
model, and then whatever *it* pointed at, and so on outward.

The result inverted the artifact's purpose: the model grew with the base rather than with the
request, and the smallest changes paid the most for it. Two things followed that made it hard to see.
The refusal read as a defect in the model — `matches no element of this model` names the model and
not the base nobody looked in — and restating an element is invisible in the output, because the
restated element expands to exactly the object already there.

## Decision

The expansion takes the knowledge root and resolves against two indexes in a fixed order: the model
first, and what the base already holds second.

- **The model wins where both hold a name.** This is what makes the change additive rather than a
  rewrite of how references resolve. Every expansion that resolved before resolves to the same
  identifier, and only a refusal can become a resolution — never the reverse.
- **Ambiguity refuses on either side.** A name matching two constructs resolves to neither, which is
  the rule the model's own index already followed and is now stated once for both.
- **The base is indexed by `title`,** because that is the name a model uses. `id` is arithmetic
  derived from the title and the boundary, so indexing by it would oblige a modeller to compute
  identifiers — the one thing moving the mapping into a script was meant to stop.
- **The root must exist, and empty is the ordinary first run.** A missing directory is a stop.
- **`bin/check_enrichment.py` takes the same root,** because it re-derives the expansion to compare
  against, and the base is now one of the inputs it re-derives from.

## Consequences

**A small request produces a small model, which is the whole point.** A rule about a promoted
definition names it and expands.

**The base is an input to the enrichment check, and that is a real coupling.** The two entry points
both run before anything is promoted, so within one pass the base cannot move. What can move it is a
promotion between them — someone runs `/model-domain`, promotes something else, then runs
`/ingest-domain` over the first staging tree. The check then reports a difference, and the difference
is true: the staged tree was derived from a base that no longer exists. What it asks for is a
re-expansion. Editing the objects to match would produce a tree derived from nothing.

**A file in the base the expansion cannot read is now a stop in the first pass rather than the
second.** It is reported with its path, because "one file carries no fence" over a tree somebody
maintains is not actionable without knowing which.

**The refusal now names both places it looked.** `no element of this model and no object the
knowledge base holds` is what a reader needs to tell a name nobody defined from a name in a base they
did not search.

### What was rejected

**Reading `graph.json`.** It already indexes the base and would have cost nothing to load. It is
derived, so it can be stale or absent, and resolving against it would make an expansion depend on
whether anyone had run the materializer. The objects are the authority and the graph restates them.

**Base-first precedence.** It sounds equivalent and is not. Where a model redefines something the
base holds under a different boundary, base-first would resolve to the stored object and change what
an expansion that works today produces. The guarantee that two runs over one model agree byte for
byte is worth more than the case it would serve.

**Requiring the model to reference by identifier.** It removes the ambiguity entirely, and it does so
by making the modeller compute `ko.` identifiers — which is the arithmetic a script owns precisely so
that judgment never touches it.

**Accepting a missing knowledge root as an empty base.** Convenient on a first run, and it turns a
mistyped root into a base holding nothing, where every reference into it refuses with a reason naming
the wrong cause.

### What would falsify this

A base where titles collide often enough that cross-model references refuse more than they resolve.
That would mean a bare name is not enough to address a promoted object, and the model's reference
fields should carry the boundary beside the name. Nothing observed yet says so, and adding the field
before it does would be the speculative generalization this repository declines.
