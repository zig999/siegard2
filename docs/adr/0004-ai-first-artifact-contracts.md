---
id: "0004"
title: Make inter-agent artifacts machine-consumable, and rank decision criteria accordingly
status: accepted
contract_version: adr/1
---

# Make inter-agent artifacts machine-consumable, and rank decision criteria accordingly

## Context

When one agent hands work to another as prose, the consumer must interpret it. Interpretation is where
control flow becomes probabilistic: two runs read the same paragraph differently and take different
branches. The framework's central claim is that guarantees belong outside model judgment, and an
artifact boundary is where that claim is either kept or lost.

The opposite failure is also real. A blanket "schematize everything" rule makes schema authoring
dominate the work, and a rule too expensive to follow gets ignored. Once one rule in a normative
document is routinely ignored, the document's authority degrades as a whole.

## Decision

Artifacts crossing an agent or phase boundary must be consumable without human interpretation:
named producer and consumer, valid states and transitions and failure outcomes, stable identifier,
provenance for material decisions, and validation at the boundary before consumption.

The schema requirement is **tiered by criticality**, not universal: an artifact that carries control
flow or becomes persisted state requires a versioned schema validated at the boundary; an artifact that
only explains something to a human does not.

`.claude/rules/contracts.md` is the single operative authority for the tier definitions and carries a
worked example. This ADR deliberately does not restate the tiers — two copies of a table diverge, and
the rule is the copy that loads when someone is authoring an artifact.

This ADR also fixes the repository's decision order, in `CLAUDE.md`: correctness and safety, then
explicit testable contracts, then deterministic control flow and validation, then traceability.

## Consequences

- Control flow becomes a lookup against a closed value rather than a reading of prose.
- Schema authoring is real, recurring work — bounded to the boundaries that carry guarantees.
- **Human convenience is deliberately excluded from the decision order.** Earlier drafts ranked it
  last among eight criteria, which made it decorative: criteria that never bind are noise. Excluding it
  is the honest form of the same choice, and it has a cost — an artifact that is easy for a script to
  consume is often tedious for a maintainer to read or write. Where that cost falls on a human, add a
  prose companion for the reader; never let control flow depend on it.
- Two other criteria were also dropped as non-binding: maintainability and lower context cost. They are
  real concerns and belong in review, but they never override correctness, contracts, determinism, or
  traceability, so listing them as tiebreakers overstated their force.

## Why this one is accepted

Unlike ADR-0001 through ADR-0003, this decision presupposes no unbuilt component. It governs how any
artifact is authored, starting with the next one, and it is falsifiable immediately: an inter-agent
artifact either carries a versioned schema at a control-flow boundary or it does not.
