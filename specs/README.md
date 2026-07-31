# Siegard specifications

Normative source 1. `CLAUDE.md` under **Normative sources** fixes the precedence and the status
vocabulary: a specification binds only when its frontmatter says `status: accepted`, and a `proposed`
one carries no normative weight.

Two families sit here, at the same precedence level and in one flat directory.

**The method** — what a repository Siegard governs does. Ids `0001`–`0004`.

**The framework** — what the Siegard product is, and how it is built. Ids `0005` and above. These
specify the software that implements the method. They do not amend the method, and where one needs a
method decision changed, that change belongs in the method specification rather than here.

The directory is flat on purpose. Splitting it into `foundations/` and `framework/` was considered and
rejected: 33 concept `sources` resolve to these paths under a constraint ADR-0010 made enforced,
`scripts/validate_specs.py` globs `specs/*.md` and would silently ignore a subdirectory, and renaming a
public artifact is breaking under `.claude/rules/compatibility.md`. An id range separates the families at
no cost.

## The method

| Id | Title | Status | Decides |
|---|---|---|---|
| [0001](0001-knowledge-object-driven-development.md) | Knowledge-object-driven development | `proposed` | the workflow every change request follows, escalation, fail-soft, acceptance, the maturity ladder |
| [0002](0002-knowledge-economy-principles.md) | Knowledge economy principles | **`accepted`** | what may be recorded as permanent knowledge, and the boundary between domain and stack fact |
| [0003](0003-knowledge-ontology-and-notation.md) | Knowledge ontology and notation | **`accepted`** | the node types, edges, notation, and attribute type system |
| [0004](0004-generation-and-reproducibility.md) | Generation and reproducibility | `proposed` | the calibrated reproducibility promise, artifact classes, generation tracks, the derived artifacts |

## The framework

Every entry is `proposed` until the evidence its own **Validation required before acceptance** section
names exists. Writing them is ordinary work and binds nothing; accepting one is a maintainer's decision.

| Id | Title | Decides | Inherits, and must not restate |
|---|---|---|---|
| [0005](0005-runtime-architecture.md) | Runtime architecture | who executes, what the framework provides, what it may never control, where determinism lives | `CLAUDE.md` **Scope** and **Determinism and state**; `.claude/rules/claude-code-authoring.md` |
| 0006 | Capability model | which capability classes exist, what each owns, how one is admitted and retired | `docs/concepts/capability.md`; ADR-0009's component classes |
| 0007 | Capability contracts | how a capability declares itself: identifier, inputs, outputs, consumed and produced artifacts, assertions, what is deterministic and what is judgment | `.claude/rules/contracts.md`; `schemas/skill.v1.json`, `schemas/agent.v1.json` |
| 0008 | Distribution layout | what `dist/.claude/` contains, the rule per directory, and what may never appear | `CLAUDE.md` **Repository layout**; `.claude/rules/distribution.md` |
| 0009 | Context assembly | the context package contract — its manifest form, budget, and stop criteria | `specs/0001` R11–R15, which already fix that resolution never blocks and never invents |
| 0010 | Hook system | which lifecycle events the framework binds, and the contract a hook honors | `CLAUDE.md` **Security**; the harness hook documentation |
| 0011 | Template system | what a template is, its schema binding, placeholders, and extension points | `specs/0004`'s generation tracks and artifact classes |
| 0012 | Target pack model | how a technology stack enters the framework, and what a pack may declare | `specs/0004`; `.claude/rules/claude-code-authoring.md` **Target packs** |
| 0013 | Framework lifecycle | versioning, deprecation, and the migration a consumer is owed | `.claude/rules/compatibility.md` |

Three documents the original plan proposed are deliberately absent:

- **a command system.** ADR-0009 records that custom commands were merged into skills; a user-invocable
  procedure is a skill, and `scripts/validate_components.py` rejects `src/claude/commands/` by name.
- **a worker model.** A unit of work with one role is a [specialized agent](../docs/concepts/specialized-agent.md).
  `worker` survives only in `reference/`, which is normative nowhere.
- **a projection or schema capability.** A [projection](../docs/concepts/projection.md) is an artifact
  generated from the knowledge graph, and a schema is an artifact contract. ADR-0010 exists because
  `projection` once named two different things.

## Order of construction

The family is not written all at once, and not in id order. `docs/bootstrap.md` holds the sequence and
the gate that settles each open question; a specification here is written when the evidence its
acceptance requires is within reach, so that it records a design rather than guesses one. The agenda that
maps each document to its gate is in that file under **The framework-architecture agenda**.
