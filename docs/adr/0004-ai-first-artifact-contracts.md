---
id: "0004"
title: Make inter-agent artifacts machine-consumable, and rank decision criteria accordingly
status: accepted
contract_version: adr/2
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

Two decisions, and the operative authority for each lives outside this record.

`.claude/rules/contracts.md` governs any artifact crossing an agent or phase boundary: what such an
artifact must carry, when a versioned schema is required and when prose is the correct form, and a worked
example of each. This ADR deliberately does not reproduce that content — two copies of a table diverge,
and the rule is the copy that loads while someone is authoring an artifact.

`CLAUDE.md` **Decision order** governs how competing designs are ranked. This ADR fixed its original
four-criterion form. **ADR-0008 amends that form**, admitting a second tier of tiebreakers beneath the
constraints, and `CLAUDE.md` carries the amended version rather than the one this ADR first recorded. The
amendment reverses one sentence of **Consequences** below, which is the sentence that dropped
maintainability and context cost; every other decision here stands.

What this record holds that has no other home is why human convenience was excluded from the ranking at
all, and what that exclusion costs.

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
  traceability, so listing them as tiebreakers overstated their force. **ADR-0008 reverses this
  sentence**: it restores both criteria as a second tier that cannot override anything, because no option
  reaches that tier until every constraint is already satisfied.

## Why this one is accepted

This decision presupposes no unbuilt component. It governs how any artifact is authored, starting with
the next one, and it is falsifiable immediately: an inter-agent artifact either carries a versioned
schema at a control-flow boundary or it does not.
