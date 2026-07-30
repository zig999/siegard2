---
id: concept.change-request
type: term
title: change request
description: The recorded request that originates every change to a repository Siegard governs.
status: proposed
contract_version: concept/1
tags: [workflow, kodd]
generated: { by: claude-opus-5, at: 2026-07-30T01:59:07Z }
sources:
  - resource: specs/0001-knowledge-object-driven-development.md
    title: Drive every change through knowledge objects, with determinism at the boundaries
  - resource: reference/SIGARD_Workflow_Specification_v0.1.md
    title: SIGARD Workflow Specification v0.1
---

# change request

The recorded request that originates every change to a repository Siegard governs. No workflow phase
runs without one, so a change with no request is not a fast path — it is work outside the framework.

A change request states what is being asked, not how to build it. It carries a `type` whose closed
vocabulary the change request contract defines; spec 0001 requires `regulatory` to be one of its values,
because an [escalation](escalation.md) predicate reads it.

It is a temporary artifact. It never becomes a [knowledge object](knowledge-object.md): a request is an
event in a project's history, while a knowledge object states something that stays true after the
request is closed.

The workflow it enters, and the phases that follow, are defined in
`specs/0001-knowledge-object-driven-development.md`, which is `proposed` — see [accepted](accepted.md).
