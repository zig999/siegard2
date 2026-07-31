---
id: "0008"
title: Assemble the distribution as a function of source, and install it without squatting
status: proposed
contract_version: spec/1
---

# Distribution layout

## Scope

This specification fixes what the [distribution](../docs/concepts/distribution.md) contains and how it
reaches a repository Siegard governs. It decides five things:

1. that the distribution is a function of [framework source](../docs/concepts/framework-source.md), and
   what that makes checkable;
2. the closed set of directories, and what each one holds;
3. the manifest — what an installed distribution records about itself;
4. installation and upgrade, including what happens to a file the consumer changed;
5. namespacing, so that installing into a repository the framework does not control collides with
   nothing already there.

It decides nothing about which capability classes exist, which is `specs/0006`, and nothing about the
generator's implementation. It fixes the generator's *output contract*, which is a different thing: the
generator is free in how it assembles, and bound in what it may produce.

It governs the framework Siegard ships. It does not govern this repository's own development process,
which `CLAUDE.md` defines.

### Provenance

No generator exists. This document is therefore the one place in the framework family most at risk of
specifying something no code has met, and it is deliberately narrow for that reason: it fixes the output
contract and the failure modes that are already known, and leaves assembly unspecified.

Two of those failure modes are documented rather than speculative. ADR-0009 records that two agents with
the same name load by filesystem read order with no documented precedence — which is what makes R11 below
a correctness requirement rather than a courtesy. And `.claude/rules/distribution.md` records that a
distribution built by hand to make a rule appear satisfied is the thing this repository must not do,
which is why `docs/bootstrap.md` open question 2 gates the generator on reproducibility rather than on
existence.

### Decided elsewhere, deliberately not restated here

`.claude/rules/distribution.md` is the single authority for four rules this document depends on and does
not repeat: that a generated file is not hand-edited, that source-only paths are excluded and which
those are, that no secret or environment-specific value appears, and that a component with a behavioral
default states that default in itself. `CLAUDE.md` **Repository layout** holds the path table, and
**The two trees** in `.claude/rules/claude-code-authoring.md` holds the boundary between the tree that
ships and the tree that does not.

Where this specification and that rule file appear to overlap, the rule file wins and this document is
the defect.

## Definitions

This specification uses these terms as the concept bundle defines them:
[distribution](../docs/concepts/distribution.md),
[framework source](../docs/concepts/framework-source.md),
[capability](../docs/concepts/capability.md),
[skill](../docs/concepts/skill.md),
[specialized agent](../docs/concepts/specialized-agent.md),
[target pack](../docs/concepts/target-pack.md),
[contract version](../docs/concepts/contract-version.md),
[provenance](../docs/concepts/provenance.md),
[least privilege](../docs/concepts/least-privilege.md).

## The tree

```
dist/.claude/
  agents/      one specialized agent per file, nesting permitted
  skills/      one directory per skill, holding SKILL.md
  hooks/       hook programs, and the settings fragment that binds them to events
  rules/       path-scoped invariants that load in the governed repository
  templates/   expansion sources, grouped by the artifact class each produces
  packs/       one directory per target pack
  schemas/     the artifact contracts a governed repository validates against
  scripts/     the deterministic logic hooks and skills invoke
  siegard.json the manifest
```

One directory per capability class of `specs/0006`, plus `schemas/` for the contracts and `rules/` for
invariants that are neither. Nothing else is installed.

## Requirements

### The distribution is a function

- **R1** — The distribution is determined by the framework source and the generator version. Running the
  generator twice over the same committed source produces byte-identical output, and a difference is a
  defect in the generator rather than an acceptable variation.
- **R2** — Every installed file originates in framework source or is computed by the generator from it.
  No file is introduced that has no source, and no file survives in the output whose source was removed.
- **R3** — Verification of the distribution is separate from producing it. The command that checks
  regenerates into a temporary location and compares; it never writes into the distribution it is
  checking, because a check that repairs what it was meant to detect reports success on a defect.

### The tree

- **R4** — The directory set above is closed. A component that fits none of these directories is not
  installed until this specification names a home for it, and a directory with nothing in it is omitted
  rather than shipped empty.
- **R5** — A directory holds one class of thing. `scripts/` holds no component definition, `agents/`
  holds no template, and `schemas/` holds no instance of the artifacts it constrains.
- **R6** — A shipped script declares the runtime dependencies it requires and exits with a named error
  when one is absent. A script that degrades silently in a repository whose environment differs is worse
  than one that refuses to run.

### The manifest

- **R7** — The distribution carries a manifest recording: the framework version, the source revision it
  was built from, the generator version, every installed path, and the
  [contract version](../docs/concepts/contract-version.md) of every schema it ships.
- **R8** — A consumer can determine which framework version is installed by reading the manifest alone,
  without inspecting component contents or inferring from what happens to be present.
- **R9** — The manifest is the [provenance](../docs/concepts/provenance.md) record for an upgrade: a
  later run compares against it to decide what changed, so an upgrade is a diff against a recorded state
  rather than an overwrite of an unknown one.

### Installation and upgrade

- **R10** — Installation is idempotent. Installing the same version twice leaves the repository in the
  same state as installing it once, and produces no duplicate component under a different name.
- **R11** — An upgrade does not silently overwrite an installed file that diverges from what the manifest
  records. It detects the divergence, names the file, and stops. A consumer's local change is either
  theirs to keep or theirs to discard; it is never the framework's to erase without saying so.
- **R12** — Retiring a capability removes its files and its manifest entries together. A path left behind
  after retirement is an orphan that a later reader will mistake for an installed capability.
- **R13** — Installation adds no permission and disables no check in the receiving repository. A
  component's grant is stated in the component, and the installation of the framework is not the moment
  a grant widens.

### Namespacing

- **R14** — Every installed component's name carries the framework's reserved prefix. Two agents with the
  same name load by filesystem read order with no documented precedence, so a generic name in a
  repository the framework does not control is a correctness hazard and not a matter of taste.
- **R15** — The framework claims no path outside its own directories in the receiving repository, and
  writes no file that a repository's own tooling owns.
- **R16** — Where the framework must contribute to a shared configuration file, it contributes a fragment
  the consumer adopts rather than rewriting a file the consumer maintains. Two documented mechanisms carry
  a hook without editing `settings.json`: a skill or subagent may declare hooks in its own frontmatter,
  and a plugin bundles `hooks/hooks.json` and is enabled as a unit
  (https://code.claude.com/docs/en/hooks, retrieved 2026-07-31). The first is scoped to that component's
  lifetime by `specs/0010` R18, so a session-wide guarantee is carried by the plugin form or installed by
  the consumer deliberately — never by the framework editing a file it does not own.

## Validation required before acceptance

1. A generator exists, `make dist` runs it, and running it twice from the same source produces identical
   output. R1 through R3 are unenforced until then — `docs/bootstrap.md` open question 2.
2. A test asserts that no source-only path and no secret reaches the output, per the exclusion list in
   `.claude/rules/distribution.md`.
3. A fixture installs the generated distribution into a downstream-shaped repository, Claude Code loads
   the installed components, and the loop of `docs/bootstrap.md` stage 2 runs against them. This is what
   turns R10 through R13 from description into behavior, and it is also ADR-0009 condition 2.
4. A second fixture upgrades an installed distribution over a locally modified file and is shown to stop
   rather than overwrite, covering R11 in the direction that matters.
5. R14 is applied to the components that already exist. `concept-author` and `knowledge-change` carry
   unprefixed names today, so either they are renamed before anything consumes them or this requirement
   is wrong and must be replaced by a namespacing mechanism that does not depend on names.
6. The manifest has a versioned schema in `schemas/`, since a consumer branches on it — which
   `.claude/rules/contracts.md` already requires of an artifact carrying persisted state.
