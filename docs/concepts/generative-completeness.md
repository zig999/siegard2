---
id: concept.generative-completeness
type: term
title: generative completeness
description: Whether a generation scope holds every domain fact production needs, evaluated as a blocking validation.
status: accepted
contract_version: concept/1
tags: [generation, validation, kodd]
generated: { by: claude-opus-5, at: 2026-07-30T15:26:04Z }
sources:
  - resource: foundation/0004-generation-and-reproducibility.md
    title: Produce the system from knowledge, and lock what reproduces it
---

# generative completeness

Whether a [generation scope](generation-scope.md) holds every [domain knowledge](domain-knowledge.md) fact
production needs: attributes fully typed, identities declared, stateful definitions carrying a total
[lifecycle](lifecycle.md), every [rule](rule.md) expressible or exemplified, every reference resolving.

Completeness is a validation, and it blocks. A gap is tolerable where knowledge is documentation, because a
reader works around it; it is fatal where knowledge produces software, because whatever reads the gap must
either stop or invent, and invention is how the same knowledge stops producing the same system.

Completeness covers domain facts only. A missing naming convention is not an incompleteness, because
[stack knowledge](stack-knowledge.md) is not a fact the knowledge base was ever meant to hold.

It is **not** the maturity ladder of spec 0001. The ladder measures binding force — nothing, review,
mechanical rejection. Completeness measures sufficiency for production. A rule can be complete and
unasserted, or carry an [assertion](assertion.md) inside a scope that is incomplete. Two axes, deliberately
orthogonal, and reporting one as the other misstates both.

Nor does it contradict [fail-soft](fail-soft.md): resolution reports a gap and continues, validation
rejects, and the two act at different phases.
