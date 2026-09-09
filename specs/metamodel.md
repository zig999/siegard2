---
id: "SPEC-003"
title: Metamodel — the five normative classes
status: proposed
contract_version: spec/1
---

# Metamodel — the five normative classes

## Scope

This specification fixes the ontology of a Siegard specification: which normative classes
exist, their closed subtypes, how nodes anchor to one another, how identity works independent
of storage, where each class is stored, and which projections are derived. It is the authority
the class schemas and the validator implement.

It decides the class set (exactly five), the admission tests that keep the set closed, the
subtype vocabularies, the anchor rules, and the storage mapping.

### Decided elsewhere, deliberately not restated here

- The floor, the ceiling, and the decision log — `specs/minimal-documentation.md` (SPEC-001).
- The Domain Model element fields, naming derivations, and diagram projection rules —
  `specs/domain-model-files.md` (SPEC-002), which this specification positions as the storage
  chapter of the Domain Model class.

## Admission tests

The class set and every subtype vocabulary stay closed under two tests:

- **Class test** — a normative class exists only if it has its own verification mode: a way of
  being wrong that no other class checks. A candidate that verifies like an existing class is a
  subtype or a reference, never a class.
- **Subtype test** — a subtype exists only if it changes validation or reference rules. A
  subtype that changes neither is a tag, and tags do not exist.

## The five classes

| class | answers | verified by |
|---|---|---|
| Domain Model | what exists and how it is structured | reference resolution, reachability, consistency boundaries |
| Rule | what must always hold (universal) | falsifiable condition → conformance test |
| Scenario | what happens in one concrete case (example) | executable as an acceptance test |
| Contract | what is promised across a boundary | direction and the upstream chain, resolved by the validator; a change over time surfaces as drift on every file the trace binds to the node |
| Architecture Constraint | what limits the solution space | fitness function over the implementation |

Every node of every class is complete: no provenance meta-fields, no open markers (SPEC-001
R8); a fact the material does not state is decided and disclosed in the decision log (SPEC-001
R9–R10).

### Domain Model

- **Subtypes** — `aggregate-root`, `entity`, `value-object`, `domain-service`, `enumeration`,
  as SPEC-002 R5–R13 fixes them; each changes required fields or reference rules (the R6
  table), so each passes the subtype test.
- **Context descriptor** — every context directory carries `_context.md`: the context's
  description, responsibility, and `strategic` (`core` | `supporting` | `generic`). The
  underscore keeps it outside the element slug space. It declares no relationships: the context
  map is a projection (below).

### Rule

- **Subtypes** — three, each changing validation:
  - `invariant` — `constrains` must resolve inside one aggregate; holds immediately.
  - `policy` — `constrains` may cross aggregates or contexts and `consistency`
    (`immediate` | `eventual`) is then required; immediate across an aggregate boundary is a
    validation error — that demand is a boundary redrawn, not a rule.
  - `state-machine` — anchored to one `aggregate-root` and its status `enumeration`; carries
    `initial`, `terminal`, `transitions`, `rejections`; the validator checks totality over the
    set: every pairing of a non-terminal state with a mentioned trigger is a transition or a
    rejection, and an undecided pairing is a decision to make and log, never silence.
- **Structure** — `statement` (one falsifiable condition) is required; `expression` optional.
  A rule carries no examples: a concrete case is a Scenario anchored to the rule.
- **One condition is one sentence.** The sentence count is the half of "one falsifiable
  condition" the validator decides; whether one sentence carries one condition is judgment, read
  off `--shape` naming the far end of the class. A second sentence is refused, with no escape
  hatch: it is a definition (SPEC-001 R3, the element's), an example (a Scenario's), or a second
  condition (a second Rule's), and each already has a home. The check is a speed bump, not a
  wall — a semicolon evades it — and its worth is that the rule is named at the moment of
  writing rather than in a report after.
- **`statement` governs.** Where both are declared, `expression` restates the condition
  `statement` fixes in a form a consumer evaluates directly, and adds no obligation of its
  own. An obligation that reaches the specification through `expression` alone is one no
  reading of `statement` can hold the specification to, and two normative fields with no
  precedence make which one binds a matter of which the reader opened. An `expression` whose
  claims exceed its `statement` is a `statement` owed the claim, or a second rule.

### Scenario

- **No subtypes** — the subject's class already distinguishes an invariant example from an
  end-to-end acceptance case, so a subtype would be a tag.
- **Structure** — `subject` (exactly one anchor: a Domain Model element, a Rule, or a
  Contract) and `given` / `when` / `then` are required; `involves` optionally lists the other
  identities the scenario touches — the references the capability map derives from.

### Contract

- **Subtypes** — `domain-event` (named in the past tense; `payload` required), `command`
  (`payload` required; may be refused, `refusal` optionally naming the value-object it
  surfaces), `api` (`operations` required), `capability` (the system's promise to its users;
  lives only in the reserved `system` namespace).
- **Direction** — `direction: published | consumed` is required on `domain-event`, `command`
  and `api`; `consumed` requires `upstream` naming the published contract it depends on. A
  `capability` is always published.
- **Payloads** reference Domain Model elements. A third-party system is an upstream contract
  named by the capability it supplies; the vendor is implementation.

### Architecture Constraint

- **No subtypes.** `statement` is required and is one sentence, as a Rule's is; `scope` is
  `system` or a context slug; `fitness` optionally states the mechanical check that verifies it. Integration strategies
  (anti-corruption layer, messaging, storage choices) live here — they constrain the solution,
  never the domain.
- **`fitness` states the condition, never a command or a step.** Which step decides a
  constraint is declared by a project's own registry — `commands[].decides` in
  `schemas/standard.json`, resolved by `bin/deliver.py --standard <file> --specification
  <root>` — so the check runs with that project's suite and is owed by every delivery, the
  node carries no artifact the project chose, and a registry can be reported against the
  constraints it leaves undecided. A step decided by nothing is a constraint held by reading
  alone, and the report says which.

## Identity and references

- **R1** — Identity is the node's path from the specification root, without `.md` —
  `domain/troubleshooting/case`, `rules/troubleshooting/case-transitions`. Identity is defined
  by the metamodel, not by storage: if a future revision inlines a class into its parent's
  file, identity becomes the parent's path plus a local slug, and every reference survives.
- **R2** — A reference is a bare slug inside the same directory and the full identity
  everywhere else. Every reference must resolve; renaming a node updates every inbound
  reference in the same change. A slug is unique inside a directory and not across the
  specification, so a slug two nodes answer to is written as the full identity wherever it is
  written — in a declared field and in prose alike. Prose is where this bites: a field's
  reference is resolved and checked, while a bare name in a body is resolved by whoever reads
  it, and one that two nodes answer to resolves differently for two readers. What a reader
  cannot resolve, a report names rather than guesses.
- **R3** — `system` is a reserved namespace: no bounded context may take that slug.

## Storage mapping

```text
<spec-root>/
├── domain/<context-slug>/_context.md, <element-slug>.md     (SPEC-002)
├── rules/<context-slug>/<rule-slug>.md
├── scenarios/<context-slug>/<scenario-slug>.md
├── scenarios/system/<scenario-slug>.md          (a capability's scenario, owned by no context)
├── contracts/system/<capability-slug>.md
├── contracts/<context-slug>/<contract-slug>.md
├── constraints/<constraint-slug>.md
└── decision-log.md
```

- **R4** — A node gets its own file when something outside its parent references it or when it
  changes independently of its parent; today that is every node of every class, flat per
  context, kebab-case slugs, no type in filenames (SPEC-002 R1–R3 generalized). Moving a class
  to inline storage is a change to this specification, never a per-model choice.
- **R5** — The decision log sits at the specification root (SPEC-001 R9). It is mandatory and
  non-normative: it constrains nothing; it discloses.

## Projections

- **R6** — A projection is generated from the collection, is never hand-edited, and carries
  nothing normative that the files do not state. The initial closed set:
  - **class diagram** — per context, from Domain Model (SPEC-002 R15);
  - **context map** — from Contracts and from cross-context references: directions and parties
    derive who owes compatibility to whom; a consumed contract whose payload is the upstream's
    own element adopts that model and one whose payload is its own translates it, read from the
    payload and declared nowhere else; an element naming another context's element by identity
    shares that model, drawn apart from consumption; a context pair with neither has gone
    separate ways, and that is the map saying so. How a translation is built — an
    anti-corruption layer, a mapping — stays an Architecture Constraint;
  - **state diagram** — per state-machine rule;
  - **capability map** — capability → contexts, derived from the references of the scenarios
    anchored to each capability;
  - **system overview** — contexts, strategic classification, each aggregate with what it
    holds (counted, never held to a threshold), capabilities, constraints.

## What is not normative

- **System** — the collection itself; its view is the overview projection.
- **Bounded Context** — a namespace (`<context-slug>/`), not a node; its metadata lives in
  `_context.md`, its relationships in the context-map projection.
- **Technical artifacts** — DTOs, repositories, controllers, ORM mappings, tables, topics,
  adapters: they emerge from implementation or derive from constraints, and no class admits
  them.
- **Provenance machinery** — intake mapping, `sources`, `rationale`, proposals and
  ratification rounds: replaced by the decision log (SPEC-001).

Where the previous vocabulary went: aggregate/entity/value-object/enumeration/domain-service →
Domain Model subtypes; invariant/policy → Rule subtypes; lifecycle → the `state-machine` Rule;
domain-event/command/api → Contract subtypes; use-case/capability/saga → `capability` Contract
with its Scenarios; context relationships and strategic view → projections; anti-corruption
layer → Architecture Constraint.

## Validation required before acceptance

1. One schema per class encodes the subtypes, anchors and vocabularies above, and a validator
   resolves every reference and identity rule (R1–R3), rejects a provenance meta-field, and
   enforces state-machine totality — a fixture collection proves each rejection and one full
   valid specification.
2. Every projection in R6 generates deterministically from the fixture: two runs produce
   identical output, and removing any contributing fact changes it.
3. SPEC-001 and SPEC-002 stay consistent with this specification; where they disagree, this
   one wins and the change updates both.
4. A rule declaring both `statement` and `expression` states the precedence in one place: the
   schema's own `expression` description says `statement` governs, and a fixture proves an
   `expression` carrying an obligation no reading of its `statement` holds is a defect a reviewer
   sees rather than a reading a consumer has to choose between.
5. For R2: a bare slug two nodes answer to is reported ambiguous and resolved to neither — a
   fixture with a deliberate collision across two classes proves it, because resolving to
   whichever sorts first would be wrong in silence.
6. A `statement` carrying more than one sentence is refused, on a Rule and on an Architecture
   Constraint alike, in the whole run and in `--node` — a fixture proves each — and the sound
   fixture carries none.
