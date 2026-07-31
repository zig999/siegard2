---
id: "0012"
title: Admit one stack at a time, and let a pack assume its technology instead of abstracting over it
status: accepted
contract_version: spec/1
---

# The target pack model

## Scope

This specification fixes the [target pack](../docs/concepts/target-pack.md) as a distributable unit. It
decides five things:

1. that exactly one pack is active in a governed repository, and what that buys;
2. what a pack is composed of, and what it may not contain;
3. how a pack's version relates to the framework's, and which contracts it declares itself against;
4. what changing or retiring a pack owes the artifacts already generated from it;
5. isolation — that no pack depends on another, and no pack extends a framework-owned vocabulary.

It does not decide what a pack *declares*. `foundation/0004` is the authority for that, and
[target pack](../docs/concepts/target-pack.md) already records the shape: identity, version, and the
artifact classes it produces with the track of each and the node types each is yielded by, and nothing
else. This document decides the unit around that declaration.


### Provenance

No pack exists, and no fixture exercises one. This document is therefore written entirely from decisions
already taken elsewhere, and its own contribution is deliberately small: five requirements about the unit,
and a set of inheritances it does not restate.

The one thing it adds that nothing else holds is the consequence of the single-pack rule. That a pack may
*assume* its technology rather than abstract over it is what makes a template concrete enough to promise
byte identity, and it is the reason the framework can refuse the vendor-neutral indirection that
`foundation/0005` R4 forbids. Stating that consequence is the work here; the rest is
citation.

### Decided elsewhere, deliberately not restated here

- what a pack declares, and what it must leave to its agent's own knowledge of the stack — `foundation/0004`,
  with the shape recorded in [target pack](../docs/concepts/target-pack.md);
- that a pack is framework work rather than the architecture of one downstream system — `foundation/0005` R13;
  and that a fixture is optional evidence rather than a condition of admission — `foundation/0005` R12;
- that a pack carries one stack, holds one producer per declared artifact class, and carries no business
  rule — `foundation/0006` R10;
- the closed vocabulary of [artifact classes](../docs/concepts/artifact-class.md) and the
  [track](../docs/concepts/generation-track.md) each is produced on — `foundation/0004`;
- every constraint on the templates a pack owns — `foundation/0011`;
- that each of a pack's agents has one role, produces one artifact class, and receives the minimum tool
  grant its role requires — `foundation/0006` R5 and R6;
- that a target path the manifest does not lock comes from a validated, frozen
  [placement decision](../docs/concepts/placement-decision.md) — `foundation/0004` R52;
- breaking change and migration rules — `foundation/0013` R3a and R10–R12.

## Definitions

This specification uses these terms as the concept bundle defines them:
[target pack](../docs/concepts/target-pack.md),
[stack knowledge](../docs/concepts/stack-knowledge.md),
[domain knowledge](../docs/concepts/domain-knowledge.md),
[artifact class](../docs/concepts/artifact-class.md),
[generation track](../docs/concepts/generation-track.md),
[generation manifest](../docs/concepts/generation-manifest.md),
[placement decision](../docs/concepts/placement-decision.md),
[specialized agent](../docs/concepts/specialized-agent.md),
[knowledge object](../docs/concepts/knowledge-object.md),
[capability](../docs/concepts/capability.md),
[fixture](../docs/concepts/fixture.md),
[contract version](../docs/concepts/contract-version.md),
[distribution](../docs/concepts/distribution.md).

## Requirements

### One pack

- **R1** — The active pack is recorded in the governed repository's own configuration, before any generation
  runs, rather than inferred from what happens to be installed. That exactly one pack is active is
  `foundation/0004`'s decision, not this document's; what this requirement adds is that the choice is a written
  fact, because a pack inferred from installation makes the technology of a generated artifact a function of
  resolution order.
- **R2** — Because one pack is active, a pack assumes its technology. It introduces no abstraction whose
  purpose is to accommodate a second stack, and no indirection that exists in case one is added later.
- **R3** — The active pack is recorded in the [generation manifest](../docs/concepts/generation-manifest.md)
  with its version, so that reproducing a generation names the pack that produced it. An artifact whose
  producing pack is unknown cannot be reproduced and cannot be safely regenerated.

### Composition

- **R4** — A pack ships nothing beyond the [specialized agents](../docs/concepts/specialized-agent.md) and
  templates that `foundation/0004` R13 and R51 compose it from — one producer per declared artifact class: no
  [knowledge object](../docs/concepts/knowledge-object.md), no schema, and no hook. The schema a template's
  output is validated against belongs to the artifact class and is framework-owned, so a pack that shipped one
  would be extending a vocabulary R6 reserves to the framework. Enforcement stays framework-owned for the same
  reason: a hook decides what is permitted, and a pack that could ship one could permit what the framework
  denies.
- **R5** — A pack holds stack knowledge only. Naming, layout, layering, idiom, and how a construct becomes a
  storage representation are its business, and none of them appears in an authored knowledge artifact.
- **R6** — A pack maps node types to the artifact classes they yield, and **declares** the mapping, per
  `foundation/0004` R14. Owning the fact and declaring it are separate questions, and an earlier draft of this
  requirement answered only the first: the mapping sat in the pack while nothing model-free could read it,
  which left `foundation/0004` R23's plan derivation with no way to know what a knowledge object demands. A pack
  does not extend the artifact class vocabulary, which is framework-owned: a class a pack needs and the
  framework does not hold is a request to change `foundation/0004`.
- **R7** — A pack declares nothing its own agent already knows **and nothing model-free needs to read**. Path
  derivation, expansion order, and naming rules meet both conditions — they are the agent's competence, and
  the only thing that consumes them is the agent itself — so declaring them re-authors stack knowledge the
  framework deliberately does not hold. The node-type mapping of R6 fails the second condition, which is why
  it is declared and these are not. A target path is the case that looks like an exception and is not: it is
  read by the plan, but through the frozen
  [placement decision](../docs/concepts/placement-decision.md) of `foundation/0004` R52 rather than through a
  declared derivation rule.

### Version and compatibility

- **R8** — A pack is its own plugin, carrying its own version in its own plugin manifest, and declares the
  [contract versions](../docs/concepts/contract-version.md) it was built against. A consumer can therefore
  tell whether an installed pack and an installed framework are compatible without running them, and adding
  a stack requires no framework release — see `foundation/0008` R23 and.
- **R9** — A framework contract change that invalidates a conforming pack is a breaking change, and the pack
  is versioned rather than silently expected to keep working.
- **R10** — A pack that no longer declares itself against any supported framework contract version is
  refused at installation rather than loaded and allowed to fail during generation.

### Change and retirement

- **R11** — Replacing the active pack is a breaking change for every artifact generated from the previous
  one. The change states what must be regenerated and what cannot be, and it does not present a pack swap as
  a configuration adjustment.
- **R12** — Retiring a pack removes its agents and templates together with its manifest entries, and names
  the replacement or states that none exists.
- **R13** — A pack is admitted with a fixture, which is what demonstrates the pack serves any repository on
  its stack rather than the one repository it was extracted from. Retirement is not the mirror of that and
  does not get a second fixture invented for symmetry: what retiring a pack owes is the migration and the
  test that fails against the old behavior, which `foundation/0006` R16 already requires of any capability
  another consumed.

### Isolation

- **R14** — No pack depends on another pack, reads another pack's templates, or extends another pack's agent.
  A shared expansion is framework-owned or duplicated deliberately.
- **R15** — A pack carries no fact about a single downstream repository. This is the constraint most likely
  to be violated when a pack is extracted from a working system, because everything in that system looks
  like a convention until a second repository disagrees.

## Outstanding evidence

What this document states and nothing has yet exercised. A condition kept here is a debt;
removing one because the document binds would turn an open debt into a silent one.

1. One pack exists and a fixture exercises it end to end, producing at least one artifact on each
   [generation track](../docs/concepts/generation-track.md). Every requirement here is unexercised.
2. A **second** pack exists for a different stack. R2, R6, and R14 cannot be validated by one pack: a single
   pack always looks isolated, always looks like it assumes nothing improper, and never tests whether the
   artifact class vocabulary is genuinely technology-independent. This is the condition most likely to
   falsify the model, and it is the reason one working pack must not be treated as
   sufficient evidence.
3. R15 is tested by extracting a pack from one real repository and running it against a second on the same
   stack, with every fact the second repository disagrees with recorded. A pack that cannot survive that is
   the downstream architecture `foundation/0005` R13 excludes, wearing a pack's name.
4. A pack swap is performed under R11, showing what regeneration recovers and what it does not.
5. Where a pack's source lives is settled. `foundation/0004` R13 states a pack is distributed together
   under `src/claude/`; `foundation/0008` R23 states a pack is a separate plugin and that the framework
   distribution contains no pack, and its directory listing has no `packs/`. A pack under
   `src/claude/` would be emitted into the framework distribution, which R23 forbids; a pack
   anywhere else contradicts R13. Both are accepted at equal precedence with no supersession, so
   this is recorded and left for a maintainer rather than resolved by whichever document a script
   reads first. Nothing reaches a real pack before the generation pipeline needs one, so the
   decision is owed then. A fixture pack has a home already and does not depend on it.
