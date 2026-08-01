---
id: "0015"
title: Compile only accepted knowledge, so that promotion is required for something
status: superseded
contract_version: adr/1
---

# Compile only accepted knowledge, so that promotion is required for something

**Superseded by `docs/adr/0018-a-knowledge-object-carries-no-status.md`.** The gate below has no scope
left to guard — the generation path it sat on was removed — and the promotion it made consequential was
removed with the `status` field itself. Kept for history and for the migration 0018 defines.

## Context

Two accepted specifications disagreed, and nothing in either resolved it.

`foundation/0001-knowledge-object-driven-development.md` R23 puts a `proposed` knowledge object at
level 0 of the maturity ladder, where it "binds nothing" and "enters context only". R26 makes a
knowledge object derived from existing code or material born `proposed`, recording the source it was
read from, and "requires a maintainer to promote" it — because deriving knowledge from an artifact
"cannot canonize a defect as a rule".

`foundation/0004-generation-and-reproducibility.md` said nothing about `status` at all. Neither did
the materializer, the knowledge validator, or scope resolution: the field was read by the projections
and by nothing that decided anything.

So generation compiled `proposed` knowledge, and the promotion R26 demands was demanded for nothing.
A defect read out of existing material became source with nobody approving it, which is the exact
outcome R26 exists to prevent. The gap was invisible because every knowledge object in the framework's
own fixture was `proposed` — not by decision, but because all seven knowledge-object scaffolds
hardcode `status: proposed` and nothing had promoted the fixture. The default survived by omission and
looked like a state somebody chose.

This surfaced while designing the ingestion path, where it matters most: material arriving from an
outside domain analysis is precisely the `proposed`, provenance-carrying knowledge R26 governs.

## Decision

A generation scope holds only knowledge objects whose `status` is `accepted`. A member or a declared
root at any other status blocks the scope, named. `foundation/0004` R54 states it.

Three boundaries make the gate narrow rather than sweeping.

**It is on the scope, not on the materializer.** Validation must keep validating a `proposed` object —
a validator that refused would never report what an object has to fix before promotion — and context
resolution must keep reading one, because R23 admits it into context by name. What changes is only
what *compiles*.

**It blocks rather than skips.** R21 already makes a scope fail closed. A scope that dropped an
unaccepted member would generate less software than was asked for and report success.

**It does not reach ADRs.** An ADR is a graph node and never a knowledge object; it is no member of a
scope and yields no artifact. Gating it would block generation on the status of a rationale record.

`superseded` is excluded by the same rule and needs no separate clause: generating from retired
knowledge would produce the system that was replaced.

## Consequences

**It is a breaking change** under `.claude/rules/compatibility.md` — it "changes the observable
contract of an installed user-invocable skill", because `generate` now refuses a scope it used to
compile. The obligations that rule states, and what happened to each:

- the break is stated here and in `foundation/0004` R54;
- the migration path is promotion: a repository generating from `proposed` knowledge promotes what it
  meant to compile. Nothing persisted is invalidated and no artifact needs rewriting;
- no contract is versioned, because none changed — the gate is behavior over a field the ontology
  already required;
- tests assert both directions: a proposed root, a proposed member reached by expansion, and a
  superseded root each block; a proposed ADR does not; and the accepted scope still resolves, so the
  blocking tests are not passing because everything blocks;
- **release documentation is not updated, because none exists.** The obligation is unmet and recorded
  as unmet, for the same reason `docs/adr/0014-a-verdict-over-an-empty-base-names-nothing.md` records
  it.

**The framework's own evidence had to be promoted.** All 27 knowledge objects in
`fixtures/knowledge-two-context/` were `proposed`, and 21 of them produced the 59 artifacts in
`fixtures/generation-run/out`. They are now `accepted`, which is the honest status for objects authored
as framework evidence: they were not derived from code, so R26 never reached them. No test asserted on
their status, so nothing was weakened by the promotion — the gate is exercised directly instead, which
is better evidence than a fixture's resting state.

**`fixtures/pack-minimal/` was rooted on a superseded object.** Its generation run declared
`ko.rule.sales.proposal-validity` as the root and its scope carried it as a member. Rooting generation
on retired knowledge was always wrong; no gate read `status`, so nothing reported it, and the four
derived artifacts were regenerated from an accepted root. Two tests in the pipeline suite mutated that
object's file to prove a scope invalidates and an unresolvable member blocks — both now derive the path
from the root's own identifier, so a future change of root moves them with it rather than leaving them
green and vacuous.

### What was rejected

**Leaving it as it was and recording the conflict.** Cheapest, and it keeps a rule that requires
nothing: R26's promotion would remain a step with no consequence, and the first ingestion of an outside
domain analysis would turn unreviewed material into source.

**Warning instead of blocking** — generating anyway and reporting how many objects in the scope are
unaccepted. It reads as a compromise and is not one: R21 makes a scope fail closed, so a warning would
be the one place in the generation path that degrades, and the report nobody reads is the report that
was chosen for being easy to ignore.

**Gating the materializer instead.** It would have been a smaller change and it breaks two things the
ladder depends on: validation could no longer tell a proposed object what to fix, and resolution could
no longer put one in context, which R23 requires by name.

### What would falsify this

A repository that legitimately generates from knowledge it has not accepted — a spike, a throwaway
prototype, a migration in progress. If that case is real and recurring, the gate belongs on the run
rather than on the scope, as a declared and recorded exception rather than a status read. Nothing has
shown it yet, and inventing the escape hatch before the case would be the speculative generalization
this repository refuses.
