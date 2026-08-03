---
id: "0002"
title: Hold the minimum knowledge specialized agents need to reproduce the system
status: accepted
contract_version: spec/1
---

# Knowledge economy principles

## Scope

This specification fixes the economic constraints on what a repository Siegard governs records as
permanent knowledge. It decides three things: the governing principle, the test that admits or removes an
element of permanent knowledge, and the boundary between the two kinds of fact a software project holds.

It decides nothing about *how* knowledge is represented — which node types exist, what notation they use,
or how software is produced from them. Those are separate specifications that cite this one:
`specs/0003` for the ontology and the notation, `specs/0004` for generation and reproducibility. The
dependency is declared in their **Scope** sections rather than asserted here, because three specifications
sit at one precedence level and none outranks another.

It governs the framework Siegard ships. It does not govern this repository's own development process,
which `CLAUDE.md` defines, and it does not govern the concept bundle in `docs/concepts/`, which
`docs/adr/0005-okf-derived-concept-model.md` governs.

### Decided elsewhere, deliberately not restated here

| Question | Authority |
|---|---|
| The workflow every change request follows | spec 0001 |
| Why coverage figures are observability rather than gates | spec 0001 R25 |
| The constraint order, and the exclusion of human convenience | `CLAUDE.md` **Decision order** |
| That one concept has one authoritative definition | `CLAUDE.md` **Authority placement** |
| That an abstraction requires a current requirement and a testable contract | `CLAUDE.md` **Scope** |
| Where stack knowledge lives, once the knowledge base has excluded it | undecided; `specs/0004` proposes an answer |

Two copies of a rule diverge. Where this specification needs one of the above, it cites it.

## The governing principle

> The permanent knowledge stored in the [knowledge base](../docs/concepts/knowledge-base.md) is the
> minimum necessary for [specialized agents](../docs/concepts/specialized-agent.md), using their own
> knowledge of architecture and technology, to deterministically produce the same software behaviour.

Siegard is not building a universal compiler. It is building a knowledge base precise enough to orchestrate
agents that are already capable, and the difference decides what belongs in an artifact.

The failure this principle exists to prevent is not imprecision. It is a representation that grows until
maintaining it costs more than writing the software it describes. A framework that reaches that point is
technically elegant and economically worthless, and nothing in a schema detects the condition — which is
why the principle is normative and the [representation ratio](../docs/concepts/representation-ratio.md) is
instrumented.

Two tests derive from the principle.

**Minimum sufficient representation.** An element of permanent knowledge exists only if it increases the
capability to generate software or the capability to verify knowledge consistency automatically. An element
that does neither is removed, and removal is the default where the test is ambiguous.

**The differentiation test.** The knowledge base holds only what differentiates this system from another
system built on the same technology.

The second test is stated as differentiation rather than as "what an agent already knows", because what an
agent knows is not observable and cannot be validated, while what differentiates two systems can be argued
from two knowledge bases.

## The boundary

A fact is [domain knowledge](../docs/concepts/domain-knowledge.md) when changing it changes *this* system.
A fact is [stack knowledge](../docs/concepts/stack-knowledge.md) when changing it changes *every* system
built on the same technology.

| Fact | Changing it changes | Kind |
|---|---|---|
| A proposal expires after thirty days | this system | domain |
| A monetary amount carries scale two | this system | domain |
| Which attributes form an identity | this system | domain |
| Which state transitions are legal | this system | domain |
| What a bounded context publishes | this system | domain |
| Table names are the pluralized entity name | every system on the technology | stack |
| Where a repository interface sits in the tree | every system on the technology | stack |
| The layering convention of a project | every system on the technology | stack |
| How a guard clause is expressed idiomatically | every system on the technology | stack |
| Whether a migration follows or precedes a schema change | every system on the technology | stack |
| How a by-identity reference becomes a foreign key | every system on the technology | stack |

The right-hand column is not a smaller kind of the left. It is a different kind, it already exists inside a
competent specialized agent, and authoring it buys no differentiating content while costing maintenance on
every change.

This specification states the boundary **negatively**: the knowledge base does not hold stack knowledge.
Where stack knowledge does live is a separate decision, and stating the exclusion without it keeps the
boundary usable now rather than after that decision is settled.

## Definitions

Terms used normatively below.

| Term | Concept |
|---|---|
| knowledge base | [knowledge-base](../docs/concepts/knowledge-base.md) |
| knowledge object | [knowledge-object](../docs/concepts/knowledge-object.md) |
| domain knowledge | [domain-knowledge](../docs/concepts/domain-knowledge.md) |
| stack knowledge | [stack-knowledge](../docs/concepts/stack-knowledge.md) |
| representation ratio | [representation-ratio](../docs/concepts/representation-ratio.md) |
| specialized agent | [specialized-agent](../docs/concepts/specialized-agent.md) |
| capability | [capability](../docs/concepts/capability.md) |
| accepted | [accepted](../docs/concepts/accepted.md) |
| fixture | [fixture](../docs/concepts/fixture.md) |

## Requirements

- **R1** — The knowledge base holds the minimum permanent knowledge sufficient for specialized agents,
  using their own knowledge of architecture and technology, to deterministically produce the same software
  behaviour.
- **R2** — An element of permanent knowledge exists only if it increases the capability to generate software
  or the capability to verify knowledge consistency automatically. An element that does neither MUST be
  removed, and removal is the default where the test is ambiguous.
- **R3** — The knowledge base MUST hold only what differentiates this system from another system built on
  the same technology.
- **R4** — The knowledge base MUST NOT hold a naming convention, a directory layout, a project structure, a
  stack architectural pattern, a language idiom, or the mapping from a reference to a storage
  representation.
- **R5** — An authored artifact MUST NOT restate what a specialized agent supplies from its own knowledge
  of a technology.
- **R6** — Where the kind of a fact is contested, the deciding question MUST be whether changing the fact
  changes this system or every system built on the same technology. An argument from what an agent is
  presumed to know is not a valid application of R3.
- **R7** — The representation ratio MUST be instrumented and reported. A rising ratio MUST be answered by
  removing elements of permanent knowledge, never by adding validators to the elements that remain.
- **R8** — No gate, threshold, or acceptance criterion is expressed as a representation-ratio figure, for
  the reason spec 0001 R25 gives about assertion coverage.

## What this specification does not decide

- the unit of the representation ratio in R7, and any range that would count as healthy: a ratio needs two
  generated systems before a number means anything, and inventing one now would produce the target-chasing
  R8 forbids;
- where stack knowledge lives once R4 has excluded it from the knowledge base;
- which node types, notation, or artifacts satisfy R2 and R3 — `specs/0003` and `specs/0004` answer that,
  and each is falsifiable against these tests rather than derived from them mechanically;
- whether an element that fails R2 is removed immediately or on the next change that touches it.

## What satisfied acceptance

This specification presupposed no unbuilt component, and both conditions it stated are met:

1. a maintainer accepted it on 2026-07-30;
2. the four concepts it uses normatively and introduced with it — knowledge base, domain knowledge, stack
   knowledge, representation ratio — are present in `docs/concepts/` with rows in the bundle index, and
   `make validate` passes over the bundle.

What exercised it before acceptance was the reduction R2 and R3 forced on the draft this specification was
separated from: an authored generation ruleset removed in favour of a specialized agent's own knowledge of
its technology, and three attribute parameters replaced by system-level defaults. A principle that changed
nothing would not have been worth accepting.

R7 is the one requirement here that no evidence yet satisfies: no system has been generated, so no ratio
exists. Acceptance therefore carries a live obligation to instrument, and the absence of a measurement MUST
be reported as absence rather than as a healthy ratio.
