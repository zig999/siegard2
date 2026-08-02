---
id: "0003"
title: Store the domain analysis as a typed ontology, and derive the graph from it
status: accepted
contract_version: spec/1
---

# The knowledge ontology and notation

## Scope

How a governed repository stores the domain analysis: the notation every object is written in, the
eight kinds a construct takes, the edges that connect them, the attribute type system, identity, body
form, and the graph derived from the whole.

Two things this document keeps apart, and its own title names both. The **notation** is how a fact is
stored — the frontmatter fence, the envelope every object carries whatever it is, the two body
sections, the arithmetic between an identifier and a path. The **ontology** is which kinds exist and
what each demands of its own content. A profile is one ontology written in the notation, and a second
profile would change the kinds without touching the form.

Not here: how a request becomes a domain analysis (`foundation/0002`).

## The kinds, and what each records

One kind per construct, and nothing folded into a field of something else. A subdomain and a
relationship between contexts were once fields of another object, and neither could carry an origin, a
reason, or a gap of its own — a construct with no identifier is a construct nothing can reference,
review, or correct.

| Kind | Records | `ddd` |
|---|---|---|
| `subdomain` | a partition of the problem space, classified where effort is worth its cost | — |
| `context` | a bounded context, and the relationships it holds with others | — |
| `aggregate` | a consistency boundary, with the definition that is its root | — |
| `definition` | what a thing is, with its typed attributes | `entity`, `value-object`, `aggregate-root`, `read-model`, `domain-error` |
| `rule` | one falsifiable condition | `invariant`, `domain-rule`, `policy`, `specification`, `quality-attribute` |
| `lifecycle` | the states a definition holds and how it moves | — |
| `interface` | what a context publishes or consumes | `domain-event`, `integration-event`, `published-language`, `api` |
| `process` | an ordered path across the above | `domain-service`, `saga`, `use-case` |

`ddd` is carried only where a kind covers several constructs. Where it is absent the kind **is** the
construct, and a `ddd` beside it would name one fact twice.

Two things a domain has and this ontology does not record. The domain itself is the governed
repository, so it needs no object. The ubiquitous language is emergent: it is the set of `definition`
objects, and a synonym is declared in `definition.aliases[]` rather than listed anywhere.

Two things it refuses. Stack knowledge — a repository, a factory, a module, a layering choice — has no
kind and is recorded as excluded. A decision record is a graph node and never an object.

## The edge table

| Edge | Origin → target | Out | In | Traversed | Depth |
|---|---|---|---|---|---|
| `boundary` | any → `context` or `aggregate` | 1..1 | 0..n | yes | 1 |
| `subdomain` | `context` → `subdomain` | 1..1 | 0..n | yes | 1 |
| `aggregate.root` | `aggregate` → `definition` | 1..1 | 0..1 | yes | 1 |
| `depends_on` | any → any | 0..n | 0..n | yes | 2 |
| `governed_by` | any → decision record | 0..n | 0..n | yes | 1 |
| `attributes[].target` | `definition` → `definition` | 0..n | 0..n | yes | 1 |
| `attributes[].of` | `definition` → `definition` | 0..n | 0..n | yes | 1 |
| `attributes[].lifecycle` | `definition` → `lifecycle` | 0..n | 0..n | yes | 1 |
| `lifecycle.subject` | `lifecycle` → `definition` | 1..1 | 0..1 | yes | 1 |
| `transitions[].guard` | `lifecycle` → `rule` | 0..n | 0..n | yes | 1 |
| `rejections[].error` | `lifecycle` → `definition` | 0..n | 0..n | yes | 1 |
| `steps[].ko` | `process` → any | 0..n | 0..n | yes | 1 |
| `context_relationships[].with` | `context` → `context` | 0..n | 0..n | only when expansion crosses a context | 1 |

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

## Body sections, by kind

| kind | sections, in order |
|---|---|
| `subdomain` | `## Answer` · `## Responsibilities` |
| `context` | `## Answer` · `## Responsibilities` |
| `aggregate` | `## Answer` · `## Invariants` |
| `definition` | `## Answer` · `## Invariants` |
| `rule` | `## Answer` · `## Conditions` |
| `lifecycle` | `## Answer` · `## State semantics` |
| `interface` | `## Answer` · `## Semantics` |
| `process` | `## Answer` · `## Outcomes` |

## Requirements

### Kinds

- **R1** — The `type` vocabulary is closed: `subdomain`, `context`, `aggregate`, `definition`, `rule`,
  `lifecycle`, `interface`, `process`. It is 1:1 with the construct vocabulary of `foundation/0002`:
  every construct an analysis produces is a kind, and no kind is a field of another object.
- **R2** — Every construct the analysis produces MUST take exactly one kind, or be recorded as excluded
  with the reason. A construct fitting no kind MUST NOT be recorded silently.
- **R3** — A ninth kind is admitted only when the analysis produces a construct none of the eight
  records, and it MUST be recorded with the construct that demanded it. The vocabulary follows what an
  analysis produces rather than what a validator finds convenient to distinguish, so a kind is refused
  for having no construct behind it and never for being cheap to fold into another.
- **R4** — A decision record is a permanent graph node and MUST NOT be a knowledge object. Rationale
  belongs with the fact it decided: an object whose `origin` is `modeled` MUST carry the reason, and one
  whose `origin` is `stated` MUST NOT be made to invent one. What a body may not carry is fixed by R41.
- **R5** — A knowledge object MUST answer exactly one question, declared in `question`.
- **R6** — A `definition` MUST declare `attributes`. One whose `ddd` is `entity`, `aggregate-root`, or
  `read-model` MUST declare `identity`; one whose `ddd` is `value-object` or `domain-error` MUST NOT.
- **R7** — A `rule` MUST declare `statement`, and `expression` or `examples`. A `rule` with
  `ddd: quality-attribute` MUST declare the bounded context it constrains, once per context.
- **R8** — A `lifecycle` MUST declare `subject`, `states`, `initial`, `transitions`, and `rejections`,
  and its transition table MUST be total: for every pairing of a state with a trigger, either a
  transition or a rejection exists. Every state MUST be reachable from `initial`, and every non-terminal
  state MUST have an outgoing transition.
- **R9** — An `interface` MUST declare `version`, `schema`, and `ownership` ∈ `published | consumed`.
- **R10** — A `subdomain` MUST declare `subdomain_type` ∈ `core | supporting | generic`. A `context`
  MUST declare the `subdomain` it partitions. An `aggregate` MUST declare the `context` it sits in and
  the `definition` that is its `root`.
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
- **R16** — Every knowledge object MUST declare exactly one `boundary`, except a `subdomain` and a
  `context`, which are scopes rather than members and whose absence of one identifies a partition root.
  Membership MUST be derived from each member's `boundary` field, and a scope MUST NOT enumerate what it
  holds.
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

- **R26** — `id`, `type`, `title`, `contract_version`, `generated`, and `origin` are required of every
  object. `question`, `description`, and `out_of_scope` are required of one that declares no open
  `kind: authoring` gap, and excused of one that does — which is what says a pass has not reached it. A
  knowledge object MUST NOT declare a status, a maturity level, or an approval state, and which pass has
  run is not one either: an open gap already records it, and a field saying so would be a second home
  for one fact. A consumer MUST NOT gate on such a field.
- **R27** — Every fact a machine reads to produce or validate something MUST live in frontmatter. Nothing
  decides anything by parsing body prose.
- **R28** — Where R26 requires `out_of_scope`, it MUST carry at least one entry. Absence cannot be
  inferred, and silence reads as permission.
- **R29** — A synonym MUST be declared in `aliases` and MUST NOT appear in any body.
- **R30** — A consumer MUST preserve a frontmatter field it does not know.
- **R31** — The frontmatter contract MUST ship as a schema with per-type required fields expressed
  conditionally, and the distribution MUST ship a boundary validator that enforces it.
- **R32** — The knowledge base MUST declare, once, the defaults every attribute inherits and the body
  length ceiling. A validator MUST NOT supply either: where a declaration is absent, the check is
  reported as unenforceable.

### Identity and layout

- **R33** — An id has the form `dm.<kind>.<scope>.<slug>` with kebab-case segments, where `<scope>` is
  the bounded context the object sits in. A `subdomain` and a `context` take `dm.<kind>.<slug>`, because
  each is itself a scope. A `lifecycle` takes the slug of its subject. A path MUST be computable from an
  id and an id from a path, with no lookup, and a validator MUST enforce the agreement — nothing
  allocates an id, so a disagreement is a defect rather than a convention a writer is trusted to have
  followed.
- **R34** — An id MUST NOT be sequential, and no id allocator exists.
- **R35** — A knowledge object that changes `type`, `boundary`, or its name MUST receive a new id, and the object
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
