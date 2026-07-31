---
id: "0008"
title: Rank cost and maintainability as tiebreakers below the constraint order
status: accepted
contract_version: adr/1
---

# Rank cost and maintainability as tiebreakers below the constraint order

## Context

ADR-0004 fixed the decision order at four criteria and explicitly dropped two others. Its Consequences
section stated: "Two other criteria were also dropped as non-binding: maintainability and lower context
cost. They are real concerns and belong in review, but they never override correctness, contracts,
determinism, or traceability, so listing them as tiebreakers overstated their force."

That argument answers a *ranking* proposal, where a fifth criterion sits below the fourth and could in
principle be traded against it. It does not answer a second tier that applies only among options which
already satisfy all four constraints. Such a tier cannot override anything: no option reaches it until
every constraint is met.

Meanwhile context cost already binds. `.claude/rules/claude-code-authoring.md` caps `CLAUDE.md` at 200
lines and instructs the author to move content out as it grows. That rule has no justification other
than context cost. A criterion that governs an existing rule while the decision order denies it is not
excluded — it is unrecorded, which is the condition this repository treats as drift.

The practical gap: two designs that both satisfy correctness, contracts, determinism, and traceability
are currently indistinguishable, and the framework has no stated reason to prefer the smaller one.
Correct and needlessly expensive is a reachable outcome, and for a framework whose scarce resource is
the consumer's context window, an expensive outcome is a real defect.

## Decision

The ranking carries two groups instead of one list, and `CLAUDE.md` **Decision order** is the operative
authority for both groups and for how they interact. This ADR does not reproduce either group.

What this record holds is the reasoning that rule cannot carry.

A tier beneath the constraints cannot weaken them, because no option arrives there until every constraint
is already met. That is precisely what distinguishes this from the ranking proposal ADR-0004 rejected,
where a fifth criterion sat beside the fourth and could be traded against it. The rejection was correct
about ranking and silent about tiering, and this ADR fills that silence rather than reversing a judgment.

Recoverability and diagnosability were kept out of the second tier deliberately, and that was the
substantive risk in admitting a tier at all. Something nobody can recover or diagnose is unsafe, which
places it in the first group; filing it among tiebreakers would have made the most important property
here the most negotiable one.

## How the conflict with ADR-0004 was resolved

This reverses one sentence of an accepted ADR. Superseding ADR-0004 wholesale would have been wrong: it
would have dragged an unrelated and working decision — the criticality-tiered schema requirement —
through a restatement.

Three routes were open. A maintainer took the first: revise rather than supersede, leaving ADR-0004
accepted for its artifact-contract decision. That revision is recorded in prose on both sides — this
record names what it reverses, and ADR-0004 cites this id at the point of the change.

The two rejected routes are recorded because a reader should see what the choice cost. Superseding
ADR-0004 would have duplicated the contract tiers into a new record. Rejecting this ADR would have
required recording why the inconsistency with the 200-line cap is acceptable, and no such reason was
found.

## Consequences

- Two equally correct designs become comparable. "Smallest sufficient" gains a stated basis instead of
  being implied by the existing prohibition on speculative generalization.
- A reviewer gains vocabulary for rejecting an over-built but correct design, which was previously
  unrejectable on any stated ground.
- Cost: the second tier is a tiebreaker, not a test. Two readers can disagree about which design is
  smallest without either violating a constraint, and the tier does not make that choice mechanical.
  It bounds the argument rather than settling it.
- Cost: a reader of ADR-0004 must follow its prose citation of this record to know that one sentence of
  what they are reading has been reversed. Nothing validates that citation, so it can rot unnoticed.

## What satisfied acceptance

A maintainer accepted this ADR on 2026-07-30. All three conditions it set were met first:

1. a maintainer resolved the conflict with ADR-0004 by the amendment route rather than by supersession;
2. `CLAUDE.md` **Decision order** carries the two-group form, so it no longer states the four-criterion
   version this ADR revises;
3. the relation was in frontmatter as `amends: "0004"`, not only in prose, so `make validate` decided it
   rather than a reader inferring it — and ADR-0004 cites the amending id at the point of the change,
   which the validator also checked. That field was removed on 2026-07-31; the prose citation on both
   sides is what remains, and nothing checks it.

Acceptance changes one thing beyond this record's own status: the amendment now **binds**. ADR-0004 stays
`accepted` for its artifact-contract decision, and the sentence of its Consequences that dropped
maintainability and context cost is reversed in force rather than merely annotated. `CLAUDE.md` **Decision
order** was already carrying the amended rule; it now carries it with a binding record behind it instead of
on its own authority.

This ADR was also the only one ever to declare `amends`. The relation was removed on 2026-07-31 as
ceremony carried for a single case — which is the cost this record's own Consequences section had
already named.
