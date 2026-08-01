---
id: "0018"
title: Drop the knowledge lifecycle, so what the base holds is what binds
status: accepted
contract_version: adr/1
---

# Drop the knowledge lifecycle, so what the base holds is what binds

## Context

`foundation/0003` R26 gave every knowledge object a `status` from `proposed | accepted | superseded`,
R35 required a retired object to be kept in the base carrying `superseded_by`, and `foundation/0001`
R11 and R12 made an authored object born `proposed` and put its promotion behind a maintainer.
`docs/adr/0015-only-accepted-knowledge-compiles.md` then gave the field its one consequence: a
generation scope holding a member at any other status was blocked.

Three things have changed since, and together they leave the field paying nothing.

**The consumer of the gate is gone.** The generation path — the scope, the plan, the manifest, the
materializer, the `generate` skill — was removed from `src/claude/` on this branch. Nothing in the
distribution reads `status` to decide anything. `foundation/0004-generation-and-reproducibility.md`,
where ADR-0015 put R54, no longer exists. What remains is a required field that the schema validates
and no capability branches on, which is the exact condition ADR-0015 opened by describing.

**The promotion never had a mechanism.** `foundation/0001` R12 admitted "a maintainer's decision, or a
deterministic approval mechanism the governed repository defines" and the framework shipped neither.
The workflow machinery that could have carried one was removed in
`docs/adr/0016-remove-the-workflow-machinery.md`. A consumer inherited an obligation with nothing to
discharge it, and ADR-0015's own evidence records what that produces: every object in the framework's
fixture sat at `proposed` "not by decision, but because all seven knowledge-object scaffolds hardcode
`status: proposed`". The default survived by omission there too.

**Retention contradicts single authority.** R35 kept a retired object in the base beside the one that
replaced it, so the base held two answers to one question and relied on every reader honouring a field
excluded from traversal in both directions. `foundation/0003` R5 gives one object one question;
retention is the one place the ontology handed a reader two.

## Decision

A knowledge object, a knowledge graph node, and a consumer's decision record carry no status. What the
knowledge base holds is current and binds; a superseded revision is not retained. `foundation/0001` R11
and `foundation/0003` R26 and R35 state it, and this record does not repeat them.

ADR-0015 is superseded by this one. Its gate has no scope left to guard and its premise — that
promotion must be required for something — is answered by removing the promotion rather than by
finding it a consumer.

Two boundaries keep this from reaching further than it should.

**It does not touch this repository's own artifacts.** A specification, an ADR, and a concept file in
`docs/concepts/` keep `status`, because a maintainer decides those and the vocabulary in
`docs/adr/README.md` is exercised — this record is written `accepted` and supersedes another. What is
removed is the lifecycle the *framework* imposed on a *consumer's* knowledge.

**Provenance stays, and is what `proposed` was actually being read for.** `generated`, `verified`, and
`sources` still record who wrote an object, when, and from what material. A reader asking whether a fact
was read out of existing code rather than stated by the business is answered by `sources`, which names
the artifact — a strictly better answer than a three-value enum that named nothing.

## Consequences

**It is a breaking change** under `.claude/rules/compatibility.md`, on two entries: a schema alteration
that makes previously invalid instances valid, and one that makes previously valid instances invalid.
The obligations that rule states, and what happened to each:

- the break is stated here and in `foundation/0001` R11 and `foundation/0003` R26 and R35;
- three contracts are versioned rather than mutated: `knowledge-object/2`, `knowledge-graph/2`, and
  `knowledge-decision/2`, each with its superseded entry in `schemas/contract-versions.json` and an
  executable hop in `scripts/migrate_contracts.py`;
- the migration for a `superseded` object is deletion, not a stamp. `knowledge_object_1_to_2` refuses
  one rather than dropping the field, because stamping a retired revision `/2` would readmit it to the
  base as a current fact — which is the outcome R35's removal exists to prevent. A base holding one
  migrates mechanically; a base holding a retired revision has a decision to make and is told so;
- **the migration and version checks did not run, and neither did any test.** `scripts/` imports
  `generator_lib` from `src/claude/bin/`, which this branch deletes, so `make validate`, `make test`,
  `make knowledge`, and `make dist-check` all fail before reaching anything this change touches. The
  obligation to add a migration test is unmet and recorded as unmet, for the same reason
  `docs/adr/0014-a-verdict-over-an-empty-base-names-nothing.md` records one;
- release documentation is not updated, because none exists.

**The migration was exercised, once, and it refused.** The 27 authored objects of
`fixtures/knowledge-two-context/` were migrated through `knowledge_object_1_to_2`. It refused exactly
one — `ko.rule.sales.proposal-validity`, the retired revision that existed to instantiate
`superseded_by` — which was deleted, its replacement `ko.rule.sales.proposal-expiration` already
carrying the fact. That is the only run this change has behind it, and it is recorded because
`docs/adr/0019-the-repository-keeps-no-fixtures.md` then removed the tree it ran over: the evidence
existed, and no longer does.

**`dist/.claude/` was removed rather than regenerated.** The committed tree still shipped
`knowledge-object/1` with `status` in it, and `make dist` cannot run on this branch, so the choice was
between keeping a distribution that contradicts its own source and holding none. A maintainer chose
none on 2026-08-01; the 62 files are in this commit's parent. `make dist` rebuilds it, and both
`make validate` and `make dist-check` fail loudly in the meantime rather than passing over an absent
tree — verified: `check_capabilities.py` exits 2 and `verify_dist.py` exits 1.

### What was rejected

**Keeping `status` as an optional field nobody reads.** It costs one line in a schema and it is the
condition this record was written to end: a field a validator enforces and no capability branches on
teaches every reader that the base has a maturity model, and the first consumer to build a gate on it
rebuilds ADR-0015 without its argument.

**Keeping supersession and dropping only `proposed`.** `superseded_by` was the one field naming a node
that was deliberately not an edge, with a traversal prohibition in both directions written specifically
for it — R13, R18, and the graph's `edge_kinds` each carried a clause for the exception. Keeping the
exception to retain history that version control already holds is the worse trade.

**A `deprecated` flag instead, per OKF.** ADR-0005 derived this contract from Open Knowledge Format,
which defines `draft | stable | deprecated`, and adopting OKF's vocabulary would close the documented
divergence. It answers the same question the same way: a consumer would have to decide what a
`deprecated` object means for what it generates, and nothing in this framework does.

### What would falsify this

A consumer that needs to record a domain fact as agreed-but-not-yet-in-force — a rule taking effect on
a date, a regulation in a grace period. That is a fact about the domain with a date attached, and it
belongs in the object as a typed attribute or as a `lifecycle`, not in a framework-imposed enum over
the object itself. If instead a consumer needs review state per object, with a mechanism that sets it
and a capability that reads it, this decision is wrong and the field returns with both.
