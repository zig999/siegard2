---
id: "0006"
title: Separate the development environment from distributable framework source
status: proposed
contract_version: adr/1
---

# Separate the development environment from distributable framework source

## Context

Before this decision, `.claude/` served two roles a reader could not tell apart. It configures the
Claude Code agent that develops Siegard, and the `CLAUDE.md` layout table also labeled it *framework
source* — the input a generator assembles into `dist/.claude/`. ADR-0002 decides that the distribution
is generated from framework source but never says where that source lives.

The label was already wrong. Every artifact under `.claude/` — four rules and two skills —
governs work in this repository: each references `specs/`, `docs/adr/`, `docs/concepts/`, `dist/`, or
this repository's `make` targets, and none could be installed into a target repository as written.
Nothing has broken because nothing distributable exists yet. It becomes a defect at the first
shippable component:

- a distributable rule or hook authored under `.claude/` takes effect in this repository immediately,
  before any validator has run against it, and its blast radius is the factory that builds it;
- the generator has no positive input contract. `.claude/rules/distribution.md` says which paths to
  exclude from the output and nothing names what to include;
- a maintainer cannot tell from a path whether a component ships.

## Decision

Three trees, each with one role:

| Tree | Role |
|---|---|
| `.claude/` | configuration for the agent that develops Siegard. Never shipped. |
| `src/claude/` | the components Siegard ships. The generator's only component input. |
| `dist/.claude/` | the generated distribution (ADR-0002). |

Stated so it can be violated:

- A component that would be installed into a target repository belongs in `src/claude/` from the
  moment it is first authored, not after it is validated.
- `.claude/` and `src/claude/` never mirror each other. A component present in both is a defect, not
  convenience.
- A path under `src/claude/` determines the component's path in the distribution. The generator's
  mapping is positional, not interpretive.
- A file under `src/claude/` is inert in this repository. Exercising it requires the generator, a
  fixture, or an explicit test — never the ambient session.
- A script that ships as part of a component belongs under `src/claude/`. `scripts/` holds this
  repository's own tooling: validation, transformation, packaging, state derivation. A script both
  sides need is a signal to extract the shippable part, not to reference across the boundary.

## Consequences

- The generator gains a positive input contract naming `src/claude/`, instead of only an exclusion
  list applied to whatever it found.
- Authoring a distributable component loses its fastest feedback loop: the component no longer takes
  effect in the session that wrote it. Dogfooding becomes an explicit act — install the generated
  distribution, or exercise a fixture. Cost accepted: this is the trade ADR-0002 already made on the
  output side, applied to the input side.
- Path-scoped rules must name every tree they govern. All four files in `.claude/rules/` gained
  coverage in the change that recorded this ADR — `contracts.md` scoped to `src/claude/agents/**`, the
  other three to `src/claude/**`. A new rule must decide which trees it scopes to: one scoped only to
  `.claude/**` stays silent while a shippable component is authored.
- Nothing moves. All six artifacts under `.claude/` are factory governance, so this change is a
  relabeling and a declaration, not a migration.
- `src/claude/` is declared and not created, per `CLAUDE.md`: a declared path is a commitment, created
  when the first artifact needs it.

## Validation required before acceptance

This ADR binds nothing until:

1. the first distributable component exists under `src/claude/`, and nothing under `.claude/`
   duplicates it;
2. the generator reads `src/claude/` as its component input, and `make dist` produces
   `dist/.claude/` from it;
3. a test asserts that no path under `.claude/` reaches the distribution;
4. a fixture installs the generated distribution and exercises the component as a downstream-shaped
   case.

Until then, the layout table in `CLAUDE.md` carries the path commitment, as it already does for
`specs/`, `templates/`, `tests/`, and `fixtures/`.
