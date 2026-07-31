# Bootstrap plan

This repository holds governance, the knowledge layer, the thin workflow path, and — since 2026-07-31 —
a generator and a committed distribution. This file records what to build next and which rules start
binding as each piece lands.

## Why sequencing matters here

`CLAUDE.md` forbids speculative generalization: introduce an abstraction only when a current
requirement needs it and its reusable contract can be tested. That rule applies to the framework's own
architecture, which is why the event model, the generated distribution, and the orchestrator/agent
split were held as `proposed` records rather than asserted as invariants.

Rules distilled from working code are testable. Rules written ahead of it are guesses that read like
requirements. Build the thin path, then promote the rules it actually needed.

On 2026-07-31 a maintainer promoted every remaining `proposed` artifact — eleven specifications, three
ADRs, nineteen concepts — in one decision, ahead of the sequence below. This file's job does not change
because of that. A status says which text is authoritative; it does not say which mechanism exists, and
almost none of the mechanisms below do. What the promotion did change is the cost of correcting a design
that turns out to be wrong: `.claude/rules/compatibility.md` now governs each of those documents, so the
correction is a breaking change with a migration path and a migration test.

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
3. ~~**An orchestrator that consumes it**~~ **Done.** `scripts/orchestrate.py` chooses its transition
   from a closed field — `state` on one contract, `verdict` on the other — of an artifact that passed
   its schema at the boundary. The mapping is `CONSUMED`, a dict; adding a producer is adding a row.
   Nothing in it reads prose, which is stage 2's abandonment criterion not having fired.
4. ~~**One appended event** and **one derivation of workflow state**~~ **Done.**
   `schemas/workflow-event.v1.json` and `scripts/workflow_lib.py`: an append-only log, state replayed
   from it by `derive()`, and `guard()` holding the transition table. Ordering is `seq`, so replay
   depends on neither a clock nor file order.
5. ~~**A user-invocable skill**~~ **Authored.** `src/claude/skills/knowledge-change/SKILL.md`, with
   `disable-model-invocation` set per ADR-0009. Authored is not done, by the same rule that applied to
   `concept-author`: it is inert here, and only the generator with an installed fixture exercises it.
6. ~~**`make validate`, `make test`** over the above, and a fixture~~ **Done.**
   `fixtures/knowledge-change-loop/` runs all seven phases of R2 with one validation failure and one
   recovery; `scripts/replay_workflow.py --check` is wired into `make validate`, and
   `tests/test_workflow_events.py` covers each guard condition in both directions.
7. ~~**The generator and `make dist`**~~ **Done.** `scripts/generate_dist.py` assembles
   `dist/.claude/` as a plugin root, and `scripts/verify_dist.py` regenerates into a temporary tree
   and compares. `make check` therefore runs end to end for the first time. What this does *not*
   settle is step 2 and step 5: a generated component is still not a loaded one, and nothing has
   watched Claude Code resolve either of them. That is the next step rather than this one.

## Construction decisions

Four questions the build order raised before any code answered them. Each is recorded here because
leaving it implicit would let the first component that meets it decide by accident.

**D1 — the plugin root is `dist/.claude/`.** `CLAUDE.md` **Repository layout** and
`.claude/rules/distribution.md` both name that path, and `specs/0008` **Decided elsewhere** states that
where that specification and that rule file appear to overlap, the rule file wins. The harness manifest
therefore lands at `dist/.claude/.claude-plugin/plugin.json`. Decided 2026-07-31; no edit to `CLAUDE.md`
was needed.

**D2 — two proposed mechanisms were discarded rather than built.** A "bootstrap default" tier for numeric
limits was proposed, holding a provisional uncalibrated value between a caller-supplied one and a
calibrated one. It contradicts `specs/0001` R10 and `specs/0007` R19, and R20 names the exact failure it
would institutionalize: a value chosen once to get a first run moving becoming a framework default nobody
decided to ship. A five-value artifact lifecycle vocabulary was proposed alongside it; `specs/0004` R45
fixes a closed set of three, and the **Artifact persistence** section of that document already records why
collapsing persistence, normativity, and derivation into one axis was rejected. Neither is built, and no
accepted specification changed to refuse them.

**D3 — `templates/` holds scaffolds, and a template is something else.** `CLAUDE.md` gives `templates/`
the role "artifact generators that conform to schemas", which is a generator for an artifact *this*
repository authors. `specs/0011` R1 defines a template as the mechanism of the deterministic generation
track, producing an artifact class from the closed vocabulary of `specs/0004` R8 — where `specification`
and `adr` do not appear. Two mechanisms, one word, and
`docs/adr/0010-projection-names-the-graph-derived-artifact.md` exists because `projection` named two
referents once already. `docs/concepts/scaffold.md` records the distinction and is `proposed`: only
`templates/` and a script use the term, and implementation does not promote vocabulary.

**D4 — where a target pack's source lives is unresolved, and is named rather than merged.**
`specs/0004` R13 states a pack is "distributed together under `src/claude/`". `specs/0008` R23 states a
pack is a separate plugin and "the framework distribution contains no pack", and that document's directory
listing says `packs/` is absent. `CLAUDE.md` **Repository layout** defines `src/claude/` as the components
the framework *ships* and offers no third location. A pack under `src/claude/` here would be emitted into
the framework distribution, which R23 forbids; a pack anywhere else contradicts R13. Both are accepted, at
equal precedence, with no supersession between them, so **Conflict protocol** in `CLAUDE.md` applies: this
is recorded and left for a maintainer rather than resolved by whichever specification a script happened to
read first. Nothing in the build reaches a real pack before the generation pipeline exists, so the decision
is owed then and not now. A fixture pack has a home already and does not depend on it.

## Sequencing

Five stages. Each one names what it would falsify, because a stage that cannot fail teaches nothing.

1. **A design authority, no framework code.** Spec 0001, the retirement of the v0.1 draft, the concepts
   the spec uses normatively, and the specification contract that makes any of it checkable. Falsifies
   nothing by itself — it is the baseline against which the later stages become falsifiable. **Done.**
   Spec 0001 was accepted on 2026-07-31 on the evidence of stage 2, with the requirements its three unmet
   conditions covered moved to `specs/0014-acceptance-closure-and-escalation.md` rather than accepted
   unexercised. Normative source 1 now binds for the workflow as well as the knowledge layer.
2. **The first workflow loop, over knowledge only.** `request → impact analysis → knowledge authoring →
   validation → acceptance`, with no generated code and no context resolution: in a five-object bundle
   the impact set *is* the context. This is steps 3–6 above, plus the minimal generator, because a
   fixture cannot install components by hand. This is the stage that settles the **open architectural
   questions** below, and ADR-0009 condition 2.
   Abandonment criterion: if the orchestrator needs to interpret prose to choose a transition, the
   artifact design is wrong — fix the schemas, not the prompt. This stage carries the risk of the whole
   plan.

   **Done except the generator.** The loop runs, and the abandonment criterion did not fire: the
   orchestrator reads a closed field and there is no branch in it that inspects prose. Two corrections
   the work forced on this stage's own description, both recorded rather than quietly absorbed. The five
   phase names above are shorthand for R2's seven, not a shorter path — R2 states escalation inserts
   phases and never removes one, so context resolution is recorded as *degenerate* rather than skipped,
   and "knowledge authoring" is the implementation phase. And the minimal generator is not done, so
   ADR-0009 condition 2 remains open: nothing has yet installed a component and watched Claude Code load
   it.
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
| acceptance order: no specification accepted before the one it depends on (`specs/README.md`) | the derived prerequisite check runs in `make validate` | **active**; edges derived from acceptance conditions, three prerequisites found today, both outcomes tested |
| concept frontmatter contract (`schemas/concept.v1.json`) | the validator runs in `make validate` | **active**; the `sources` path constraint became enforced with ADR-0010, which records the deleted-source failure that demanded it |
| ADR frontmatter contract (`schemas/adr.v2.json`), including supersession and amendment | the validator runs in `make validate` | **active**; `amends` exercised for the first time by ADR-0008 over ADR-0004 |
| non-restatement: an ADR's `## Decision` cites an operative rule instead of repeating it (`docs/adr/README.md`) | the check runs in `make validate` | **active**, six ADRs de-duplicated to satisfy it |
| migration test for a contract bump (`.claude/rules/compatibility.md`) | a test suite exists | **active**; the `adr/1` → `adr/2` debt was paid by `scripts/migrate_contracts.py` and `fixtures/migration-adr-v1-v2/`, and `check_contract_versions.py` now fails a bump that registers no path |
| contract integrity: constraints cannot change without a version bump (`.claude/rules/compatibility.md`) | `check_contract_versions.py` runs in `make validate` | **active**; a digest over the assertion vocabulary, so a reworded description is not a bump and a changed constraint is |
| component contracts (`schemas/skill.v1.json`, `schemas/agent.v1.json`) | the validator runs in `make validate` | **active**, exercised by `concept-author` |
| result contract (`schemas/concept-authoring-result.v1.json`) validated at the boundary | the thin-path orchestrator or a test consumes the agent's result | **active**: `scripts/orchestrate.py` validates it before consumption, and rejection is tested |
| workflow event contract (`schemas/workflow-event.v1.json`), its conditionals, and the transition guard | `scripts/workflow_lib.py` runs under test | **active**, every guard condition covered in both directions |
| impact analysis contract (`schemas/impact-analysis.v1.json`), R4's closed verdict | the orchestrator consumes it | **active**, exercised by `fixtures/knowledge-change-loop/` |
| a workflow fixture's log and derived state are replayed and never hand-edited | `replay_workflow.py --check` runs in `make validate` | **active** |
| knowledge-object contract (`schemas/knowledge-object.v1.json`), per-type conditionals and the attribute type system | the validator runs in `make validate` (spec 0003 R37) | **active**, exercised by `fixtures/knowledge-two-context/` |
| materialized graph contract (`schemas/knowledge-graph.v1.json`) | the materializer emits `graph.json` | **active** |
| the checks spec 0003 defers to a script — R11, R15, R18, R20, R22, R28, R29, R38, R43–R48 | `scripts/validate_knowledge.py` runs in `make validate` | **active**, both outcomes tested per check |
| projections are derived and never hand-edited (R42, R51) | `project_knowledge.py --check` runs in `make validate` | **active** |
| ontology utilization measured (R52) | `measure_ontology.py --check` runs in `make validate` | **active**, three removal candidates found |
| `make validate` in `/siegard-verify` step 1 | a `Makefile` target exists | **active**, five artifact classes plus two derived-tree checks |
| `make test` in `/siegard-verify` step 1 | a framework test suite exists | **active**, 296 tests: 98 over the knowledge layer, 59 over the workflow loop, 39 over the generator and the distribution, 35 over the specification set, 33 over contract versioning and migration, 32 over the three validators that had none |
| `make dist-check` in `make check` | a generator and a committed `dist/` exist | **active**; `verify_dist.py` regenerates into a temporary tree and compares, and separately holds the committed tree to the invariants specs/0008 states about the output |
| security invariants (`CLAUDE.md` **Security**) | stated; enforcement waits for the first hook | **partly active** |
| `src/claude/` holds every shippable component (`CLAUDE.md` layout) | the first distributable component is authored | **active**; the generator reads that tree and nothing else, and a test asserts no path under `.claude/` reaches the distribution |
| "do not hand-edit generated artifacts" (`rules/distribution.md`) | a generator and `make dist` exist | **active**; a hand edit fails `make dist-check` on the recorded digest and again on the comparison. Not yet *enforced* — that is the hook of open question 5 |
| "no source-only paths in the distribution" | `dist/` is generator-produced | **active**, with the rejection direction covered: a planted file under `specs/` in the output is reported |
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

`CLAUDE.md` states what must hold; it does not choose these designs. Each question below carries the gate
that would settle it, and a gate is met by a mechanism under test, never by a status change: the promotion
of 2026-07-31 closed question 1, whose gate was already met, and left the rest exactly where they were.
Until a gate is met, do not treat the design named as demonstrated, whatever the status of the document
that describes it.

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

   **Settled.** Every gate condition was met — `schemas/workflow-event.v1.json`,
   `scripts/workflow_lib.py`, `tests/test_workflow_events.py`, `fixtures/knowledge-change-loop/` — and
   `docs/adr/0011-append-only-workflow-events-derived-by-replay.md` was accepted on 2026-07-31, which
   records the decision the evidence had been waiting for. This is the one question whose gate was met
   before its record was accepted rather than after.
2. **How the distribution is produced.** That `dist/.claude/` is generated, reproducible, and never
   hand-edited is settled by `CLAUDE.md` **Repository layout** and `.claude/rules/distribution.md`. Its
   *shape* is settled too, as of 2026-07-31: a plugin root, per ADR-0012 and `specs/0008`, so the generator
   has a target rather than a blank page. Gate: a generator in `scripts/` that `make dist` runs; running it twice from
   the same source produces identical output; a test asserting no source-only path (`specs/`, `tests/`,
   `fixtures/`, `docs/`, `.claude/`) reaches the output; a test asserting no secret or
   environment-specific value does.

   **Settled.** Every condition is met by `scripts/generate_dist.py`, `scripts/verify_dist.py`, and
   `tests/test_generator.py`, and `dist/.claude/` is committed and verified by `make dist-check`.

   Four things the work decided that the gate did not ask for, recorded because each was a choice and
   not a discovery. `source_revision` is a content digest over the framework source rather than a commit
   SHA: a SHA would make the committed distribution unverifiable, since generating at commit N-1 records
   N-1 and committing the result produces N. The manifest carries no timestamp, because a minted value
   would differ between two runs over identical source and R4 calls that a defect — `specs/0008` R12 does
   not ask for one. Which schemas ship is an explicit classification asserted total against `schemas/`, so
   a new contract forces a decision instead of inheriting one. And `__pycache__` is excluded from
   verification: a consumer who runs a shipped executable once will have it, and reporting it as an
   unmanaged file would make every upgrade check fail after first use.

   One correction to the gate's own framing. An earlier reading of R6 took "verification is separate from
   production" to mean the verifier may not use the generator. R6 says the opposite — it "regenerates into
   a temporary location and compares" — and what it forbids is writing into the distribution being
   checked. `verify_dist.py` does both: it regenerates and compares, *and* it holds the committed tree to
   the invariants `specs/0008` states about the output. The second layer is the one that survives a
   generator which is consistently wrong, because a comparison alone would produce the same defect twice
   and report agreement.
3. **Which component classes exist and what each owns.** `CLAUDE.md` **Authority placement** requires one
   authoritative definition per concept, which constrains any division of work without choosing one.
   There is no command class — ADR-0009 records the commands-into-skills merge. Gate: one entry point,
   one orchestrator, and one specialized agent completing a workflow together; the orchestrator choosing
   its transition from a validated artifact's closed `state` field with no interpretation of prose; the
   specialized agent's tool grant demonstrably the minimum its role requires; a fixture exercising the
   path end to end. If a class turns out to be ceremony for the workflows the framework actually runs,
   drop it rather than populate it.

   **Partly met.** The entry point and the orchestrator exist, and the orchestrator's transition is a
   lookup on a closed field with no prose read — that condition is met and tested. Two are not: the
   specialized agent never ran, because it is inert here until the generator installs it, so its result
   was consumed as a recorded artifact rather than produced; and "completing a workflow together" is
   therefore unproven. One thing the work did settle by demonstration: the orchestrator is a script, not
   a prompt and not an agent. Whether `orchestrator` names a component class the framework *ships* is
   still open — see `docs/concepts/orchestrator.md`, which records the term and leaves the class
   question here.
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

## The framework-architecture agenda

A proposal on 2026-07-30 asked for eleven specifications describing the Siegard product: runtime
architecture, a capability model and its contracts, the distribution layout, context assembly, a command
system, a worker model, a hook system, a template system, target packs, and the framework lifecycle. The
gap it names is real. `specs/` fixes the method a governed repository follows; nothing fixes the product
that implements it, and the four specifications there do not claim to.

It is recorded as an agenda rather than written as eleven specifications, for the reason this file already
gives: a contract for a component that does not exist is a guess that reads like a requirement. Three of
the eleven would answer an open question above by assertion instead of meeting its gate, and
`docs/concepts/capability.md` already settles what an unexercised capability is — an intention. An agenda
that names, per topic, who holds the authority now and which gate would move it costs one section and
forecloses nothing.

| Topic | Who holds the authority today | What would settle it |
|---|---|---|
| runtime architecture | `CLAUDE.md` **Scope**; `.claude/rules/claude-code-authoring.md` | stage 2, once the thin path has run |
| capability model, capability contracts | `docs/concepts/capability.md`; `schemas/skill.v1.json`, `schemas/agent.v1.json` | open question 3's gate |
| distribution layout | `CLAUDE.md` **Repository layout**; `.claude/rules/distribution.md` | open question 2's gate — a generator |
| context assembly | `specs/0001` **Context resolution**; `docs/concepts/context-package.md` | stage 3, with the selection instrumentation |
| command system | ADR-0009: there is no command class | nothing — the class does not exist |
| worker model | `docs/concepts/specialized-agent.md` | open question 3's gate |
| hook system | `CLAUDE.md` **Security** | open question 5's gate — the first hook under test |
| template system | `specs/0011`, `specs/0004`; `docs/concepts/generation-track.md` | stage 4 — 0004's acceptance is no longer the blocker |
| target pack model | `.claude/rules/claude-code-authoring.md` **Target packs**; `specs/0004` | a pack with a fixture, after 0004 is accepted |
| framework lifecycle | `.claude/rules/compatibility.md` | the migration test that rule is already owed |

The framework specifications this agenda eventually produces belong in `specs/` at `0005` and above.
Splitting `specs/` into subdirectories was considered and rejected: 33 concept `sources` resolve to those
paths under a constraint ADR-0010 made enforced, and renaming a public artifact is breaking under
`.claude/rules/compatibility.md`. An id range separates the two families at no cost.

Four vocabulary decisions from the same proposal, recorded so the terms do not re-enter:

- a unit of work with one role is a **specialized agent**. `worker` is v0.1 vocabulary, which was
  normative nowhere and this repository no longer carries;
- a user-invocable procedure is a **skill**. ADR-0009 records that there is no command class, and
  `scripts/validate_components.py` already rejects `src/claude/commands/` by name;
- a **projection**, a schema, and a template are artifact classes, not kinds of capability. ADR-0010
  exists because `projection` named two referents once already;
- the tier that holds `specs/` is a **normative source**, named in `CLAUDE.md`. `foundations` is not a
  second name for it.

**Discovery** is the act that produces a [change request](concepts/change-request.md), upstream of the
seven phases in `specs/0001`. It is not an eighth phase and it changes nothing in that specification.

Three of the agenda's topics were settled on 2026-07-31 by reading the harness documentation rather than by
reasoning, and `docs/adr/0012-distribute-the-framework-as-a-claude-code-plugin.md` records the decision. The
framework is distributed as a plugin, which supplies what the first draft of `specs/0008` had invented: a
`hooks/hooks.json` that is in force while the plugin is enabled, so enabling the framework installs its own
enforcement; a `bin/` directory that puts executables on the Bash tool's `PATH`, so shipped scripts have a
documented home; and automatic namespacing of skills as `/<plugin>:<skill>`, which removed a reserved-prefix
requirement rather than satisfying it. A target pack is its own plugin. Two findings that had been recorded
as open — that Siegard could not install its own hooks, and that a rename of `concept-author` and
`knowledge-change` was owed — were closed by the evidence, the second by the work turning out to be
unnecessary.

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

Each of these is a session-wide guarantee, which is what decides how it ships: not in a component's
frontmatter, where `specs/0010` R18 would scope it to that component's lifetime, but in the distribution's
`hooks/hooks.json`, in force while the plugin is enabled. ADR-0012 records why that route exists and the
documentation that establishes it.

Treat these as the point where governance becomes real. Until then, the rules in this repository
depend on cooperation.

## In place

- **Version control.** Git, on `main`, with `origin` at `git@github.com:zig999/siegard2.git`.
  Traceability, reproducible generation from committed source, and migration history all presuppose it.
- **Eight enforced artifact contracts.** Specifications (`schemas/spec.v1.json`), concepts
  (`schemas/concept.v1.json`), ADRs (`schemas/adr.v2.json`, with `adr.v1.json` kept readable),
  distributable components (`schemas/skill.v1.json`, `schemas/agent.v1.json`), knowledge objects
  (`schemas/knowledge-object.v1.json`), and the two the workflow loop added — workflow events
  (`schemas/workflow-event.v1.json`) and impact analysis (`schemas/impact-analysis.v1.json`) — each with
  a boundary validator in `scripts/`, all wired to `make validate`. These are the only rules in this
  repository that are checked rather than trusted. The component contracts were authored before the first component, deliberately, so it was born
  against them (ADR-0009); the specification contract was authored in the same change as the first
  specification, for the same reason.
- **A design authority.** `specs/0001-knowledge-object-driven-development.md`, `accepted` on 2026-07-31, is
  the first occupant of normative source 1. It fixes the workflow, the escalation predicates, the calibrated
  fail-soft claim, and the maturity ladder that decides when a knowledge object gains mechanical force.
  Its **Provenance** section records what the SIGARD v0.1 draft contributed, what forced a rewrite, and
  where the draft went once `reference/` was removed; it was non-normative input at every precedence
  level.
- **The first distributable component.** `src/claude/agents/concept-author.md`, with its result
  contract in `schemas/concept-authoring-result.v1.json`. It is a component under `src/claude/` that
  nothing under `.claude/` duplicates, and it exercises the component contract for the first time. The
  rest of open question 4 above — generator input, exclusion test, fixture — remains open.
- **The thin path, less the generator.** `scripts/orchestrate.py`, `scripts/workflow_lib.py`, and
  `scripts/replay_workflow.py`, over `schemas/workflow-event.v1.json` and
  `schemas/impact-analysis.v1.json`, with `src/claude/skills/knowledge-change/SKILL.md` as the entry
  point and `fixtures/knowledge-change-loop/` as the case. It runs all seven phases of spec 0001 R2,
  including a validation failure and a recovery under a stated attempt limit, and it is the change that
  turned the boundary check on `concept-authoring-result/1` from a declared gap into a tested one. What
  it does not prove is in that fixture's **What it is not evidence for**, and the shortfall is the same
  one everywhere: no component has been installed and loaded, because there is no generator.

## Not yet in place

- No `templates/`. No fixture exercises the generation pipeline of spec 0004 or the distribution. The
  workflow of spec 0001 now has one, `fixtures/knowledge-change-loop/`, which exercises its control flow
  but produces no code and no context package.
- Every specification, ADR, and concept is `accepted` as of 2026-07-31, so normative source 1 now binds for
  the generation pipeline, the acceptance closure, escalation, and the whole framework family as well as
  for the knowledge layer and the workflow. Most of that binds on a maintainer's decision rather than on
  evidence: the open questions below and the acceptance conditions inside each promoted document are the
  measure of what is still unbuilt, and they did not close when the statuses changed. Read a `status:
  accepted` here as "this is the design of record", not as "this was demonstrated".
  Spec 0003 was accepted on 2026-07-30 after every condition it set was met by a component that
  exercises it — see `fixtures/knowledge-two-context/README.md` for the evidence, and that
  specification's **What satisfied acceptance** for the six defects building the evidence exposed and
  repaired before acceptance rather than after. Four findings remain open there; none is a
  contradiction. From here `.claude/rules/compatibility.md` governs changes to spec 0003, so a repair
  that invalidates a conforming knowledge object is a breaking change rather than a revision.
- `make test` runs 257 tests: 98 over the knowledge layer, 59 over the workflow loop, 35 over the
  specification set, 33 over contract versioning and migration, and 32 over the three validators that
  previously had none. The figure read 193 until 2026-07-31, when counting the suites module by module
  found the specification set was 35 rather than 36. A count nothing derives drifts, which is the argument
  for the check `scripts/check_contract_versions.py` now applies to schemas rather than an argument for a
  more careful reader.

  `validate_adrs.py`, `validate_concepts.py`, and `validate_components.py` were untested code enforcing
  tested contracts until `tests/test_validators.py`, which covers each one in both directions through its
  real entry point. `validate_specs.py` is covered for its concept links and its acceptance order and not
  for the rest of what it does, so a green `make test` is still not evidence that its frontmatter, section,
  or requirement-numbering checks work — it is the one validator left in that state. Covered in full:
  `validate_knowledge.py`, `knowledge_graph_lib.py`, `project_knowledge.py`, `measure_ontology.py`,
  `workflow_lib.py`, `orchestrate.py`, `check_contract_versions.py`, and `migrate_contracts.py`.
  `replay_workflow.py` is exercised by `make validate` rather than by a test of its own.

  One cost worth stating rather than absorbing: `validate_adrs.py` compares every `## Decision` line
  against 215 operative statements, so a full run costs about five seconds. `tests/test_validators.py`
  mutates a single-ADR subset for that reason and runs the whole tree once, which is why the suite takes
  seventeen seconds rather than a minute.
- No `.claude/rules/security.md`. `CLAUDE.md` **Security** states the invariants; sanitization, path,
  subprocess, and network detail wait until the first hook or script needs them — see open question 5.
- **No installation, therefore no loaded component.** The generator exists and `dist/.claude/` is
  committed and verified, so open question 2 is closed and its half of open question 4 with it. What is
  still open is the other half, and it is now the single largest gap: `concept-author` and the
  `knowledge-change` skill are *assembled* rather than *inert*, which is a smaller claim than it sounds.
  Nothing has installed the plugin into a repository and watched Claude Code resolve either of them. That
  is ADR-0009 condition 2 and the remainder of open question 4.

  One thing did stop being a claim. `dist/.claude/bin/orchestrate.py` runs from the plugin root against a
  real event log and derives the recorded state, and `workflow_lib.py` resolves its schemas from
  `dist/.claude/schemas/` rather than from this repository — `bin/` sits beside `schemas/` at the plugin
  root exactly as `scripts/` sits beside `schemas/` here. A shipped executable therefore works outside
  `scripts/`, which is the first thing in this repository to do so. A shipped *component* still has not
  been loaded by the harness, and the two are not the same evidence.
- No contract for a context package or a specification delta. Spec 0001 R11 requires the first and R16
  constrains the second; the workflow loop records both phases without producing either artifact, because
  nothing consumes them to choose a transition yet. Spec 0001 states each artifact's schema arrives with
  the phase that produces it, so these arrive with stage 3 and stage 4.
