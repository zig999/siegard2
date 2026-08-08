---
id: "SPEC-002"
title: Domain Model file convention
status: proposed
contract_version: spec/1
---

# Domain Model file convention

## Scope

This specification fixes how a Domain Model is recorded: one markdown file per element, flat
inside one directory per bounded context, and the naming, reference, and derivation rules that
make the collection the single normative source. A class diagram is optional and derived; this
specification guarantees it is derivable and forbids it from carrying anything normative.

It decides file naming, element identity, the field set per element type, the closed
vocabularies, the attribute-versus-relationship boundary, and the projection rules a diagram
generator follows.

### Decided elsewhere, deliberately not restated here

- The minimal-documentation floor and ceiling, and the decision log that replaces in-artifact
  gaps — `specs/minimal-documentation.md` (SPEC-001).
- Invariants, scenarios, contracts, and architecture constraints — sibling layers, each with its
  own specification; the Domain Model records structure only.
- State transitions: an enumeration lists the possible states, but which operation moves which
  state to which lives in the behavioral layers, never here.

## Layout and naming

```text
domain/
└── <context-slug>/
    ├── _context.md
    ├── case.md
    ├── case-id.md
    ├── case-status.md
    ├── investigation.md
    └── evidence.md
```

- **R1** — One element, one file, flat: `domain/<context-slug>/<element-slug>.md`. No
  subdirectories below the context. Beside the elements sits the context descriptor
  `_context.md` (SPEC-003) — the underscore keeps it outside the element slug space.
- **R2** — Slugs are kebab-case (`^[a-z0-9]+(-[a-z0-9]+)*$`) of the ubiquitous-language term.
  The filename is the identity; there is no `name` field. Display and code forms are derived,
  never stored: `case-status` → `CaseStatus` (PascalCase). The one exception is an acronym the
  derivation miscases: an optional `display` field may state the form (`display: ISBNCode`),
  and it must reduce back to the slug.
- **R3** — The element type never enters the filename. Reclassifying an element (entity →
  aggregate-root) changes one frontmatter line and breaks no reference.
- **R4** — A reference is the target's slug: bare (`investigation`) inside the same context,
  qualified (`<context-slug>/<element-slug>`) across contexts. Renaming a file is an identity
  change: every inbound reference updates in the same change, and validation fails otherwise.

## Element structure

Frontmatter carries everything structured; the body carries prose under exactly two headings,
`## Description` (what the concept represents in the domain — never how it is implemented) and
`## Responsibility` (why the concept exists; its one main responsibility). A heading with
nothing to say carries the literal line `None.`

- **R5** — `type` is one of the closed set: `aggregate-root`, `entity`, `value-object`,
  `domain-service`, `enumeration`.
- **R6** — Fields by type. Required (✓), optional (○), forbidden (—):

  | field           | aggregate-root | entity | value-object | domain-service | enumeration |
  |-----------------|:---:|:---:|:---:|:---:|:---:|
  | `attributes`    | ✓ | ✓ | ✓ | — | — |
  | `aggregate`     | — | ✓ | — | — | — |
  | `relationships` | ○ | ○ | ○ | — | — |
  | `operations`    | ○ | ○ | — | ✓ | — |
  | `values`        | — | — | — | — | ✓ |
  | `display`       | ○ | ○ | ○ | ○ | ○ |

  An aggregate is named by its root's slug — no separate aggregate file exists. An entity's
  `aggregate` names the root that owns it. A value object never declares `aggregate`: values
  are shareable and belong to no consistency boundary.
- **R7** — Elements carry no provenance meta-fields — no `gaps`, `sources`, `rationale`, or
  `proposal` (SPEC-001 R8). A fact the material does not state is decided by the analysis, the
  element carries the decided value like any other, and the decision is appended to the
  decision log (SPEC-001 R9) naming the file and field it filled. An attribute typed `unknown`
  is forbidden — an undetermined type is a decision to make and log, never a placeholder.

## Attributes and relationships — one home per fact

- **R8** — The boundary is the target's identity. A link to a primitive, a value object, or an
  enumeration is an **attribute**. A link to an entity or an aggregate root is a
  **relationship**. No fact appears as both.
- **R9** — Primitive types are the closed set `string`, `integer`, `decimal`, `boolean`,
  `date`, `datetime`. Every other attribute type must resolve to a `value-object` or
  `enumeration` element in the collection, by slug. An attribute whose value repeats declares
  `many: true`; absent means one value.
- **R10** — A relationship declares `target`, `type`, `cardinality`, and — when two
  relationships share a target pair or the edge needs a label — `role`. Types are the closed
  set `composition`, `reference`, `association`; cardinalities are the closed set `1`, `0..1`,
  `0..*`, `1..*` and state the target end. The source end is fixed by rule: `1` for
  `composition`, `0..*` otherwise, overridable with `source-cardinality`.
- **R11** — Every relationship is declared exactly once, on the owning or navigating side.
  `composition` never crosses an aggregate boundary, and its entity target must declare
  `aggregate` naming the composing side's aggregate; `reference` is how an element points at
  another aggregate's root, always by identity.
- **R12** — Operations are kebab-case verb slugs, names only; parameters, returns and refusals
  live in the behavioral layers. Enumeration `values` are kebab-case; code forms
  (`SCREAMING_SNAKE`, `camelCase`) are derived. Attribute names are snake_case.
- **R13** — Generalization is deliberately absent: no element specializes another, and variation
  is modeled by composition or by an enumeration. Revisiting this is a change to this
  specification, not a per-model choice.

## The diagram is derived

- **R14** — A class diagram is optional. When wanted, it is generated from the collection —
  Mermaid `classDiagram` as the reference target — and carries nothing the files do not state.
  A hand-edited diagram is not a Domain Model artifact.
- **R15** — Projection rules, so two generators draw the same picture: each element is a class
  with its stereotype (`<<AggregateRoot>>`, `<<Entity>>`, `<<ValueObject>>`, `<<Service>>`,
  `<<Enumeration>>`); attributes render inside the class box with their declared types;
  operations render by derived camelCase name with empty parentheses; relationships render as
  edges labeled with `role` where declared, both end cardinalities shown, composition with the
  filled diamond on the source; an aggregate's boundary is the root plus every entity whose
  `aggregate` names it, value objects always outside; enumerations render with their values.

## Validation required before acceptance

1. A schema (`schemas/domain-element.json` or successor) encodes R5–R13, and a validator
   resolves every reference and every non-primitive attribute type, rejecting a collection with
   a dangling slug, a duplicated fact (R8), or a composition crossing an aggregate (R11).
2. A fixture collection under `domain/` validates, and a generated Mermaid diagram from it
   round-trips: every normative fact in the diagram traces to a file, and removing any R15
   input changes the output.
3. The template `templates/domain-model-element.md` stays in step with R5–R12.
