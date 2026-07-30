---
id: "0009"
title: Derive component contracts from Anthropic's documented constraints
status: proposed
contract_version: adr/2
---

# Derive component contracts from Anthropic's documented constraints

## Context

The first distributable component is about to be authored, and nothing checks that a component
under `src/claude/` is something Claude Code can actually load. The harness itself does not fill
that gap — its documented failure modes are silent:

- a SKILL.md with malformed frontmatter loads with empty metadata, so the skill keeps working
  when typed but Claude loses the description it matches against;
- an unknown frontmatter field is ignored, so a typo like `tool:` for `tools:` ships an agent
  that silently inherits every tool;
- two agents with the same name load by filesystem read order, with no documented precedence.

The constraints that prevent this live in Anthropic's documentation, which is external and
versioned. Encoding it from a model's memory is forbidden by `.claude/rules/claude-code-authoring.md`
("cite the documentation page that specifies it"); encoding it once and never re-checking it decays
at the documentation's release cadence.

Research against the live pages (retrieved 2026-07-29) also settled a structural question: custom
slash commands were merged into skills — `.claude/commands/deploy.md` and
`.claude/skills/deploy/SKILL.md` both create `/deploy`. A framework born now has no reason to ship
the legacy form.

## Decision

Two component classes, two contracts, one validator:

- `schemas/skill.v1.json` for `src/claude/skills/<name>/SKILL.md`;
- `schemas/agent.v1.json` for `src/claude/agents/**/*.md`;
- `scripts/validate_components.py` at the boundary, wired into `make validate`.

**There is no command class.** A user-invocable procedure is a skill; `/name` remains the
interface. The validator rejects `src/claude/commands/` by name, and rejects any other component
class until a contract for it exists.

Three sourcing rules govern the contracts' content:

1. A constraint enters a contract only from Anthropic documentation, with the page URL and
   retrieval date cited in the schema, or as a named Siegard addition justified by an accepted
   Siegard rule. Community material may inform judgment; it never binds.
2. Where Siegard is stricter than the harness, the divergence is deliberate, listed below, and
   marked in the schema field it constrains.
3. When the documentation changes, the contract changes as a version bump under
   `.claude/rules/compatibility.md`, never as an in-place edit — existing components become
   detectably outdated instead of silently non-conforming.

### Siegard divergences from harness behavior

| Divergence | Harness behavior | Why Siegard diverges |
|---|---|---|
| agent `tools` required | optional; omitted inherits every tool | `CLAUDE.md` Security: the absence of a statement is not a grant |
| agent `permissionMode` excludes `bypassPermissions` | documented mode | a shipped component must not skip every prompt in a repository Siegard does not control |
| skill `name`, `description` required | `name` is display-only, `description` recommended | an undiscoverable skill is the documented failure mode of malformed frontmatter; Siegard refuses to ship it deliberately |
| skill `name` = directory name; agent filename = `name` | mismatch permitted | the directory or `name` field is the real identity; a file that disagrees with it breaks traceability |
| SKILL.md body ≤ 500 lines is a failure | documented as guidance | a guidance line that nothing checks is prose; the decision order puts contracts above convenience |
| `additionalProperties: false` | unknown fields silently ignored | the silent-typo failure mode above |

### Sources

Normative for these contracts, all retrieved 2026-07-29:

- https://code.claude.com/docs/en/skills — skill field inventory and semantics; the
  commands-into-skills merge; malformed-frontmatter behavior.
- https://code.claude.com/docs/en/sub-agents — agent field inventory, requiredness, enums,
  name-collision behavior.
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices — hard limits
  on skill `name` (64 chars, lowercase/digits/hyphens, no reserved words) and `description`
  (non-empty, 1,024 chars); the 500-line guidance.

A constraint not present in these pages on that date is not in the contracts. Re-verify the pages
before any contract version bump, and record the new retrieval date.

### Judgment practices, recorded but not yet rules

The same research yielded practices no schema can decide: descriptions in third person stating
what and when, with the key use case first; gerund or noun-phrase names, never `helper`/`utils`;
concise bodies that assume model competence; progressive disclosure with references one level
deep; degrees of freedom matched to task fragility; consistent terminology; no time-sensitive
content; evaluations before extensive documentation.

These are context, deliberately not encoded anywhere normative yet: rules distilled from working
components are testable, rules written ahead of them are guesses (`docs/bootstrap.md`). Promote
them into `.claude/rules/claude-code-authoring.md` when the first components exercise them.

## Consequences

- The first agent and skill are authored against a checked contract instead of against memory of
  the documentation.
- `additionalProperties: false` means a new harness field is a contract version bump, not a quiet
  addition. Cost accepted: that is the compatibility mechanism working as designed, and the
  alternative readmits the silent-typo failure mode.
- The contracts encode a snapshot. The retrieval date is recorded so staleness is a checkable
  fact rather than a suspicion; nothing yet forces re-verification, and that gap stays open until
  a mechanism needs it.
- Any later decision about component classes must reflect the commands-into-skills merge recorded
  here, rather than reintroducing a command class the harness no longer has.
- Two enforcement gaps are deliberate: the validator checks structure, not that a component works
  (fixtures and evals own that), and nothing verifies `src/claude/` against the live documentation
  continuously (re-verification happens at contract bumps).

## Validation required before acceptance

1. The first skill and the first agent under `src/claude/` pass `scripts/validate_components.py`,
   and at least one deliberately malformed component is shown to fail it.
2. A generated distribution installs those components into a downstream-shaped fixture and Claude
   Code loads them — the contract's claim is loadability, and only loading tests it.
3. The judgment practices above are promoted to, or deliberately dropped from,
   `.claude/rules/claude-code-authoring.md` based on that first authoring experience.
