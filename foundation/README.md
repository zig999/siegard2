# Siegard specifications

What the Siegard framework must do. Every requirement here is satisfied by the distributed framework or
by the repository that installs it — never by whatever produced the distribution.

A specification binds when its frontmatter says `status: accepted`. A `proposed` one carries no
normative weight.

## The set

| Id | Title | Status | Decides |
|---|---|---|---|
| [0001](0001-knowledge-object-driven-development.md) | The method | **`accepted`** | what a change starts from, what impact establishes, what classification decides, what an authored object records |
| [0002](0002-domain-analysis.md) | Domain analysis | **`accepted`** | the order the analysis follows, what the model records about its certainty, how an element is identified |
| [0003](0003-knowledge-ontology-and-notation.md) | Knowledge ontology and notation | **`accepted`** | where each DDD construct lands, the node types, edges, attribute types, notation, identity, body form, and the derived graph |
| [0004](0004-runtime-architecture.md) | Runtime architecture | **`accepted`** | who executes, how a capability is found, where a guarantee lives |
| [0005](0005-capability-model.md) | The capability model | **`accepted`** | the closed set of capability classes, what each owns, admission and retirement |
| [0006](0006-capability-contracts.md) | Capability contracts | **`accepted`** | what a capability declares about itself |

## This version of the framework

Siegard builds and modifies a knowledge graph from a system context a person supplies, mapping the
impact of every request against what already exists. The path is: the request, a domain model, an impact
analysis, a classification, the knowledge objects, and the graph derived from them.

There is no change request artifact. A request is prose plus the material it names, and `0001` R2 says
so rather than leaving it to be discovered.

Nothing here specifies generation, templates, or distribution. Those documents are removed rather than
kept as obligations over mechanisms that do not exist, and each returns with the capability it governs.

## Rules for this directory

Each document decides one thing and stays inside it. A document may name another document where its own
scope ends; it never cites a requirement of another document, and it never cites code.

Ids are sequential with no gaps. A document's requirements are numbered from R1 with no gaps, no letter
suffixes, and no retired entries kept as placeholders.

A requirement states an obligation and nothing else. Rationale, history, and what a decision cost belong
in a decision record.
