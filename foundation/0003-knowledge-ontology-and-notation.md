---
id: "0003"
title: Store the domain analysis as a typed ontology, and derive the graph from it
status: accepted
contract_version: spec/1
---

# The knowledge ontology and notation

## Scope

How a governed repository stores the domain analysis: the six knowledge object types, where each DDD
construct lands, the edges that connect them, the attribute type system, identity, body form, and the
graph derived from the whole.

Not here: how a request becomes a domain model (`foundation/0002`).

## Where each DDD construct lands

| DDD construct | Recorded as | Home |
|---|---|---|
| Domain | nothing | the governed repository is the domain |
| Subdomain | field | `boundary.subdomain_type` ∈ `core \| supporting \| generic` |
| Bounded context | **type** | `boundary`, `ddd: bounded-context` |
| Context map | field | `boundary.context_relationships[]` |
| Context relationship pattern | field | `boundary.context_relationships[].pattern` |
| Ubiquitous language | emergent | the set of `definition` objects; synonyms in `definition.aliases[]` |
| Entity | field | `definition`, `ddd: entity` |
| Value object | field | `definition`, `ddd: value-object` |
| Aggregate | **type** | `boundary`, `ddd: aggregate` |
| Aggregate root | field | `definition`, `ddd: aggregate-root` |
| Read model | field | `definition`, `ddd: read-model` |
| Domain error | field | `definition`, `ddd: domain-error` |
| Invariant | field | `rule`, `ddd: invariant` |
| Business rule | field | `rule`, `ddd: domain-rule` |
| Policy | field | `rule`, `ddd: policy` |
| Specification pattern | field | `rule`, `ddd: specification` |
| Quality attribute | field | `rule`, `ddd: quality-attribute` |
| State machine | **type** | `lifecycle` |
| Domain event | field | `interface`, `ddd: domain-event` |
| Integration event | field | `interface`, `ddd: integration-event` |
| Published language | field | `interface`, `ddd: published-language` |
| Open host service, API | field | `interface`, `ddd: api` |
| Domain service | field | `process`, `ddd: domain-service` |
| Saga, process manager | field | `process`, `ddd: saga` |
| Use case | field | `process`, `ddd: use-case` |
| Repository, factory, module, layering | nothing | stack knowledge |
| Architectural decision | node, not a knowledge object | ADR |

## The edge table

| Edge | Origin → target | Out | In | Traversed | Depth |
|---|---|---|---|---|---|
| `boundary` | any → `boundary` | 1..1 | 0..n | yes | 1 |
| `depends_on` | any → any | 0..n | 0..n | yes | 2 |
| `governed_by` | any → ADR | 0..n | 0..n | yes | 1 |
| `attributes[].target` | `definition` → `definition` | 0..n | 0..n | yes | 1 |
| `attributes[].of` | `definition` → `definition` | 0..n | 0..n | yes | 1 |
| `attributes[].lifecycle` | `definition` → `lifecycle` | 0..n | 0..n | yes | 1 |
| `lifecycle.subject` | `lifecycle` → `definition` | 1..1 | 0..1 | yes | 1 |
| `transitions[].guard` | `lifecycle` → `rule` | 0..n | 0..n | yes | 1 |
| `rejections[].error` | `lifecycle` → `definition` | 0..n | 0..n | yes | 1 |
| `steps[].ko` | `process` → any | 0..n | 0..n | yes | 1 |
| `context_relationships[].with` | `boundary` → `boundary` | 0..n | 0..n | only when expansion crosses a context | 1 |

## The attribute primitives

| Primitive | Required parameters |
|---|---|
| `string` | `max_length` |
| `text` | — |
| `integer` | — (`min`, `max` optional) |
| `decimal` | `precision`, `scale` |
| `money` | — (inherits the system default) |
| `boolean` | — |
| `date` | — |
| `datetime` | — (inherits the system default) |
| `duration` | — |
| `enum` | `lifecycle` **or** `values[]` |
| `ref` | `target`, `binding` |
| `list` | `of`, `binding` (`min_items`, `max_items` optional) |

## Body sections, by type

| type | sections, in order |
|---|---|
| `definition` | `## Answer` · `## Invariants` |
| `rule` | `## Answer` · `## Conditions` |
| `lifecycle` | `## Answer` · `## State semantics` |
| `interface` | `## Answer` · `## Semantics` |
| `boundary` | `## Answer` · `## Responsibilities` |
| `process` | `## Answer` · `## Outcomes` |

## Requirements

### Node types

- **R1** — The `type` vocabulary is closed: `definition`, `rule`, `lifecycle`, `interface`, `boundary`,
  `process`.
- **R2** — Every construct the analysis produces MUST land in exactly one place named by the mapping
  above. A construct with no entry there MUST NOT be recorded until the mapping names its home.
- **R3** — A seventh type is admitted only when it requires a frontmatter field no existing type requires
  and enables a mechanical check no existing type enables. Both MUST be recorded with the case that
  demanded it.
- **R4** — An ADR is a permanent graph node and MUST NOT be a knowledge object. Rationale — the
  alternative rejected, the cost accepted, what would falsify the decision — MUST NOT appear in a
  knowledge object.
- **R5** — A knowledge object MUST answer exactly one question, declared in `question`.
- **R6** — A `definition` MUST declare `attributes`. One whose `ddd` is `entity`, `aggregate-root`, or
  `read-model` MUST declare `identity`; one whose `ddd` is `value-object` or `domain-error` MUST NOT.
- **R7** — A `rule` MUST declare `expression` or `examples`. A `rule` with `ddd: quality-attribute` MUST
  declare the bounded context it constrains, once per context.
- **R8** — A `lifecycle` MUST declare `subject`, `states`, `initial`, `transitions`, and `rejections`,
  and its transition table MUST be total: for every pairing of a state with a trigger, either a
  transition or a rejection exists. Every state MUST be reachable from `initial`, and every non-terminal
  state MUST have an outgoing transition.
- **R9** — An `interface` MUST declare `version`, `schema`, and `ownership` ∈ `published | consumed`.
- **R10** — A `boundary` with `ddd: bounded-context` MUST declare `subdomain_type`.
- **R11** — A `process` MUST declare `steps` as an ordered list naming knowledge-object ids, and MUST NOT
  restate the content of any step's object.
- **R12** — An edge or attribute reference whose origin and target lie in different bounded contexts MUST
  target an `interface`. A violation is reported, never repaired.

### Edges and the graph

- **R13** — The edge vocabulary is closed, per the edge table. Every field that names another node and
  must resolve is an edge there.
- **R14** — Every edge type declares its cardinality and whether expansion traverses it, and a validator
  MUST enforce both. Expansion MUST follow only traversed edges.
- **R15** — Two or more `lifecycle` objects MUST NOT name the same `definition` as `subject`.
- **R16** — Every knowledge object MUST declare exactly one `boundary`, except a `boundary` with
  `ddd: bounded-context`. Membership MUST be derived from each member's `boundary` field, and a
  `boundary` MUST NOT enumerate its members.
- **R17** — The knowledge graph is derived from the objects and MUST NOT be authored. It is the instance
  level; the ontology is the schema level, and the two MUST NOT be used interchangeably.
- **R18** — An edge naming an id the graph does not hold MUST be reported as a defect, together with
  orphans and cycles, and MUST NOT be repaired.

### The attribute type system

- **R19** — The attribute primitive vocabulary is closed, per the primitives table. A free-text type MUST
  be rejected.
- **R20** — Every attribute MUST declare the parameters its primitive requires and does not inherit.
- **R21** — A parameter repeated across attributes MUST be declared once as a system default and
  overridden only where an attribute differs. A default MUST live in the knowledge base and MUST NOT be
  supplied by whatever reads it.
- **R22** — An attribute holding lifecycle state MUST declare `enum` with `lifecycle` naming a
  `lifecycle` id, and MUST NOT repeat the state names.
- **R23** — A `ref` or a `list` MUST declare `binding`, and one whose target lies in another aggregate
  MUST declare `binding: by-identity`. How a binding becomes a storage representation MUST NOT be
  recorded.
- **R24** — A `ref` or `list` target the graph does not hold MUST be reported as a defect.
- **R25** — The type system MUST be expressed in the frontmatter schema, which is its single authority.

### The notation

- **R26** — `id`, `question`, `type`, `contract_version`, `generated`, `out_of_scope`, and `boundary` are
  required. A knowledge object MUST NOT declare a status, a maturity level, or an approval state: what
  the base holds is current and binds, and a consumer MUST NOT gate on such a field.
- **R27** — Every fact a machine reads to produce or validate something MUST live in frontmatter. Nothing
  decides anything by parsing body prose.
- **R28** — Every knowledge object MUST declare `out_of_scope` with at least one entry.
- **R29** — A synonym MUST be declared in `aliases` and MUST NOT appear in any body.
- **R30** — A consumer MUST preserve a frontmatter field it does not know.
- **R31** — The frontmatter contract MUST ship as a schema with per-type required fields expressed
  conditionally, and the distribution MUST ship a boundary validator that enforces it.
- **R32** — The knowledge base MUST declare, once, the defaults every attribute inherits and the body
  length ceiling. A validator MUST NOT supply either: where a declaration is absent, the check is
  reported as unenforceable.

### Identity and layout

- **R33** — An id has the form `ko.<type>.<boundary>.<slug>` with kebab-case segments. For
  `type: boundary` the form is `ko.boundary.<context>` for a bounded context and
  `ko.boundary.<context>.<aggregate>` for an aggregate. A path MUST be computable from an id and an id
  from a path, with no lookup.
- **R34** — An id MUST NOT be sequential, and no id allocator exists.
- **R35** — A knowledge object that changes `type` or `boundary` MUST receive a new id, and the object
  under the previous id MUST be removed together with every reference to it. A retired revision MUST NOT
  be retained in the base; version control holds what the base held.
- **R36** — A file MUST hold exactly one knowledge object, at the depth R33 fixes.
- **R37** — A derived file MUST NOT be hand-edited.

### Body form

- **R38** — A body MUST carry exactly the two sections its type names, with literal headings, in the
  stated order, and MUST NOT carry another heading. A section with no content carries the literal line
  `None.`
- **R39** — A body MUST place one sentence per line.
- **R40** — A normative statement MUST use exactly one RFC 2119 keyword, in uppercase, and MUST NOT use a
  pronoun.
- **R41** — A body MUST NOT contain rationale, history, alternatives, or a motivating narrative, and MUST
  NOT be the only place a fact a machine reads appears.
- **R42** — A relationship MUST NOT exist only in prose or only in a diagram.
- **R43** — A validator MUST enforce the body length ceiling, reported as a single-responsibility
  violation under R5 rather than as a formatting warning.
- **R44** — Where machine consumption and human readability conflict, machine consumption MUST win, and
  the human cost MUST be compensated by a projection rather than by an exception to a form rule.

### Projections

- **R45** — Projections are limited to an index, a glossary, and a context map. A fourth requires a
  recorded case that demands it.
- **R46** — A projection MUST be reproducible from the graph and MUST NOT be a normative source.
- **R47** — Type utilization and edge traversal utility MUST be measured. A type holding under 5% of
  nodes with no check branching on it, or an edge no resolution reads, MUST be removed rather than
  retained for symmetry.
