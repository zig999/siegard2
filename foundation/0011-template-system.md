---
id: "0011"
title: Hold a template to byte identity, and give it no way to reach outside its inputs
status: accepted
contract_version: spec/1
---

# The template system

## Scope

This specification fixes what a template is and what it may do. It decides five things:

1. what a template produces, and the guarantee that makes it a template rather than an agent;
2. what a template may read — and the reaches that byte identity forbids;
3. how a template refers to knowledge, and what it does when knowledge is missing;
4. the split between the [stack knowledge](../docs/concepts/stack-knowledge.md) a template holds and the
   [domain knowledge](../docs/concepts/domain-knowledge.md) it must never hold;
5. ownership, override, and versioning.

It decides nothing about the vocabulary of [artifact classes](../docs/concepts/artifact-class.md) or which
track each is produced on, which `foundation/0004` fixes; nothing about what a
[target pack](../docs/concepts/target-pack.md) declares, which is `foundation/0012`; and nothing about a
template's syntax, which is implementation.


### Provenance

No template exists, and a scaffold directory is a path to create when
the first artifact needs it. Templates arrive with the first artifact that needs one.

The determinism requirements below are not speculative, though. R4 through R6 are the generalization of a
defect this framework already hit and fixed once: an early draft of the workflow event contract ordered
entries by their timestamp, which made replay depend on a clock the framework does not control, and the
correction was to order by an explicit sequence and require the caller to supply every instant and
identifier. A template promising byte identity has exactly the same exposure, and R4 through R6 are that
lesson written down before a template can repeat it.

### Decided elsewhere, deliberately not restated here

- the closed vocabulary of artifact classes, and the [generation track](../docs/concepts/generation-track.md)
  each is produced on — `foundation/0004`;
- what byte identity means as a promise, and which artifacts carry it rather than behavioural conformance
  — `foundation/0004`, which is also the authority for
  [artifact persistence](../docs/concepts/artifact-persistence.md);
- that the mapping from a node type to the classes it yields belongs to a pack rather than to the framework,
  and is declared by it — [artifact class](../docs/concepts/artifact-class.md), `foundation/0004` R14;
- that a template expands into exactly one artifact class and names its output's schema — `foundation/0006` R9;
- what a capability declares about itself — `foundation/0007`.

## Definitions

This specification uses these terms as the concept bundle defines them:
[artifact class](../docs/concepts/artifact-class.md),
[generation track](../docs/concepts/generation-track.md),
[generation plan](../docs/concepts/generation-plan.md),
[generation scope](../docs/concepts/generation-scope.md),
[generation manifest](../docs/concepts/generation-manifest.md),
[generative completeness](../docs/concepts/generative-completeness.md),
[knowledge object](../docs/concepts/knowledge-object.md),
[domain knowledge](../docs/concepts/domain-knowledge.md),
[stack knowledge](../docs/concepts/stack-knowledge.md),
[target pack](../docs/concepts/target-pack.md),
[contract version](../docs/concepts/contract-version.md),
[artifact persistence](../docs/concepts/artifact-persistence.md).

## Requirements

### What a template is

- **R1** — A template is the mechanism of the deterministic
  [generation track](../docs/concepts/generation-track.md), expanding structured knowledge into exactly one
  artifact class. What that track promises — no model in the loop, and identical input yielding
  byte-identical output — is defined by that concept and by `foundation/0004`, listed above as inherited, and is
  not restated here. This requirement binds the definition to an artifact; R2 states what follows from it.
- **R2** — A template that cannot hold byte identity is not a weaker template. Its artifact class moves to
  the judged track and a [specialized agent](../docs/concepts/specialized-agent.md) produces it instead.
  This is the consequence the inherited definition does not carry, and it is this document's own
  contribution: the guarantee is never relaxed to keep the mechanism, because a promise that bends once
  bends per exception until nothing tests it.
- **R3** — A template's output is validated against the schema the template names, before it is written. An
  artifact that fails is rejected, and nothing downstream consumes it.

### What a template may read

- **R4** — A template reads only its declared inputs. It reads no clock, no environment variable, no
  random source, no network, and no file its inputs did not name. Each of those is a way for output to
  differ between two runs over the same knowledge, which R2 forbids.
- **R5** — Where an output must carry a timestamp, an identifier, a version, or any other value the
  knowledge does not hold, that value is supplied as an input by the caller and recorded in the
  [generation manifest](../docs/concepts/generation-manifest.md). The template never mints one.
- **R6** — Iteration over a collection follows a total order derived from the knowledge itself. Directory
  order, mapping insertion order, and hash order are not orders; they are sources of a diff nobody
  authored.
- **R7** — A template performs no side effect beyond producing its declared output. It writes no other
  file, mutates no input, and records nothing outside the manifest.

### Knowledge, and its absence

- **R8** — A template refers to knowledge by its ontology identifier, never by file path. A path is a fact
  about how a repository is arranged, and a template that depends on one breaks when the arrangement
  changes without the knowledge changing.
- **R9** — A template reads only within the [generation scope](../docs/concepts/generation-scope.md) it was
  given. Reaching outside the scope makes the recorded scope a description of intention rather than of what
  was read.
- **R10** — A missing required input is a failure naming what is absent. A template never substitutes a
  default for a domain fact the knowledge does not hold: a default invented at expansion time is a domain
  fact authored by the framework, which is what
  [generative completeness](../docs/concepts/generative-completeness.md) exists to prevent.
- **R11** — A branch in a template reads a closed field of a knowledge object. A template does not branch on
  prose, on the presence of a substring, or on anything a reader would have to interpret.

### What a template holds, and what it must not

- **R12** — A template holds stack knowledge: naming, layout, idiom, and how a construct is expressed in its
  technology. This is the template's purpose, and none of it is authored in the knowledge base.
- **R13** — A template holds no domain knowledge and no business rule. Every domain fact in the output comes
  from a knowledge object, so that changing a fact means changing knowledge rather than editing a template.
- **R14** — A template carries nothing specific to a single downstream repository — no service name, no
  environment, no path a particular system chose — which is `foundation/0005` R13 applied to the artifact where
  hard-coding one is easiest. A template serves every repository on its stack.

### Ownership, override, and versioning

- **R15** — A template is owned by exactly one target pack, or by the framework where its artifact class is
  independent of technology. Two packs do not share a template; a shared expansion is either framework-owned
  or duplicated deliberately.
- **R16** — A consumer does not edit a shipped template in place. An override is a declared replacement
  recorded in the [distribution manifest](../docs/concepts/distribution-manifest.md) under `foundation/0008` R12,
  so that a later upgrade can tell a customization from a divergence and stop rather than overwrite.
- **R17** — A template's contract version changes whenever its output changes for the same input. That is a
  change every consumer can observe in a diff, so it is a version bump under
  `foundation/0013` R3a rather than a revision. The bump rate for a template is therefore high —
  reformatting whitespace in produced output is a bump — and that is the price of R2 rather than a defect in
  this rule. A maintainer who finds the rate intolerable has found an argument about which artifact classes
  belong on the deterministic track at all, not a licence to skip the bump quietly.
- **R18** — A template does not decide whether its output is committed, recomputed, or discarded. That is the
  artifact class's persistence, fixed by `foundation/0004`.

## Outstanding evidence

What this document states and nothing has yet exercised. A condition kept here is a debt;
removing one because the document binds would turn an open debt into a silent one.

1. One template exists, produces one artifact class, and a fixture expands it. Every requirement here is
   unexercised.
2. A test expands the same knowledge twice and asserts byte-identical output, and a second test asserts that
   a template reaching for a clock or an environment variable is detected. R2 without R4 tested is a promise
   with an open door behind it.
3. R6 is tested against a collection whose natural traversal order differs from its declared order — the
   case that produces a spurious diff and is invisible in a fixture with one element.
4. R10 is tested in the failing direction: expansion over knowledge missing a required fact reports the gap
   rather than emitting a default.
6. One artifact class is moved from the deterministic track to the judged track, or the reverse, on the
   evidence of R2 — showing the track is a measured property rather than a label assigned once.
