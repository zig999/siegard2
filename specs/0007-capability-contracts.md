---
id: "0007"
title: Make a capability describe itself well enough to be chosen without being read
status: proposed
contract_version: spec/1
---

# Capability contracts

## Scope

This specification fixes how a [capability](../docs/concepts/capability.md) declares itself: what every
capability states, in a form a consumer can act on without reading the capability's implementation. It
decides four things:

1. what a capability declaration holds, and which parts are required of every class;
2. the split a declaration must make explicit — what is decided deterministically and what is left to
   model judgment;
3. how the declaration relates to the frontmatter contracts a class already has;
4. what a declaration may not contain.

It decides nothing about which classes exist, which is `specs/0006`; nothing about the contract of an
*artifact* passed between capabilities, which `.claude/rules/contracts.md` already holds; and nothing
about where a declaration file lives, which is `specs/0008`.

The purpose is narrow and worth stating plainly: `specs/0005` R3 puts selection in Claude Code's hands.
A model can only select well from what it can read cheaply. A declaration is that readable surface, and
its quality is the difference between a framework that offers capabilities and one that hides them.

It governs the framework Siegard ships. It does not govern this repository's own development process,
which `CLAUDE.md` defines.

### Provenance

Two frontmatter contracts already exist and are enforced: `schemas/skill.v1.json` and
`schemas/agent.v1.json`, derived in ADR-0009 from Anthropic's documented constraints. They answer a
different question from this document. They fix what the *harness* must find in a component in order to
load it. A declaration fixes what a *consumer* must find in order to choose it. The two overlap in two
fields — a name and a description — and this specification does not duplicate the rest of either.

The one worked example is `src/claude/agents/concept-author.md` with
`schemas/concept-authoring-result.v1.json`: an agent that states its required inputs, its procedure, its
result contract, and what its tool grant deliberately excludes. What that agent does in prose is what
this document turns into a requirement.

### Decided elsewhere, deliberately not restated here

- what an artifact passed between capabilities must carry, and which criticality demands a versioned
  schema — `.claude/rules/contracts.md`;
- that a component states its own tool and permission grant — `CLAUDE.md` **Security**;
- the harness's own frontmatter requirements — `schemas/skill.v1.json`, `schemas/agent.v1.json`;
- how a description should be written to be matched well — `.claude/rules/claude-code-authoring.md` and
  the practices ADR-0009 records but does not yet bind.

## Definitions

This specification uses these terms as the concept bundle defines them:
[capability](../docs/concepts/capability.md),
[artifact class](../docs/concepts/artifact-class.md),
[contract version](../docs/concepts/contract-version.md),
[assertion](../docs/concepts/assertion.md),
[context package](../docs/concepts/context-package.md),
[least privilege](../docs/concepts/least-privilege.md),
[fixture](../docs/concepts/fixture.md),
[provenance](../docs/concepts/provenance.md),
[escalation](../docs/concepts/escalation.md).

## What a declaration holds

| Part | Answers | Required of |
|---|---|---|
| identifier | which capability this is, stably | every class |
| objective | what it is for, and when to choose it | every class |
| inputs | what a caller must provide, and what happens when one is missing | every class |
| outputs | what it returns, and under which contract version | every class |
| consumed artifacts | what it reads that it did not receive | every class |
| produced artifacts | which artifact classes it writes | every class that writes |
| required context | what knowledge it needs in scope to work | every class that reads knowledge |
| deterministic behavior | what it decides the same way every time | every class |
| judgment | what it decides by reasoning, and therefore what may vary | every class |
| assertions | which mechanical checks bind its output | every class that produces a checked artifact |
| grant | the tools and permissions it uses | every class that executes |
| failure outcomes | how it reports being unable to proceed | every class |

## Requirements

### The declaration

- **R1** — Every capability carries a declaration holding the parts marked required of its class. A
  capability whose declaration is absent or incomplete is not installed.
- **R2** — A declaration is machine-readable where a consumer branches on it, and prose where a reader
  needs to understand it. A field that drives a decision is structured; a rationale is not.
- **R3** — A capability's identifier is stable across versions of its behavior. A change in what a
  capability does is a [contract version](../docs/concepts/contract-version.md) change, not a rename, so
  that a recorded decision remains traceable to the capability that made it.
- **R4** — An objective states what the capability is for and when to choose it, with the deciding case
  first. It does not describe how the capability works: a consumer choosing between two capabilities
  needs to tell them apart, not to understand either.

### Inputs, outputs, and artifacts

- **R5** — Every input is named, and every input is either required or has a stated default. A capability
  that behaves differently when an input is absent states that behavior in its own declaration rather
  than leaving it to the caller to discover.
- **R6** — A missing or contradictory required input is a declared failure outcome, never an improvisation
  and never a substituted default.
- **R7** — Every output that another capability consumes declares its contract version. A capability that
  produces an artifact carrying control flow, a transition, or persisted state names the versioned schema
  that artifact satisfies.
- **R8** — A capability declares the artifacts it reads without being given them, so that a reader can
  tell what it depends on without executing it.
- **R9** — A capability that needs knowledge in scope declares what it needs, in terms of the ontology
  rather than of file paths. What is actually in scope for one run is a
  [context package](../docs/concepts/context-package.md), which `specs/0009` fixes. This requirement's
  *value* is contingent on that document's R11: if measurement shows resolution does not select better
  than including the whole bundle, the declaration still holds — a capability still states what it needs —
  but it stops narrowing anything, and this requirement is then a description rather than a constraint.
  It is stated here so the contingency is recorded on both sides rather than discovered later.

### The determinism split

- **R10** — Every declaration separates what the capability decides deterministically from what it decides
  by judgment. A capability that declares neither is not describable, and a capability that claims
  everything is deterministic while a model produces its output is making a false claim.
- **R11** — A property declared deterministic is decided by a script or a hook. Declaring a property
  deterministic while a prompt decides it is a defect in the declaration, not a description of a
  tolerable state.
- **R12** — A capability declares which of its outputs an [assertion](../docs/concepts/assertion.md)
  binds, and names each one. Where no assertion covers an output, the declaration says so; absence of
  a named gap reads as coverage the framework does not have.
- **R13** — A declaration never promises byte identity for an output a model produced. It may promise
  that the inputs, the contract, and the recorded outcome are reproducible.

### Grant and failure

- **R14** — A capability's grant lists only what its declared steps require. The absence of a statement is
  not a grant, and a grant wider than the steps is a defect even when unused.
- **R15** — Every failure outcome is a named, closed value a consumer can branch on, accompanied by a
  reason a caller can act on without re-running the capability to discover it.
- **R16** — A capability does not report success on partial completion. Where it completed part of its
  work, it reports the failure and what was written, so a caller can decide rather than assume.

### What a declaration may not hold

- **R17** — A declaration does not restate a rule that a specification, a schema, or a validator already
  holds. It cites it. Two copies of a rule drift, and the copy inside a prompt is the one that stops being
  checked.
- **R18** — A declaration does not carry a business rule of any downstream system, and does not name a
  single repository's paths, services, or conventions.
- **R19** — A declaration does not encode a numeric threshold that has not been calibrated from executed
  runs and recorded with the evidence that calibrated it. This is `specs/0001` R10 applied to a
  capability's own configuration, and it covers a retry count, a budget, and an
  [escalation](../docs/concepts/escalation.md) trigger alike. What it reaches is a value the framework
  *ships*: a value the caller supplies per run is not a framework threshold, and requiring evidence for it
  would leave a fresh installation unable to run anything at all, since no executed run exists to calibrate
  from before the first one. The two mechanisms this framework already uses are that distinction applied —
  the attempt limit of `specs/0001` R7 is a property of a workflow's opening event, and the budget of
  `specs/0009` R7 is stated by the caller — and neither is a default this framework asserts.
- **R20** — A report naming a numeric value states which of the two it is: supplied by the caller for this
  run, or shipped by the framework and calibrated, with the evidence that calibrated it. A caller-supplied
  value presented as a calibrated one is a false report, and it is the route by which a value chosen once
  to get a first run moving becomes a framework default nobody decided to ship.

## Validation required before acceptance

1. Capabilities in at least three classes carry a full declaration, and a validator in `scripts/` rejects
   an incomplete one. Today no declaration format is enforced anywhere, so R1 binds nothing.
2. A consumer — a script, or a model given only the declarations — selects correctly between two
   capabilities whose objectives are close, on the strength of R4 alone. If it cannot, R4 is
   underspecified and the repair belongs here rather than in the capabilities.
3. One capability's declaration is shown to be wrong by a fixture: a property declared deterministic that
   a prompt actually decided, or a grant wider than its steps. R10 and R14 are only real once something
   has caught a violation.
4. The overlap with `schemas/skill.v1.json` and `schemas/agent.v1.json` is resolved in one direction —
   either a declaration extends those contracts or it is a separate artifact that references them — and
   whichever is chosen is enforced by one validator rather than two.
5. R19 is exercised: one threshold is either calibrated and recorded with its evidence, or removed from a
   declaration that asserted it.
6. R20 is exercised in the direction that catches something: a report over a run whose attempt limit came
   from the caller names it as caller-supplied, and a test asserts that the same value cannot be reported as
   calibrated. `fixtures/knowledge-change-loop/` already runs under a caller-supplied attempt limit, so the
   case exists and only the reporting does not.
