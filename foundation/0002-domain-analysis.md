---
id: "0002"
title: Analyse a request into a domain model, strategic before tactical
status: accepted
contract_version: spec/1
---

# Domain analysis

## Scope

How a request becomes a domain model: the order the analysis follows, what the model records about its
own certainty, and how an element in it is identified.

Not here: how the analysis is stored once classified (`foundation/0003`), or who executes it
(`foundation/0004`).

## The DDD vocabulary

The analysis records constructs in these kinds, and no others.

| Kind | Covers |
|---|---|
| `subdomain` | a partition of the problem space, classified `core`, `supporting`, or `generic` |
| `context` | a bounded context, and the relationships it holds with others |
| `aggregate` | a consistency boundary, with the definition that is its root |
| `definition` | an entity, value object, aggregate root, read model, or domain error |
| `rule` | an invariant, domain rule, policy, specification, or quality attribute |
| `lifecycle` | the states a definition holds and how it moves between them |
| `interface` | a domain event, integration event, published language, or API |
| `process` | a domain service, saga, or use case |

A construct that is stack knowledge — a repository, a factory, a module, a layering choice, a naming
convention, a directory layout, or how a reference becomes a storage representation — has no kind and is
recorded as excluded.

## Requirements

### The analysis

- **R1** — Domain analysis MUST follow DDD in strategic-before-tactical order: subdomains, bounded
  contexts and their relationships, aggregates, definitions, rules, lifecycles, interfaces, processes.
- **R2** — Every construct the analysis produces MUST take exactly one kind from the vocabulary above, or
  be recorded as excluded with the reason. A construct fitting no kind MUST NOT be recorded silently.

### What the model records about itself

- **R3** — Every element MUST declare its origin: `stated` where the request says it, `modeled` where the
  analysis decided it. An element whose origin is `modeled` MUST carry the reason it was decided that
  way.
- **R4** — The analysis MUST NOT supply a parameter the request does not state. A length, a precision, a
  currency, or a period that nobody stated is left absent rather than chosen.
- **R5** — A question the analysis refused to decide MUST be recorded, with what its answer would change
  and which elements it blocks. An unanswered question is an output of the analysis, never a gap to fill.
- **R6** — A model that records no open question and no excluded construct MUST be treated as unreviewed
  rather than as complete.

### Identity

- **R7** — Every element MUST carry an identifier of the form `dm.<kind>.<scope>.<slug>`, where `<kind>`
  is its kind, `<scope>` is the context it belongs to, and `<slug>` is its name in kebab-case. A
  `subdomain` and a `context` take `dm.<kind>.<slug>`, because each is itself a scope. A `lifecycle`
  takes the slug of its subject.
- **R8** — An identifier MUST be derived from the element rather than allocated. No allocator exists, no
  identifier is sequential, and the same model MUST yield the same identifiers on every run.
- **R9** — Two elements MUST NOT carry one identifier. A collision is reported as a defect in the
  analysis, never resolved by adding a suffix.
- **R10** — An element that changes its kind, its scope, or its name becomes a different element. Nothing
  carries an identifier across such a change.
