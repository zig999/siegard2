# The domain profile

One file per kind, plus the tables a kind draws on. Together they are what a domain graph is composed
from: `nodes/` says what each of the eight constructs is, `tables/` says what all eight share, and
`domain-graph.json` says which parts have to exist before a graph can be composed at all.

This tree does not ship. It is authored source, and the distribution carries a composed form of it.

## Why it is split

`src/claude/schemas/domain-object.json` holds all of this in one file, because a consumer's boundary
validator loads a schema standalone and a cross-file `$ref` would be resolved over the network. That
constraint is real and binds the *shipped* artifact — it does not bind what the shipped artifact is
written from. The repository already works this way once more: `schemas/knowledge-notation.json` states
the envelope's assertions once, and every profile carries them rather than restating them.

So the `$ref`s here are relative paths between sibling files, resolvable offline against a local base
URI, and the composition into one self-contained document is what makes them safe to ship.

## Layout

```
domain/
  domain-graph.json          what a graph is composed from, and where each part lives
  nodes/
    subdomain.json           a partition of the problem space
    context.json             a linguistic boundary
    aggregate.json           a consistency boundary
    definition.json          what a thing is, with its typed attributes
    rule.json                one falsifiable condition
    lifecycle.json           the states a definition holds
    interface.json           what a context publishes or consumes
    process.json             an ordered path across the rest
  tables/
    envelope.json            manifest of the shared fields; restates nothing
    identifiers.json         identifier patterns and path arithmetic
    primitives.json          the twelve attribute types
    vocabularies.json        every closed enumeration
    edges.json               the edge table, with cardinality and traversal
    body-sections.json       the two headings per kind, and body form
    invariants.json          cross-kind assertions, cross-node rules, and `rationale`
```

A node file declares only what its kind decides. It is a JSON Schema fragment, not a standalone
validator: the envelope it carries is decided elsewhere, and composing the two is what produces a
document that can validate a file.

Keys prefixed `x-` are composition metadata. JSON Schema ignores an unknown keyword, so each file
remains a valid schema document while carrying the table a composer reads. The one `x-` key that is not
documentation is `invariants.json#/x-cross-kind/*/schema`: each holds the assertion itself, and the prose
beside it gives the reason and never restates the rule.

## How a node states what it requires

Each required field is alternated separately against a gap naming that field:

```json
{ "anyOf": [
    { "required": ["boundary"] },
    { "required": ["gaps"],
      "properties": { "gaps": { "contains": {
        "required": ["field"],
        "properties": { "field": { "const": "boundary" } } } } } } ] }
```

`domain-object/1` alternates once per kind instead — every field, or `gaps` — which any gap over any
field satisfies. A node short of `boundary` while declaring a gap about `owner` passes it. `boundary` is
the parent pointer, so what that admits is a node that validates while hanging off nothing.

The shape is load-bearing beyond validation. `obligations()` in `src/claude/bin/check_knowledge.py`
recovers each kind's required-field set by reading it out of the composed contract, and reads both
forms for as long as both exist. A third shape raises rather than returning an empty set: an empty set
is indistinguishable from a kind that requires nothing, and every object would pass while nothing was
checked.

## What this tree changes, and what it only records

Vocabulary changes **applied here** and not in the shipped contract. Each is a break, and composing this
tree is what would carry it across:

| Applied here | Shipped contract says | Effect |
|---|---|---|
| `nodeId` | `knowledgeObjectId` | rename only |
| `steps[].node` | `steps[].ko` | frontmatter break; every process node changes |
| `governed_by` removed | `governed_by` present | field removal; targets `adr.NNNN`, which this network holds no node for |
| per-field gap alternation | per-kind alternation | refuses objects the shipped contract admits |

One correction was applied to **both**, because leaving it here alone would have fixed the source and
not the product: `boundaryId` was a single pattern with an optional trailing segment, and the tail
applies to both alternatives — so it admitted `dm.context.<a>.<b>` and `dm.aggregate.<a>`, neither of
which is a scope this profile holds.

Everything else is a faithful decomposition. Where the tree and the shipped contract disagree, or where
a rule is stated and nothing decides it, the divergence is **recorded and not resolved** — in `x-open` on
the file that carries the field, and in `x-owed` in `tables/invariants.json`. Every entry there is a check
this profile requires and no shipped script performs.

Two readings are worth naming, because a reader of `nodes/` would otherwise assume them settled:

- `owner` is declared by the profile with no conditional, so any kind may carry it. It is written into
  the three scope kinds here as optional, which is a reading. Nothing states it and nothing enforces it.
- `context_relationships[].with` is typed `boundaryId` in the shipped contract, which admits an
  aggregate. Only a context relates to a context, so it is narrowed to `contextId` here.

## What is missing before this is the source

The composition step, as a repository artifact. The tree has been shown to compose — resolving the
sibling `$ref`s and splicing `nodes/*.json` with `x-cross-kind[*].schema` yields one self-contained
document of 13 `allOf` blocks, the same count the shipped contract carries — but nothing in this
repository performs it. Until something does, this tree and `src/claude/schemas/domain-object.json` are
two homes for one set of facts, and **the shipped file is the authority**.

Closing it is two pieces of work: a composer that emits the self-contained document, and a check that
the committed distribution matches what the composer produces. A check that repairs what it was meant to
detect reports success on a defect, so the second compares and does not write.

Both were previously described as following the shape of `make dist-check`. There is no `Makefile` and no
`scripts/` in this repository any more, so there is no shape to follow and no harness to add either to —
which is itself part of the work.

## What this tree does not let an analysis record

Soundness and completeness are different questions, and the sections above are all about the first. Eight
facts a domain analysis produces have no node, no edge and no field here, so each lands in a body — which
`tables/edges.json` opens by saying is not knowledge, because two readings of one paragraph produce two
graphs.

- a state transition emitting a domain event — `transitions[]` has no edge to an `interface`
- the payload of an interface — `schema` is a free string, with no edge to the definitions that form it
- who consumes a published interface — `ownership` marks each node alone, and nothing links the pair
- a saga's compensating steps — `steps[]` carries an identifier per step and nothing else
- the direction of a context relationship — `customer-supplier` and `conformist` are directional, and
  nothing says which side is upstream, nor requires the other context to agree
- whether a rule spanning two aggregates is eventually consistent
- a command, as distinct from an API operation or a use case
- the decision behind a boundary — `governed_by` was removed and no kind replaced it

Each is a breaking change to add, so each belongs to a contract version rather than to a correction.
