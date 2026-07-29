# Bootstrap plan

This repository currently contains governance and no implementation. This file records what to build
first and which rules start binding as each piece lands.

## Why sequencing matters here

`CLAUDE.md` forbids speculative generalization: introduce an abstraction only when a current
requirement needs it and its reusable contract can be tested. That rule applies to the framework's own
architecture, which is why the event model, the generated distribution, and the orchestrator/agent
split are recorded as `proposed` ADRs rather than asserted as invariants.

Rules distilled from working code are testable. Rules written ahead of it are guesses that read like
requirements. Build the thin path, then promote the rules it actually needed.

## The thin end-to-end path

One workflow, as small as it can be while still crossing every boundary the framework claims:

```
command  →  orchestrator  →  specialized agent  →  validated artifact  →  event  →  projection
```

Concretely, in order:

1. ~~**A validated artifact and its schema.**~~ **Done.** `schemas/concept.v1.json` with the boundary
   validator `scripts/validate_concepts.py`, wired to `make validate`. The concept bundle in
   `docs/concepts/` is the first artifact class the framework actually enforces rather than describes —
   see `docs/adr/0005-okf-derived-concept-model.md`.
2. **A specialized agent that produces it.** One role, minimum tools, output validated at the boundary
   before anything consumes it.
3. **An orchestrator that consumes it** and chooses a transition from the artifact's closed `state`
   field — a lookup, not an interpretation.
4. **One appended event** recording what happened, and **one projection** deriving current state by
   replaying events.
5. **A command** that starts and resumes the workflow, doing nothing but validating input and
   delegating.
6. **`make validate`, `make test`** over the above, and a fixture in `fixtures/` shaped like a real
   downstream case.
7. **The generator and `make dist`**, once there is enough source to assemble.

## Which rule activates when

Several rules in this repository still describe components that do not exist. Each becomes enforceable
at a specific point:

| Rule | Activates when | State |
|---|---|---|
| concept frontmatter contract (`schemas/concept.v1.json`) | the validator runs in `make validate` | **active** |
| `make validate` in `/siegard-verify` step 1 | a `Makefile` target exists | **active**, concepts only |
| `make test` in `/siegard-verify` step 1 | a framework test suite exists | pending |
| "do not hand-edit generated artifacts" (`rules/distribution.md`) | a generator and `make dist` exist | pending |
| "no source-only paths in the distribution" | `dist/` is generator-produced | pending |
| every capability needs a fixture (`CLAUDE.md` scope) | `fixtures/` holds its first case | pending |
| migration tests (`rules/compatibility.md`) | a second contract version exists | pending |
| ADR-0001, ADR-0002, ADR-0003 | their **Validation required** sections are satisfied | pending |

`make validate` is active but narrow: it validates the concept bundle and nothing else. Do not read a
green `make validate` as coverage of a change that did not touch `docs/concepts/`.

Until a row's condition holds, the rule is a commitment, not a check. Report it as not run rather than
as satisfied.

## Enforcement is not in this file, or in CLAUDE.md

Claude Code treats `CLAUDE.md` and `.claude/rules/` as context, not as enforced configuration. The
agent may not follow them. Anything that must hold regardless of model judgment belongs in a
`PreToolUse` hook or a deterministic script.

This is the same argument the framework makes internally — a rule that can live in a validator should
not live only in a prompt — applied to the framework's own governance. Candidates, once the thin path
exists:

- a `PreToolUse` hook rejecting writes under `dist/` that did not come from the generator;
- a boundary validator rejecting any inter-agent artifact that fails its schema;
- a hook rejecting a schema change that does not bump `contract_version`.

Treat these as the point where governance becomes real. Until then, the rules in this repository
depend on cooperation.

## In place

- **Version control.** Git, on `main`, with `origin` at `git@github.com:zig999/siegard2.git`.
  Traceability, reproducible generation from committed source, and migration history all presuppose
  it. Nothing has been pushed yet.

## Not yet in place

- No `specs/`, `templates/`, `tests/`, or `fixtures/`.
- `schemas/` and `scripts/` hold only the concept contract and its validator.
- No framework test suite, so `make test` fails by design rather than passing vacuously.
- No generator, therefore no authoritative `dist/`.
