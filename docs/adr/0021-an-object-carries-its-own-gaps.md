---
id: "0021"
title: Let an object carry its own gaps, and let the contract branch on them
status: accepted
contract_version: adr/1
---

# Let an object carry its own gaps, and let the contract branch on them

## Context

A knowledge object is generatively incomplete by construction. `foundation/0002` R4 forbids the
analysis from supplying a parameter the request does not state, so a model reaches classification
without a bounded string's length, without an entity's identity strategy, without a lifecycle's
rejections. `foundation/0003` R6 through R11 require every one of those before an object of that
type conforms.

`foundation/0001` R9 says what to do: the missing fact "is reported as a gap on the construct it
belongs to, with what would fill it. Nothing fills a gap on the domain's behalf."

Today the gap is reported on the *classification entry*, and `knowledge-intake-plan/2` holds it
there. Then one of two things happens, and both lose it. Where the gap blocks a required field, the
authoring step returns `blocked` and writes no object — so the fact that the domain owes an answer
survives only in a run report nobody keeps. Where it does not block, the object is written and the
plan is discarded, and with it the record that anything was owed at all.

The reference run measured the shape of the loss: 24 constructs classified, 6 objects authored, and
the twelve open questions the model recorded — nine of which bore on more than one construct — reached
no artifact that outlives the run.

So R9 is satisfied on an artifact that is thrown away, and the base holds no trace of what the domain
has not yet said.

## Decision

A knowledge object carries `gaps`: one entry per fact its node type requires and does not have, each
naming the field in dotted-path form, and each declaring a `kind`.

`kind` is `domain` or `authoring`. A `domain` gap can be closed only by whoever knows the domain, and
no capability of this framework may close one. An `authoring` gap is one the framework's own steps
close — the retrieval question, the declared out-of-scope, the summary. A `domain` gap also carries
`why`: what the domain would have to say to fill it. On an `authoring` gap the field name says
everything, and requiring prose there would produce a sentence written to satisfy a validator.

The per-type requirements of `foundation/0003` R6 through R11 become an alternation: an object of a
type either declares everything that type requires, or declares `gaps`. A non-empty `gaps` **is** the
object's incompleteness. There is no flag to set and none to forget.

## Consequences

**It is a breaking change** under `.claude/rules/compatibility.md` on the second entry — the
alternation makes a previously invalid instance valid. `knowledge-object/4` carries it, with its lock
entry, an executable hop from `/3`, and a migration test. The hop adds nothing: every `/3` object
satisfied its type's requirements outright, so none has a gap to declare and inventing one would
assert the domain owes an answer nobody asked for.

**The base now holds incomplete objects, and that is the change.** Until now an entry short of a fact
was `blocked` and nothing was written — `src/claude/agents/knowledge-author.md` and the ingestion
procedure both say so, in the words "never an object written at a lower tier". That rule is reversed
here, deliberately, and the reversal is the cost this record accepts: a base that says "this entity
exists and its identity strategy is unstated" is more useful than a base that says nothing about the
entity, provided the incompleteness cannot be mistaken for completeness. The alternation is what makes
it unmistakable.

**A validator must check that a gap names a field its node type would actually require.** The schema
cannot express it: `gaps[].field` is a dotted path and the requirement it excuses is a conditional
elsewhere in the same document. Without the check, `gaps: [{kind: domain, field: colour}]` would
excuse an object from declaring `attributes`, and an object incomplete in a way nobody named would
pass as one justified.

It was named here as owed before it existed, and it exists: `check_gap_fields.py`, which derives the
per-type requirements from the contract's own conditionals rather than restating them. **It found a
defect on its first run, in this repository.** The alternation this record introduces had been
applied over a `rule`'s existing `expression`-or-`examples` alternation and overwritten it, so
`foundation/0003` R7 had silently stopped being enforced by the contract. The two now nest, and a
test holds the restored rule from both sides.

That is the argument for the check made better than this record could have made it: the first thing
it caught was not a consumer's invented field name but a requirement this change had quietly
dropped.

### Why this is not the status field that was removed

The change that removed `status` warned about exactly this shape: the first consumer to build a gate
on a field like it rebuilds the maturity ladder without the argument that justified one. The warning
is answered rather than ignored.

**`status` was asserted; `gaps` is derived.** A maintainer wrote `accepted` on an object, and nothing
could tell a considered `accepted` from a default that survived by omission — the gate that read it recorded that
every object in the framework's own fixture sat at `proposed` because seven scaffolds hardcoded it.
A gap names a field, and whether that field is required and absent is decidable by reading the object
against its contract. A wrong `gaps` is a checkable defect; a wrong `status` was not.

**`status` had no consumer; `gaps` has the contract itself.** That was the whole complaint against it: a
required field the schema validated and no capability branched on. Here the branch is *in* the
schema — the per-type alternation accepts a different document depending on the field — so the
consumer is the boundary validator, which cannot drift from the rule because it is the rule.

**It is not review state.** The decision that removed `status` left one opening — a field could
return for review state per object, with a mechanism that sets it and a capability that reads it.
`gaps` is not that: it records what the *domain* has not said, not what a *reviewer* has not done. An
object with no gaps has not been reviewed and does not claim to have been. So this record adds a
field beside that decision rather than reversing it.

### What was rejected

**Keeping the gap on the classification and keeping the classification.** It would preserve R9 at no
contract cost, and it puts the answer to "what does this object still need" in a second document that
must be found, matched by identifier, and kept in step with a base that changes without it. One
authoritative definition per concept says the object holds what is true of the object.

**One `kind`, or none.** The two were conflated when the analyst reported `question` and `out_of_scope`
as gaps and the authoring step filled them without objection. Both behaviours were right and the
contract could not say so. Without `kind`, a report of thirty gaps cannot tell the reader what is
waiting on them from what is waiting on the machine, and the reader stops reading it.

**`why` on every gap.** Symmetric and worse: on an `authoring` gap the field name is the whole
content, and a required prose field with nothing to say is filled with something written to pass.

**A boolean `complete`, or a count.** Both are the derived value without the content, so neither says
what is missing, and a count can be wrong in a way a list cannot.

### What would falsify this

A base where `gaps` accumulates and nothing ever closes one. That would mean the field records a debt
no mechanism collects, and the honest response is to make an object with a `domain` gap refuse to be
consumed rather than to keep a list nobody reads. The distinction to watch is between gaps that close
and gaps that age, and this repository cannot see either yet: it holds no knowledge base, and the
first evidence will come from a consuming repository.
