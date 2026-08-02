---
id: "0022"
title: Close the loop the pipeline left open, and stop describing artifacts nothing produces
status: accepted
contract_version: adr/1
---

# Close the loop the pipeline left open, and stop describing artifacts nothing produces

## Context

A recorded review of one full run — a request modelled, classified and authored against an empty
base — named twelve defects. Four had already been answered by the change that replaced the
classification agent with an expansion: the contradiction over whether a retrieval question is a
gap, the missing `validation-evidence` schema, the identifier derived twice, and the cost of holding
DDD and the ontology in two agents. Seven survived it, and one is deliberately left open.

What the seven have in common is worth naming, because it is not a shared cause but a shared shape:
each is a place where the distribution *described* something it did not do. Six shipped files told a
consumer that an index, a glossary, a context map and a graph exist and must never be hand-edited,
and nothing produced any of them. A plan required a `ddd` of every classified entry while the object
contract rejected one on a lifecycle, so a classification had to invent a value the boundary would
refuse. `sources` was documented as the material an object was read from and accepted an artifact
this framework had generated. Frontmatter carrying four load-bearing values had no contract after the
validator that checked them was removed. Scripts imported PyYAML and nothing said so. Contracts named
a producer and never a consumer, though the rule requires both. An impact analysis ran for every
request, as a specification demands, and no capability ever read one.

A description nothing enforces is not a weaker rule than one that is enforced. It is a different kind
of thing: it teaches a reader something false about what the software does.

## Decision

Each of the seven is closed by making the description true, and the correction is the same shape
every time — the thing described is either built or narrowed to what exists.

`bin/materialize.py` derives the graph and the three projections the ontology admits, so the rule
against hand-editing them governs files that exist. `ddd` becomes conditional on the node type in
`knowledge-intake-plan/5`, matching the object contract exactly. `sources` refuses the identifier
prefixes this framework mints. `knowledge-system/1` fixes the shape of the four defaults without
choosing any of their values. `consumer` joins `producer` on every artifact passed between
capabilities, and `domain-model` names both of its readers rather than leaving the second implicit.
The impact analysis becomes the second step of the ingestion, before anything is written.

Two of the seven could not be closed the way the review proposed, and the reason is the same for
both. The plugin manifest is a harness-owned vocabulary that closes its object, so there is nowhere
in it to declare a runtime dependency; what a consumer gets instead is a guard on every third-party
import naming the install, and rule **C05** in `check_component_prose.py` keeps the declaration in
each script's docstring true and every guard present. And the materializer performs one of the four
cross-object checks that were owed — that every reference resolves — while three remain owed and are
now stated as three rather than as "nothing performs them".

## Consequences

**Seven contracts move rather than mutate**, each with its lock entry, an executable hop and a test:
`knowledge-object/5`, `staged-knowledge-object/2`, `knowledge-intake-plan/5` and then `/6`,
`domain-model/4`, `impact-analysis/4`, `knowledge-authoring-result/2`, `validation-evidence/3`, plus
`knowledge-system/1` which is new. The hops differ on purpose. Naming a consumer adds a value the
artifact always had and never stated, so those are additive. Dropping `ddd` from a lifecycle entry is
a deletion that loses nothing, because whatever a `/4` plan carried there was invented to satisfy a
requirement that should not have existed. Refusing a framework identifier in `sources` **refuses**
rather than dropping the entry: `sources` is what a reviewer reads to tell a fact read out of an
existing artifact from one the business stated, so an object left with fewer sources than it was
written from would be making a weaker claim than the one somebody checked.

**One of the seven was a live defect, and the fix exposed why nothing had caught it.** The `ddd`
conflict was not theoretical: the expansion emitted `ddd: ""` for a lifecycle, which fails the plan's
own pattern, so any model carrying a state machine produced an invalid plan. No test model held a
lifecycle. One does now, and it asserts the object carries no `ddd` while every other type still
requires one.

**`knowledge-system` gained a contract because the argument against one expired.** Leaving it
unvalidated was defensible while the knowledge validator checked its four facts by name — a schema
would have been a second home for them. That validator went with the generation path, so the facts
went from checked in one place to checked in none, and a scaffold that fills in no default cannot
catch a value edited to nonsense afterwards. The contract fixes the shape of a timezone, a currency,
an identity strategy and a line ceiling, and chooses none of them: those are facts about the
repository that installs Siegard.

**The tenth defect is left open by decision.** No test runs the whole pipeline over a real base from
model to promoted objects. What exists instead is a chain of per-step tests over the modeller's own
worked example, each holding one boundary. That is weaker in one specific way — it cannot catch a
defect that only appears when the steps compose — and the reference run itself is the only evidence
the composition works. It is recorded here rather than buried, because a reader is entitled to know
which of the twelve was answered and which was declined.

### What was rejected

**Deleting the references instead of building the materializer.** It was the cheaper of the two
corrections the review offered and it removes the wrong thing. `knowledge-graph/2` describes an
artifact the ontology requires to be derived and never authored; deleting the prose would have left
the contract with no producer and no explanation, which is the state that produced this record.

**A dependency field in the plugin manifest.** It would make every conforming manifest invalid,
because the harness owns that vocabulary and closes the object. A framework that broke its own
manifest to document a dependency would have documented nothing a consumer could install.

**`consumer` as a free string.** A closed value is what makes it checkable, and the one artifact with
two readers names both rather than widening to prose. An artifact whose consumer cannot be named is
an artifact nobody reads, and that is a finding rather than a field to soften.

### What would falsify this

A consumer whose base legitimately holds an object sourced from a framework artifact — a knowledge
object derived from an earlier *generated* model, in a repository that keeps those as material. The
refusal in `knowledge-object/5` would then be blocking a real case, and the right answer is a
separate field naming derived provenance rather than widening `sources` back. Nothing has shown it,
and inventing the field before the case would be the speculative generalization this repository
refuses.
