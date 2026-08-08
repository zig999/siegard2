---
id: "SPEC-001"
title: Minimal documentation
status: proposed
contract_version: spec/1
---

# Minimal documentation

## Scope

This specification fixes what the analyse step must always produce: the smallest artifact set
sufficient for a reader to comprehend the system the material describes, with every artifact
complete — no open markers, no provenance meta-fields — and every decision the analysis made on
the material's behalf disclosed in one place a human can review afterward.

It decides the floor (what every analysis owes), the ceiling (what no analysis may add), the
decide-and-disclose discipline that replaces in-artifact gaps, and which halves the validator
enforces mechanically.

### Decided elsewhere, deliberately not restated here

- The shape of each normative class and its vocabularies — the metamodel and its schemas.
- The Domain Model file convention — `specs/domain-model-files.md` (SPEC-002).
- How the analysis reads material and evolves a standing model — the analyse skill.

## Definitions

- **Comprehension set** — the answers a reader must be able to extract from the specification
  without opening the source material: which contexts exist and how they relate; what each
  recurring term of the material means; what changes together; what must always hold; what
  crosses boundaries; and how tracked things change state.
- **Floor** — the artifacts every analysis owes because some comprehension question has no other
  home.
- **Ceiling** — the rule that an artifact answering no comprehension question does not exist.
- **Decision log** — the single, append-only record of every fact the analysis decided rather
  than read from the material.

## Requirements

### Floor — what every analysis produces

- **R1** — Every analysis produces at least one context, complete: strategic classification and
  every structural fact its elements require. Nothing is left as an open question inside an
  artifact.
- **R2** — Every context holds at least one definition: a linguistic boundary with no language
  is not comprehensible.
- **R3** — Every recurring term of the material surfaces in the specification exactly once: as
  an element's name or as an alias on the element it means.
- **R4** — What the material does not state, the analysis decides. The artifact carries the
  decided value like any other — no placeholder, no `unknown`, no gap marker — and the decision
  is appended to the decision log. An artifact field left undecided is a floor violation.

### Ceiling — what no analysis adds

- **R5** — Conditional classes exist only where the material states the behavior they record. A
  class the material never speaks to is absent, and its absence needs no marker.
- **R6** — Every element earns its place by being reachable from a comprehension question; an
  element nothing reaches is bloat and fails validation.
- **R7** — No artifact restates another's statement. Prose explains; every operative claim lives
  in exactly one addressable home.
- **R8** — Artifacts carry no provenance meta-fields: no `gaps`, no `sources`, no `rationale`,
  no `proposal`. What the material stated and what the analysis decided read identically in the
  specification; the decision log is where the two are told apart.

### The decision log

- **R9** — One decision log per specification root, append-only. Each entry records: the
  location it filled (file and field, resolvable), what the material left unstated, the value
  decided, and why that value. An entry whose location does not resolve fails validation.
- **R10** — The log is disclosure, never a gate: the analysis decides and proceeds, and no
  entry blocks delivery. A human reviews the log after the fact; disagreement is an ordinary
  change to the artifact, not a ratification protocol.
- **R11** — The validator enforces the mechanically decidable half: R1's required fields, R2,
  R6's reachability, R8's absent fields, and R9's resolvable locations. R3, R5 and R7 are the
  analysis's judgment; the report is where a reviewer checks them.

## Validation required before acceptance

1. The validator rejects a specification with a context holding no definition, an unreachable
   element, any provenance meta-field, or a decision-log entry whose location does not resolve
   — a fixture proves each.
2. The analyse skill states the floor, the ceiling, and the decide-and-disclose discipline, and
   its output on a benchmark material yields artifacts with zero open markers and a log whose
   entries all resolve.
