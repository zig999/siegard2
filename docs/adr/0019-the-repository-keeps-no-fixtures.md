---
id: "0019"
title: Keep no fixtures, and say what stopped being checked
status: accepted
contract_version: adr/1
---

# Keep no fixtures, and say what stopped being checked

## Context

`fixtures/` held 115 files across seven trees: a two-context knowledge base, a committed generation
run and its output, two target packs, a consumer context package, an upgrade recipe, and a retirement
record. `foundation/0005` R11 has always said a fixture is one kind of evidence and "never a condition
of shipping", so nothing was blocked on them — but a great deal was *checked* through them. Thirteen
test modules and one script read the trees, and five lines of `make validate` ran over them.

Most of that had already stopped working. This branch deletes `src/claude/bin/`, and every validator,
materializer, and projector the fixture checks called lived there. `make validate`, `make test`, and
`make knowledge` fail at import today, before reaching anything a fixture could prove. What remained
was a large committed tree that nothing could execute against and that every subsequent change had to
be migrated through — the change that removed the knowledge lifecycle had just paid that cost,
migrating 27 objects by hand-driven script because the generator could not.

The import failure is narrower than it looks, and the measurement is recorded here because the first
reading of it was wrong: `scripts/` needs exactly two of the deleted modules, `cli.py` in twelve scripts
and `frontmatter_lib.py` in five. Nothing under `scripts/` reaches for the rest of `src/claude/bin/`.
Restoring those two to the import path makes the generator and every validator run again, which is what
made the verification below possible at all.

A maintainer decided on 2026-08-01 to remove the trees and everything that reads them.

## Decision

This repository holds no fixtures. `fixtures/` is deleted, together with the tests and the script that
existed only to run against it. `docs/concepts/fixture.md` stays, because `foundation/0005` R11 uses
the term normatively and a term a binding requirement uses needs a definition whether or not an
instance exists.

No specification changes. R11 already made a fixture optional and named three other channels — a test,
an eval, a run in a consuming repository — so an empty `fixtures/` was always a state the framework
permitted. This record exists because *permitted* is not the same as *free*, and what it cost is below.

## Consequences

**What was deleted.** `fixtures/` entire. Thirteen test modules: `test_knowledge_fixture`,
`test_knowledge_bodies`, `test_knowledge_checks`, `test_knowledge_rejections`, `test_knowledge_repairs`,
`test_projections`, `test_context_resolution`, `test_scaffold_in_use`, `test_pack_typescript`,
`test_generation_pipeline`, `test_generation_e2e`, `test_hooks`, and `tests/support.py`, which was the
copy-the-fixture-and-break-one-thing harness the first six were built on. `scripts/measure_ontology.py`,
whose only input was `fixtures/*/knowledge`. Two classes in `test_lifecycle.py`, and the `template` and
`pack` subjects of `scripts/check_existence_claims.py`, whose evidence globs pointed into
`fixtures/pack-*/`. The `knowledge` target and five lines of `validate` in the `Makefile`.

**What stopped being checked, named rather than absorbed.** This is the cost, and it is not small:

- **every rejection the ontology contract makes.** `foundation/0003` validation item 2 enumerated
  eleven, and `test_knowledge_rejections` was the discharge. Nothing now proves the schema rejects
  what it says it rejects;
- **the positive half of every rejection test.** `test_knowledge_fixture` asserted the pristine tree
  reported clean, which is what distinguished a working validator from one that rejects everything.
  That distinction is gone in both directions at once;
- **the cross-context, totality, and cardinality checks** of R12, R8, and R14 — `test_knowledge_checks`,
  covering both outcomes each;
- **body form** — R38 through R43, in `test_knowledge_bodies`;
- **projection reproducibility.** R46 requires a projection to be reproducible from the graph;
  `test_projections` regenerated and compared byte-for-byte;
- **the R47 utilization measurement.** A type under 5% of nodes with no check branching on it must be
  removed, and nothing measures node shares now;
- **the four repairs `foundation/0003` records.** `test_knowledge_repairs` was the evidence that each
  repair holds in both directions.

Each returns with the validator it exercises, against whatever base that validator is given. Recording
them here is the point of this ADR: an obligation nobody has written down is an obligation nobody
reinstates.

**`make validate` is now four checks.** ADRs, contract versions, components, and component prose, then
capabilities. It no longer touches a knowledge base, because there is none to touch. The comment in the
`Makefile` where the `knowledge` target stood states that `foundation/0003` R31's boundary validator is
an obligation on `src/claude/` rather than on this file, and that what is missing here is a base to run
it against — rather than leaving a target that would report success over an empty glob.

**The checks were run against a restored import path, not against the branch as it stands.** `cli.py`
and `frontmatter_lib.py` were recovered from the previous commit onto `PYTHONPATH`, which is what
`make validate` and `make test` will do for themselves once those two modules have a home again.
Under it: `validate_adrs.py` passes, `check_existence_claims.py` passes, `check_contract_versions.py`
reports nothing against the three contracts 0018 bumped, and the suite runs 306 tests. Of its 139
failures and errors, none names a fixture or any `knowledge-*` contract version — every one resolves
to an artifact this branch deleted before either change: the `bin/` modules themselves,
`hooks.declaration.json`, three removed scaffolds, and `src/claude/CLAUDE.md`, which ships as a
component class no schema covers.

That is evidence about the change, not a green build. `make check` has not passed and cannot until the
import path is repaired.

**A change proposed for `CLAUDE.md` and not applied.** Its layout table carries a `fixtures/` row, its
**Scope** section carries two paragraphs governing how a fixture is proposed and authorized, and
**Commands** names `make knowledge`. All three are now wrong. `CLAUDE.md` is the maintainer's file, so
the exact replacement text was written out in the session that made this change and applied to nothing.
Until a maintainer applies it, `CLAUDE.md` describes a tree that does not exist.

### What was rejected

**Keeping the trees and letting them rot.** They would be migrated through every future contract bump —
0018 had just done exactly that for 27 objects — buying nothing, because no validator can run against
them on this branch. A fixture nothing executes is a committed tree with the authority of evidence and
none of the property.

**Keeping the knowledge base and deleting the rest.** The most defensible half: `knowledge-two-context`
backed seven of the thirteen deleted modules and is the only tree that exercised the ontology, which is
the part of the framework that still exists. It was rejected because the validators it feeds are the
ones this branch deleted, so retaining it preserves the migration cost and restores no check. It is
also the tree most cheaply rebuilt — it is authored, not derived — when a validator returns to read it.

**Deleting the trees and leaving the tests and scripts pointing at them.** Cheapest, and it produces
the failure mode this repository is most consistently built against: a suite that fails for a reason
unrelated to what it asserts, which trains a reader to skip the output.

### What would falsify this

A validator or generator returning to `src/claude/bin/` and having nothing to run against — at which
point the answer is a new fixture proposed under `CLAUDE.md` **Scope**, naming the failure mode it
catches, and not the restoration of these seven trees. The trees are in version control at this
commit's parent for whoever needs to read what they held.
