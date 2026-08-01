---
id: "0005"
title: Close the set of capability classes, and give each one thing it owns
status: accepted
contract_version: spec/1
---

# The capability model

## Scope

What a capability is as a unit of the Siegard product: which classes exist, what each owns, what admits
one, and how one is retired.

Not here: how a capability declares itself (`foundation/0006`).

## The classes

| Class | Owns | Run by |
|---|---|---|
| skill | an invocable procedure | the harness, on `/name` or by description match |
| specialized agent | producing exactly one validated artifact from one role | the harness, when delegated to |
| hook | enforcing one guarantee at a lifecycle event | the harness, unconditionally at that event |
| script | state derivation and validation | a skill, a hook, or a maintainer |
| template | expanding into one artifact class | a script or an agent that owns the expansion |
| target pack | one technology stack: its agents and its templates | selected per repository |

## Requirements

### The set

- **R1** — The classes above are the closed set of things that execute or are delegated to. A component
  that fits none of them is not shipped until a class for it exists, and adding a class requires its own
  contract and at least one capability occupying it. An artifact is not a component and needs no class.
- **R2** — A class with no capability in it is removed rather than kept open.
- **R3** — One class owns each decision. Where two classes could each hold a rule, the rule goes to the
  one whose contract can test it.

### What each class owns

- **R4** — A skill holds a procedure and is the only class a user invokes directly. A skill whose effects
  reach outside the session declares that it is not model-invocable, so that a side effect is never
  triggered by a description match.
- **R5** — A specialized agent has exactly one role and produces exactly one artifact class. It does not
  choose what runs next, does not delegate to another agent, and does not run the validator that checks
  its own output.
- **R6** — An agent's tool grant is the minimum its role requires, stated in the agent itself. An agent
  that only reads and writes files does not receive a shell.
- **R7** — A hook holds exactly one guarantee, so that a denial names a single condition and a hook can
  be retired without taking another guarantee with it.
- **R8** — A script holds state derivation and validation, and it is never prompt text.
- **R9** — A template expands into exactly one artifact class and names the schema its output must
  satisfy. A template that can produce two unrelated artifact classes is two templates.
- **R10** — A target pack carries one technology stack, holding one producer for each artifact class it
  declares. A pack carries no business rule and nothing specific to a single downstream repository.

### Admission

- **R11** — A behavior becomes a capability when it has a declared contract and something exercises
  it — a test, a fixture, an eval, or a run in a consuming repository. A fixture is one such evidence and
  never a condition of shipping.
- **R12** — A capability declares a contract version for every artifact it produces that another
  capability consumes. A consumer selects behavior on that version and never infers it from shape.
- **R13** — A capability is reached through the distribution, never through a path a consumer is expected
  to know by convention.

### Lifecycle

- **R14** — A capability is `proposed`, `active`, `deprecated`, or `retired`. `proposed` ships nothing;
  `active` is installed; `deprecated` is installed, still working, and documented as going away;
  `retired` is absent from the distribution.
- **R15** — A capability moves to `deprecated` before `retired`, and the deprecation names the
  replacement or states plainly that none exists.
- **R16** — Retiring a capability another consumed requires a migration and a test that fails against the
  old behavior.
- **R17** — A capability's status is derived from checkable facts — whether the distribution installs it,
  and whether it is documented as going away — never from a label maintained by hand.
