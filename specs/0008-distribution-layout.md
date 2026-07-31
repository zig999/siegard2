---
id: "0008"
title: Ship the framework as a plugin, so enabling it installs the enforcement
status: proposed
contract_version: spec/1
---

# Distribution layout

## Scope

This specification fixes what the [distribution](../docs/concepts/distribution.md) contains and how it
reaches a repository Siegard governs. It decides six things:

1. that the distribution is a Claude Code plugin, and what the harness therefore provides;
2. that its content is a function of [framework source](../docs/concepts/framework-source.md);
3. the closed set of directories — those the harness recognizes, and those that are Siegard's own;
4. the two records an installation carries, and which fields each owns;
5. installation and upgrade, including what happens to a file the consumer changed;
6. namespacing and shadowing, and why no component carries a reserved prefix.

It decides nothing about which capability classes exist, which is `specs/0006`, and nothing about the
generator's implementation. It fixes the generator's *output contract*: the generator is free in how it
assembles and bound in what it may produce.

It governs the framework Siegard ships. It does not govern this repository's own development process,
which `CLAUDE.md` defines.

### Provenance

No generator exists, so nothing here has been exercised. What has changed since the first draft of this
document is that its central assumption was wrong, and the documentation said so.

That draft described a tree copied into the consumer's `.claude/`, with a reserved name prefix on every
component. Two reviews found it failing on its own terms: it could not install its own hooks, because every
hook `docs/bootstrap.md` names is a session-wide guarantee and this document forbade rewriting a
`settings.json` it does not own; and its `scripts/` directory was an invented convention. The plugin form
resolves both, and removes the prefix requirement rather than satisfying it.
`docs/adr/0012-distribute-the-framework-as-a-claude-code-plugin.md` records the decision and its sourcing.

### Sources

Normative for every harness behavior relied on here, retrieved 2026-07-31, with the full citation in
ADR-0012:

- https://code.claude.com/docs/en/plugins — the plugin root, the recognized directories, the manifest and
  its `name` as skill namespace, `version` and the commit-SHA fallback, hooks in `hooks/hooks.json`,
  executables in `bin/`, the restriction of plugin `settings.json` to two keys, and that a project or user
  agent definition overrides a same-named plugin agent while a skill does not;
- https://code.claude.com/docs/en/hooks — `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}`.

A behavior absent from those pages on that date is not relied on, and R10 below is what that rule produced.

### Decided elsewhere, deliberately not restated here

`.claude/rules/distribution.md` is the single authority for four rules this document depends on and does
not repeat: that a generated file is not hand-edited, that source-only paths are excluded and which those
are, that no secret or environment-specific value appears, and that a component with a behavioral default
states that default in itself. `CLAUDE.md` **Repository layout** holds the path table, and **The two trees**
in `.claude/rules/claude-code-authoring.md` holds the boundary between the tree that ships and the tree that
does not. Where this specification and that rule file appear to overlap, the rule file wins and this
document is the defect.

## Definitions

This specification uses these terms as the concept bundle defines them:
[distribution](../docs/concepts/distribution.md),
[distribution manifest](../docs/concepts/distribution-manifest.md),
[generation manifest](../docs/concepts/generation-manifest.md),
[framework source](../docs/concepts/framework-source.md),
[capability](../docs/concepts/capability.md),
[skill](../docs/concepts/skill.md),
[specialized agent](../docs/concepts/specialized-agent.md),
[target pack](../docs/concepts/target-pack.md),
[contract version](../docs/concepts/contract-version.md),
[provenance](../docs/concepts/provenance.md),
[least privilege](../docs/concepts/least-privilege.md),
[lifecycle](../docs/concepts/lifecycle.md).

## The tree

```
dist/.claude/                      the plugin root
  .claude-plugin/
    plugin.json                    read by the harness: name, description, version
  skills/<name>/SKILL.md           invoked as /<plugin>:<name>
  agents/*.md                      one specialized agent per file, nesting permitted
  hooks/hooks.json                 in force while the plugin is enabled
  bin/                             executables, on the Bash tool's PATH while enabled
  schemas/                         Siegard's own; the harness does not read these
  templates/                       Siegard's own
  siegard-manifest.json            Siegard's own record of what was installed
```

Two groups, and the difference matters. `skills/`, `agents/`, `hooks/`, and `bin/` are recognized by the
harness and are how a capability reaches a consumer. `schemas/`, `templates/`, and `siegard-manifest.json`
are Siegard's, resolved through `${CLAUDE_PLUGIN_ROOT}`, and depend on no harness support at all.

`packs/` is absent. A [target pack](../docs/concepts/target-pack.md) is its own plugin — see R23.

## Requirements

### The distribution is a plugin

- **R1** — The distribution is a plugin root: a directory holding `.claude-plugin/plugin.json`. Enabling the
  plugin installs every capability it carries, and no file the consumer maintains is rewritten to achieve
  it.
- **R2** — `plugin.json` sets `version` explicitly. A plugin without one falls back to its commit SHA, which
  makes every commit a release and takes the framework's version out of the framework's hands.
- **R3** — Hooks ship in `hooks/hooks.json` and are in force while the plugin is enabled. This is what makes
  a session-wide guarantee installable, and it is the reason this document specifies a plugin rather than an
  overlay.

### The distribution is a function

- **R4** — The distribution is determined by the framework source and the generator version. Running the
  generator twice over the same committed source produces byte-identical output, and a difference is a
  defect in the generator rather than an acceptable variation.
- **R5** — Every installed file originates in framework source or is computed by the generator from it. No
  file is introduced that has no source, and no file survives whose source was removed.
- **R6** — Verification is separate from production. The command that checks regenerates into a temporary
  location and compares; it never writes into the distribution it is checking, because a check that repairs
  what it was meant to detect reports success on a defect.

### The tree

- **R7** — The directory set above is closed. A component that fits none of these is not shipped until this
  specification names a home for it, and a directory with nothing in it is omitted rather than shipped
  empty.
- **R8** — Only `plugin.json` goes inside `.claude-plugin/`. Every other directory sits at the plugin root;
  a component placed inside `.claude-plugin/` is not loaded.
- **R9** — A shipped executable lives in `bin/`, declares the runtime dependencies it requires, and exits
  with a named error when one is absent. A script that degrades silently in a repository whose environment
  differs is worse than one that refuses to run.
- **R10** — The framework ships no rule file it depends on. `rules/` is not a recognized plugin directory,
  so whether a shipped path-scoped invariant loads at all is unverified. An invariant that must hold is a
  hook; an invariant that may be advisory is carried by the component it governs.

### The two records

- **R11** — An installation carries exactly two records, and each owns distinct fields. `plugin.json` is the
  harness's: identity, description, version. The
  [distribution manifest](../docs/concepts/distribution-manifest.md) is Siegard's, and nothing in it
  duplicates the other.
- **R12** — The distribution manifest records the source revision it was built from, the generator version,
  every installed path, the [contract version](../docs/concepts/contract-version.md) of every schema
  shipped, each capability's [lifecycle](../docs/concepts/lifecycle.md) status, and every declared override.
- **R13** — A consumer reads the installed framework version from `plugin.json` and everything else from the
  distribution manifest, without inspecting component contents or inferring from what happens to be
  present.
- **R14** — The distribution manifest is the [provenance](../docs/concepts/provenance.md) record for an
  upgrade: a later run compares against it to decide what changed, so an upgrade is a diff against a
  recorded state rather than an overwrite of an unknown one.
- **R15** — Where a produced artifact's placement must be recorded, that is the
  [generation manifest](../docs/concepts/generation-manifest.md)'s field and not this one. The two records
  answer different questions — what is installed here, and where did a generation put things — and neither
  is called "the manifest" without its qualifier.

### Installation and upgrade

- **R16** — Enabling the plugin is idempotent. Enabling the same version twice leaves the repository in the
  same state as enabling it once, and produces no duplicate component under a different name.
- **R17** — An upgrade does not silently overwrite an installed file that diverges from what the
  distribution manifest records. It detects the divergence, names the file, and stops. A consumer's local
  change is either theirs to keep or theirs to discard; it is never the framework's to erase without saying
  so.
- **R18** — Retiring a capability removes its files and its manifest entries together. A path left behind
  after retirement is an orphan a later reader will mistake for an installed capability.
- **R19** — Installation adds no permission and disables no check in the receiving repository. A plugin's
  `settings.json` supports only `agent` and `subagentStatusLine`, and the framework sets neither: activating
  an agent as the main thread would replace how the consumer's Claude Code behaves by default.

### Namespacing and shadowing

- **R20** — A skill carries no reserved prefix. The plugin's `name` is the namespace and the harness applies
  it, so a prefix would be both redundant and visible in every invocation.
- **R21** — A consumer's own agent definition overrides a same-named plugin agent. The framework detects and
  reports that shadowing rather than trying to prevent it by choosing an unlikely name: the precedence
  resolves in the consumer's favour, which is correct, and the exposure is a capability silently lost rather
  than a load order nobody can predict. A name chosen to be improbable is a convention hoped to work; a
  check is a check.
- **R22** — The framework claims no path outside its own plugin root, and writes no file that a repository's
  own tooling owns.

### Packs

- **R23** — A [target pack](../docs/concepts/target-pack.md) is a separate plugin with its own version, and
  the framework distribution contains no pack. `specs/0004` R17 states the framework ships no default pack,
  so a `packs/` directory inside this distribution would be one the framework's own rules guarantee is
  always empty.

## Validation required before acceptance

1. A generator exists, `make dist` runs it, running it twice from the same source produces identical output,
   and `claude plugin validate` passes on the result. R4 through R6 are unenforced until then —
   `docs/bootstrap.md` open question 2.
2. A test asserts that no source-only path and no secret reaches the output, per the exclusion list in
   `.claude/rules/distribution.md`.
3. A fixture loads the generated plugin with `--plugin-dir`, Claude Code loads its components, and the loop
   of `docs/bootstrap.md` stage 2 runs against them. This is ADR-0009 condition 2, and it is what turns R1
   through R3 and R16 through R19 from description into behavior.
4. One hook ships in `hooks/hooks.json` and is shown to fire and to deny in the loaded fixture. R3 is the
   central claim of this document's design, and it is documented rather than demonstrated until then.
5. A second fixture upgrades an installed distribution over a locally modified file and is shown to stop
   rather than overwrite, covering R17 in the direction that matters.
6. The shadowing check of R21 exists: a fixture installs the plugin into a repository holding an agent of
   the same name and the framework reports it.
7. The distribution manifest has a versioned schema in `schemas/`, since a consumer branches on it — which
   `.claude/rules/contracts.md` already requires of an artifact carrying persisted state. It arrives with
   the generator that first produces one.
8. A target pack ships as a second plugin and installs and versions independently, exercising R23.
