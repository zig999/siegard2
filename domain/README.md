# The domain profile

One file per kind, plus the tables a kind draws on. Together they are what a domain graph is composed
from: `nodes/` says what each of the eight constructs is, `tables/` says what all eight share, and
`domain-graph.json` says which parts have to exist before a graph can be composed at all.

This tree does not ship. It is authored source, and the distribution carries a composed form of it.

## Why it is split

`src/claude/schemas/domain-object.json` holds all of this in one 1249-line file, because a consumer's
boundary validator loads a schema standalone and a cross-file `$ref` would be resolved over the
network. That constraint is real and binds the *shipped* artifact — it does not bind what the shipped
artifact is written from. The repository already works this way twice over: `schemas/knowledge-notation.json`
states the envelope once and `scripts/check_notation_agreement.py` holds the shipped profile to it, and
`schemas/contract-versions.json` does the same for a constraint digest.

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
    invariants.json          cross-kind conditionals, and rules that need the whole network
```

A node file declares only what its kind decides. It is a JSON Schema fragment, not a standalone
validator: the envelope it carries is decided elsewhere, and composing the two is what produces a
document that can validate a file.

Keys prefixed `x-` are composition metadata. JSON Schema ignores an unknown keyword, so each file
remains a valid schema document while carrying the table a composer reads.

## What this tree changes, and what it only records

Three vocabulary changes are **applied here** and not in the shipped contract. Each is a break, and
composing this tree is what would carry it across:

| Applied here | Shipped contract says | Effect |
|---|---|---|
| `nodeId` | `knowledgeObjectId` | rename only |
| `steps[].node` | `steps[].ko` | frontmatter break; every process node changes |
| `governed_by` removed | `governed_by` present | field removal; targets `adr.NNNN`, which this network holds no node for |

Everything else is a faithful decomposition. Where the monolith and the specification disagree, or
where a rule is stated and nothing decides it, the divergence is **recorded and not resolved** — in
`x-open` on the file that carries the field, and in `x-owed` in `tables/invariants.json`. The list
there is short and every entry is a check the specification requires and no shipped script performs.

Two are worth naming in passing, because a reader of `nodes/` would otherwise assume them settled:

- `owner` is declared by the profile with no conditional, so any kind may carry it. It is written into
  the three scope kinds here as optional, which is a reading. Nothing states it and nothing enforces it.
- `context_relationships[].with` is typed `boundaryId` in the monolith, which admits an aggregate. Only
  a context relates to a context, so it is narrowed to `contextId` here.

## What is missing before this is the source

The composition step. Until it exists, this tree and `src/claude/schemas/domain-object.json` are two
homes for one set of facts, and **the shipped file is the authority**. Closing that is two pieces of
work: a composer that emits the self-contained document, and a check that the committed distribution
matches what the composer produces — the same shape as `make dist-check`, and for the same reason.
A check that repairs what it was meant to detect reports success on a defect.
