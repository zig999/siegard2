# Siegard specifications

What the Siegard framework must do. Every requirement here is satisfied by the distributed framework or
by the repository that installs it — never by whatever produced the distribution. A specification binds
when its frontmatter says `status: accepted`; a `proposed` one carries no normative weight.

Two families sit here, at the same precedence level and in one flat directory.

**The method** — what a repository Siegard governs does.

**The framework** — what the Siegard product is, and how it is built. These specify the software that
implements the method. They do not amend the method, and where one needs a method decision changed, that
change belongs in the method specification rather than here.

Ids are allocated sequentially across both families, and the tables below are the authority for which
family a document belongs to. An earlier version of this file claimed the id range separated the two at no
cost; `0014` falsified that within a day of the framework family being written, by being a method
specification numbered after them. A number records when a document was written, not what it governs.

The directory is flat on purpose. Splitting it into `foundations/` and `framework/` was considered and
rejected: 33 concept `sources` resolve to these paths, a validator globbing `specs/*.md` would silently
ignore a subdirectory, and renaming a public artifact is breaking under `specs/0013` R3a.

## The method

| Id | Title | Status | Decides |
|---|---|---|---|
| [0001](0001-knowledge-object-driven-development.md) | Knowledge-object-driven development | **`accepted`** | the workflow's phases and transitions, context resolution, what acceptance requires of a decision and its evidence, the maturity ladder |
| [0002](0002-knowledge-economy-principles.md) | Knowledge economy principles | **`accepted`** | what may be recorded as permanent knowledge, and the boundary between domain and stack fact |
| [0003](0003-knowledge-ontology-and-notation.md) | Knowledge ontology and notation | **`accepted`** | the node types, edges, notation, and attribute type system |
| [0004](0004-generation-and-reproducibility.md) | Generation and reproducibility | **`accepted`** | the calibrated reproducibility promise, artifact classes, generation tracks, the derived artifacts |
| [0014](0014-acceptance-closure-and-escalation.md) | Acceptance closure and escalation | **`accepted`** | how the acceptance closure is computed, what the gate reports, how escalation is decided |

## The framework

A specification binds when its frontmatter says `status: accepted`. Where one was accepted ahead of the
evidence it asked for, that evidence is listed under its **Outstanding evidence** section and is owed. A
change to a requirement is a breaking change under `specs/0013` R3a rather than a revision.

**No framework specification is accepted before the method specification it depends on.** Every one of the
nine rests on `specs/0001` or `specs/0004`; accepting a framework document while its foundation binds
nothing would give it an authority its own basis does not have. The rule held through the promotion of
2026-07-31: `specs/0001` was already accepted, and `specs/0004` was accepted in the same decision, so no
framework document ended up resting on a foundation that binds nothing. What the rule does not reach is the
question that decision left open — whether either foundation had earned its own acceptance.

That rule is checked rather than trusted, as of 2026-07-31. `scripts/validate_specs.py` derives the
prerequisite graph from the acceptance conditions each document already writes — no frontmatter field was
added, because a declared dependency and a stated one would be two authorities for the same relation — and
it reports an unresolved reference, a prerequisite marked met while its target is not accepted, an accepted
document still carrying an unmet prerequisite, and a cycle. What it cannot see is stated in that script's
docstring: an accepted document replaces its acceptance section with what satisfied it, so the check works
on the proposed side and on the moment of promotion, not retrospectively.

| Id | Title | Decides | Inherits, and must not restate |
|---|---|---|---|
| [0005](0005-runtime-architecture.md) | Runtime architecture | who executes, what the framework provides, what it may never control, where determinism lives | — |
| 0006 | Capability model | which capability classes exist, what each owns, how one is admitted and retired | `docs/concepts/capability.md` |
| 0007 | Capability contracts | how a capability declares itself: identifier, inputs, outputs, consumed and produced artifacts, assertions, what is deterministic and what is judgment | `specs/0005` R16a; `schemas/skill.json`, `schemas/agent.json` |
| 0008 | Distribution layout | that the distribution is a plugin, a function of source; the closed directory set; the two records; install, upgrade, and shadowing | — |
| 0009 | Context assembly | the context package contract — its manifest form, budget, and stop criteria | `specs/0001` R11–R15, which already fix that resolution never blocks and never invents |
| 0010 | Hook system | the constraints a hook honors: handler type, exit-code discipline, failing closed, and what a hook cannot guarantee | `specs/0005` R20–R22; the harness hook documentation |
| 0011 | Template system | what a template is, what it may read, how it refers to knowledge, and ownership, override, and versioning | `specs/0004`'s generation tracks and artifact classes |
| 0012 | Target pack model | how a technology stack enters the framework as a unit: one active pack, its composition, its own version, and its retirement | `specs/0004`; `specs/0005` R12 and R13 |
| 0013 | Framework lifecycle | versioning, what makes a change breaking, deprecation, and the migration a consumer is owed | — |

Three documents the original plan proposed are deliberately absent:

- **a command system.** Custom commands were merged into skills; a user-invocable
  procedure is a skill, and `scripts/validate_components.py` rejects `src/claude/commands/` by name.
- **a worker model.** A unit of work with one role is a [specialized agent](../docs/concepts/specialized-agent.md).
  `worker` is vocabulary from the v0.1 draft, which was normative nowhere and this repository no longer
  carries.
- **a projection or schema capability.** A [projection](../docs/concepts/projection.md) is an artifact
  generated from the knowledge graph, and a schema is an artifact contract. That distinction exists because
  `projection` once named two different things.

## Order of construction

The family is not written all at once, and not in id order. The producing repository holds the sequence, and
the gate that settles each open question; a specification here is written when the evidence its
acceptance requires is within reach, so that it records a design rather than guesses one. The agenda that
maps each document to its gate is in that file under **The framework-architecture agenda**.

Acceptance running ahead of that sequence, as it did on 2026-07-31, does not close the gates. Each remains
open, listed in every promoted document's **What satisfied acceptance** section, and the sequence is still
what has to be built. What changed is the cost of being wrong: a design these documents got wrong now costs
a migration to correct rather than an edit.
