---
id: "0008"
title: Rank cost and maintainability as tiebreakers below the constraint order
status: proposed
contract_version: adr/1
---

# Rank cost and maintainability as tiebreakers below the constraint order

## Context

ADR-0004 fixes the decision order in `CLAUDE.md` at four criteria and explicitly drops two others. Its
Consequences section states: "Two other criteria were also dropped as non-binding: maintainability and
lower context cost. They are real concerns and belong in review, but they never override correctness,
contracts, determinism, or traceability, so listing them as tiebreakers overstated their force."

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

Two groups instead of one list.

A valid option must preserve, in order:

1. correctness and safety;
2. explicit, testable contracts and stated compatibility guarantees;
3. deterministic control flow, validation, and state;
4. traceability and reproducibility.

Among options that satisfy all four, prefer, in order:

1. the smallest sufficient design;
2. lower runtime and context cost;
3. easier testing, recovery, and maintenance.

A tier-two criterion never settles a question tier one has already settled, and never licenses giving up
a constraint. Recoverability and diagnosability do not belong to tier two: an artifact nobody can
recover or diagnose is a safety problem, and it is criterion 1.

## Conflict with ADR-0004

This reverses one sentence of an accepted ADR, and does so deliberately. It restores exactly the two
criteria ADR-0004 dropped, in exactly the form — tiebreakers — that its Consequences section rejects.

It does not touch ADR-0004's other decision, the criticality-tiered schema requirement. Superseding
ADR-0004 wholesale would therefore be wrong: it would drag an unrelated and working decision through a
restatement.

`CLAUDE.md`'s **Decision order** section is unchanged by the change that recorded this ADR. Under the
conflict protocol, an agent does not merge or choose between contradictory statements at equal
precedence. Resolution requires a maintainer choosing one of:

1. accept this ADR and amend ADR-0004's Consequences to cite it, leaving ADR-0004 accepted for its
   artifact-contract decision — the smallest resolution, and one the status vocabulary does not yet
   describe;
2. supersede ADR-0004 with an ADR restating both decisions, at the cost of duplicating the tier
   definitions;
3. reject this ADR, and record why the inconsistency with the 200-line cap is acceptable.

## Consequences

- Two equally correct designs become comparable. "Smallest sufficient" gains a stated basis instead of
  being implied by the existing prohibition on speculative generalization.
- A reviewer gains vocabulary for rejecting an over-built but correct design, which is currently
  unrejectable on any stated ground.
- Cost: the second tier is a tiebreaker, not a test. Two readers can disagree about which design is
  smallest without either violating a constraint, and the tier does not make that choice mechanical.
  It bounds the argument rather than settling it.
- If the maintainer takes route 1 above, the ADR vocabulary gains an amendment relation, and
  `schemas/adr.v1.json` gains the field that makes the relation validatable. Route 2 needs neither, and
  costs a duplicated decision instead.

## Validation required before acceptance

1. a maintainer resolves the conflict with ADR-0004 by one of the three routes above;
2. `CLAUDE.md`'s **Decision order** section is rewritten in the same change, since it currently states
   ADR-0004's four-criterion form and would otherwise contradict this decision;
3. the amendment or supersession relation is recorded in frontmatter, not only in prose, so
   `make validate` can decide it.
