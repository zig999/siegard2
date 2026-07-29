# Siegard Code

Siegard Code builds the Claude Code framework that other repositories install. Its product is a
versioned distribution of Claude Code components assembled under `dist/.claude/`. This repository
does not build a business application.

## Language

Write every artifact in this repository in English (en-US): source, generated distribution, specs,
ADRs, schemas, tests, fixtures, docs, and commit messages. Conversation with a maintainer may use
any language; committed content may not.

## Decision order

When valid options remain, prefer, in order:

1. correctness and safety;
2. explicit, testable contracts;
3. deterministic control flow and validation;
4. traceability and reproducibility.

A later criterion never overrides an earlier one. Criteria deliberately excluded, including human
convenience, are recorded in `docs/adr/0004-ai-first-artifact-contracts.md`.

## Repository layout

| Path | Contains | Role |
|---|---|---|
| `specs/` | accepted specifications | normative source 1 |
| `docs/adr/` | accepted decision records | normative source 2 |
| `schemas/` | machine-readable artifact contracts | normative source 3 |
| `scripts/` | validation, transformation, packaging, state derivation | implementation |
| `templates/` | artifact generators that conform to schemas | implementation |
| `tests/` | contract, transition, validation, and packaging tests | implementation |
| `fixtures/` | downstream-shaped cases that exercise capabilities | evidence |
| `src/claude/` | the Claude Code components the framework ships | framework source |
| `dist/.claude/` | assembled distribution | generated, never hand-edited |
| `.claude/` | rules and skills that govern work in this repository | development environment, never shipped |
| `docs/concepts/` | framework vocabulary, one concept per file | vocabulary authority |
| `docs/` | bootstrap plan, guides | explanatory |

`.claude/` and `src/claude/` are different trees and never mirror each other. `.claude/` configures the
agent that develops Siegard; `src/claude/` holds what Siegard ships. A component that would be
installed into a target repository belongs in `src/claude/` from the moment it is first authored, and
stays inert here until the generator, a fixture, or a test exercises it — never the ambient session.
`docs/adr/0006-separate-development-environment-from-framework-source.md` records the boundary.

Most of these paths do not exist yet. Each one is a commitment: create it when the first artifact
needs it, and do not invent a different location.

## Commands

`make validate` (schemas and contracts), `make test` (framework tests), `make dist` (regenerate
`dist/.claude/` from source), `make check` (all three).

No target exists yet. When the command or validator for an affected area is missing, name the gap and
state that the check did not run. Never substitute an improvised check, and never report a check as
passed unless it executed successfully.

## Normative sources

Precedence for every repository artifact:

1. accepted specifications in `specs/`;
2. accepted ADRs in `docs/adr/` for decisions no specification defines;
3. schemas and contracts in `schemas/` derived from those decisions;
4. implementation and tests;
5. explanatory documentation and examples.

Accepted means `status: accepted` in the artifact's frontmatter; `docs/adr/README.md` defines the
status vocabulary. A `proposed` artifact carries no normative weight and binds nothing.

This file defines how Claude Code works here; it does not replace a specification or an ADR.

## Conflict protocol

When normative sources conflict:

- stop before encoding a new interpretation;
- name the conflicting files and the incompatible statements;
- resolve the highest-level normative source first;
- update dependent artifacts in the same change;
- never silently merge or choose between contradictory rules.

## Authority placement

Keep one authoritative definition per concept. Do not place the same authority in more than one
component.

Prompts may instruct an agent how to apply a rule, but must not become the sole authority for a rule
that can live in a specification, schema, or deterministic validator.

Reuse an existing concept when its semantics remain valid, and use one name for it across specs,
schemas, code, and tests. `docs/concepts/` is the authority for framework vocabulary; add a concept
file there before using a term normatively.

## Determinism and state

- Persist workflow state outside the conversation.
- Treat conversation history and auto memory as non-normative. Verify any claim they make against
  persisted state or source before acting on it.
- Make transition guards deterministic and testable.
- Decide mechanically decidable checks in hooks or scripts. Use agents for work that genuinely
  requires model judgment.
- Record the inputs, outputs, evidence, and contract version needed to reproduce a decision.

Determinism applies to control flow, validation, and recorded state. It does not require a model's
semantic output to be byte-identical across runs.

## Scope

Work here must improve the framework itself. Out of scope: features for a specific business
application, customer business rules, architecture chosen for one downstream system, support for other
agent harnesses, and application code presented as framework functionality.

Every framework capability must be exercised by at least one fixture in `fixtures/` shaped like a
real downstream case. That fixture is the only feedback loop this scope fence leaves open.

Do not generalize speculatively. Introduce an abstraction only when a current requirement needs it
and its reusable contract can be tested. This applies to the framework's own architecture.

## Where the rest lives

Conditional and procedural rules load on demand and are not repeated here:

- `.claude/rules/contracts.md` — inter-agent artifact contracts
- `.claude/rules/compatibility.md` — breaking changes and migration
- `.claude/rules/distribution.md` — generated distribution and packaging
- `.claude/rules/claude-code-authoring.md` — authoring Claude Code components
- `/siegard-change` — procedure for changing a framework artifact
- `/siegard-verify` — procedure for verifying a change before reporting it
- `docs/bootstrap.md` — what to build first, and which rule activates when
