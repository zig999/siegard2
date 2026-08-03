---
id: "0006"
title: Close the set of capability classes, and give each one thing it owns
status: accepted
contract_version: spec/1
---

# The capability model

## Scope

This specification fixes what a [capability](../docs/concepts/capability.md) is as a unit of the Siegard
product, which classes of capability exist, what each class owns, and how one enters and leaves the
framework. It decides four things:

1. the closed set of capability classes, and the rule for adding a class to it;
2. what each class owns, and what it may not own;
3. admission — what must be true before a declared behavior is a capability;
4. the lifecycle a capability follows, through to retirement.

It decides nothing about how a capability *declares* itself, which is `foundation/0007`; nothing about where
the distribution puts one, which is `foundation/0008`; and nothing about the internals of hooks, templates, or
packs, each of which has its own specification. `foundation/0005` fixes the frame this fills: it is R9 through
R13 there that this document makes specific.


### Provenance

The classes below are the ones the framework has, plus the ones a specification already commits it to.
How many are occupied is not restated here, and an earlier version of this paragraph is why: it said
"two", stayed at two while a hook and a skill were built, and a reader trusted it. The count is derived
on every run — the [distribution manifest](../docs/concepts/distribution-manifest.md) records the class of
each installed capability under `foundation/0008` R12, which is R17 applied rather than described. Read
it there.

What the manifest cannot settle is which classes are occupied by a capability as against by an artifact
that merely resembles one. The template class is the case worth naming: what `src/claude/templates/` holds
is [scaffolds](../docs/concepts/scaffold.md), which that concept distinguishes from a template, so they
ship without occupying the class. A real template belongs to a
[target pack](../docs/concepts/target-pack.md), and no pack is distributed.

Two classes the original framework plan proposed are not here. **Command** is absent because custom
commands were merged into skills; the invocation `/name` survives, the class does
not, and `scripts/validate_components.py` rejects `src/claude/commands/` by name. **Worker** is absent
because a unit of work with one role is a specialized agent; `worker` is vocabulary from the v0.1 draft,
which was normative nowhere and is no longer in this repository.

### Decided elsewhere, deliberately not restated here

- what a capability is, in one sentence — [capability](../docs/concepts/capability.md);
- that a component states its own tool and permission grant — `foundation/0005` R11;
- where instruction content belongs, given the harness's loading semantics —
  `foundation/0012`, which fixes the target pack as a unit, and `foundation/0004`, which fixes what one declares;
- the frontmatter a skill and an agent must carry — `schemas/skill.json`, `schemas/agent.json`;
- breaking change and migration rules — `foundation/0013` R3a and R10–R12.

## Definitions

This specification uses these terms as the concept bundle defines them:
[capability](../docs/concepts/capability.md),
[skill](../docs/concepts/skill.md),
[specialized agent](../docs/concepts/specialized-agent.md),
[target pack](../docs/concepts/target-pack.md),
[distribution](../docs/concepts/distribution.md),
[fixture](../docs/concepts/fixture.md),
[artifact class](../docs/concepts/artifact-class.md),
[projection](../docs/concepts/projection.md),
[least privilege](../docs/concepts/least-privilege.md),
[contract version](../docs/concepts/contract-version.md).

## The classes

| Class | Owns | Loaded or run by |
|---|---|---|
| skill | an invocable procedure, and the only entry point a user reaches | the harness, on `/name` or by description match |
| specialized agent | producing exactly one validated artifact from one role | the harness, when delegated to |
| hook | enforcing one guarantee at a lifecycle event | the harness, unconditionally at that event |
| script | durable control flow, state derivation, and validation | a skill, a hook, or a maintainer |
| template | expanding into one artifact class | a script or an agent that owns the expansion |
| target pack | one technology stack: its agents and its templates | selected per repository, not per request |

The set covers what **executes or is delegated to**. A [projection](../docs/concepts/projection.md), a
schema, a rule file, and a knowledge object are **artifacts**: they are what capabilities consume and
produce, they are shipped where a consumer needs them, and none of them is a capability class. A shipped
artifact therefore needs no entry here, which is what lets `foundation/0008` install `schemas/` without this
document growing a class for it.

## Requirements

### The set of classes

- **R1** — The classes above are the closed set of things that execute or are delegated to. A *component*
  that fits none of them is not shipped until a class for it exists, and adding a class requires its own
  contract and at least one capability occupying it. A shipped
  *artifact* is not a component and needs no class.
- **R2** — A class with no capability in it is removed rather than kept open. An empty class invites a
  component to be shaped to fit the framework instead of the work.
- **R3** — One class owns each decision. Where two classes could each hold a rule, the rule goes to the
  one whose contract can test it, and the other cites it.

### What each class owns

- **R4** — A skill holds a procedure and is the only class a user invokes directly. There is no command
  class. A skill whose effects reach outside the session declares that it is not model-invocable, so that
  a side effect is never triggered by a description match.
- **R5** — A specialized agent has exactly one role and produces exactly one artifact class. It does not
  choose the next phase, does not delegate to another agent, and does not run the validator that checks
  its own output — a guarantee a producer self-reports is not a guarantee.
- **R6** — An agent's tool grant is the minimum its role requires, stated in the agent itself. An agent
  that only reads and writes files does not receive a shell.
- **R7** — A hook holds exactly one guarantee, so that a denial names a single condition and a hook can be
  retired without taking another guarantee with it. That a guarantee is enforced by a hook rather than by
  model judgment, and that a hook rejects rather than repairs, are `foundation/0005` R5 and R22 and are cited
  here rather than restated. `foundation/0010` fixes how a hook honors them.
- **R8** — A script holds state derivation and validation, and it is never prompt text.

  An earlier form added *durable control flow* and named a script as where an orchestrator's logic lives.
  Both are gone: `foundation/0005` R23 states that the framework does not sequence, and R5 there was
  narrowed to keep control flow out of the class of things a script must decide. A script that sequenced
  capabilities would be the component R2 of that document forbids, whatever tree it sat in.
- **R9** — A template expands into exactly one [artifact class](../docs/concepts/artifact-class.md) and
  names the schema its output must satisfy. A template that can produce two unrelated artifact classes is
  two templates. A template belongs to a [target pack](../docs/concepts/target-pack.md), or to the framework
  where its artifact class is independent of technology — `foundation/0011` R15 owns that division.
- **R10** — A target pack carries one technology stack, holding one producer for each artifact class it
  declares: a template for a class on the deterministic track, a specialized agent for a class on the judged
  track. `foundation/0004` R13 and R51 own that correspondence and this requirement does not restate it; what
  matters here is that R5 above is what forces it, since an agent producing exactly one artifact class
  cannot cover a pack that declares two judged ones. A pack carries no business rule and nothing specific to
  a single downstream repository, which is `foundation/0005` R13 applied rather than restated here.

### Admission

- **R11** — A behavior becomes a capability when it has a declared contract and something exercises
  it — a test, a fixture, an eval, or a run in a consuming repository. A [fixture](../docs/concepts/fixture.md)
  is one such evidence and never a condition of shipping: nothing is withheld from the distribution for
  want of one.
- **R12** — A capability declares a [contract version](../docs/concepts/contract-version.md) for every
  artifact it produces that another capability consumes. A consumer selects behavior on that version and
  never infers it from an artifact's shape.
- **R13** — A capability is reached through the [distribution](../docs/concepts/distribution.md), never
  through a path a consumer is expected to know by convention.

### Lifecycle

- **R14** — A capability is `proposed`, `active`, `deprecated`, or `retired`. `proposed` ships nothing;
  `active` is installed; `deprecated` is installed, still working, and documented as going away;
  `retired` is absent from the distribution.
- **R15** — A capability moves to `deprecated` before `retired`, and the deprecation names the
  replacement or states plainly that none exists. Removing an installed capability without that step is a
  breaking change made silently.
- **R16** — Retiring a capability that another consumed requires the migration
  `foundation/0013` R3a demands, and a test that fails against the old behavior.
- **R17** — A capability's status is derived from checkable facts — whether the distribution installs it,
  and whether it is documented as going away — and not from a label maintained by hand. The
  [distribution manifest](../docs/concepts/distribution-manifest.md) carries the status of each installed
  capability under `foundation/0008` R12, which is what makes the `deprecated` state of R14 observable from an
  installation rather than only from a release.

## Outstanding evidence

What this document states and nothing has yet exercised. A condition kept here is a debt;
removing one because the document binds would turn an open debt into a silent one.

1. At least one capability exists in each of at least four classes, each with a fixture. Today two
   classes are occupied, so R1's closed set is a commitment rather than a demonstrated division of work.
2. One class is dropped or one is added on the evidence of R2, showing the set is genuinely revisable
   rather than fixed by this document.
3. A hook enforces a guarantee under test with both outcomes covered, so R7 constrains something that
   exists.
4. One capability completes the full lifecycle of R14 through R16, including the migration, so that
   deprecation is a mechanism rather than a described intention.
5. A deterministic check derives capability status per R17. Until then the statuses in this framework are
   maintained by reading, which R17 forbids as the permanent answer.
