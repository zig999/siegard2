---
id: concept.impact-analysis
type: term
title: impact analysis
description: The phase that decides whether a change request requires permanent knowledge to change.
status: accepted
contract_version: concept/1
tags: [workflow, kodd, determinism]
generated: { by: claude-opus-5, at: 2026-07-30T01:59:07Z }
sources:
  - resource: specs/0001-knowledge-object-driven-development.md
    title: Drive every change through knowledge objects, with determinism at the boundaries
---

# impact analysis

The phase that decides whether a [change request](change-request.md) requires permanent knowledge to
change. It produces a validated artifact carrying a verdict from the closed set `none`, `update`,
`create`, and naming every implicated [knowledge object](knowledge-object.md) and ADR by identifier.

It runs for every change request, including one whose verdict turns out to be `none`. It is on the
default path for two reasons: it is the decision function for [escalation](escalation.md), so skipping
it leaves nothing to decide against; and it is cheap, because it classifies a request against the
[knowledge graph](knowledge-graph.md) rather than authoring knowledge.

Its verdict is a closed field, which is what lets an orchestrator choose the next transition by lookup
rather than by reading prose — see [transition guard](transition-guard.md).

Impact analysis is also one half of the closure that decides acceptance. The other half is the observed
diff, and the two are unioned so that independence does not depend on the analysis being complete — see
[fail-soft](fail-soft.md).
