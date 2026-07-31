---
id: "0008"
title: Ship the framework as a plugin, so enabling it installs the enforcement
status: accepted
contract_version: spec/1
---

# Distribution layout

## Scope

This specification fixes what the [distribution](../docs/concepts/distribution.md) contains and how it
reaches a repository Siegard governs. It decides six things:

1. that the distribution is a Claude Code plugin, and what the harness therefore provides;
2. what a consumer can check about the installation they hold, and what its manifest accounts for;
3. the closed set of directories — those the harness recognizes, and those that are Siegard's own;
4. the two records an installation carries, and which fields each owns;
5. installation and upgrade, including what happens to a file the consumer changed;
6. namespacing and shadowing, and why no component carries a reserved prefix.

It decides nothing about which capability classes exist, which is `specs/0006`, and nothing about how a
distribution is assembled or verified. This document binds the result, not the build: it states what must
be true of a distribution in a consumer's hands, and says nothing about who produced it or how.


### Provenance

No generator exists, so nothing here has been exercised. What has changed since the first draft of this
document is that its central assumption was wrong, and the documentation said so.

That draft described a tree copied into the consumer's `.claude/`, with a reserved name prefix on every
component. Two reviews found it failing on its own terms: it could not install its own hooks, because every
hook named below is a session-wide guarantee and this document forbade rewriting a
`settings.json` it does not own; and its `scripts/` directory was an invented convention. The plugin form
resolves both, and removes the prefix requirement rather than satisfying it.

### Sources

Normative for every harness behavior relied on here, retrieved 2026-07-31, with the full citation in
the plugin documentation:

- https://code.claude.com/docs/en/plugins — the plugin root, the recognized directories, the manifest and
  its `name` as skill namespace, `version` and the commit-SHA fallback, hooks in `hooks/hooks.json`,
  executables in `bin/`, the restriction of plugin `settings.json` to two keys, and that a project or user
  agent definition overrides a same-named plugin agent while a skill does not;
- https://code.claude.com/docs/en/hooks — `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}`.

A behavior absent from those pages on that date is not relied on, and R10 below is what that rule produced.

### Decided elsewhere, deliberately not restated here

How a distribution is assembled and verified — regenerating for byte identity, comparing into a
temporary tree, never hand-editing the output, which paths a build excludes — is not stated here, because
none of it is something a consumer satisfies or observes. A build obligation is answerable to whoever
runs the build, and naming that party would put this document in the business of describing a producer
rather than a product.

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

### What the distribution is, as a consumer can check it

These are properties of the artifact in a consumer's hands, verifiable from the installation itself,
with no access to whatever produced it.

- **R4** — Every installed file is accounted for by the [distribution manifest](../docs/concepts/distribution-manifest.md):
  it names the framework source the file came from and a digest of what was installed. A consumer can
  therefore tell what they hold apart from what they were meant to hold, without the framework's source.
- **R5** — No installed file lacks a source, and none survives whose source was removed. An installation
  is exactly what its framework version defines and carries no residue of an earlier one.
- **R5b** — The distribution carries only what a consumer needs to run the framework. A path that exists
  to develop the framework — its specifications, tests, fixtures, explanatory documentation, and the
  development environment that governs its own repository — is absent. A consumer who received one could
  not tell a rule they must satisfy from a rule that governed the people who built it.
- **R5c** — No secret, credential, token, or environment-specific value appears anywhere in the
  distribution. An absolute path true only on the machine that built it is such a value.
- **R6** — An installation is reproducible from the framework version alone: two consumers on the same
  version hold byte-identical trees. This is what makes R4's digest comparable across installations
  rather than local to one.

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
  [generation manifest](../docs/concepts/generation-manifest.md)'s field and not this one. The distribution
  manifest and the generation manifest answer different questions — what is installed here, and where did a
  generation put things — and neither is called "the manifest" without its qualifier where both could be
  meant. (The pair R11 closes is a different pair: `plugin.json` and the distribution manifest are the two
  records an *installation* carries, while a generation manifest belongs to a governed repository and is
  never installed.)

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

## Outstanding evidence

What this document states and nothing has yet exercised. A condition kept here is a debt;
removing one because the document binds would turn an open debt into a silent one.

1. A generator exists, `make dist` runs it, running it twice from the same source produces identical output,
   and `claude plugin validate` passes on the result. R4 through R6 are unenforced until then —
   the gate below.
2. A test asserts that no development-only path and no secret reaches the output, per R5b and R5c.
3. A fixture loads the generated plugin with `--plugin-dir`, Claude Code loads its components, and the loop
   of the first end-to-end run runs against them. This is what turns R1
   through R3 and R16 through R19 from description into behavior.
4. One hook ships in `hooks/hooks.json` and is shown to fire and to deny in the loaded fixture. R3 is the
   central claim of this document's design, and it is documented rather than demonstrated until then.
5. A second fixture upgrades an installed distribution over a locally modified file and is shown to stop
   rather than overwrite, covering R17 in the direction that matters.
6. The shadowing check of R21 exists: a fixture installs the plugin into a repository holding an agent of
   the same name and the framework reports it.
7. The distribution manifest has a versioned schema in `schemas/`, since a consumer branches on it — which
   `specs/0005` R16a already requires of an artifact carrying persisted state. It arrives with
   the generator that first produces one.
8. A target pack ships as a second plugin and installs and versions independently, exercising R23.
