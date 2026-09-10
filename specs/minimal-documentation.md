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
- **R3** — Every recurring term of the material surfaces in the specification exactly once, as
  the name of the element it means. There is no alias mechanism: where the material uses two
  words for one thing, the analysis picks the one that best carries the term and the other
  surfaces nowhere. `display` corrects a slug's derived casing and never records a synonym.
  A recurring phrase that names no element is a term owed a name, not a phrase to repeat: a
  noun phrase restated across nodes is one definition kept in as many places as it appears.
- **R4** — What the material does not state, the analysis decides. The artifact carries the
  decided value like any other — no placeholder, no `unknown`, no gap marker — and the decision
  is appended to the decision log. An artifact field left undecided is a floor violation.

### Ceiling — what no analysis adds

- **R5** — Conditional classes exist only where the material states the behavior they record. A
  class the material never speaks to is absent, and its absence needs no marker.
- **R6** — Every element earns its place by being reachable from a comprehension question; an
  element nothing reaches is bloat and fails validation. Two element types are exempt because
  they answer a comprehension question by existing: an **aggregate root**, which is a consistency
  boundary and is the entry point other elements are reached *through* rather than *from*, and a
  **domain service**, which is a named behavior the material stated. Every other type — entity,
  value object, enumeration — is held to reachability. This exemption was `bin/spec.py`'s
  behaviour before it was stated here, carried in a code comment while this rule read as absolute;
  the statement is the specification catching up to the validator, not a change to what validates.
- **R7** — No artifact restates another's statement. Prose explains; every operative claim lives
  in exactly one addressable home.
- **R8** — Artifacts carry no provenance meta-fields: no `gaps`, no `sources`, no `rationale`,
  no `proposal`. What the material stated and what the analysis decided read identically in the
  specification; the decision log is where the two are told apart.
- **R14** — Prose explains what the node governs. It does not argue that the node is consistent
  with its neighbours. What a node does not govern is a boundary and belongs in its prose: an
  agent deciding which node governs a task reads that boundary and would otherwise decide from
  a resemblance. Why it does not contradict a sibling is an argument about the specification's
  own composition, and its home is the change that made it — never the artifact a downstream
  reader must open to conform, and not the log either (R9). A sentence carrying both keeps the
  boundary and drops the argument. This is judgment, not a mechanical check: the report is where
  a reviewer sees a specification whose prose has become its own defence.

### The decision log

- **R9** — One decision log per specification root, append-only. Each entry records: the
  location it filled (file and field, resolvable), what the material left unstated, the value
  decided, and why that value. An entry whose location does not resolve fails validation. `why`
  carries one claim a reviewer can reject, never the argument that the specification composes:
  that argument records no decided value, so it has no entry of its own and reaches the log only
  inside an entry about something else, restating the prose of the node that entry locates
  (R7, R14). Its home is the change that made it. A fact a planning step read from material
  outside the specification root — the intake a plan was cut from — and gave an addressable home
  is recorded in the same log as read: the location it filled, what no node stated, and where it
  was found. It decides no value and carries no `why`; a read entry and a decided one are told
  apart by shape, and the specification root holds the provenance of a node whose material it
  does not keep.
- **R10** — The log is disclosure, never a gate: the analysis decides and proceeds, and no
  entry blocks delivery. A human reviews the log after the fact; disagreement is an ordinary
  change to the artifact, not a ratification protocol.
- **R11** — The validator enforces the mechanically decidable half: R1's required fields, R2,
  R6's reachability, R8's absent fields, and R9's resolvable locations. R3, R5, R7 and R14 are
  the analysis's judgment; the report is where a reviewer checks them.

### Facts surfaced after authoring

- **R13** — An unstated fact surfaced after the specification is authored — a planning step
  finding that no node states a fact an objective or a criterion needs — is decided by the same
  discipline as R4 and disclosed in the same log (R9, R10), never left standing as a stop for a
  person whose only move is to trigger the decision. Two bounds hold the route: the deciding
  context has not seen the work that surfaced the fact — a decision made by whoever cut the
  tasks would bend the specification to fit them — and a fact the specification contradicts
  rather than omits is not decided at all: that is a conflict between the scope and the
  specification, and only a person settles it. A fact the specification's own nodes already
  state is read, not decided, and earns no log entry. A fact the supplied material states is read,
  not decided, and is recorded as read (R9): the analysis reads material to author every node,
  and an entry per node would restate the specification, but a node the specification gains
  after authoring has the log as its only index, and a work root is not kept.

### Language

- **R12** — Every specification is written in English (en-US), whatever language the material
  is in: every identifier, slug, statement, scenario line, payload name, and decision-log entry.
  Material in another language is translated to its ubiquitous-language term's closest English
  equivalent before that term names anything. The material's own word may still appear in a
  `## Description`, where it helps a reader map a name back to the source — that is prose, not
  an identity, and SPEC-002 R2 governs how a Domain Model slug in particular carries this.
  Analysis judgment decides the translation, the same as R3, R5 and R7; nothing here is
  mechanically checkable, so the report is where a reviewer checks it.

## Validation required before acceptance

1. The validator rejects a specification with a context holding no definition, an unreachable
   element, any provenance meta-field, or a decision-log entry whose location does not resolve
   — a fixture proves each.
2. The analyse skill states the floor, the ceiling, the decide-and-disclose discipline, and the
   English-language requirement, and its output on a benchmark material — including material
   written in another language — yields artifacts with zero open markers, every identifier and
   statement in English, and a log whose entries all resolve.
3. For R13: the planning route classifies an unstated fact apart from a contradiction, the
   deciding context receives the fact without the task that surfaced it, every decided fact
   lands as a decision-log entry whose location resolves, and a planted contradiction comes
   back as the standing stop rather than a decision — a benchmark case proves each. A fact read
   from the intake lands as an entry recorded as read, and the validator refuses one carrying
   `found` beside a decided value or a `why`, and one carrying neither shape — a fixture proves
   each.
4. For R14, and for the judgment halves R11 leaves to the report: `bin/spec.py --shape` reports
   what each class runs to, names every `statement` carrying more than one sentence, closes each
   node's prose transitively, and lists the names that prose holds and no node does — reporting
   whatever it finds, and refusing nothing on a size. A fixture proves each, and proves the
   report survives a specification that does not yet hold.
5. For R3: no schema admits an alias field, and the analyse skill states that a phrase recurring
   across nodes is a name owed rather than a phrase repeated.
6. For R3, R7 and R14, the readings that make judgment reviewable: `--shape` names the longest
   phrase each set of nodes shares in its normative fields, every normative field speaking about
   the specification rather than the domain, every node whose prose names more siblings than its
   fields declare, and how far each `why` of the decision log runs. Every one of those sections
   reports `(none)` over the sound fixture — a section that always finds something is a floor and
   not a finding, and a fixture test proves each. The sections that rank and cut show a node the
   reader answers for wherever it appears, past the cut, and change no total by being scoped:
   over a populated root the far end of a ranking belongs to what was written before, so a node
   written now would otherwise never reach the one reader obliged to fix it. Each class's own far
   end is named and not only counted, wherever the class holds enough nodes to have a
   distribution at all.
7. Every distributed artifact citing a requirement of this specification carries a sentence
   of it verbatim in «…» beside the citation, and `tests/test_spec_citations.py` proves each
   such quote is a substring of the requirement it names.
