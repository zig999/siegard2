---
id: concept.fail-soft
type: term
title: fail-soft
description: Context resolution degrades instead of blocking, and acceptance is evaluated independently of the context that was read.
status: proposed
contract_version: concept/1
tags: [kodd, determinism, validation]
generated: { by: claude-opus-5, at: 2026-07-30T01:59:07Z }
sources:
  - resource: specs/0001-knowledge-object-driven-development.md
    title: Drive every change through knowledge objects, with determinism at the boundaries
---

# fail-soft

Two properties that only work together.

**Resolution degrades instead of blocking.** Where context resolution cannot satisfy a selection rule —
a root it cannot locate, a cycle it cannot resolve, contradictory knowledge, an exhausted budget — it
records the degradation in the [context package](context-package.md) and the workflow continues. The
v0.1 draft required resolution to fail and forbade implementation from starting, which stops a project
on the knowledge gaps it is trying to fill.

**Acceptance is evaluated independently of what was read.** The checks that decide acceptance are
computed from the [impact analysis](impact-analysis.md) artifact, the [knowledge
graph](knowledge-graph.md), and the actual diff — never from the context package the implementer
consumed. The validation closure covers every knowledge object the diff touches, whether or not impact
analysis named it, so independence does not leak when an implementation touches a path outside its plan.

Without the second property, the first is just permission to work from incomplete knowledge.

## What it does not guarantee

Fail-soft guarantees that acceptance is evaluated **independently**. It does not guarantee that an
invalid implementation cannot be accepted. The strength of the evaluation is mechanical where the
impacted [knowledge object](knowledge-object.md) carries an [assertion](assertion.md), and independent
review where it does not — and independent review is mitigation, not a guarantee.

The acceptance gate reports which of the two applied for each impacted knowledge object, and names every
gap. A report that presents review as a guarantee is a false report.
