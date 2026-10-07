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

- **R9** — One decision log beside every node that received a decision: `<slug>.log.md` in
  the node's own directory, append-only, moving with its node. Each entry records: the field it
  filled (resolvable in the node beside it), what the material left unstated, the value
  decided, and why that value. An entry is never edited or removed. Where a node leaves the
  specification, the change that removes it appends an entry to its log retiring the field:
  where the fact is held now, or that it is held nowhere; where a field leaves a node that
  stays, the same. A log whose node does not exist fails validation unless its last entry
  retires a field, and an entry whose field does not resolve fails validation unless a later
  entry retires that field. The latest entry over a field is the disclosure that stands. A log
  is frontmatter alone: text after its fence is not an entry and fails validation. `why`
  carries one claim a reviewer can reject, never the argument that the specification composes:
  that argument records no decided value, so it has no entry of its own and reaches the log only
  inside an entry about something else, restating the prose of the node that entry locates
  (R7, R14). Its home is the change that made it. A fact a planning step read from material
  outside the specification root — the intake a plan was cut from — and gave an addressable home
  is recorded in that node's log as read: the field it filled, what no node stated, and where it
  was found. It decides no value and carries no `why`; a read entry and a decided one are told
  apart by shape, and the specification root holds the provenance of a node whose material it
  does not keep. A node the material does not name is disclosed by the entry over the field its
  class requires — `type` for an element, a rule or a contract, `strategic` for a context,
  `subject` for a scenario, `statement` for a constraint — whose `unstated` says the material
  names no such thing; a node beside no such entry is one the material described.
- **R10** — The log is disclosure, never a gate: the analysis decides and proceeds, and no
  entry blocks delivery. A human reviews the logs after the fact; disagreement is an ordinary
  change to the artifact, not a ratification protocol. Where no such review is made, a decision
  stands until behavior contradicts it and a corrective change revises the artifact — and the
  disclosed decisions later revised are reported by the telemetry — counted beside those that
  stand, each revised one named with the route that revised it and how long after — so the trade
  that removed the stop stays measured rather than assumed.
- **R11** — The validator enforces the mechanically decidable half: R1's required fields, R2,
  R6's reachability, R8's absent fields, and R9's log rules — a node beside every log or a
  retirement closing it, every field head declared by that node, no text after the fence. R3,
  R5, R7 and R14 are
  the analysis's judgment; the report is where a reviewer checks them.

### Facts surfaced after authoring

- **R13** — An unstated fact surfaced after the specification is authored — a planning step
  finding that no node states a fact an objective or a criterion needs — is decided by the same
  discipline as R4 and disclosed in the node's log (R9, R10), never left standing as a stop for a
  person whose only move is to trigger the decision. Two bounds hold the route: the deciding
  context has not seen the work that surfaced the fact — a decision made by whoever cut the
  tasks would bend the specification to fit them — and a fact the specification contradicts
  rather than omits is not decided at all: that is a conflict between the scope and the
  specification, and only a person settles it. A fact the specification's own nodes already
  state is read, not decided, and earns no log entry. A fact the supplied material states is read,
  not decided, and is recorded as read (R9): the analysis reads material to author every node,
  and an entry per node would restate the specification, but a node the specification gains
  after authoring has the log as its only index, and a work root is not kept.

### What the material must hold

- **R15** — Material that states no fact any of the five classes admits is an absent input, never a
  specification to decide: the analysis stops before any write, names what the material would have
  to state, and writes no node and no log entry. The stop is over the input and precedes every
  decision, so R4 and R10 are untouched — there is nothing yet to decide and nothing yet to disclose.
  It holds over an empty root, where the floor would otherwise be produced from nothing, and over a
  populated root, where material that names nodes and states no change about them is material that
  states nothing. It is never a question about the material's content: what the stop names is the
  input that was absent, and supplying it is a new invocation.

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
   element, any provenance meta-field, a decision log beside no node whose last entry retires
   nothing, a log entry whose field the node does not declare, or a log carrying text after its
   fence — a fixture proves each.
2. The analyse skill states the floor, the ceiling, the decide-and-disclose discipline, and the
   English-language requirement, and its output on a benchmark material — including material
   written in another language — yields artifacts with zero open markers, every identifier and
   statement in English, and logs whose fields all resolve. The benchmark is
   `tests/fixtures/benchmarks/analyse/`: its materials, written in Portuguese, and under
   `iteration-1/` each run's verbatim report, written root and grading, recorded once per
   iteration and never overwritten; `tests/test_benchmarks.py` holds every recorded root sound
   under the validator as it stands, free of open markers, and every expectation the grading
   marks mechanical recomputed from the root rather than trusted.
3. For R13: the planning route classifies an unstated fact apart from a contradiction, the
   deciding context receives the fact without the task that surfaced it, every decided fact
   lands as an entry in the node's own log whose field resolves, and a planted contradiction comes
   back as the standing stop rather than a decision — a benchmark case proves each. The cases are
   `tests/fixtures/benchmarks/unstated-route/`: the corpus, nine case roots each with its fact
   and the inputs the decider is handed, and under `iteration-1/` each case's verbatim return and
   score; `tests/test_benchmarks.py` holds every case root sound and every scored case at the
   outcome the corpus expects. A fact read from the intake lands as an entry recorded as read,
   and the validator refuses one carrying `found` beside a decided value or a `why`, and one
   carrying neither shape — a fixture proves each.
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
   fields declare, how far each `why` across the decision logs runs, and which fields a log
   decided more than once. Every one of those sections
   reports `(none)` over the sound fixture — a section that always finds something is a floor and
   not a finding, and a fixture test proves each. The sections that rank and cut show a node the
   reader answers for wherever it appears, past the cut, and change no total by being scoped:
   over a populated root the far end of a ranking belongs to what was written before, so a node
   written now would otherwise never reach the one reader obliged to fix it. Each class's own far
   end is named and not only counted, wherever the class holds enough nodes to have a
   distribution at all. Beside those sections, as a reading rather than a finding, `--shape`
   counts how many of each node's declared fields its log decided, ranked with the far end named
   and the scoped node shown past the cut — the one line that tells a reviewer which node the
   material barely described (R4, R8). It reports a count over the sound fixture, because the
   fixture's own disclosed decisions are what it counts, and a fixture test proves the count, that
   a read entry and a retirement are not counted, and that a scoped node is marked.
7. Every distributed artifact citing a requirement of this specification carries a sentence
   of it verbatim in «…» beside the citation, and `tests/test_spec_citations.py` proves each
   such quote is a substring of the requirement it names.
8. For R15: the analyse skill states the stop among its required inputs, as a stop over an absent
   input and never as a question about the material's content, and `tests/test_skill_contract.py`
   holds the sentence. For the disclosure R9 adds over a node the material does not name: the
   analyse skill and the unstated-fact decider each state it beside the entry they write, and the
   same test holds the skill's sentence.
