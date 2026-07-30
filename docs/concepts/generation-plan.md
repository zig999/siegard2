---
id: concept.generation-plan
type: term
title: generation plan
description: The derived, inspectable list of what one generation will produce, validated before any file is written.
status: proposed
contract_version: concept/1
tags: [generation, determinism, kodd]
generated: { by: claude-opus-5, at: 2026-07-30T15:26:04Z }
sources:
  - resource: specs/0004-generation-and-reproducibility.md
    title: Produce the system from knowledge, and lock what reproduces it
---

# generation plan

The derived list of what one generation will produce: for each entry, the knowledge object, the
[artifact class](artifact-class.md), the [track](generation-track.md), and whether the entry is **locked** —
a path already recorded in the [generation manifest](generation-manifest.md) — or **new**.

A plan is a consequence, never a design. It is derived from a [generation scope](generation-scope.md), a
[target pack](target-pack.md)'s declaration, and the manifest, and it holds no rule of its own. A plan
someone authors would be a second representation competing with the knowledge it came from.

Two properties earn the plan its existence. It is **validated before any file is written** — every reference
resolves, every class is declared, no two entries claim one path, every locked path still exists — so a
defect surfaces before the filesystem changes. And it is **inspectable without writing**, which makes a dry
run possible.

The locked-or-new flag is what lets a diff mean something: variation in a new entry is expected, variation in
a locked entry is a finding.

A target-path collision is reported as a defect rather than resolved by a policy. Two objects competing for
one path is a modelling error or an agent error, and a rule that silently picked a winner would hide both.

Its [persistence](artifact-persistence.md) is `run-scoped`. A plan is a function of the scope, the pack
declaration, and the manifest, so keeping one would store what those three already determine.
