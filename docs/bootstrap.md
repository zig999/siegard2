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
command  →  orchestrator  →  specialized agent  →  validated artifact  →  event  →  workflow state
```

Concretely, in order:

1. ~~**A validated artifact and its schema.**~~ **Done.** `schemas/concept.v1.json` with the boundary
   validator `scripts/validate_concepts.py`, wired to `make validate`. The concept bundle in
   `docs/concepts/` is the first artifact class the framework actually enforces rather than describes —
   see `docs/adr/0005-okf-derived-concept-model.md`.
2. **A specialized agent that produces it.** One role, minimum tools, output validated at the boundary
   before anything consumes it. Decide its tree before writing it: a component installed downstream
   goes under `src/claude/agents/`, one that only serves this repository under `.claude/agents/`
   (`CLAUDE.md` **Repository layout**). This is the first component that has to answer that question,
   and answering it is what makes the boundary real rather than declared.

   **Authored.** `src/claude/agents/concept-author.md` — distributable, since the knowledge layer is
   a framework capability — with its result contract in `schemas/concept-authoring-result.v1.json`.
   Authored is not done: the agent is inert here by that same rule, so "output validated at the boundary"
   is only proven when steps 3–6 run it against a fixture. Its tool grant deliberately excludes the
   shell — the boundary validator is the consumer's check, not the producer's self-report.
3. **An orchestrator that consumes it** and chooses a transition from the artifact's closed `state`
   field — a lookup, not an interpretation.
4. **One appended event** recording what happened, and **one derivation of workflow state** reading those
   events back.
5. **A user-invocable skill** that starts and resumes the workflow, doing nothing but validating
   input and delegating. Claude Code merged custom commands into skills, so this entry point is a
   skill with `disable-model-invocation` set — see ADR-0009.
6. **`make validate`, `make test`** over the above, and a fixture in `fixtures/` shaped like a real
   downstream case.
7. **The generator and `make dist`**, once `src/claude/` holds enough to assemble.

## Sequencing

Five stages. Each one names what it would falsify, because a stage that cannot fail teaches nothing.

1. **A design authority, no framework code.** Spec 0001, the retirement of the v0.1 draft, the concepts
   the spec uses normatively, and the specification contract that makes any of it checkable. Falsifies
   nothing by itself — it is the baseline against which the later stages become falsifiable. **Done**,
   pending one maintainer decision: the status of spec 0001.
2. **The first workflow loop, over knowledge only.** `request → impact analysis → knowledge authoring →
   validation → acceptance`, with no generated code and no context resolution: in a five-object bundle
   the impact set *is* the context. This is steps 3–6 above, plus the minimal generator, because a
   fixture cannot install components by hand. This is the stage that settles the **open architectural
   questions** below, and ADR-0009 condition 2.
   Abandonment criterion: if the orchestrator needs to interpret prose to choose a transition, the
   artifact design is wrong — fix the schemas, not the prompt. This stage carries the risk of the whole
   plan.
3. **Graph and context resolution.** Only once the bundle is large enough for selection to matter, with
   the reproducibility test and the instrumentation — selection recall, tokens per change — that decides
   whether resolution pays for itself. Falsifies the determinism claim, which becomes a test rather than
   an adjective. Abandonment criterion: if recall is indistinguishable from sending the whole bundle,
   simplify to inclusion by tag or domain.
4. **The code side.** Specification delta, implementation, layered validation and evidence, the
   independent validation closure, and the acceptance gate that reports each knowledge object's mode.
   Falsifies fail-soft and the normative inversion in its first concrete case.
5. **Escalation thresholds, assertion promotion, and knowledge derived from code.** Last, because every
   item needs history the earlier stages produce. R10 forbids inventing the thresholds before then.

Measure in stage 3, not stage 5: selection recall and tokens per change are the only evidence that the
economic premise holds, and finding it false is worth far more early than late.

## Which rule activates when

Several rules in this repository still describe components that do not exist. Each becomes enforceable
at a specific point:

| Rule | Activates when | State |
|---|---|---|
| specification contract (`schemas/spec.v1.json`), frontmatter and body structure | the validator runs in `make validate` | **active**, exercised by every specification in `specs/` |
| concept frontmatter contract (`schemas/concept.v1.json`) | the validator runs in `make validate` | **active** |
| ADR frontmatter contract (`schemas/adr.v2.json`), including supersession and amendment | the validator runs in `make validate` | **active**; `amends` exercised for the first time by ADR-0008 over ADR-0004 |
| non-restatement: an ADR's `## Decision` cites an operative rule instead of repeating it (`docs/adr/README.md`) | the check runs in `make validate` | **active**, six ADRs de-duplicated to satisfy it |
| migration test for a contract bump (`.claude/rules/compatibility.md`) | a test suite exists | **owed**: `adr/1` → `adr/2` happened without one |
| component contracts (`schemas/skill.v1.json`, `schemas/agent.v1.json`) | the validator runs in `make validate` | **active**, exercised by `concept-author` |
| result contract (`schemas/concept-authoring-result.v1.json`) validated at the boundary | the thin-path orchestrator or a test consumes the agent's result | pending |
| knowledge-object contract (`schemas/knowledge-object.v1.json`), per-type conditionals and the attribute type system | the validator runs in `make validate` (spec 0003 R37) | **active**, exercised by `fixtures/knowledge-two-context/` |
| materialized graph contract (`schemas/knowledge-graph.v1.json`) | the materializer emits `graph.json` | **active** |
| the checks spec 0003 defers to a script — R11, R15, R18, R20, R22, R28, R29, R38, R43–R48 | `scripts/validate_knowledge.py` runs in `make validate` | **active**, both outcomes tested per check |
| projections are derived and never hand-edited (R42, R51) | `project_knowledge.py --check` runs in `make validate` | **active** |
| ontology utilization measured (R52) | `measure_ontology.py --check` runs in `make validate` | **active**, three removal candidates found |
| `make validate` in `/siegard-verify` step 1 | a `Makefile` target exists | **active**, five artifact classes plus two derived-tree checks |
| `make test` in `/siegard-verify` step 1 | a framework test suite exists | **active**, 59 tests over the knowledge layer |
| `make dist-check` in `make check` | a generator and a committed `dist/` exist | pending |
| security invariants (`CLAUDE.md` **Security**) | stated; enforcement waits for the first hook | **partly active** |
| `src/claude/` holds every shippable component (`CLAUDE.md` layout) | the first distributable component is authored | pending |
| "do not hand-edit generated artifacts" (`rules/distribution.md`) | a generator and `make dist` exist | pending |
| "no source-only paths in the distribution" | `dist/` is generator-produced | pending |
| every capability needs a fixture (`CLAUDE.md` scope) | `fixtures/` holds its first case | **active** for the knowledge layer; pending for every other capability |
| migration tests (`rules/compatibility.md`) | a second contract version exists | pending |

`make validate` is active but narrow: it validates specifications, ADRs, the concept bundle, and
distributable components — frontmatter, cross-file identity, and required structure. It executes nothing
and loads nothing into Claude Code. Do not read a green `make validate` as coverage of a change that did
not touch `specs/`, `docs/adr/`, `docs/concepts/`, or `src/claude/`, and do not read it as evidence that
a component works.

Until a row's condition holds, the rule is a commitment, not a check. Report it as not run rather than
as satisfied.

## Open architectural questions

`CLAUDE.md` states what must hold; it does not choose these designs, and neither does anything else yet.
Each question below carries the gate that would settle it. Until a gate is met, the design named is a
candidate, not a decision — do not build on it as if it were fixed, and do not record it as one.

These gates were the acceptance conditions of ADRs that recorded candidate designs for components that
do not exist. Five such ADRs were removed once their operative rules were held by `CLAUDE.md` alone; the
gates outlived them, because a gate is a test and a candidate design is not.

Two were restored rather than removed, on 2026-07-30. ADR-0004 and ADR-0008 carry the reasoning behind the
**Decision order** — why human convenience is excluded from the ranking, and why a second tier of
tiebreakers beneath the constraints does not weaken them. `docs/adr/README.md` states that an ADR's
rationale "has no other home", so removing those two destroyed content nothing replaced, which is a
different case from removing a record that only duplicated a rule.

1. **Which persistence model records workflow state.** `CLAUDE.md` **Determinism and state** requires it
   persisted outside the conversation and transitions reconstructible from records alone. The leading
   candidate is an append-only event log with state derived by replay. Gate: one event schema in
   `schemas/` carrying `contract_version`; one workflow-state derivation with a test asserting replay is
   deterministic; one transition guard with a test for both outcomes; a fixture exercising the loop end to
   end. If a mutable record turns out to be sufficient for the workflows the framework actually runs, take
   it — the event model costs a migration burden on every schema change, and nothing has yet earned it.
2. **How the distribution is produced.** That `dist/.claude/` is generated, reproducible, and never
   hand-edited is settled by `CLAUDE.md` **Repository layout** and `.claude/rules/distribution.md`. What
   is open is the generator. Gate: a generator in `scripts/` that `make dist` runs; running it twice from
   the same source produces identical output; a test asserting no source-only path (`specs/`, `tests/`,
   `fixtures/`, `docs/`, `.claude/`) reaches the output; a test asserting no secret or
   environment-specific value does. Until then, do not create `dist/` by hand to make a rule look
   satisfied.
3. **Which component classes exist and what each owns.** `CLAUDE.md` **Authority placement** requires one
   authoritative definition per concept, which constrains any division of work without choosing one.
   There is no command class — ADR-0009 records the commands-into-skills merge. Gate: one entry point,
   one orchestrator, and one specialized agent completing a workflow together; the orchestrator choosing
   its transition from a validated artifact's closed `state` field with no interpretation of prose; the
   specialized agent's tool grant demonstrably the minimum its role requires; a fixture exercising the
   path end to end. If a class turns out to be ceremony for the workflows the framework actually runs,
   drop it rather than populate it.
4. **That the source and development trees stay separate in practice.** The boundary is stated in
   **The two trees** in `.claude/rules/claude-code-authoring.md`, which loads whenever either tree is
   read, and the first distributable component now sits under `src/claude/`.
   Gate: the generator reads `src/claude/` as its component input; a test asserts that no path under
   `.claude/` reaches the distribution; a fixture installs the generated distribution and exercises the
   component as a downstream-shaped case.
5. **How a security guarantee gets enforced.** The invariants are stated in `CLAUDE.md` **Security** and
   bind now. What is missing is enforcement. Gate: the first hook or script exercising "validate before
   acting" and "reject rather than repair" under test — which is also what turns the deferred
   `.claude/rules/security.md` from a plan into a rule distilled from working code.

## Enforcement is not in this file, or in CLAUDE.md

Claude Code treats `CLAUDE.md` and `.claude/rules/` as context, not as enforced configuration. The
agent may not follow them. Anything that must hold regardless of model judgment belongs in a
`PreToolUse` hook or a deterministic script.

This is the same argument the framework makes internally — a rule that can live in a validator should
not live only in a prompt — applied to the framework's own governance. Candidates, once the thin path
exists:

- a `PreToolUse` hook rejecting writes under `dist/` that did not come from the generator;
- a boundary validator rejecting any inter-agent artifact that fails its schema;
- a hook rejecting a schema change that does not bump `contract_version`;
- a `PreToolUse` hook rejecting any write to `CLAUDE.md`, which the **Golden rule** in that file states
  and cannot itself enforce. It is the sharpest case in this list: the rule restricting the agent lives
  in the file the agent would have to edit to remove it.

Treat these as the point where governance becomes real. Until then, the rules in this repository
depend on cooperation.

## In place

- **Version control.** Git, on `main`, with `origin` at `git@github.com:zig999/siegard2.git`.
  Traceability, reproducible generation from committed source, and migration history all presuppose it.
- **Five enforced artifact contracts.** Specifications (`schemas/spec.v1.json`), concepts
  (`schemas/concept.v1.json`), ADRs (`schemas/adr.v2.json`, with `adr.v1.json` kept readable), and
  distributable components
  (`schemas/skill.v1.json`, `schemas/agent.v1.json`), each with a boundary validator in `scripts/`, all
  wired to `make validate`. These are the only rules in this repository that are checked rather than
  trusted. The component contracts were authored before the first component, deliberately, so it was born
  against them (ADR-0009); the specification contract was authored in the same change as the first
  specification, for the same reason.
- **A design authority.** `specs/0001-knowledge-object-driven-development.md`, `proposed`, is the first
  occupant of normative source 1. It fixes the workflow, the escalation predicates, the calibrated
  fail-soft claim, and the maturity ladder that decides when a knowledge object gains mechanical force.
  Its **Provenance** section records what the SIGARD v0.1 draft under `reference/` contributed and what
  forced a rewrite; that draft is non-normative input at every precedence level.
- **The first distributable component.** `src/claude/agents/concept-author.md`, with its result
  contract in `schemas/concept-authoring-result.v1.json`. It is a component under `src/claude/` that
  nothing under `.claude/` duplicates, and it exercises the component contract for the first time. The
  rest of open question 4 above — generator input, exclusion test, fixture — remains open.

## Not yet in place

- No `templates/`. `tests/` and `fixtures/` now exist, but only for the knowledge layer: no fixture
  exercises the workflow of spec 0001, the generation pipeline of spec 0004, or the distribution.
- `specs/0002` and `specs/0003` are `accepted`; `0001` and `0004` are `proposed`. Normative source 1 now
  binds for the knowledge layer and binds nothing for the workflow or the generation pipeline.
  Spec 0003 was accepted on 2026-07-30 after every condition it set was met by a component that
  exercises it — see `fixtures/knowledge-two-context/README.md` for the evidence, and that
  specification's **What satisfied acceptance** for the six defects building the evidence exposed and
  repaired before acceptance rather than after. Four findings remain open there; none is a
  contradiction. From here `.claude/rules/compatibility.md` governs changes to spec 0003, so a repair
  that invalidates a conforming knowledge object is a breaking change rather than a revision.
- `make test` runs 59 tests, all over the knowledge layer. The validators for specifications, ADRs,
  concepts, and components remain untested code enforcing tested contracts; only
  `validate_knowledge.py`, `knowledge_graph_lib.py`, `project_knowledge.py`, and
  `measure_ontology.py` are covered. Do not read a green `make test` as coverage of the other four.
- No `.claude/rules/security.md`. `CLAUDE.md` **Security** states the invariants; sanitization, path,
  subprocess, and network detail wait until the first hook or script needs them — see open question 5.
- No generator, therefore no authoritative `dist/`. `src/claude/` now holds the generator's first
  input, and until steps 3–6 exist, `concept-author` is authored-but-unexercised: no orchestrator
  consumes its result, no test validates the result contract at the boundary, and no fixture runs it.
