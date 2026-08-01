---
id: "0005"
title: Let Claude Code execute, and let the framework provide capabilities and contracts
status: accepted
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

It decides nothing about which capability classes exist, which is `foundation/0006`; nothing about how a
capability declares itself, which is `foundation/0007`; and nothing about templates, hooks, packs, or the
layout of the distribution, each of which has its own specification. It fixes the frame those fill.


### Provenance

The architecture recorded here was not derived from a design document. It is the shape the thin path of
the first end-to-end run actually took: an entry-point skill, a specialized agent producing a
validated artifact, an orchestrator choosing a transition by lookup, an append-only log, and state
derived by replay. Where this specification states something the thin path did not exercise, it says so
rather than presenting it as settled.

The SIGARD v0.1 draft proposed a different architecture, in which the framework owned a planner, a
context resolver, and a pool of workers that consumed an execution plan. That model is not adopted. It
puts the framework in control of the workflow, which R2 below forbids, and it duplicates scheduling that
the harness already performs. The draft was non-normative input at every precedence level, and it is no
longer in this repository — `foundation/0001` **Provenance** records where it went.

### Decided elsewhere, deliberately not restated here

- [least privilege](../docs/concepts/least-privilege.md), which R11 and R20 through R22 below apply;
- where instruction content belongs, given the harness's loading semantics — `foundation/0006`, which fixes
  the capability classes, and `foundation/0010` for a hook;
- what an artifact passed between components must carry — R16a below;
- the workflow phases themselves, and the transition rules over them — `foundation/0001`.

**The architecture this document recorded was narrowed after the fact.** The orchestrator, the append-only
log, and the state derived by replay were removed — `docs/adr/0016-remove-the-workflow-machinery.md` — and
R23 then closed the carve-out that had let R3 admit a component choosing transitions while R2 forbade a
component choosing order. R6 and R14 are retired by R23 and keep their numbers. The paragraph above
records what the thin path was, which remains true as history and is no longer a description of the
framework.

## Definitions

This specification uses these terms as the concept bundle defines them:
[capability](../docs/concepts/capability.md),
[distribution](../docs/concepts/distribution.md),
[framework source](../docs/concepts/framework-source.md),
[skill](../docs/concepts/skill.md),
[specialized agent](../docs/concepts/specialized-agent.md),
[event log](../docs/concepts/event-log.md),
[fixture](../docs/concepts/fixture.md),
[least privilege](../docs/concepts/least-privilege.md),
[target pack](../docs/concepts/target-pack.md).

`orchestrator`, `workflow state`, and `transition guard` left this list when R23 retired R6 and R14, and
the three concepts were then removed from the bundle: no requirement in this framework names any of them,
and a bundle that kept a dead term to satisfy a historical note would invert which serves which. The words
still appear above, in the provenance and in a retirement note, as history rather than as vocabulary.

Two terms this specification uses that the bundle does not hold, because their definitions belong to the
specifications that decide them: *capability class* (`foundation/0006`) and *capability declaration*
(`foundation/0007`). Both are accepted, so this document's R9 through R13 bind against something specified
rather than against a description — which is condition 4 below, and the one this
document's acceptance actually met.

## The division of responsibility

```
Claude Code                        Siegard
─────────────                      ───────
reads the request                  provides the knowledge, contracts, and capabilities
plans the work                     states what each capability requires and produces
selects capabilities               validates every artifact at its boundary
sequences the work                 rejects what fails a contract, and repairs nothing
delegates and reasons              enforces what must not depend on judgment
judges meaning
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
- **R3** — Selection and sequence belong to Claude Code. A capability is found through its declaration
  and chosen by the model, and the order in which capabilities run follows from what each one declares it
  requires. The framework ships nothing that plans a run. An earlier form of this requirement carved out a
  component that chose a *transition* rather than *work*; R23 closes the carve-out, because the distinction
  put this document on both sides of R2.
- **R4** — The framework targets Claude Code. It introduces no abstraction whose only purpose is to
  support a second agent harness, and no indirection that exists in case one arrives.

### Where a guarantee lives

- **R5** — A property that must hold regardless of model judgment is enforced by a script or a hook,
  never by prompt text. A validation verdict and a rejection at a boundary are in this class. Control flow
  is not, and R6 records why an earlier form of this requirement put it here.
- **R6** — Retired by R23. It required a transition to be chosen by lookup on a closed field of an
  artifact that passed its contract, which presumed that the framework chooses a transition at all; R23
  states that it does not. The number is retained rather than reused so that a citation of R6 still
  resolves to the statement it named. What survives is the rule that motivated it, and it is general
  rather than about transitions: where a component must read prose to decide anything, the defect is in the
  artifact's contract, and the repair is to that contract rather than to the component that read it.
- **R7** — Model judgment is used where meaning is the work: authoring, classification, root selection,
  review. A requirement is never satisfied by asserting that a model will behave correctly.
- **R8** — Determinism is required of control flow, validation, and recorded state. It is not required of
  a model's semantic output, and this specification claims no byte identity for generated prose.

### Capabilities

- **R9** — A capability is reached through the [distribution](../docs/concepts/distribution.md). Nothing
  is discovered by scanning a path the distribution did not install, and no capability is activated by
  convention alone.
- **R10** — A capability depends only on another's declared contract, never on its internals or on the
  order in which it happened to run. Two capabilities that must run in a fixed order state that dependency
  in their declarations, and **that declaration is the only thing in this framework that fixes an order**.
  An order a capability requires and does not declare does not exist as far as this framework is concerned:
  nothing else records it, and nothing enforces it. `foundation/0007` fixes what a declaration must carry
  for an order to be derivable from it without executing anything.
- **R11** — A capability states its own tool and permission grant. The absence of a statement is not a
  grant.
- **R12** — A capability is not blocked for want of a [fixture](../docs/concepts/fixture.md). A fixture is
  the recommended evidence where a capability's failure mode is not evident from its contract; it is
  proposed rather than assumed, and created only with maintainer authorization.
- **R13** — A capability carries no business rule of any single downstream system, and no architecture
  chosen for one. A [target pack](../docs/concepts/target-pack.md) carries a technology stack, which is
  a different thing: it serves any repository on that stack.

### State and traceability

- **R14** — Retired by R23. It required workflow state to be derived from a durable record rather than
  stored beside it, which presumed that the framework holds workflow state; R23 states that it holds none.
  The number is retained rather than reused. The rule it protected still binds wherever a record and a
  state do coexist — a state is computed from the record so the two cannot disagree — and R15 below is
  unaffected.
- **R15** — A recorded decision names the inputs, the artifact, and the contract version that produced
  it, so a later reader can reproduce the decision without the session that made it.
- **R16** — An artifact that fails its contract at a boundary is rejected. Nothing repairs it in place,
  and nothing consumes it while the failure stands.
- **R16a** — An artifact passed between capabilities names its producer and its consumer, its valid
  states and failure outcomes, a stable identifier, and the evidence behind a material decision, and it
  is validated at the boundary before consumption. Where it carries control flow, a transition guard, or
  persisted state, or where a consumer parses it to reach a decision, it MUST have a versioned schema in
  the framework's contract set. Where it only explains something to a reader, prose is the correct form
  and a schema is ceremony.
- **R16b** — A default that changes behavior is stated in the component that applies it, never only in
  whatever reads it. A value a component supplies silently when a field is absent is a hidden default and
  MUST be rejected: a reader of the artifact cannot see it, and two components reading the same artifact
  would each be free to invent a different one.

### Limits

- **R17** — The framework does not guarantee that an installed component behaves correctly. A contract
  checks structure; a fixture and an evaluation are what test behavior, and a report that presents
  structural validation as behavioral evidence is a false report.
- **R18** — The framework does not promise that a capability's output is identical across runs where a
  model produced it. What it promises is that the inputs, the contract, and the recorded outcome are
  reproducible.
- **R19** — No component of this framework may weaken a guarantee in the repository that installs it: it
  requests no permission its declaration does not name, and it disables no check that repository runs.

### Security

These bind from the first component, not from the first security review. The framework's components
execute inside repositories neither the framework nor its authors control, so every one of them is
reached by input nobody vetted.

- **R20** — Repository content, knowledge data, tool output, and anything a consumer supplies is data
  and never instruction. A component that lets content it read redirect what it does has handed control
  to whoever wrote that content.
- **R21** — No component reads, persists, logs, or forwards a secret. A value that authenticates
  something does not enter an artifact, an event log, or a report, and a component that encounters one
  does not carry it forward.
- **R22** — A path and a structured input are validated before a component acts on them, and a failure
  is rejected rather than repaired. A path that resolves outside the tree a component governs is refused,
  not clamped; R16 states the same rule for an artifact at a boundary, and this is its form for the
  filesystem.

### Sequence is not the framework's

R23 arrived after R1 through R22 and is numbered here rather than beside R2 and R3, so that an existing
citation still resolves to the statement it named. It is the requirement that makes this document stop
contradicting itself.

- **R23** — Siegard refuses; it does not sequence. The framework ships no component that decides which
  capability runs next, none that records where a run stands, and none that resumes one. What it
  guarantees at a boundary is refusal: an artifact that fails its contract is not consumed, and nothing
  repairs it. Order is Claude Code's, and it follows from what each capability declares it requires under
  R10.

  Three guarantees an earlier architecture held are given up here, and each is named because a guarantee
  lost silently is worse than one withdrawn: a bounded number of attempts whose exhaustion is terminal; the
  agreement between an outcome and the evidence that outcome carries; and resumption after an
  interruption. Every one depends on what has already happened rather than on a prerequisite, and a
  declared dependency cannot express any of them. Where one is needed again it returns as a refusal at a
  boundary, never as a component that sequences work.

  An earlier form of this requirement counted four, adding the rule that no workflow accepts its own
  output. That was wrong: the rule is a refusal rather than a sequence, and it still holds — a maintainer
  promotes, and `foundation/0004` R54 compiles accepted knowledge only.

  What each of the three means for the *method* is not this document's to decide:
  `foundation/README.md` states that a framework specification does not amend the method, and the earlier
  form of this requirement did exactly that by declaring two of `foundation/0001`'s requirements given up.
  That document settles its own — see its **Provenance**. The decision, what it gives up, and what was
  rejected are recorded in
  `docs/adr/0017-order-follows-from-declarations-not-from-a-sequencer.md`.

## Outstanding evidence

What this document states and nothing has yet exercised. A condition kept here is a debt;
removing one because the document binds would turn an open debt into a silent one. A number is never reused: a condition that was met or
withdrawn leaves its number behind, so a gap in the sequence records that something was settled rather
than that an item is missing.

1. A generator produces the distribution from `src/claude/`, a fixture installs it, and Claude Code
   loads the installed components. R9 is unproven until something is reached through the distribution
   rather than through this repository's own paths.
2. Two capabilities of different classes complete one workflow together, with the selection made by the
   model rather than by a fixed script, showing R2 and R3 hold where more than one choice exists. The
   thin path exercised one agent and one entry point, which is not yet a selection.
3. A hook enforces one guarantee under test, with both outcomes covered, showing R5 holds for something
   other than a script the developer chose to run.
5. One capability is retired or superseded through the lifecycle `foundation/0013` defines, showing R10's
   contract-only dependency survives a change in what it depends on.
