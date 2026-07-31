---
id: "0009"
title: Fix the context package as a contract, and measure whether resolution earns its place
status: accepted
contract_version: spec/1
---

# Context assembly

## Scope

This specification fixes the contract of the [context package](../docs/concepts/context-package.md) — the
artifact that names exactly the knowledge one run of context resolution puts in scope — and the conditions
under which context resolution is worth performing at all. It decides five things:

1. the package's form: what it carries, and what a consumer may read because of it;
2. how a budget is stated and recorded;
3. the closed set of stop criteria, that each is recorded rather than inferred, and the separate record of
   what degraded during the run;
4. which relationships expansion may follow;
5. the measurement that decides whether resolution outperforms sending the whole bundle, and the
   consequence if it does not.

It defines contracts, not an algorithm. Expansion order, traversal strategy, and any caching are
implementation, and this document deliberately leaves them free. R17 is the one bound on that freedom, and
it is a bound on *change* rather than a choice of order: whatever order an implementation picks is fixed by
the contract version it declares, because a package that recomputes to a different set after an upgrade
cannot be the `claim-recorded` artifact R13 says it is.

It decides nothing about the ontology's edges, which `specs/0003` fixes and this document only agrees to
respect; nothing about the workflow phase that produces the package, which `specs/0001` fixes; and
nothing about how a capability declares the context it needs, which is `specs/0007` R9.

It also adds nothing to `specs/0006`'s closed set of capability classes, and it is worth stating rather
than leaving to inference: expansion is deterministic, so whatever performs it is a script under
`specs/0005` R5 and `specs/0006` R8, and root selection is model judgment under `specs/0001` R12. No
resolver class is needed, and none is proposed here.

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
[change request](../docs/concepts/change-request.md),
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
- **R2** — The package is the boundary of what may be read while it is in scope. A consumer reads no
  knowledge the package does not name, and a consumer that needs something absent reports a gap rather
  than reading around the package. Reading around it makes the recorded scope a description of intent
  rather than of fact.
- **R3** — Each entry names an identifier and the content hash of what was read. The hash is what lets a
  later reader establish which version a decision was made against without storing a second copy of it.
- **R4** — Each root carries the claim that justified selecting it, in the package itself. A root with no
  claim is indistinguishable from an arbitrary inclusion, and the review that judgment depends on has
  nothing to read.
- **R5** — The package records the [change request](../docs/concepts/change-request.md) and the
  resolution run it was assembled for, so that [provenance](../docs/concepts/provenance.md) runs from a
  decision back to the scope that informed it. That pair identifies the run using vocabulary the concept
  bundle already holds; an earlier draft said *task*, which the bundle does not define and which therefore
  bound nothing.
- **R6** — One package serves one run of context resolution. The phases downstream of that run read it,
  and the next resolution produces a new package rather than extending this one. `specs/0001` R7 is what
  makes this concrete rather than tidy: a validation failure returns the workflow to implementation and
  the failed check's knowledge object enters the *next* resolution as a mandatory root, so a package
  carried across that boundary would state a scope the later attempt was never granted.

### Budget and stopping

- **R7** — The budget is stated by the caller, in a unit the package records, and the package records what
  was consumed against it. A framework-chosen budget would be a threshold asserted without evidence,
  which `specs/0001` R10 forbids.
- **R8** — Expansion stops for exactly one recorded reason, from the closed set: the closure is complete,
  the budget is exhausted, a declared depth limit is reached, or a relationship could not be resolved.
  The reason is recorded in the package, never inferred by a reader from what is present. A stop reason is
  not the record of everything that went wrong during the run, which is R15's separate field: one traversal
  can meet several conditions and stop on one.
- **R9** — Expansion follows only relationships the [ontology](../docs/concepts/ontology.md) declares. A
  relationship absent from `specs/0003`'s edge table is not traversed, and a traversal a capability wants
  that the ontology does not hold is a request to change the ontology.

### Whether resolution earns its place

- **R10** — Every resolution run records the roots it selected and the volume of context the package
  produced, in the unit R7 states. Those records, read against what the change turned out to need, are
  what make both of `docs/bootstrap.md` stage 3's measurements computable — selection recall and tokens
  per change — and R11 is decided on both rather than on volume alone. Recall is computable only after the
  change closes, which is why this requirement asks for the record rather than for the figure. This is
  observability: no gate, threshold, or acceptance criterion is expressed as a recall or coverage figure.
- **R11** — Context resolution is retained only while measurement shows it selects better than including
  the whole bundle for the repository in question. Where it does not, it is replaced by the simpler
  mechanism, and this specification's machinery is retired rather than kept for completeness.
- **R12** — The measurement in R10 is calibrated from executed runs, and any depth or budget default the
  framework later ships is recorded together with the evidence that produced it. This document asserts no
  such default.

### Persistence

- **R13** — A package is never committed. Its
  [artifact persistence](../docs/concepts/artifact-persistence.md) is `claim-recorded`, and that value is
  derived rather than chosen: the body recomputes from the recorded roots, the graph, the budget, and the
  expansion's contract version with no model in the loop (`specs/0001` R12), and something outside the run
  pins its identity, because R3's hashes and R5's identity exist so that a later decision can be traced
  back to it. Those four are the declared inputs `specs/0004` R48 requires the claim to record. `specs/0004`
  defers this artifact's persistence until its contract exists; R1 above is that contract, so this document
  decides the value under `specs/0004`'s rule rather than asserting one of its own. A stored copy would be
  a second authority for knowledge the graph already holds.
- **R14** — A degradation recorded in the package is carried forward with it. A consumer that reads a
  degraded package is told it is degraded, because [fail-soft](../docs/concepts/fail-soft.md) guarantees
  independence of evaluation and not sufficiency of what was assembled.

### The degradation record

R14 requires a degradation to be carried forward and nothing above says what one is. `specs/0001` R13 names
four — a root that cannot be located, a cycle that cannot be resolved, contradictory knowledge, an exhausted
budget — and R8's closed set of stop reasons holds neither the cycle nor the contradiction, while holding a
depth limit R13 does not name. The two vocabularies were written for different questions and were never
reconciled; these requirements reconcile them. `specs/0001` is accepted and is the authority where they
still appear to differ, which is the rule this document's **Decided elsewhere** already states.

- **R15** — The package records a list of degradations separately from the single stop reason of R8. Each
  entry carries a code from the closed set `unresolved_root | unresolved_relationship | cycle |
  contradictory_knowledge | budget_exhausted | depth_limit`, the subject it was observed on, and a
  structured reference to the evidence. A run that meets several conditions records several entries; one
  field cannot hold them, and losing all but the first is what makes the acceptance gate of `specs/0001`
  R14 report less than what happened.
- **R16** — The first four codes of R15 are the four degradations `specs/0001` R13 names, and the last two
  are the truncations. `budget_exhausted` and `depth_limit` are degradations for the same reason R13 gives
  for the budget: the closure was cut short and knowledge that belonged in scope is absent. `closure_complete`
  is the one stop reason of R8 that is never a degradation, and `unresolved_root`, `cycle`, and
  `contradictory_knowledge` are never stop reasons, because `specs/0001` R13 requires resolution to continue
  past each of them. Where the stop reason is not `closure_complete`, the degradation list holds a matching
  entry.

### Expansion order

- **R17** — Expansion order is fixed by the [contract version](../docs/concepts/contract-version.md) the
  package records, and a change to the order that changes which knowledge objects a package holds is a
  contract version change under `.claude/rules/compatibility.md`. This document still specifies no order,
  which the **Scope** above leaves free deliberately; what it forbids is an order free to differ between two
  runs of one contract version. Without this, R13's `claim-recorded` is a label: `specs/0004` R48 requires a
  discarded body to recompute to the recorded content hash, and a package truncated by a budget or a depth
  limit recomputes to a different set the moment the traversal reorders. Under this requirement the failure
  becomes visible as a version mismatch instead of a hash that silently stops matching.

## What satisfied acceptance

Accepted on 2026-07-31 by maintainer decision, which `CLAUDE.md` **Normative sources** makes sufficient on
its own. The conditions this document had set were **not** met. They are kept below rather than deleted,
because they are the evidence this document still owes and removing them on acceptance would turn an open
debt into a silent one.

What that costs is stated rather than glossed. From here `.claude/rules/compatibility.md` governs this
document, so a change to a requirement is a breaking change owing a migration path and a migration test
rather than a revision — and the first component built against it is the thing most likely to demand
exactly such a change. `specs/0001-knowledge-object-driven-development.md` was accepted the other way, on
evidence, with the requirements its three unmet conditions covered moved out to
`specs/0014-acceptance-closure-and-escalation.md` rather than accepted unexercised. That route was
available and was not taken here.

### Conditions recorded before acceptance, still outstanding

1. A bundle large enough for selection to matter exists as a fixture, and resolution runs against it.
   Every requirement here is unexercised today, and R11 in particular cannot be satisfied by argument —
   `docs/bootstrap.md` stage 3.
2. The measurement of R10 is taken and recorded, and the result is acted on: either resolution is retained
   with the evidence that justifies it, or R11 is applied and this specification is narrowed to the
   simpler mechanism. Accepting this document before that measurement would bind machinery the evidence
   might discard.
3. A test asserts that the same roots, graph, budget, and expansion contract version produce a
   byte-identical manifest, which is `specs/0001` R12's determinism claim made checkable.
4. A test covers R2's rejection direction: a consumer that reads an artifact the package does not name is
   detected. Without it, R2 is a convention rather than a boundary.
5. The stop reasons of R8 are each produced by a fixture at least once, including the unresolvable case,
   so the closed set is shown to be complete rather than assumed.
6. R13's `claim-recorded` is exercised rather than declared: the schema of R1 carries the persistence
   value, and a test discards a package and rebuilds it from its recorded roots, graph version, budget, and
   expansion contract version. A persistence value nothing recomputes is a label, which is the failure
   `specs/0004`'s rule was written to prevent. The rebuild is run against a package the budget truncated,
   because a package that reached closure recomputes under any order and therefore tests nothing about R17.
7. A fixture records more than one degradation in one run under R15 while recording exactly one stop reason
   under R8, and a test asserts that a stop reason other than `closure_complete` has a matching degradation
   entry (R16). Each of `specs/0001` R13's four is produced at least once, which is what shows the closed
   set of R15 covers the vocabulary the accepted specification already binds.
8. ~~`specs/0001` is accepted.~~ **Met** on 2026-07-31. This document's foundation — R11 through R15 there —
   now binds, so what remains unmet above is this document's own evidence rather than its basis.
