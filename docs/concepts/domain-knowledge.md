---
id: concept.domain-knowledge
type: term
title: domain knowledge
description: A fact whose change changes this system, and the only kind of fact the knowledge base holds.
status: accepted
contract_version: concept/1
tags: [knowledge, kodd]
generated: { by: claude-opus-5, at: 2026-07-30T14:49:05Z }
sources:
  - resource: specs/0002-knowledge-economy-principles.md
    title: Hold the minimum knowledge specialized agents need to reproduce the system
---

# domain knowledge

A fact whose change changes *this* system: that a proposal expires after thirty days, that a monetary
amount carries scale two, which attributes form an identity, which state transitions are legal, what a
bounded context publishes.

Domain knowledge is what the [knowledge base](knowledge-base.md) holds, and the only thing it holds. The
test that places a fact here rather than in [stack knowledge](stack-knowledge.md) is differentiation:
domain knowledge distinguishes this system from another system built on the same technology.

The test is deliberately about differentiation rather than about what an agent happens to know. What an
agent knows is not observable and cannot be validated; what differentiates two systems can be argued from
two knowledge bases.
