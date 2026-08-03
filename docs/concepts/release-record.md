---
id: concept.release-record
type: term
title: release record
description: What changed between one framework version and the last, read to decide whether to upgrade.
status: accepted
contract_version: concept/1
tags: [framework, lifecycle]
generated: { by: claude-opus-5, at: 2026-07-31T01:49:02Z }
sources:
  - resource: foundation/0013-framework-lifecycle.md
    title: Version the framework so a break is always announced, and a migration is always executable
---

# release record

What changed between one framework version and the one before it: every
[contract version](contract-version.md) shipped, every one dropped, every [capability](capability.md) whose
[lifecycle](lifecycle.md) status changed, and the harness versions the release was verified against.

A consumer reads it to decide whether to upgrade, rather than diffing two distributions. Where a release
breaks compatibility it says so here, names what breaks, and points to the migration — which is what makes a
documented break legible without reading the specifications that decided it.

It answers *what changed between versions*, which neither of the other two records answers: the
[distribution manifest](distribution-manifest.md) describes one installation as it stands, and the
[generation manifest](generation-manifest.md) records where a generation put its artifacts.
