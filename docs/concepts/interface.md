---
id: concept.interface
type: term
title: interface
description: The knowledge object type describing what a bounded context exposes to, or consumes from, another.
status: proposed
contract_version: concept/1
tags: [knowledge, kodd, ddd, compatibility]
generated: { by: claude-opus-5, at: 2026-07-30T15:19:55Z }
sources:
  - resource: specs/0003-knowledge-ontology-and-notation.md
    title: Represent domain knowledge as a typed ontology in an AI-first notation
---

# interface

The [knowledge object](knowledge-object.md) type that answers "what does this context expose or consume": a
domain event, an integration event, a published language, or an exposed API.

An interface is the only type that carries a version, because it is the only type with a consumer outside
its own [boundary](boundary.md). It also declares whether it is published or consumed: a published interface
is one this repository can break and must therefore version, while a consumed one belongs to someone else.

An interface is what a reference crossing a bounded context must target. A definition in one context
reaching directly into a definition in another is the coupling bounded contexts exist to prevent, and
routing the reference through an interface is the form that check takes.

**Not an artifact contract.** `.claude/rules/contracts.md` and `contract_version` concern contracts *between
framework components* — a schema a producer and a consumer agree on. This term concerns a *domain* interface
between bounded contexts. The two were deliberately given different names so that one word does not denote
both; see [contract version](contract-version.md) for the other sense.
