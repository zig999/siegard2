---
id: "0014"
title: Let an impact analysis say the base was empty, rather than forbid the first change
status: accepted
contract_version: adr/1
---

# Let an impact analysis say the base was empty, rather than forbid the first change

## Context

`impact-analysis/1` required `implicated` to hold at least one entry whenever the verdict was `update`
or `create`. The reason was good and is unchanged: a verdict asserting that permanent knowledge must
change, while naming nothing that changes, is a verdict with nothing behind it.

It had one false positive, and it was not a small one. `foundation/0001` R1 puts every change to a
governed repository through a change request, and R3 runs impact analysis for every one of them. The
*first* change to a repository is therefore an impact analysis over a base holding nothing — and it
implicates nothing, because nothing exists to implicate. The contract rejected the only shape that case
can take.

The consequence was that a repository could not be brought under Siegard through Siegard's own workflow.
Ingesting a domain analysis into an empty knowledge base was blocked at phase two, and the block was
invisible: both workflow fixtures run against a populated base, so nothing exercised the case and
nothing reported it. It surfaced only when the ingestion path was designed.

What `/1` could not distinguish is the whole of it: a verdict that named nothing **because nothing
existed** and a verdict that named nothing **because the producer did not look** have the same shape,
and only the second is a defect.

## Decision

`impact-analysis/2` adds a required `base_state`, from the closed set `empty | populated`, and
conditions the existing rule on it.

- Over a `populated` base, `update` and `create` still require a non-empty `implicated`. The check that
  earned its place keeps it.
- Over an `empty` base, any verdict may implicate nothing.
- Over an `empty` base, the verdict may not be `update`. Nothing that does not exist can be updated, and
  admitting that pair would trade one unrepresentable case for one incoherent one.

`base_state` covers the knowledge base and the concept bundle together, because `implicated` may name
either. The name says "base" and the scope is both layers; the field's description carries that, and
naming it `prior_state` was considered and dropped as a rename that buys precision the description
already supplies.

It is recorded rather than derived. The analysis is what observed the repository, and a consumer reading
the artifact afterwards cannot re-observe the state it was classified against.

The orchestrator reads `/2` and **not** `/1`. Accepting both would leave two live readings of one
decision, and because the two versions map to identical outcomes nothing would ever force a `/1`
document forward — the migration would be decorative. A `/1` document is migrated and then consumed.

## Consequences

**It is a breaking change**, under the test in `.claude/rules/compatibility.md`: an instance that was
invalid becomes valid, and a `/1` document is now missing a field the contract requires. Every
obligation that rule states is met except one, and the exception is named rather than glossed.

- the break is stated here;
- the migration path is executable, registered in `scripts/migrate_contracts.py` for the hop;
- the contract is versioned rather than mutated, with `impact-analysis/1` kept in the lock carrying
  `superseded_by`;
- a test asserts the case `/1` rejected and `/2` admits, and a test asserts the migration's inference;
- **release documentation is not updated, because none exists.** The concept
  `docs/concepts/release-record.md` describes one and no such document is in this repository. The
  obligation is unmet and recorded as unmet.

The migration infers `base_state: populated` for every `/1` document, and the inference is total rather
than a default. `update` and `create` were only valid with a non-empty `implicated`, so something
existed. `none` asserts that what the request asks for is already held, which a base holding nothing
cannot assert. The three verdicts are exhaustive, so the migration never has to refuse and never has to
guess — an earlier reading of this hop expected `none` to be ambiguous, and it is not, because the
verdict's own meaning settles it.

### What was rejected

**Running the first ingest outside the workflow**, as a declared bootstrap. It is the cheapest option
and it puts the first knowledge a repository holds beyond every mechanism the framework exists for: no
change request, no recorded impact, no acceptance. R1 admits no bootstrap exemption, and writing one
into a specification to avoid a contract bump would be paying in authority to save a migration.

**Seeding the bounded-context boundaries by hand** so that the first ingest becomes an `update` over
them. The contract stays untouched and the seeding is unrecorded knowledge authoring — the rejected
option above, wearing a smaller hat.

**Relaxing the rule for every verdict.** Dropping `minItems` outright would have been a smaller diff and
would have discarded a check that catches a real defect on every subsequent change. The narrow
relaxation is the point: the check now fires exactly where it can be true.

### What would falsify this

A second case where a verdict legitimately implicates nothing over a populated base. If one appears,
`base_state` is the wrong axis — the distinction would be about the request rather than about the
repository, and the field would be recording the wrong observation.
