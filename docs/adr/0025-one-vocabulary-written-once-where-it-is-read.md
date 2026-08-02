---
id: "0025"
title: Let the analysis write the knowledge, and stop converting one vocabulary into another
status: accepted
contract_version: adr/1
---

# Let the analysis write the knowledge, and stop converting one vocabulary into another

## Context

A fact reaches the base through two representations and a conversion between them. A `domain-model/4`
describes constructs in DDD's vocabulary; `bin/expand_model.py` maps each into one of six node types
and writes a `staged-knowledge-object/2` under a staging tree; `bin/promote_staged.py` substitutes the
version line and moves the file into the base as a `knowledge-object/5`. Seven steps, four contracts,
two trees, for one fact.

The conversion exists because the vocabularies differ — eight DDD kinds collapsing into six node
types. Three of those collapses are reversible through the `ddd` field and two are not: a `subdomain`
becomes `boundary.subdomain_type` and a context relationship becomes an entry in
`boundary.context_relationships[]`, so neither survives as a construct anything can address.

What the collapse buys is worth naming, because it was a real argument. Six types are six shapes a
validator distinguishes, and `foundation/0003` R3 prices a seventh at a frontmatter field no existing
type requires **and** a mechanical check no existing type enables. Splitting `boundary` into `context`
and `aggregate` fails the second half: the checks that would follow — a context declares no parent, an
aggregate declares one — are already mechanical, expressed as a nested conditional on `ddd`.

That pricing assumes the type vocabulary exists to make the *base* checkable. The decision below
changes what the vocabulary is for, which is why R3 does not settle it.

Three findings from the work that preceded this record shaped what follows.

**The envelope was already one thing written twice.** Stripped of annotations, `knowledge-object.json`
and `staged-knowledge-object.json` differ in exactly four places — the version const, the required
list, `$defs.attribute`, and the `rule` conditional. Every one carries *completeness*: whether a
primitive's parameters are demanded yet, whether a rule's expression is demanded yet. None is about
what a node type is. `schemas/knowledge-notation.json` now states that envelope once and
`scripts/check_notation_agreement.py` holds both profiles to it.

**A staged object already records that a pass has not run.** An open `kind: authoring` gap says the
enrichment has not written that field, and `docs/adr/0021-an-object-carries-its-own-gaps.md` states
the rule that follows: a non-empty `gaps` *is* the object's incompleteness, and there is no flag to
set and none to forget.

**The gap alternation was half enforced.** The per-type conditional reads "everything this type
requires, **or** `gaps`", and `gaps` there is any gap over any field — so an object short of one fact
while declaring a gap about another satisfied the contract. Nothing noticed because the expansion
derived every gap from those same requirements. `bin/check_gap_fields.py` now closes the converse.

## Decision

The analysis writes the knowledge, in one vocabulary, in the place it is read.

- **The notation and the profile are separate things.** The notation is the envelope, the frontmatter
  fence, the two body sections and the identifier arithmetic — how a fact is stored. A profile decides
  which kinds exist and what each demands of its own content. `foundation/0003` already separates them
  in its own section structure; only the schema conflated them.
- **One profile, eight kinds**, 1:1 with the vocabulary `foundation/0002` fixes: `subdomain`,
  `context`, `aggregate`, `definition`, `rule`, `lifecycle`, `interface`, `process`. Identity is
  `dm.<kind>.<scope>.<slug>`, which R7 and R8 of that specification already require and which the file
  layout now uses.
- **`foundation/0003` R3 is reframed, not waived.** A type stops being a shape the base distinguishes
  and becomes the kind a construct *is*. The bar it sets — a field no other type requires, a check no
  other type enables — priced a seventh type inside a vocabulary chosen for validation. Under a
  vocabulary chosen for correspondence, admitting a kind is not an addition to weigh but a construct
  the analysis already produces, and refusing it is what would need a reason.
- **R4 is reversed: `rationale` is admitted.** It forbade rationale in a knowledge object on the
  grounds that "the analysis that decided it holds it, reachable through `sources`" — and nothing held
  it, because the model had no durable home. The analysis is now the object, so the reason a fact was
  decided sits with the fact, reachable rather than promised.
- **`knowledge-object/5` and `staged-knowledge-object/2` are retired**, with `retired_by`, in the third
  state `docs/adr/0020-retire-the-generation-contracts.md` defines. So is `knowledge-intake-plan/7`,
  whose producer was the expansion. `domain-model/4` is retired in favour of a record holding what is
  not an element — the request, the state, the open questions, the exclusions.
- **`staged` is derived and never stored.** An object with an open `kind: authoring` gap has not been
  enriched. A field saying the same thing would be a second home for it, and the two can disagree.
- **Staging and promotion go.** The objects are written where they are read, and `git diff` is the
  review surface — which is what the first entry point already relies on.

## Consequences

**A small change stays small.** The model was already per-request; what made it grow with the base was
that a reference resolved only within it, so a rule about a promoted definition had to restate the
definition. That was fixed separately —
`docs/adr/0024-a-reference-resolves-against-the-base-as-well-as-the-model.md` — and this removes the
second copy the fix still had to travel through.

**Three guarantees leave the expansion and need homes, and two are already built.** The gap derivation
becomes the converse check, delivered ahead of this record. The enrichment boundary loses its
re-derivation — a producer writing by judgment offers no function to run again — and is replaced by
`bin/seal_analysis.py`, which records what was written once, immediately, by something other than the
producer. What remains is the identifier arithmetic, which becomes verification rather than
generation: a validator recomputes each id and path from the object and refuses a mismatch.

**The tree stops being byte-identical across runs, and that is permitted.** `foundation/0004` R8 binds
determinism to control flow, validation and recorded state, and states that it does not bind a model's
output. What replaces the guarantee is the validation, not the reproduction, and the claim in the
capability declaration that two runs over one model produce identical trees is removed rather than
left standing as something no longer true.

**The seal removed a coupling this change would otherwise have inherited.** Re-derivation made the
knowledge base an input to the enrichment check, so a promotion between the two entry points reported
a difference nobody had made. A record of what was written has no such dependency.

**Two decisions lose the moment they were taken at.** An impact verdict of `none` arrives after the
objects exist rather than before, so it asks for a discard rather than preventing a write; and
promoting an object whose `kind: domain` gaps are open stops being a decision somebody takes, because
there is no promotion. The first is recoverable through version control. The second is a policy change:
an object that says which fact it lacks is admitted, and the gap is what a reader sees.

**Release documentation is not updated, because none exists.** The obligation under
`.claude/rules/compatibility.md` is unmet and recorded as unmet, as
`docs/adr/0020-retire-the-generation-contracts.md` and
`docs/adr/0014-a-verdict-over-an-empty-base-names-nothing.md` record the same gap.

### What was rejected

**Keeping both profiles so a fact recorded without analysis has somewhere to go.** Brownfield adoption
is a real case: a repository records what its system already does, with no DDD analysis behind it, and
those facts carry no origin, no rationale and no open question. Nothing in this change produces one, so
keeping the profile would ship a contract with no producer — which is what
`docs/adr/0022-close-the-loop-the-pipeline-left-open.md` exists to stop. The case is named here and the
profile returns when a capability writes one.

**Splitting the file without splitting the vocabulary.** A per-element layout over the six node types
would give the same diff granularity at a fraction of the cost. It also keeps the conversion, and the
conversion is what a subdomain and a context relationship do not survive. The layout was never the
problem.

**A `staged` field.** Simpler to read and a maturity state by any other name, which `foundation/0001`
R11 and `foundation/0003` R26 both forbid. It would also be permanent: `additionalProperties` is true
so that an unknown field is preserved, and removing a known one therefore requires an explicit
rejection that stays in the schema forever — `status` and `superseded_by` are still there as exactly
that.

**Composing the envelope with `$ref`.** It is what JSON Schema references are for and it is
unavailable: a shipped validator loads its schema standalone under jsonschema 4.10, which resolves an
unknown remote reference by fetching it, and a consumer's boundary check must not reach the network to
decide whether an object is valid.

### What would falsify this

A base where the eight kinds do not partition what analyses actually produce — a construct that is two
kinds at once, or a kind nothing ever writes. The first would mean correspondence is not 1:1 after all
and the collapse was carrying real work; the second would mean a kind was admitted because the
vocabulary had room rather than because a construct needed it, which is the cost R3 was written to
price.
