---
id: "0008"
title: Rank cost and maintainability as tiebreakers below the constraint order
status: proposed
contract_version: adr/2
amends: "0004"
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

Three routes were open. A maintainer took the first: amend rather than supersede, leaving ADR-0004
accepted for its artifact-contract decision. The consequences of that choice are now in place —
`schemas/adr.v2.json` carries the `amends` field, `docs/adr/README.md` defines the relation and requires
the amended record to cite the amending one in its body, and ADR-0004 does.

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
- Cost: the ADR vocabulary carries an amendment relation that exists for this one case. A reader must now
  follow `amends` to know whether the record in front of them still says what it appears to say.

## Validation required before acceptance

The three conditions this ADR set are met, and the fourth is a maintainer's alone:

1. **met** — a maintainer resolved the conflict with ADR-0004 by the amendment route;
2. **met** — `CLAUDE.md` **Decision order** carries the two-group form, so it no longer states the
   four-criterion version this ADR revises;
3. **met** — the relation is in frontmatter as `amends: "0004"`, not only in prose, so `make validate`
   decides it rather than a reader inferring it;
4. **open** — the status change itself. This ADR binds nothing while `proposed`, and the amendment binds
   only while it is `accepted`, so `CLAUDE.md` currently carries the amended rule on its own authority
   while this record explains it as context. Only a maintainer closes that gap.
