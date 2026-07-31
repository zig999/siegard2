---
id: concept.escalation
type: term
title: escalation
description: The insertion of workflow phases, decided by a predicate over fields of a validated artifact.
status: accepted
contract_version: concept/1
tags: [workflow, kodd, determinism]
generated: { by: claude-opus-5, at: 2026-07-30T01:59:07Z }
sources:
  - resource: foundation/0001-knowledge-object-driven-development.md
    title: Drive every change through knowledge objects, with determinism at the boundaries
---

# escalation

The insertion of workflow phases beyond the default path, decided by a predicate over fields of a
validated artifact. Knowledge authoring, ADR review, and detailed planning are inserted this way.

Escalation is never decided by an agent's judgment about how large a change feels. The predicate reads a
closed or countable field — an [impact analysis](impact-analysis.md) verdict, a set of implicated
identifiers, a change request `type` — so the same inputs escalate the same way twice. That makes it a
[transition guard](transition-guard.md) rather than a recommendation.

A numeric threshold inside a predicate is calibrated from workflows that actually ran, and recorded with
the evidence that calibrated it. A threshold chosen on paper is a guess with a comparison operator
around it.

**A validation failure is not an escalation.** It is a return edge of the state machine: the workflow
goes back to implementation under a stated attempt limit, and the knowledge object of the failed check
becomes a mandatory root of the next resolution. Treating a failure as an escalation confuses control
flow with workflow composition, and makes the phase list depend on how many times something went wrong.
