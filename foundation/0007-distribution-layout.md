---
id: "0007"
title: Ship the framework as a plugin a consumer can check without reading it
status: accepted
contract_version: spec/1
---

# Distribution layout

## Scope

What an installation must be true of: the tree it is, the records it carries, what an upgrade may not
do, and what the framework may not claim in the repository receiving it. These are properties a
consumer checks in the tree they installed.

Not here: what *this* repository must do to build one, which is `.claude/rules/distribution.md`; nor
which capability classes exist (`foundation/0005`).

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

`skills/`, `agents/`, `hooks/` and `bin/` are recognized by the harness and are how a capability
reaches a consumer. `schemas/`, `templates/` and `siegard-manifest.json` are Siegard's, resolved
through `${CLAUDE_PLUGIN_ROOT}`, and depend on no harness support.

## Requirements

### The distribution is a plugin

- **R1** — The distribution is a plugin root: a directory holding `.claude-plugin/plugin.json`.
- **R2** — `plugin.json` sets `version` explicitly. Without one a plugin falls back to its commit SHA,
  which no consumer can compare against a release.
- **R3** — A hook ships in `hooks/hooks.json` and is in force while the plugin is enabled.

### What a consumer can check

- **R4** — Every installed file is accounted for by the distribution manifest.
- **R5** — No installed file lacks a source, and none survives whose source was removed. No
  development-only path and no secret reaches the output.
- **R6** — An installation is reproducible from the framework version alone: two consumers on the same
  version hold byte-identical trees.

### The tree

- **R7** — The directory set above is closed. A component fitting none of these is not shipped until
  this specification names its home.
- **R8** — Only `plugin.json` goes inside `.claude-plugin/`. Every other directory sits at the plugin
  root.
- **R9** — A shipped executable lives in `bin/`, declares the runtime dependencies it requires, and
  exits with a named error rather than a traceback when one is absent.
- **R10** — The framework ships no rule file it depends on. `rules/` is not a recognized plugin
  directory, so a guarantee placed there would not load.

### The two records

- **R11** — An installation carries exactly two records, and each owns distinct fields. `plugin.json`
  holds identity, description and version; the distribution manifest holds everything else.
- **R12** — The distribution manifest records the source revision it was built from, the generator
  version, and every installed path with its digest.
- **R13** — A consumer reads the installed framework version from `plugin.json` and everything else
  from the manifest.
- **R14** — The distribution manifest is the provenance record for an installation: what is installed
  here, and from what.

### Installation and upgrade

- **R15** — Enabling the plugin is idempotent. Enabling one version twice leaves the repository in the
  state one enabling leaves it in.
- **R16** — An upgrade does not silently overwrite an installed file that diverges from what the
  previous version wrote. It stops and names the divergence.
- **R17** — Retiring a capability removes its files and its manifest entries together. A path left
  behind is a capability a consumer can still reach.

### What the framework may not claim

- **R18** — Installation adds no permission and disables no check in the receiving repository.
- **R19** — A skill carries no reserved prefix. The plugin's `name` is the namespace, and the harness
  applies it.
- **R20** — A consumer's own agent definition overrides a same-named plugin agent, and the framework
  reports the shadowing rather than resolving it silently.
- **R21** — The framework claims no path outside its own plugin root, and writes no file a repository's
  own tooling owns.

### Packs

- **R22** — A target pack is a separate plugin with its own version, installed and upgraded
  independently. `packs/` is not a directory of this one.

## Outstanding evidence

What this document states and nothing has exercised. A condition kept here is a debt; removing one
because the document binds would turn an open debt into a silent one.

1. `claude plugin validate` has never been run against the generated tree, so R1 through R3 are
   documented rather than demonstrated.
2. No hook ships, so R3 is unexercised in the direction that matters — a hook firing and denying.
3. Nothing exercises R15 through R17: no upgrade over an installed tree has been performed, and no
   locally modified file has been shown to stop one.
4. No target pack exists, so R22 is unexercised.
