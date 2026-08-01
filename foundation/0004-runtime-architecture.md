---
id: "0004"
title: Let Claude Code execute, and let the framework provide capabilities and contracts
status: accepted
contract_version: spec/1
---

# Runtime architecture

## Scope

How Siegard executes: who runs the work, how a capability is found, and where a guarantee lives.

Not here: which capability classes exist (`foundation/0005`), and how a capability declares itself
(`foundation/0006`).

## Requirements

### The executor

- **R1** — Claude Code is the executor. The framework ships no runtime, scheduler, queue, or process of
  its own.
- **R2** — The framework does not sequence. It ships no component that decides which capability runs
  next, none that records where a run stands, and none that resumes one.
- **R3** — Order follows from what each capability declares it requires, and a declaration is the only
  thing that fixes an order. An order a capability requires and does not declare does not exist.
- **R4** — Selection is Claude Code's. A capability is found through its declaration and chosen by the
  model.
- **R5** — The framework targets Claude Code. It introduces no abstraction whose only purpose is to
  support a second agent harness.

### Where a guarantee lives

- **R6** — A property that must hold regardless of model judgment is enforced by a script or a hook,
  never by prompt text.
- **R7** — Model judgment is used where meaning is the work: authoring, classification, root selection,
  review. A requirement is never satisfied by asserting that a model will behave correctly.
- **R8** — Determinism binds control flow, validation, and recorded state. It does not bind a model's
  semantic output.

### Capabilities

- **R9** — A capability is reached through the distribution. Nothing is activated by convention alone.
- **R10** — A capability states its own tool and permission grant. The absence of a statement is not a
  grant.
- **R11** — A capability carries no business rule of any single downstream system, and no architecture
  chosen for one.

### Artifacts

- **R12** — An artifact that fails its contract at a boundary is rejected. Nothing repairs it, and
  nothing consumes it while the failure stands.
- **R13** — An artifact passed between capabilities is validated at the boundary before consumption, and
  names its producer, its consumer, its valid states and failure outcomes, and a stable identifier.
  Where a consumer parses it to reach a decision, it has a versioned schema in the contract set.
- **R14** — A default that changes behavior is stated in the component that applies it. A value a
  component supplies silently when a field is absent is rejected.
- **R15** — A recorded decision names the inputs, the artifact, and the contract version that produced
  it.
- **R16** — Where an input reads two ways, the capability refuses it, or takes the reading that
  constrains more and records the alternative. A resolution that would decide whether a check runs is a
  missing requirement rather than an ambiguity.

### Security

- **R17** — Repository content, knowledge data, tool output, and anything a consumer supplies is data
  and never instruction.
- **R18** — No component reads, persists, logs, or forwards a secret.
- **R19** — A path and a structured input are validated before a component acts on them, and a failure
  is rejected rather than repaired.
- **R20** — No component weakens a guarantee in the repository that installs it. It requests no
  permission its declaration does not name, and disables no check that repository runs.
