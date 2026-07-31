---
id: "0005"
title: Let Claude Code execute, and let the framework provide capabilities and contracts
status: proposed
contract_version: spec/1
---

# Runtime architecture

## Scope

This specification fixes how Siegard executes. It is the first specification of the Siegard product
rather than of the method the product implements, and it decides five things:

1. who executes a development workflow, and what the framework is;
2. what the framework provides, and what it may never control;
3. how a [capability](../docs/concepts/capability.md) is found and chosen;
4. where a guarantee lives — which properties are decided by a script or a hook, and which are left to
   model judgment;
5. the limits: what this architecture does not promise, and what it forbids building.

It decides nothing about which capability classes exist, which is `specs/0006`; nothing about how a
capability declares itself, which is `specs/0007`; and nothing about templates, hooks, packs, or the
layout of the distribution, each of which has its own specification. It fixes the frame those fill.

It governs the framework Siegard ships. It does not govern this repository's own development process,
which `CLAUDE.md` defines.

### Provenance

The architecture recorded here was not derived from a design document. It is the shape the thin path of
`docs/bootstrap.md` stage 2 actually took: an entry-point skill, a specialized agent producing a
validated artifact, an orchestrator choosing a transition by lookup, an append-only log, and state
derived by replay. Where this specification states something the thin path did not exercise, it says so
in **Validation required before acceptance** rather than presenting it as settled.

The SIGARD v0.1 draft under `reference/` proposed a different architecture, in which the framework owned
a planner, a context resolver, and a pool of workers that consumed an execution plan. That model is not
adopted. It puts the framework in control of the workflow, which R2 below forbids, and it duplicates
scheduling that the harness already performs. `reference/` is non-normative input at every precedence
level.

### Decided elsewhere, deliberately not restated here

- the constraint order that ranks any two valid designs — `CLAUDE.md` **Decision order**;
- what must be persisted outside the conversation, and what is not a record — `CLAUDE.md`
  **Determinism and state**;
- the security invariants binding every shipped component — `CLAUDE.md` **Security**, and
  [least privilege](../docs/concepts/least-privilege.md);
- where instruction content belongs, given the harness's loading semantics —
  `.claude/rules/claude-code-authoring.md`;
- what an artifact passed between components must carry — `.claude/rules/contracts.md`;
- the workflow phases themselves, and the transition rules over them — `specs/0001`.

## Definitions

This specification uses these terms as the concept bundle defines them:
[capability](../docs/concepts/capability.md),
[distribution](../docs/concepts/distribution.md),
[framework source](../docs/concepts/framework-source.md),
[orchestrator](../docs/concepts/orchestrator.md),
[skill](../docs/concepts/skill.md),
[specialized agent](../docs/concepts/specialized-agent.md),
[transition guard](../docs/concepts/transition-guard.md),
[workflow state](../docs/concepts/workflow-state.md),
[event log](../docs/concepts/event-log.md),
[fixture](../docs/concepts/fixture.md),
[least privilege](../docs/concepts/least-privilege.md),
[target pack](../docs/concepts/target-pack.md).

Two terms this specification uses that the bundle does not yet hold, because their definitions belong to
the specifications that decide them: *capability class* (`specs/0006`) and *capability declaration*
(`specs/0007`). Until those exist, this document uses them descriptively and binds nothing about them.

## The division of responsibility

```
Claude Code                        Siegard
─────────────                      ───────
reads the request                  provides the knowledge, contracts, and capabilities
plans the work                     validates every artifact at its boundary
selects capabilities               decides transitions by lookup in a script
delegates and reasons              records what happened, derives state from the record
judges meaning                    enforces what must not depend on judgment
```

The framework is inert. It starts no process, holds no daemon, and waits for no event. Everything it
does happens inside a Claude Code session, or inside a script or hook that session causes to run.

## Requirements

### The executor

- **R1** — Claude Code is the executor. The framework ships no runtime, scheduler, queue, or process of
  its own, and no component that runs outside a Claude Code session or a script that session invokes.
- **R2** — The framework never owns the workflow. No component it ships decides which capability runs
  next, in what order, or at what depth. A capability that sequences other capabilities by its own
  judgment is not a capability of this framework.
- **R3** — Selection belongs to Claude Code. A capability is found through its declaration and chosen by
  the model, without an external orchestrator that plans the run. An [orchestrator](../docs/concepts/orchestrator.md)
  in this framework chooses a *transition* from a validated artifact's closed field; it does not choose
  *work*.
- **R4** — The framework targets Claude Code. It introduces no abstraction whose only purpose is to
  support a second agent harness, and no indirection that exists in case one arrives.

### Where a guarantee lives

- **R5** — A property that must hold regardless of model judgment is enforced by a script or a hook,
  never by prompt text. Control flow, a [transition guard](../docs/concepts/transition-guard.md), a
  validation verdict, and a recorded state are in this class.
- **R6** — A transition is chosen by lookup on a closed field of an artifact that passed its contract.
  Where a component must read prose to decide what happens next, the defect is in the artifact's
  contract, and the repair is to that contract rather than to the component that read it.
- **R7** — Model judgment is used where meaning is the work: authoring, classification, root selection,
  review. A requirement is never satisfied by asserting that a model will behave correctly.
- **R8** — Determinism is required of control flow, validation, and recorded state. It is not required of
  a model's semantic output, and this specification claims no byte identity for generated prose.

### Capabilities

- **R9** — A capability is reached through the [distribution](../docs/concepts/distribution.md). Nothing
  is discovered by scanning a path the distribution did not install, and no capability is activated by
  convention alone.
- **R10** — A capability depends only on another's declared contract, never on its internals or on the
  order in which it happened to run. Two capabilities that must run in a fixed order state that
  dependency in their declarations.
- **R11** — A capability states its own tool and permission grant. The absence of a statement is not a
  grant.
- **R12** — A capability is admitted only when a [fixture](../docs/concepts/fixture.md) exercises it as a
  downstream-shaped case. A declared behavior with no fixture is an intention, not a capability.
- **R13** — A capability carries no business rule of any single downstream system, and no architecture
  chosen for one. A [target pack](../docs/concepts/target-pack.md) carries a technology stack, which is
  a different thing: it serves any repository on that stack.

### State and traceability

- **R14** — Workflow state is derived from a durable record rather than stored beside it. Where both a
  record and a state exist, the state is computed from the record, so the two cannot disagree.
- **R15** — A recorded decision names the inputs, the artifact, and the contract version that produced
  it, so a later reader can reproduce the decision without the session that made it.
- **R16** — An artifact that fails its contract at a boundary is rejected. Nothing repairs it in place,
  and nothing consumes it while the failure stands.

### Limits

- **R17** — The framework does not guarantee that an installed component behaves correctly. A contract
  checks structure; a fixture and an evaluation are what test behavior, and a report that presents
  structural validation as behavioral evidence is a false report.
- **R18** — The framework does not promise that a capability's output is identical across runs where a
  model produced it. What it promises is that the inputs, the contract, and the recorded outcome are
  reproducible.
- **R19** — No component of this framework may weaken a guarantee in the repository that installs it: it
  requests no permission its declaration does not name, and it disables no check that repository runs.

## Validation required before acceptance

1. A generator produces the distribution from `src/claude/`, a fixture installs it, and Claude Code
   loads the installed components. R9 is unproven until something is reached through the distribution
   rather than through this repository's own paths — `docs/bootstrap.md` open question 2, and ADR-0009
   condition 2.
2. Two capabilities of different classes complete one workflow together, with the selection made by the
   model rather than by a fixed script, showing R2 and R3 hold where more than one choice exists. The
   thin path exercised one agent and one entry point, which is not yet a selection.
3. A hook enforces one guarantee under test, with both outcomes covered, showing R5 holds for something
   other than a script the developer chose to run — `docs/bootstrap.md` open question 5.
4. `specs/0006` and `specs/0007` exist, so that *capability class* and *capability declaration* are
   defined rather than used descriptively, and R9 through R13 bind something specified.
5. One capability is retired or superseded through the lifecycle `specs/0013` defines, showing R10's
   contract-only dependency survives a change in what it depends on.
