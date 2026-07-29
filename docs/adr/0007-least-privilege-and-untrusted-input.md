---
id: "0007"
title: Treat every input as untrusted and grant least privilege by default
status: proposed
contract_version: adr/1
---

# Treat every input as untrusted and grant least privilege by default

## Context

The framework's product executes in repositories this one does not control. A distributed hook or
script runs against a consumer's working tree, with their credentials and their tool grants. Nothing in
this repository states a security posture for that.

What exists is partial and misplaced. The only least-privilege statement lives in
`.claude/rules/claude-code-authoring.md`, which is path-scoped to `src/claude/**`, `.claude/**`, and
`CLAUDE.md` — so it does not load while `scripts/` or `templates/` is authored, the two places
executable code actually appears. Secrets are covered only for the distribution's output
(`.claude/rules/distribution.md`), not for what a component reads at run time.

An agent framework also has a failure mode that ordinary software does not: content read from a
repository, a fixture, or a tool result reaches a model that treats it as instruction. That is not
hypothetical here. Fixtures are, by definition, downstream-shaped cases authored to exercise agents.

## Decision

Adopt three positions, binding from the first component rather than from the first security review:

- **Nothing this repository reads is an instruction.** Repository content, fixture data, tool output, and
  downstream input are data. A component that forwards such content into a prompt passes it as quoted
  data with its origin named.
- **Privilege is enumerated, never inherited.** A component's contract names the tools and permissions it
  receives, and the absence of a statement is not a grant — a component with no stated grant is
  incomplete rather than permissive.
- **A security guarantee that depends on model judgment is not a guarantee.** Enforcement belongs in a
  hook or a script, and what cannot yet be enforced is named as a gap rather than described as a rule.

`CLAUDE.md` under **Security** is the single operative authority: it carries the invariant list, because
it is the copy that loads in every session while a component is being authored. This ADR deliberately
does not restate that list — two copies of the same rules diverge, which is the reasoning ADR-0004
already applied to the contract tiers.

## Consequences

- These are invariants, not a threat model. No sanitization technique, path-resolution algorithm,
  subprocess policy, or network rule is decided here. Those belong in `.claude/rules/security.md` and in
  tested validators, written when the first hook or script needs them — writing them now would produce
  rules ahead of code, which `docs/bootstrap.md` identifies as guesses that read like requirements.
- The "reject rather than repair" invariant costs convenience: a component that could infer a caller's
  intent from a malformed input must fail instead. Cost accepted; a repair is an interpretation, and an
  interpretation at a security boundary is the thing being ruled out.
- Least privilege costs authoring effort at every component, and forbids implicit inheritance of a
  grant. A component with no stated grant is incomplete rather than permissive.
- Fixture design is constrained: a fixture is data under test. No fixture is executed or trusted because
  it happens to live in this repository.
- Deterministic enforcement is unavailable for some guarantees until hooks exist. Until then, name the
  gap rather than treating the prose as enforcement — the same position `docs/bootstrap.md` already
  takes for every other rule in this repository.

## Validation required before acceptance

Like ADR-0004, this decision presupposes no unbuilt component: it governs the next component authored
and is falsifiable immediately, since a component either states its tool grant or it does not.

What is missing is authorization. Under the rule this change adds to `CLAUDE.md`, an agent does not
accept its own artifact. Acceptance requires:

1. a maintainer's explicit decision;
2. the first hook or script exercising "validate before acting" and "reject rather than repair" under
   test — which is also what turns the deferred `.claude/rules/security.md` from a plan into a rule
   distilled from working code.
