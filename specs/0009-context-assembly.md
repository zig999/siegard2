---
id: "0009"
title: Fix the context package as a contract, and measure whether resolution earns its place
status: proposed
contract_version: spec/1
---

# Context assembly

## Scope

This specification fixes the contract of the [context package](../docs/concepts/context-package.md) — the
artifact that names exactly the knowledge one task may read — and the conditions under which context
resolution is worth performing at all. It decides five things:

1. the package's form: what it carries, and what a consumer may read because of it;
2. how a budget is stated and recorded;
3. the closed set of stop criteria, and that each is recorded rather than inferred;
4. which relationships expansion may follow;
5. the measurement that decides whether resolution outperforms sending the whole bundle, and the
   consequence if it does not.

It defines contracts, not an algorithm. Expansion order, traversal strategy, and any caching are
implementation, and this document deliberately leaves them free.

It decides nothing about the ontology's edges, which `specs/0003` fixes and this document only agrees to
respect; nothing about the workflow phase that produces the package, which `specs/0001` fixes; and
nothing about how a capability declares the context it needs, which is `specs/0007` R9.

It governs the framework Siegard ships. It does not govern this repository's own development process,
which `CLAUDE.md` defines.

### Provenance

Nothing here has been exercised. `docs/bootstrap.md` stage 3 is the stage that builds context resolution,
and it has not started; the thin path of stage 2 ran with resolution degenerate, because in a bundle of a
few objects the impact set already is the context.

That has a consequence this document is built around rather than hiding. Stage 3 attaches an abandonment
criterion — if selection recall is indistinguishable from sending the whole bundle, the mechanism is
replaced by inclusion by tag or domain. A specification written before that measurement could easily
specify machinery the evidence then discards. So this document fixes the *artifact* and the
*measurement*, and states as little as possible about the resolution that produces it. R11 below makes
the abandonment criterion a requirement rather than a note.

### Decided elsewhere, deliberately not restated here

`specs/0001` R11 through R15 already fix the substance of resolution's behavior: that the package is a
manifest of identifiers and hashes rather than copies, that root selection is judgment and expansion is
deterministic, that resolution never blocks and records degradation instead, that a recorded degradation
reaches acceptance, and that resolution never invents a knowledge object to fill a gap. This document
gives those decisions a contract to live in; where the two appear to differ, `specs/0001` is the
authority.

`specs/0003` owns the node types and the edges. `specs/0002` owns what may be permanent knowledge at all,
and its rule against expressing a gate as a coverage figure is why R10 below exists.

## Definitions

This specification uses these terms as the concept bundle defines them:
[context package](../docs/concepts/context-package.md),
[knowledge graph](../docs/concepts/knowledge-graph.md),
[knowledge object](../docs/concepts/knowledge-object.md),
[ontology](../docs/concepts/ontology.md),
[fail-soft](../docs/concepts/fail-soft.md),
[contract version](../docs/concepts/contract-version.md),
[provenance](../docs/concepts/provenance.md),
[representation ratio](../docs/concepts/representation-ratio.md),
[generative completeness](../docs/concepts/generative-completeness.md),
[artifact persistence](../docs/concepts/artifact-persistence.md).

## Requirements

### The package as a contract

- **R1** — The context package has a versioned schema in `schemas/`. A consumer parses it to decide what
  it may read, which is data driving a decision, and it selects behavior on its
  [contract version](../docs/concepts/contract-version.md).
- **R2** — The package is the boundary of what a task may read. A consumer reads no knowledge the package
  does not name, and a consumer that needs something absent reports a gap rather than reading around the
  package. Reading around it makes the recorded scope a description of intent rather than of fact.
- **R3** — Each entry names an identifier and the content hash of what was read. The hash is what lets a
  later reader establish which version a decision was made against without storing a second copy of it.
- **R4** — Each root carries the claim that justified selecting it, in the package itself. A root with no
  claim is indistinguishable from an arbitrary inclusion, and the review that judgment depends on has
  nothing to read.
- **R5** — The package records the identity of the task it was assembled for, so that
  [provenance](../docs/concepts/provenance.md) runs from a decision back to the scope that informed it.
- **R6** — One package serves one task. A package reused across tasks stops describing what any single
  task was permitted to read.

### Budget and stopping

- **R7** — The budget is stated by the caller, in a unit the package records, and the package records what
  was consumed against it. A framework-chosen budget would be a threshold asserted without evidence,
  which `specs/0001` R10 forbids.
- **R8** — Expansion stops for exactly one recorded reason, from the closed set: the closure is complete,
  the budget is exhausted, a declared depth limit is reached, or a relationship could not be resolved.
  The reason is recorded in the package, never inferred by a reader from what is present.
- **R9** — Expansion follows only relationships the [ontology](../docs/concepts/ontology.md) declares. A
  relationship absent from `specs/0003`'s edge table is not traversed, and a traversal a capability wants
  that the ontology does not hold is a request to change the ontology.

### Whether resolution earns its place

- **R10** — Every resolution run records the volume of context it produced and the roots it selected.
  This is observability. No gate, threshold, or acceptance criterion is expressed as a recall or coverage
  figure.
- **R11** — Context resolution is retained only while measurement shows it selects better than including
  the whole bundle for the repository in question. Where it does not, it is replaced by the simpler
  mechanism, and this specification's machinery is retired rather than kept for completeness.
- **R12** — The measurement in R10 is calibrated from executed runs, and any depth or budget default the
  framework later ships is recorded together with the evidence that produced it. This document asserts no
  such default.

### Persistence

- **R13** — A package is recomputed from its roots, the graph, and its budget rather than committed. It is
  disposable by `specs/0004`'s persistence rule, and a stored package would become a second authority for
  knowledge the graph already holds.
- **R14** — A degradation recorded in the package is carried forward with it. A consumer that reads a
  degraded package is told it is degraded, because [fail-soft](../docs/concepts/fail-soft.md) guarantees
  independence of evaluation and not sufficiency of what was assembled.

## Validation required before acceptance

1. A bundle large enough for selection to matter exists as a fixture, and resolution runs against it.
   Every requirement here is unexercised today, and R11 in particular cannot be satisfied by argument —
   `docs/bootstrap.md` stage 3.
2. The measurement of R10 is taken and recorded, and the result is acted on: either resolution is retained
   with the evidence that justifies it, or R11 is applied and this specification is narrowed to the
   simpler mechanism. Accepting this document before that measurement would bind machinery the evidence
   might discard.
3. A test asserts that the same roots, graph, and budget produce a byte-identical manifest, which is
   `specs/0001` R12's determinism claim made checkable.
4. A test covers R2's rejection direction: a consumer that reads an artifact the package does not name is
   detected. Without it, R2 is a convention rather than a boundary.
5. The stop reasons of R8 are each produced by a fixture at least once, including the unresolvable case,
   so the closed set is shown to be complete rather than assumed.
6. ~~`specs/0001` is accepted.~~ **Met** on 2026-07-31. This document's foundation — R11 through R15 there —
   now binds, so what remains unmet above is this document's own evidence rather than its basis.
