---
id: concept.change-request
type: term
title: change request
description: The recorded request that originates every change to a repository Siegard governs.
status: accepted
contract_version: concept/1
tags: [workflow, kodd]
generated: { by: claude-opus-5, at: 2026-07-30T01:59:07Z }
sources:
  - resource: foundation/0001-knowledge-object-driven-development.md
    title: Drive every change through knowledge objects, with determinism at the boundaries
---

# change request

The recorded request that originates every change to a repository Siegard governs. No workflow phase
runs without one, so a change with no request is not a fast path — it is work outside the framework.

A change request states what is being asked, not how to build it. A request that specifies the solution
has done modelling that a later capability is accountable for, and done it where nothing records whether
the request stated it or somebody decided it.

Its contract is `change-request/1`, and it arrived late for a reason worth keeping: the specification that
requires a request for every change also deferred its schema, and the deferral held until three
capabilities declared the artifact without a contract version — which the rule on declared prerequisites
then made impossible. The body stays prose, because a request explains what someone wants; the contract
adds identity, provenance, and the one field a predicate reads. `type` is `ordinary | regulatory`, two
values because exactly one [escalation](escalation.md) predicate reads it and a third would be a
distinction nothing consumes.

It is a temporary artifact. It never becomes a [knowledge object](knowledge-object.md): a request is an
event in a project's history, while a knowledge object states something that stays true after the
request is closed.

The workflow it enters, and the phases that follow, are defined in
`foundation/0001-knowledge-object-driven-development.md`, which was accepted on 2026-07-31. This concept is
therefore eligible for promotion and has not been promoted: a status change is a maintainer's decision, and
`index.md` records the eligibility rather than acting on it — see [accepted](accepted.md).
