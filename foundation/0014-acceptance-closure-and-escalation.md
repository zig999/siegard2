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

**What that authority now says has changed under this document, and one requirement here changed with it.**
`foundation/0005` R23 fixed an architecture in which Siegard refuses rather than sequences, and
`foundation/0001` then demoted its phase order to guidance and retired the requirements that named an
orchestrator and a persisted workflow state. R1 below was rewritten in consequence — it had forbidden an
agent from deciding whether to escalate, which the executor now does. R2 through R5 are unchanged; three of
them have no mechanism, which is stated where they are read rather than only here. The architectural
decision is `docs/adr/0017-order-follows-from-declarations-not-from-a-sequencer.md`.


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

- the workflow's phases and their order, and rejection at a boundary — `foundation/0001` R1 through R8.
  Two of those are retired: R5 named an orchestrator choosing transitions and R8 required persisted
  workflow state, and `foundation/0005` R23 states the framework does neither. R6 — an artifact that fails
  its contract is rejected — is the one that carries the weight here, because it is what a boundary check
  in R1 above rests on;
- that a numeric threshold in an escalation predicate is calibrated from executed workflows and recorded
  with its evidence — `foundation/0001` R10, which stayed there because it constrains how any threshold enters
  and has already been honored in practice;
- that acceptance requires a maintainer's decision or a deterministic approval mechanism, and that
  validation produces reproducible evidence — `foundation/0001` R21 and R22. The fixture that exercised
  both was removed with the workflow machinery
  (`docs/adr/0016-remove-the-workflow-machinery.md`), so neither is exercised today;
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
[provenance](../docs/concepts/provenance.md).

`transition guard` left this list with the rewrite of R1, and the concept was then removed from the
bundle: no requirement in this framework names one, and the framework holds none.

## Requirements

### Escalation

- **R1** — Escalation is decided by predicates over fields of validated artifacts. No predicate reads
  prose, so whether a condition holds is checkable rather than a matter of a model's sense of how big a
  change feels. Where an escalation inserts a step that is itself a guarantee — a maintainer's review of an
  implicated decision record is the case that matters — that the step happened is verified at a boundary
  and is not left to the executor's discretion, per `foundation/0005` R5. Formerly `foundation/0001` R9.

  An earlier form added "and no agent decides whether to escalate". That is no longer sayable:
  `foundation/0005` R3 puts sequence with Claude Code, and forbidding the executor to decide what runs
  would contradict the architecture. What replaces it is narrower and keeps what the clause was protecting
  — the *condition* is not a judgment, and an inserted *guarantee* is not optional. An escalation whose
  only enforcement is that the executor felt like honoring it is the case `foundation/0007` R25 already
  refuses in its own domain.

### The acceptance closure

- **R2** — The set of checks that decides acceptance is computed from the impact artifact, the
  [knowledge graph](../docs/concepts/knowledge-graph.md), and the actual diff. It is never computed from
  the [context package](../docs/concepts/context-package.md) the implementer consumed. Formerly
  `foundation/0001` R17.
- **R3** — The validation closure covers every [knowledge object](../docs/concepts/knowledge-object.md) the
  diff touches, whether or not the impact artifact named it. Declared impact and observed diff are unioned,
  so independence does not leak when an implementation touches a path outside its plan. Formerly
  `foundation/0001` R18.

**Nothing computes the closure of R2 and R3, and nothing reports the mode R4 requires.** The acceptance
gate they describe was never built, and the workflow phase that would have run it was removed
(`docs/adr/0016-remove-the-workflow-machinery.md`). All three are kept rather than retired for the reason
`foundation/0001` gives about its own R7: they state what the method requires of whoever does the work, and
a maintainer can honor them. What they are not, today, is a guarantee — and R5 below is the requirement
that forbids reporting them as one.

### What the gate reports

- **R4** — The acceptance gate reports, for each impacted knowledge object, the mode that decided it:
  `mechanical` where an [assertion](../docs/concepts/assertion.md) exists, `review` where none does. Every
  gap is named. Formerly `foundation/0001` R19.
- **R5** — [Fail-soft](../docs/concepts/fail-soft.md) guarantees independence of evaluation, not
  correctness of implementation. Where no assertion covers an impacted knowledge object, acceptance rests
  on independent review. A report that presents review as a guarantee is a false report. Formerly
  `foundation/0001` R20.

  **This one is unaffected and binds now.** It constrains whoever writes a report rather than a component
  that runs, so removing the machinery took nothing from it. It is also what makes the paragraph above
  safe to write: a document that records three unimplemented requirements and calls them guarantees would
  be the false report this requirement names.

## Outstanding evidence

What this document states and nothing has yet exercised. A condition kept here is a debt;
removing one because the document binds would turn an open debt into a silent one.

These are the three conditions `foundation/0001` set and did not meet, carried here with the requirements they
cover:

1. one escalation predicate is decided by a script or hook against a validated artifact, with a test
   covering both outcomes (R1). Nothing holds this yet, because `foundation/0001` R10 forbids
   inventing a threshold before executed workflows exist to calibrate it;
2. a test shows the validation closure exceeding the context closure for a change where the two differ,
   which is what makes R2 and R3 falsifiable rather than aspirational. Context resolution exists; what this
   still needs is a code diff to compute a closure over;
3. the acceptance gate reports the mode of each impacted knowledge object, and a test asserts that a
   knowledge object with no assertion is reported as `review` rather than as passing (R4, R5). This needs
   assertions, and none exists;
4. a maintainer accepts this specification. Met on 2026-07-31.

Each condition names what it waits on rather than a stage number. An earlier version pointed at "stage 3
through 5" of a build sequence that lived in a file this repository no longer holds, which left three
conditions depending on an ordering nobody could read. If building the code side shows that the closure of
R2 and R3 is indistinguishable from validating everything the diff touches without consulting the impact
artifact, simplify to the diff alone.
