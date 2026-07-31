---
id: "0014"
title: Decide acceptance from the observed diff, and escalate only on a validated field
status: accepted
contract_version: spec/1
---

# Acceptance closure and escalation

## Scope

This specification holds the five requirements moved out of
`foundation/0001-knowledge-object-driven-development.md`, which was accepted without the evidence they name.
It decides three things:

1. how the set of checks that decides acceptance is computed, and why it is not computed from what the
   implementer read;
2. what the acceptance gate must report about each impacted knowledge object, and what it may not present
   as a guarantee;
3. that [escalation](../docs/concepts/escalation.md) is decided by a predicate over a validated field.

It decides nothing about the workflow's phases, its transitions, its persisted state, or the fact that
acceptance requires a maintainer's decision. Those stayed in `foundation/0001`, which is accepted and remains
the authority for all of them.


### Why these requirements are here

`foundation/0001` set five acceptance conditions. The first end-to-end run met two: a
maintainer's acceptance, and the knowledge-only path running end to end in a fixture with every transition
chosen by lookup on a validated artifact. Three were not met — an escalation predicate decided by a script
with both outcomes tested, a test showing the validation closure exceeding the context closure, and an
acceptance gate reporting each knowledge object's mode.

Rather than accept a specification whose validation had not happened, the requirements those three
conditions covered were moved here and the conditions moved with them. `foundation/0001` now binds only what
was exercised; this document holds what was not. It is accepted with those conditions still open, so
the requirements moved here now bind on a maintainer's authority rather than on the evidence they were
moved out to wait for.

The requirement numbers in `foundation/0001` were retained as forwarding entries rather than renumbered.
`scripts/validate_specs.py` requires requirement ids to be sequential from R1 and records the reason:
renumbering silently redirects an existing citation to a different statement. Five numbers now point here
instead of being reused.

### Decided elsewhere, deliberately not restated here

- the workflow's phases and their order, the transition rules, rejection at a boundary, and that workflow
  state is persisted outside the conversation — `foundation/0001` R1 through R8;
- that a numeric threshold in an escalation predicate is calibrated from executed workflows and recorded
  with its evidence — `foundation/0001` R10, which stayed there because it constrains how any threshold enters
  and has already been honored in practice;
- that acceptance requires a maintainer's decision or a deterministic approval mechanism, and that
  validation produces reproducible evidence — `foundation/0001` R21 and R22, both exercised by
  `fixtures/knowledge-change-loop/`;
- what a context package is and how resolution degrades — `foundation/0001` R11 through R15, and `foundation/0009`.

## Definitions

This specification uses these terms as the concept bundle defines them:
[escalation](../docs/concepts/escalation.md),
[fail-soft](../docs/concepts/fail-soft.md),
[assertion](../docs/concepts/assertion.md),
[impact analysis](../docs/concepts/impact-analysis.md),
[knowledge object](../docs/concepts/knowledge-object.md),
[knowledge graph](../docs/concepts/knowledge-graph.md),
[context package](../docs/concepts/context-package.md),
[change request](../docs/concepts/change-request.md),
[transition guard](../docs/concepts/transition-guard.md),
[provenance](../docs/concepts/provenance.md).

## Requirements

### Escalation

- **R1** — Escalation is decided by predicates over fields of validated artifacts. No predicate reads
  prose, and no agent decides whether to escalate. Formerly `foundation/0001` R9.

### The acceptance closure

- **R2** — The set of checks that decides acceptance is computed from the impact artifact, the
  [knowledge graph](../docs/concepts/knowledge-graph.md), and the actual diff. It is never computed from
  the [context package](../docs/concepts/context-package.md) the implementer consumed. Formerly
  `foundation/0001` R17.
- **R3** — The validation closure covers every [knowledge object](../docs/concepts/knowledge-object.md) the
  diff touches, whether or not the impact artifact named it. Declared impact and observed diff are unioned,
  so independence does not leak when an implementation touches a path outside its plan. Formerly
  `foundation/0001` R18.

### What the gate reports

- **R4** — The acceptance gate reports, for each impacted knowledge object, the mode that decided it:
  `mechanical` where an [assertion](../docs/concepts/assertion.md) exists, `review` where none does. Every
  gap is named. Formerly `foundation/0001` R19.
- **R5** — [Fail-soft](../docs/concepts/fail-soft.md) guarantees independence of evaluation, not
  correctness of implementation. Where no assertion covers an impacted knowledge object, acceptance rests
  on independent review. A report that presents review as a guarantee is a false report. Formerly
  `foundation/0001` R20.

## Outstanding evidence

What this document states and nothing has yet exercised. A condition kept here is a debt;
removing one because the document binds would turn an open debt into a silent one.

These are the three conditions `foundation/0001` set and did not meet, carried here with the requirements they
cover:

1. one escalation predicate is decided by a script or hook against a validated artifact, with a test
   covering both outcomes (R1). Nothing holds this yet, because `foundation/0001` R10 forbids
   inventing a threshold before executed workflows exist to calibrate it;
2. a test shows the validation closure exceeding the context closure for a change where the two differ,
   which is what makes R2 and R3 falsifiable rather than aspirational. This needs context resolution, which
   is stage 3, and a code diff, which is stage 4;
3. the acceptance gate reports the mode of each impacted knowledge object, and a test asserts that a
   knowledge object with no assertion is reported as `review` rather than as passing (R4, R5). This needs
   assertions, which is stage 5.
4. a maintainer accepts this specification.

The three conditions span stages 3 through 5, so this document is the last of the method family to become
acceptable. If building the code side shows that the closure of R2 and R3 is indistinguishable from
validating everything the diff touches without consulting the impact artifact, simplify to the diff alone
before accepting rather than after.
