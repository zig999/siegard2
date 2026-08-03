---
id: "0003"
title: Represent domain knowledge as a typed ontology in an AI-first notation
status: accepted
contract_version: spec/1
---

# The knowledge ontology and notation

## Scope

This specification fixes how a repository Siegard governs represents the knowledge it holds. It decides
five things:

1. that Domain-Driven Design supplies the conceptual vocabulary, and that every construct the analysis
   produces has exactly one recorded home;
2. the [ontology](../docs/concepts/ontology.md) — which node types exist, which edges connect them, with
   what cardinality and what meaning;
3. the notation — an OKF-derived frontmatter contract, a closed attribute type system, and system-level
   defaults;
4. the folder structure, the identity scheme, and the body template, all optimized for machine consumption
   at explicit cost to human reading;
5. which projections may be generated from the ontology.

It **derives from `foundation/0002-knowledge-economy-principles.md`**, which decides what knowledge is worth
holding at all. Every node type, edge, and field below is answerable to the two tests 0002 states, and this
specification cites them rather than repeating them.

It decides nothing about how software is produced from this representation — artifact classes, the target
pack, generation scope, plan, manifest, verification, and generative completeness belong to `foundation/0004`,
which cites this one. It does not restate spec 0001's workflow or its transient artifacts.


### Decided elsewhere, deliberately not restated here

| Question | Authority |
|---|---|
| What knowledge is worth holding, and the domain/stack boundary | spec 0002 |
| The workflow every change request follows, and its transient artifacts | spec 0001 |
| The maturity ladder, and what an assertion binds | spec 0001 R23–R26 |
| How software is produced from this representation | `foundation/0004` |
| The OKF-derived frontmatter precedent and its one divergence | R-block **Notation** below |
| When an artifact requires a versioned schema | `foundation/0005` R16a |
| What makes a change breaking, and how a version is bumped | `foundation/0013` R3a, R10–R12 |
| That a hidden default is rejected | `foundation/0005` R16b |

### One deliberate naming decision

The node type describing what a bounded context exposes is named
[interface](../docs/concepts/interface.md), not "contract". This repository already uses *contract* for an
agreement between framework components — `contract_version`, `foundation/0005` R16a, the component
contracts of a Claude Code component. Using the same word for a domain-level interface would put one name
on two things.

## DDD supplies the vocabulary

Analysis proceeds in DDD's own order, strategic before tactical, because a tactical construct recorded
before its bounded context has no boundary to declare and no place in the partition:

1. classify the domain into subdomains as core, supporting, or generic;
2. draw bounded contexts and the relationships between them;
3. inside each context, find aggregates, then the entities and value objects they hold;
4. state the invariants, rules, and policies that constrain them;
5. give each stateful definition its lifecycle;
6. name the events and interfaces the context publishes or consumes;
7. describe the processes that span the above.

**DDD defines the conceptual vocabulary of the knowledge model. After analysis, its constructs are
normalized into this ontology, which is the representation consumers read.** DDD therefore does not stop at
discovery: an aggregate root yields a different structure than a plain entity, a bounded context shapes
module organization, and a published interface shapes integration. What stops at analysis is DDD as a
*method* and as a *storage structure* — the ontology is the persistent form, not the DDD diagram.

The consequence raises the stakes on one field: `ddd` is not annotation. It is read by whatever produces
software, so a wrong value produces wrong output rather than an imprecise document.

### Mapping: every DDD construct has exactly one home

| DDD construct | Recorded as | Home |
|---|---|---|
| Domain | nothing | the governed repository is the domain; a node would have one instance |
| Subdomain | field | `boundary.subdomain_type` ∈ `core \| supporting \| generic` |
| Bounded Context | **type** | `boundary`, `ddd: bounded-context` |
| Context Map | field | `boundary.context_relationships[]`, plus a generated projection |
| Ubiquitous Language | emergent | the set of `definition` objects; synonyms in `definition.aliases[]` |
| Glossary | projection | generated from `definition` objects |
| Entity | field | `definition`, `ddd: entity` |
| Value Object | field | `definition`, `ddd: value-object` |
| Aggregate | **type** | `boundary`, `ddd: aggregate` — a consistency boundary, not a definition |
| Aggregate Root | field | `definition`, `ddd: aggregate-root` |
| Entity lifecycle, state machine | **type** | `lifecycle` |
| Domain Event | field | `interface`, `ddd: domain-event` |
| Integration Event | field | `interface`, `ddd: integration-event` |
| Published Language | field | `interface`, `ddd: published-language` |
| Open Host Service, API | field | `interface`, `ddd: api` |
| Invariant | field | `rule`, `ddd: invariant` |
| Business Rule | field | `rule`, `ddd: domain-rule` |
| Policy | field | `rule`, `ddd: policy` |
| Specification pattern | field | `rule`, `ddd: specification` |
| Quality attribute, non-functional requirement | field | `rule`, `ddd: quality-attribute` |
| Domain error | field | `definition`, `ddd: domain-error` |
| Read model | field | `definition`, `ddd: read-model` |
| Domain Service | field | `process`, `ddd: domain-service` |
| Saga, Process Manager | field | `process`, `ddd: saga` |
| Use case, application flow | field | `process`, `ddd: use-case` |
| Anti-corruption Layer, Conformist, Shared Kernel, Customer-Supplier, Separate Ways | field | `boundary.context_relationships[].pattern` |
| Repository, Factory, Module, layering | nothing | stack knowledge, excluded by spec 0002 R4 |
| Architectural decision | **node, not a knowledge object** | ADR |

Collapsing the catalogue into six types discards no vocabulary. It moves the vocabulary from the type to a
field, where it stays readable, selectable, and validatable without costing a schema branch, an authoring
guide, and a projection each.

## The ontology: node types

Six node types. Five are knowledge objects; the sixth is not.

| Node | Question it answers | Distinctive required field | Check it enables |
|---|---|---|---|
| [definition](../docs/concepts/definition.md) | What is X, and what does X hold? | `attributes[]`, and `identity` where the construct has one | every attribute fully typed; every reference resolves |
| [rule](../docs/concepts/rule.md) | Under which condition does what hold? | `expression` or `examples[]` | an assertion may bind; a test may be derived |
| [lifecycle](../docs/concepts/lifecycle.md) | Which states, and which transitions are legal? | `states`, `initial`, `transitions`, `rejections` | **totality**; reachability of every state |
| [interface](../docs/concepts/interface.md) | What does this context expose or consume? | `version`, `schema`, `ownership` | a break requires a version bump and a migration |
| [boundary](../docs/concepts/boundary.md) | What is the scope, and who owns it? | `subdomain_type` | every object belongs to exactly one; crossing requires an interface |
| [process](../docs/concepts/process.md) | In which order, and with what outcome? | `steps[]` | every referenced id exists; no step content restated |
| ADR | Why was this decided, and what was rejected? | per `schemas/knowledge-decision.json` | non-restatement of an operative rule |

Each type passes the differentiation test of spec 0002 R3: two systems built on one technology differ in
their definitions, rules, lifecycles, interfaces, boundaries, and processes, and in nothing else this
ontology records.

`lifecycle` is the type admitted with the most reluctance, and it earns admission on both conditions of R6.
It requires `states` and `transitions`, which no other type requires. It enables three checks no other type
enables: reachability of every state from `initial`, a terminal state declared rather than inferred, and
totality. Decomposing a lifecycle into individual rules fails not on cost but on expressiveness — no set of
independent rules states "these are *all* the transitions", so completeness becomes unverifiable, and an
incomplete transition table is where a producer of software invents behaviour.

### Rationale has exactly one home

A `rule` states what holds. The ADR states why it was chosen, what was rejected, what cost was accepted,
and what would falsify the decision. The two never restate each other, for the reason
[operative-rule](../docs/concepts/operative-rule.md) gives: the rule loads while work happens, the decision
record opens when someone asks why, and a copy in both diverges silently.

The consequence is deliberate and uncomfortable: a human reading a `rule` gets no motivation. The
`governed_by` edge names the ADR, and following it is one hop.

## The ontology: edges, cardinality, and traversal

An ontology stating relations without cardinality cannot be validated. Every edge declares its cardinality
and whether expansion traverses it, because an unstated traversal policy makes "identical inputs produce
identical output" undefined.

Cardinality is stated in two columns, in one canonical notation, so a validator reads it rather than
interprets it. **Out** bounds how many edges of the kind one origin node declares; **In** bounds how many
arrive at one target. Both are written `<min>..<max>`, where `n` is unbounded. An earlier draft used a single
prose column, which mixed those two questions with a third — how many targets one *attribute* or one
*transition* names — and could not be parsed, so the numbers a validator enforced were a transcription
nothing checked.

| Edge | Origin → target | Out | In | Authored or structural | Traversed | Depth |
|---|---|---|---|---|---|---|
| `boundary` | any → `boundary` | 1..1 | 0..n | structural | yes | 1 |
| `depends_on` | any → any | 0..n | 0..n | authored | yes | 2 |
| `governed_by` | any → ADR | 0..n | 0..n | authored | yes | 1 |
| `attributes[].target` | `definition` → `definition` | 0..n | 0..n | structural | yes | 1 |
| `attributes[].of` | `definition` → `definition` | 0..n | 0..n | structural | yes | 1 |
| `attributes[].lifecycle` | `definition` → `lifecycle` | 0..n | 0..n | structural | yes | 1 |
| `lifecycle.subject` | `lifecycle` → `definition` | 1..1 | 0..1 | structural | yes | 1 |
| `transitions[].guard` | `lifecycle` → `rule` | 0..n | 0..n | structural | yes | 1 |
| `rejections[].error` | `lifecycle` → `definition` | 0..n | 0..n | structural | yes | 1 |
| `steps[].ko` | `process` → any | 0..n | 0..n | structural | yes | 1 |
| `context_relationships[].with` | `boundary` → `boundary` | 0..n | 0..n | authored | yes, only when expansion crosses a context | 1 |

One exception does not fit a cell and is stated here instead: a `boundary` with `ddd: bounded-context`
declares **zero** `boundary` edges, and that absence is what identifies a partition root. The exception lives
in one named place in the validator, and the table's `1..1` is the rule it excepts.

How many targets one attribute or one transition names is a question for the frontmatter contract, not for
this table. A `ref` declares exactly one `target`, a `list` exactly one `of`, a lifecycle-bound `enum`
exactly one `lifecycle`, a transition at most one `guard`, a rejection exactly one `error`, a step exactly
one `ko`, and a context relationship exactly one `with` — each because the field is a single value that
`schemas/knowledge-object.json` requires or permits. A definition holding three `ref` attributes declares
three `attributes[].target` edges, which is why every such row is `0..n` out.

Every edge in the table is traversed. That is not a coincidence to be admired but the consequence of R52
applied once: an edge no resolution reads is removed rather than retained for symmetry, and the first
measurement over a fixture found three that no resolution read.

`attributes[].of` and `rejections[].error` are in the table because R29 and R11 require both to resolve, and
nothing resolves without an edge. Their earlier absence made the vocabulary R17 calls closed incomplete: a
`list` target and a rejection's error each name a knowledge object, and each is exactly as structural as the
`ref` target and the transition guard beside them.

`references` was removed. It was authored, traversed by nothing, and required by no other statement in this
specification, which is R52's removal condition met in full. A relationship worth recording is worth
declaring as one of the edges above.

`implements` is absent: it binds code to knowledge, not knowledge to knowledge, and `foundation/0004` owns it.
`extends` is absent: it duplicated `depends_on` in every case examined.

The inverse cardinality on `lifecycle.subject` is a check, not a note: two lifecycles naming one subject is
a defect, because a definition with two state machines has no single state set to generate from.

### Supersession is a field, not an edge

`superseded_by` names the knowledge object that replaced this one, and R40 requires it. It is deliberately
**not** in the table above: expansion must never follow it, because pulling a retired object's replacement
into context — or the reverse — is how a superseded fact re-enters the work that superseded it. The target
MUST resolve, and R22 says so.

Its inverse `supersedes` was removed. R40 needs one direction, and a second field carrying the same relation
backwards is precisely what R52 means by retained for symmetry.

Membership is derived from each object's own `boundary` field. A `boundary` never enumerates its members,
because a hand-maintained membership list is a second copy of a fact the members already hold.

## The attribute type system

An attribute whose type is a free-text word cannot be expanded. Two authors writing `date` and `Date`
produce two different columns, and a `decimal` with no scale leaves the scale to whatever reads it.

The primitive vocabulary is closed, and a parameter that changes what is produced is **required**:

| Primitive | Required parameters | What the parameter changes |
|---|---|---|
| `string` | `max_length` | storage type and length, validation |
| `text` | — | unbounded text |
| `integer` | — (`min`, `max` optional) | integer width when bounds are given |
| `decimal` | `precision`, `scale` | numeric type, rounding behaviour |
| `money` | — (inherits the system default; overridable) | amount and currency representation |
| `boolean` | — | |
| `date` | — | |
| `datetime` | — (inherits the system default; overridable) | whether the value carries a zone |
| `duration` | — | ISO 8601 representation |
| `enum` | `lifecycle` **or** `values[]` | the value set and its members |
| `ref` | `target`, `binding` | embedded value versus reference by identity |
| `list` | `of`, `binding` (`min_items`, `max_items` optional) | collection representation; embedded collection versus references by identity |

Monetary precision and rounding are domain facts, not implementation detail: two systems on one technology
differ in them, which is spec 0002 R3 placing them here.

### System-level defaults, declared once

A parameter repeated on every attribute is representation cost with no differentiating content — precisely
what spec 0002 R2 removes. Three parameters are declared once and overridden only where an attribute
genuinely differs:

```yaml
# knowledge/system.md frontmatter
defaults:
  timezone: America/Sao_Paulo
  currency: BRL
  identity_strategy: surrogate
```

An override is a fact about that attribute; a repetition is noise. The default lives in the knowledge base
rather than in whatever reads it, because `foundation/0005` R16b rejects a hidden default and a
value supplied downstream is exactly that.

`knowledge/system.md` holds one further declaration for the same reason: the body length ceiling R48
enforces, as `limits.body_lines`. It is not an attribute default, so it sits under `limits` rather than
`defaults`, and a validator that carried the number instead would be the hidden default this paragraph
rejects. What the value should be is still deferred to R52's measurement.

Three rules make the type system carry DDD semantics rather than only shapes:

- an attribute holding lifecycle state declares `enum` with `lifecycle: <id>` and **never** repeats the
  state names, so the state set has one authority;
- a `ref` **or a `list`** whose target lies in another aggregate MUST use `binding: by-identity` — the DDD
  rule that an aggregate references another aggregate by identity alone, recorded once and checked
  mechanically instead of taught in a prompt. **How** that binding becomes a storage representation is stack
  knowledge, excluded by spec 0002 R4.

  `list` carries `binding` for the same reason `ref` does, and an earlier draft gave it only to `ref`. That
  asymmetry made one rule enforced on a single field and silent on an equivalent one: the identical crossing
  was rejected as a `ref` and accepted as a `list`, which left R28 claiming a mechanical check it delivered
  for half the cases. Deriving `binding` from the two boundaries instead of declaring it was rejected: the
  declaration is redundant for generation and is the whole point for validation, because it catches an author
  who believes two definitions share an aggregate when they do not;
- a `ref` whose target lies in another bounded context MUST target an `interface`.

## Notation

The frontmatter derives from Google's Open Knowledge Format v0.2, on the terms already recorded for the
concept bundle: OKF's field names and semantics where they coincide, Siegard's stricter
requirements where OKF is weaker, and one documented divergence on `status`.

This is a **separate contract** from `schemas/concept.json`. A concept file holds this framework's
vocabulary; a knowledge object holds a governed repository's domain knowledge. The type vocabularies are
disjoint on purpose — `concept.json` uses `type: term`, and no knowledge-object type is named `term`.

### Common frontmatter

```yaml
id: ko.rule.sales.proposal-expiration     # required, stable, matches the path
type: rule                                # required, closed enum, OKF field
title: Proposal expiration                # required, OKF field
description: A proposal expires 30 days after issue and cannot be accepted afterwards.
question: When does a proposal expire?    # required, Siegard addition, the retrieval key
boundary: ko.boundary.sales.proposal      # required except for a bounded-context boundary
ddd: invariant                            # required, closed enum per type
status: accepted                          # proposed | accepted | superseded
contract_version: knowledge-object/1      # required
generated: { by: claude-opus-5, at: 2026-07-30T15:19:55Z }   # required, OKF trust field
out_of_scope:                             # required, at least one entry
  - a proposal already accepted, whose acceptance is final
depends_on: [ko.definition.sales.proposal]
governed_by: [adr.0014]
tags: [sales, expiration]
```

### Per-type delta

| type | additionally required | additionally permitted |
|---|---|---|
| `definition` | `attributes[]`; `identity` when `ddd` ∈ `entity \| aggregate-root \| read-model` | `aliases[]`; `ddd` ∈ `entity \| value-object \| aggregate-root \| read-model \| domain-error` |
| `rule` | `expression` **or** `examples[]` | `statement` (prose, non-generative); `ddd` ∈ `invariant \| domain-rule \| policy \| specification \| quality-attribute` |
| `lifecycle` | `subject`, `states`, `initial`, `transitions`, `rejections` | `terminal` |
| `interface` | `version`, `schema`, `ownership` | `ddd` ∈ `domain-event \| integration-event \| published-language \| api` |
| `boundary` | `subdomain_type` | `context_relationships[]`, `owner`; `ddd` ∈ `bounded-context \| aggregate` |
| `process` | `steps[]` | `ddd` ∈ `domain-service \| saga \| use-case` |

A `boundary` with `ddd: aggregate` declares its containing context in the common `boundary` field. A
`boundary` with `ddd: bounded-context` declares no `boundary` field, and that absence identifies the
partition roots.

A `rule` with `ddd: quality-attribute` declares the bounded context it constrains, exactly as every other
rule does. An earlier draft required it to declare "the system boundary, the one boundary that is not a
bounded context", which nothing could satisfy: `boundary.ddd` is closed to `bounded-context | aggregate`, so
no object could be that boundary, and the one `ddd` value of `rule` that named it was unusable. Admitting a
third boundary kind was rejected for the reason the mapping table already gives for not modelling the domain
as a node — it would hold one instance. A quality attribute spanning every context is recorded once per
context it constrains, or it is stack knowledge that spec 0002 R4 excludes.

### What Siegard adds over OKF, and why

| Field | OKF | Here | Reason |
|---|---|---|---|
| `id` | absent | required, stable, path-derivable | an edge needs a target; a path must be computable |
| `type` | unregistered values | closed enum of six | a consumer branches on a known value |
| `question` | absent | required | the retrieval key, and the single-responsibility test made checkable |
| `contract_version` | absent | required | a consumer rejects rather than infers version from shape |
| `generated` | optional | required | provenance is not optional |
| `out_of_scope` | absent | required, non-empty | absence cannot be inferred; silence reads as permission |
| `boundary` | absent | required | the partition is what makes scoping cheap |
| `status` | `draft\|stable\|deprecated` | `proposed\|accepted\|superseded` | **divergence**, with the mapping this section records |

## Folder structure, optimized for id arithmetic

```text
knowledge/
  system.md                       system-level defaults
  index.md                        generated — OKF progressive-disclosure entry
  graph.json                      generated — materialized nodes and edges
  boundary/
    sales.md                      ko.boundary.sales
    sales.proposal.md             ko.boundary.sales.proposal          (ddd: aggregate)
  definition/
    sales/
      proposal.md                 ko.definition.sales.proposal
      proposal-expired.md         ko.definition.sales.proposal-expired  (ddd: domain-error)
  rule/
    sales/
      proposal-expiration.md      ko.rule.sales.proposal-expiration
  lifecycle/
    sales/
      proposal.md                 ko.lifecycle.sales.proposal
  interface/
    sales/
      contract-signed.md          ko.interface.sales.contract-signed
  process/
    sales/
      proposal-approval.md        ko.process.sales.proposal-approval
  decision/
    0014-proposal-validity-window.md    adr.0014
```

Both directions are arithmetic, never a search:

- id → path: `ko.<type>.<boundary>.<slug>` → `knowledge/<type>/<boundary>/<slug>.md`;
- path → id: the reverse, with no lookup table.

The single irregular case is stated rather than inferred: for `type: boundary` the path is
`knowledge/boundary/<slug>.md`, where `<slug>` may contain dots for an aggregate inside a context.

This arithmetic governs the knowledge tree only. Where produced software lives is stack knowledge, excluded
by spec 0002 R4.

| Query | Glob |
|---|---|
| every rule | `knowledge/rule/**/*.md` |
| every rule in sales | `knowledge/rule/sales/*.md` |
| everything in sales | `knowledge/*/sales/*.md` |

Both selection axes are a glob, which is why kind-first nesting was chosen over context-first. Depth is
fixed; deeper nesting makes path computation ambiguous and forces a directory listing, which is the cost
this layout exists to avoid.

## Body template

Every type has exactly **two** sections, in a fixed order, with literal headings.

| type | sections, in order |
|---|---|
| `definition` | `## Answer` · `## Invariants` |
| `rule` | `## Answer` · `## Conditions` |
| `lifecycle` | `## Answer` · `## State semantics` |
| `interface` | `## Answer` · `## Semantics` |
| `boundary` | `## Answer` · `## Responsibilities` |
| `process` | `## Answer` · `## Outcomes` |

Two sections rather than three because attributes, transitions, and steps are structured data. What can be
expanded left the body; what remains is what a reader needs and a machine ignores.

`## Answer` comes first because the answer is the payload and context is what a consumer can skip. A section
with no content carries the literal line `None.`, which is decidable; an empty section is not.

### Worked example: a definition

```markdown
---
id: ko.definition.sales.proposal
type: definition
title: Proposal
description: A priced offer issued to a customer, valid for a bounded period.
question: What is a Proposal?
boundary: ko.boundary.sales.proposal
ddd: aggregate-root
identity: { attributes: [number] }
attributes:
  - { name: number,    type: string,   max_length: 20, required: true }
  - { name: issued_at, type: datetime, required: true }
  - { name: total,     type: money,    required: true }
  - { name: state,     type: enum,     lifecycle: ko.lifecycle.sales.proposal, required: true }
  - { name: customer,  type: ref,      target: ko.definition.sales.customer, binding: by-identity, required: true }
  - { name: items,     type: list,     of: ko.definition.sales.proposal-item, binding: embedded, min_items: 1, required: true }
status: accepted
contract_version: knowledge-object/1
generated: { by: claude-opus-5, at: 2026-07-30T15:19:55Z }
out_of_scope:
  - the signed contract a proposal becomes, which is ko.definition.sales.contract
  - pricing calculation, which is ko.process.sales.proposal-pricing
---

# Proposal

## Answer

A proposal is a priced offer issued to one customer.
A proposal is the root of its aggregate, and its items have no identity outside it.

## Invariants

A proposal MUST hold at least one item.
A proposal total MUST equal the sum of its item totals.
```

`issued_at` carries no `timezone`, `total` carries no `currency`, and `identity` carries no `strategy`: all
three inherit the system defaults. Three fields left every attribute list in the repository, and nothing
about this system became less specified.

### Worked example: a rule

```markdown
---
id: ko.rule.sales.proposal-expiration
type: rule
title: Proposal expiration
description: A proposal expires 30 days after issue and cannot be accepted afterwards.
question: When does a proposal expire?
boundary: ko.boundary.sales.proposal
ddd: invariant
expression: "now() - proposal.issued_at <= P30D"
examples:
  - given: { proposal.issued_at: "2026-07-01T09:00:00Z" }
    when:  { now: "2026-07-25T09:00:00Z", trigger: accept }
    then:  { outcome: allowed }
  - given: { proposal.issued_at: "2026-07-01T09:00:00Z" }
    when:  { now: "2026-08-05T09:00:00Z", trigger: accept }
    then:  { outcome: rejected, error: ko.definition.sales.proposal-expired }
status: accepted
contract_version: knowledge-object/1
generated: { by: claude-opus-5, at: 2026-07-30T15:19:55Z }
out_of_scope:
  - a proposal already accepted, whose acceptance is final
depends_on: [ko.definition.sales.proposal]
governed_by: [adr.0014]
---

# Proposal expiration

## Answer

A proposal expires 30 days after the proposal issue date.
An expired proposal MUST NOT be accepted.

## Conditions

The window counts calendar days from the issue date, exclusive.
A proposal with no issue date is invalid and MUST be rejected before this rule is evaluated.
```

### Worked example: a lifecycle

```markdown
---
id: ko.lifecycle.sales.proposal
type: lifecycle
title: Proposal lifecycle
description: The legal states of a proposal and the transitions between them.
question: Which states may a proposal hold, and which transitions are legal?
boundary: ko.boundary.sales.proposal
subject: ko.definition.sales.proposal
states: [draft, issued, accepted, expired, cancelled]
initial: draft
terminal: [accepted, expired, cancelled]
transitions:
  - { from: draft,  trigger: issue,  to: issued }
  - { from: issued, trigger: accept, to: accepted, guard: ko.rule.sales.proposal-expiration }
  - { from: issued, trigger: expire, to: expired }
  - { from: draft,  trigger: cancel, to: cancelled }
  - { from: issued, trigger: cancel, to: cancelled }
rejections:
  - { from: draft,    trigger: [accept, expire], error: ko.definition.sales.proposal-not-issued }
  - { from: issued,   trigger: [issue],          error: ko.definition.sales.proposal-already-issued }
  - { from: terminal, trigger: [issue, accept, expire, cancel], error: ko.definition.sales.proposal-terminal }
status: accepted
contract_version: knowledge-object/1
generated: { by: claude-opus-5, at: 2026-07-30T15:19:55Z }
out_of_scope:
  - renewal after expiry, which is ko.process.sales.proposal-renewal
---

# Proposal lifecycle

## Answer

A proposal moves from draft to issued, and from issued to accepted, expired, or cancelled.
A terminal state accepts no further trigger.

## State semantics

An issued proposal is visible to the customer.
An expired proposal is retained for audit and MUST NOT be deleted.
```

Totality is a computation: 5 states × 4 triggers is 20 pairs, 5 are transitions, and the remaining 15 MUST
each be decided. Two shorthands keep the declaration from becoming padding — a trigger list expands to one
entry per trigger, and the reserved name `terminal` expands to every state listed as terminal. The validator
expands both before checking the product, so the check stays exhaustive while the artifact does not.

## AI-first form, and the human cost it accepts

The form rules are chosen for machine consumption. Several make the text worse to read, and that trade is
the requirement rather than a side effect.

| Rule | What it costs a human reader | What it buys |
|---|---|---|
| Structured data for anything a machine expands | Reading YAML instead of sentences | Prose cannot be expanded; structure can |
| Exhaustive totality, with shorthand expansion | A declaration that reads mechanically | Completeness becomes computable |
| One sentence per line | Ragged, unnatural text | `path:line` is a citable evidence anchor; a diff is one line |
| Answer before context | No motivating build-up | The first tokens carry the payload; truncation degrades gracefully |
| Fixed two-section arity | Repetitive, sometimes `None.` | A section is extractable by name with no structural parsing |
| No pronoun in a normative statement | Stilted, visibly repetitive | No antecedent to resolve, so no ambiguity to guess |
| No synonym; `aliases` declared instead | Monotone vocabulary a style guide would reject | One surface form per concept; alias resolution is a lookup |
| RFC 2119 keywords, uppercase | Shouting mid-sentence | Obligation strength is a token, not a reading |
| Rationale banished to the ADR | The rule reads as an assertion with no defence | Rule and reasoning cannot diverge |
| Explicit `out_of_scope` | Reads as padding | Absence becomes a fact instead of a silence read as permission |
| Lists ordered lexicographically by id | Loses narrative ordering | Byte-identical output for identical input |

The compensation is projections, not exceptions to a form rule.

## Projections

Three, generated from the ontology and never authored: the bundle `index.md`, a glossary derived from
`definition` objects, and a context map derived from `boundary.context_relationships`. A fourth requires a
recorded case that demands it.

A [projection](../docs/concepts/projection.md) is reproducible from the graph and is never a normative
source. A human-readable artifact that becomes authoritative reintroduces the duplication this ontology
exists to remove.

## Definitions

Terms used normatively below.

| Term | Concept |
|---|---|
| ontology | [ontology](../docs/concepts/ontology.md) |
| knowledge base | [knowledge-base](../docs/concepts/knowledge-base.md) |
| knowledge graph | [knowledge-graph](../docs/concepts/knowledge-graph.md) |
| knowledge object | [knowledge-object](../docs/concepts/knowledge-object.md) |
| definition | [definition](../docs/concepts/definition.md) |
| rule | [rule](../docs/concepts/rule.md) |
| lifecycle | [lifecycle](../docs/concepts/lifecycle.md) |
| interface | [interface](../docs/concepts/interface.md) |
| boundary | [boundary](../docs/concepts/boundary.md) |
| process | [process](../docs/concepts/process.md) |
| domain knowledge | [domain-knowledge](../docs/concepts/domain-knowledge.md) |
| stack knowledge | [stack-knowledge](../docs/concepts/stack-knowledge.md) |
| assertion | [assertion](../docs/concepts/assertion.md) |
| operative rule | [operative-rule](../docs/concepts/operative-rule.md) |
| projection | [projection](../docs/concepts/projection.md) |
| provenance | [provenance](../docs/concepts/provenance.md) |
| contract version | [contract-version](../docs/concepts/contract-version.md) |
| accepted | [accepted](../docs/concepts/accepted.md) |
| fixture | [fixture](../docs/concepts/fixture.md) |

## Requirements

### The vocabulary

- **R1** — Domain analysis MUST follow DDD in strategic-before-tactical order: subdomain classification,
  bounded contexts and their relationships, aggregates, entities and value objects, rules, lifecycles,
  published interfaces, processes.
- **R2** — Every construct the analysis produces MUST be normalized into exactly one knowledge object, one
  ADR, or one field named in the mapping table under **DDD supplies the vocabulary**. A construct with no
  entry in that table MUST NOT be recorded until the table names its home.
- **R3** — DDD constructs remain inputs to whatever produces software after analysis. A specification,
  prompt, or report MUST NOT state that DDD's role ends at analysis.
- **R4** — Ubiquitous language MUST NOT be recorded as an artifact. It is the set of `definition` objects,
  and a synonym is declared in `definition.aliases[]`.

### Node types

- **R5** — The `type` vocabulary is closed: `definition`, `rule`, `lifecycle`, `interface`, `boundary`,
  `process`.
- **R6** — A seventh type is admitted only when it requires a frontmatter field no existing type requires
  **and** enables a mechanical check no existing type enables, and only when it satisfies spec 0002 R2 and
  R3. All three conditions MUST be recorded with the concrete case that demanded the type.
- **R7** — An ADR is a permanent graph node and MUST NOT be a knowledge object. Rationale — the alternative
  rejected, the cost accepted, what would falsify the decision — MUST NOT appear in a knowledge object.
- **R8** — A knowledge object MUST answer exactly one question, declared in `question`.
- **R9** — A `definition` MUST declare `attributes`. A `definition` whose `ddd` is `entity`,
  `aggregate-root`, or `read-model` MUST declare `identity`, and one whose `ddd` is `value-object` or
  `domain-error` MUST NOT: a value object is defined by holding no identity, and requiring one would make
  the contract force a false statement about the domain.
- **R10** — A `rule` MUST declare `expression` or `examples`. A `rule` with `ddd: quality-attribute` MUST
  declare the bounded context it constrains, and a quality attribute spanning every context MUST be
  recorded once per context rather than against a boundary no object can be.
- **R11** — A `lifecycle` MUST declare `subject`, `states`, `initial`, `transitions`, and `rejections`, and
  its transition table MUST be **total**: for every pairing of a state with a trigger, either a transition or
  a rejection exists. Every state MUST be reachable from `initial`, and every non-terminal state MUST have an
  outgoing transition. A trigger list and the reserved name `terminal` are shorthands a validator expands
  before checking the product.
- **R12** — An `interface` MUST declare `version`, `schema`, and `ownership` ∈ `published | consumed`. A
  `consumed` interface is exempt from the version-bump discipline of `foundation/0013` R3a, which
  governs what this repository breaks.
- **R13** — A `boundary` with `ddd: bounded-context` MUST declare `subdomain_type`.
- **R14** — A `process` MUST declare `steps` as an ordered list naming knowledge-object ids, and MUST NOT
  restate the content of any step's object.
- **R15** — An edge or attribute reference whose origin and target lie in different bounded contexts MUST
  target an `interface`. A violation is reported, never repaired.
- **R16** — A derived artifact MUST NOT be a node type or a knowledge object.

### Edges and cardinality

- **R17** — The edge vocabulary is closed, per the table under **The ontology: edges, cardinality, and
  traversal**, and `implements` MUST NOT be an edge between knowledge objects. Every field that names
  another node and MUST resolve is an edge in that table, except `superseded_by`. A field that names a node
  and appears in neither place is a defect in this specification, not a licence to add one.
- **R18** — Every edge type MUST declare its cardinality, and the validator MUST enforce it. An ontology
  stating a relation without its cardinality is not validatable.
- **R19** — Every edge type MUST declare whether expansion traverses it and to what depth. Expansion MUST
  follow only traversed edges.
- **R20** — Two or more `lifecycle` objects MUST NOT name the same `definition` as `subject`.
- **R21** — Every knowledge object MUST declare exactly one `boundary`, except a `boundary` with
  `ddd: bounded-context`. Membership MUST be derived from each member's `boundary` field, and a `boundary`
  MUST NOT enumerate its members.
- **R22** — An edge, or a `superseded_by` field, naming an id the graph does not hold MUST be reported by
  the materializer as a defect, together with orphans and cycles, and MUST NOT be repaired. Expansion MUST
  NOT follow `superseded_by`, in either direction.
- **R23** — The ontology is the schema level and the knowledge graph is the instance level. The two terms
  MUST NOT be used interchangeably in a specification, schema, prompt, or report.

### The attribute type system

- **R24** — The attribute primitive vocabulary is closed, per the table under **The attribute type system**.
  A free-text type MUST be rejected.
- **R25** — Every attribute MUST declare the parameters its primitive requires and does not inherit.
- **R26** — A parameter repeated across attributes MUST be declared once as a system default and overridden
  only where an attribute differs. A default MUST live in the knowledge base and MUST NOT be supplied by
  whatever reads it, which `foundation/0005` R16b rejects as a hidden default.
- **R27** — An attribute holding lifecycle state MUST declare `enum` with `lifecycle` naming a `lifecycle`
  id, and MUST NOT repeat the state names.
- **R28** — A `ref` or a `list` MUST declare `binding`, and one whose target lies in another aggregate MUST
  declare `binding: by-identity`. The rule binds both primitives identically: a rule enforced on one field
  and silent on an equivalent one is not the mechanical check this requirement claims to be. How that binding
  becomes a storage representation MUST NOT be recorded, per spec 0002 R4.
- **R29** — A `ref` or `list` target the graph does not hold MUST be reported as a defect.
- **R30** — The type system MUST be expressed in the frontmatter schema, which is its single authority.

### The notation

- **R31** — Fields shared with OKF v0.2 — `type`, `title`, `description`, `tags`, `sources`, `resource`,
  `generated`, `verified`, `stale_after` — MUST keep OKF's names and semantics.
- **R32** — `id`, `question`, `contract_version`, `generated`, `out_of_scope`, and `boundary` are required,
  and `type` is a closed enum, for the reasons this specification records. `status` uses
  `proposed | accepted | superseded`, diverging from OKF, and the divergence MUST be marked in the schema.
- **R33** — Every fact a machine reads to produce or validate something MUST live in frontmatter. Nothing
  decides anything by parsing body prose.
- **R34** — Every knowledge object MUST declare `out_of_scope` with at least one entry.
- **R35** — A synonym MUST be declared in `aliases` and MUST NOT appear in any body.
- **R36** — A consumer MUST preserve a frontmatter field it does not know.
- **R37** — The frontmatter contract MUST ship as `schemas/knowledge-object.json`, with per-type required
  fields expressed conditionally in the schema, and the distribution MUST ship a boundary validator that
  enforces it.

### Identity and layout

- **R38** — An id has the form `ko.<type>.<boundary>.<slug>` with kebab-case segments. For
  `type: boundary` the form is `ko.boundary.<context>` for a bounded context and
  `ko.boundary.<context>.<aggregate>` for an aggregate inside one, and depth is fixed at those two: a
  boundary is the one type whose id names a scope rather than an object within a scope, so it takes the
  segment its members put in *their* `<boundary>` position and nothing deeper. A path MUST be computable
  from an id and an id from a path, with no lookup: `knowledge/<type>/<boundary>/<slug>.md`, and
  `knowledge/boundary/<slug>.md` for `type: boundary`, where that `<slug>` carries the dot when the
  boundary is an aggregate. The two boundary forms were stated only in **Folder structure** before, which
  left this requirement rejecting `ko.boundary.billing.invoice` — an id `schemas/knowledge-object.json`
  accepts and the fixture bundle uses — so a validator built from R38 alone would have refused the
  framework's own evidence.
- **R39** — An id MUST NOT be a sequential number, and no id allocator exists.
- **R40** — A knowledge object that changes `type` or `boundary` MUST receive a new id, and the previous
  object MUST be retained with `status: superseded` and `superseded_by`.
- **R41** — A file MUST hold exactly one knowledge object, and directory depth is fixed at the form R38
  states. The arithmetic governs the knowledge tree only.
- **R42** — `index.md` and `graph.json` are derived and MUST NOT be hand-edited.

### Body form

- **R43** — A body MUST carry exactly the two sections its type names, with literal headings, in the stated
  order, and MUST NOT carry another heading. A section with no content carries the literal line `None.`, and
  the first section MUST be `## Answer`.
- **R44** — A body MUST place one sentence per line.
- **R45** — A normative statement MUST use exactly one RFC 2119 keyword, in uppercase, and MUST NOT use a
  pronoun.
- **R46** — A body MUST NOT contain rationale, history, alternatives, or a motivating narrative, and MUST NOT
  be the only place a fact a machine reads appears.
- **R47** — A relationship MUST NOT exist only in prose or only in a diagram. A diagram is a projection.
- **R48** — The validator MUST enforce a body length ceiling, and an excess MUST be reported as a
  single-responsibility violation under R8 rather than as a formatting warning. The ceiling MUST be declared
  by the knowledge base as `limits.body_lines` in `knowledge/system.md`, and a validator MUST NOT supply a
  default for it: a ceiling supplied by whatever reads the knowledge base is the hidden default
  `foundation/0005` R16b rejects. Where the field is absent, the validator MUST report R48 as
  unenforceable rather than assume a value. The *value* remains deferred to R52's measurement; its home does
  not.
- **R49** — Where machine consumption and human readability conflict, machine consumption MUST win, and the
  human cost MUST be compensated by a projection rather than by an exception to a form rule.

### Projections and ontology governance

- **R50** — Projections are limited to `index.md`, a glossary, and a context map. A fourth requires a
  recorded case that demands it.
- **R51** — A projection MUST be reproducible from the graph and MUST NOT be a normative source.
- **R52** — Type utilization and edge traversal utility MUST be measured. A type holding under 5% of nodes
  with no check branching on it, or an edge no resolution reads, MUST be removed rather than retained for
  symmetry.

## What this specification does not decide

Deferred, because a contract written ahead of the code that needs it is a guess that reads like a
requirement:

- the grammar of `rule.expression`. It MUST be closed, total, side-effect free, and restricted to attributes
  reachable from the rule's boundary; the grammar arrives with the first consumer that evaluates one, and a
  rule not expressible in it carries `examples` instead;
- the schema of `graph.json`, which arrives with the materializer;
- the *value* of the body length ceiling in R48 and the expansion depth in the traversal table, both of
  which R52's measurement should calibrate rather than assert. Where the ceiling lives is decided: a
  maintainer settled `limits.body_lines` in `knowledge/system.md` on 2026-07-30, after building the fixture
  showed that the alternative — a validator holding the number — is the hidden default
  `foundation/0005` R16b rejects;
- the schema of `knowledge/system.md`, beyond the three defaults R26 requires it to hold and the
  `limits.body_lines` ceiling R48 requires;
- how a governed repository installs `knowledge/`, and how the distribution carries the schema and the
  validator.

