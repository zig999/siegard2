---
id: concept.distribution-manifest
type: term
title: distribution manifest
description: The record of what an installation carries, held beside the plugin manifest the harness reads.
status: accepted
contract_version: concept/1
tags: [framework, distribution]
generated: { by: claude-opus-5, at: 2026-07-31T01:49:02Z }
sources:
  - resource: .claude/rules/distribution.md
    title: Building the distribution
  - resource: docs/adr/0012-distribute-the-framework-as-a-claude-code-plugin.md
    title: Distribute the framework as a Claude Code plugin, and let the harness namespace it
---

# distribution manifest

The record of what an installation of the [distribution](distribution.md) carries: the source revision it
was built from, the generator version, every installed path, the [contract version](contract-version.md) of
every schema shipped, each [capability](capability.md)'s [lifecycle](lifecycle.md) status, and every
declared override.

It answers one question — *what is installed here, right now* — and it is the reason an upgrade is a diff
against a recorded state rather than an overwrite of an unknown one.

It sits beside, and never duplicates, the plugin manifest. `plugin.json` is the harness's record and carries
identity and version because the harness reads them; this record is Siegard's, and carries what nothing else
does.

Distinct from the generation manifest, which records where each produced artifact
went. Two records with the same short name is the failure
`docs/adr/0010-projection-names-the-graph-derived-artifact.md` exists to undo, so neither is called "the
manifest" without its qualifier.
