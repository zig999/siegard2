---
id: concept.stack-knowledge
type: term
title: stack knowledge
description: A fact whose change changes every system built on the same technology, and which the knowledge base therefore never holds.
status: proposed
contract_version: concept/1
tags: [knowledge, kodd]
generated: { by: claude-opus-5, at: 2026-07-30T14:49:05Z }
sources:
  - resource: specs/0002-knowledge-economy-principles.md
    title: Hold the minimum knowledge specialized agents need to reproduce the system
---

# stack knowledge

A fact whose change changes *every* system built on the same technology: that table names are the
pluralized entity name, where a repository interface sits in the tree, the layering convention of a
project, how a guard clause is expressed idiomatically, how a by-identity reference becomes a foreign key.

Stack knowledge is not a smaller kind of [domain knowledge](domain-knowledge.md). It is a different kind,
and it differentiates one technology from another rather than one system from another. Its exclusion from
the [knowledge base](knowledge-base.md) is stated by `specs/0002-knowledge-economy-principles.md` rather
than here.

The reason is economic rather than aesthetic. Stack knowledge already exists inside a competent
[specialized agent](specialized-agent.md), so authoring it buys no differentiating content and costs
maintenance on every change — the failure the [representation ratio](representation-ratio.md) is
instrumented to expose.

Where stack knowledge *does* live is a separate question this term does not answer. Stating the boundary
negatively — the base does not hold it — keeps the boundary usable before that question is settled.
