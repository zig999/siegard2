---
id: concept.orchestrator
type: term
title: orchestrator
description: The component that chooses a workflow transition by lookup on a validated artifact's closed field, and records what happened.
status: accepted
contract_version: concept/1
tags: [determinism, workflow]
generated: { by: claude-opus-5, at: 2026-07-31T00:35:31Z }
sources:
  - resource: specs/0001-knowledge-object-driven-development.md
    title: Drive every change through knowledge objects, with determinism at the boundaries
  - resource: .claude/rules/contracts.md
    title: Inter-agent artifact contracts
---

# orchestrator

The component that chooses a workflow transition by lookup on a closed field of an artifact that
passed its contract at the boundary, and records the result in the [event log](event-log.md).

An orchestrator holds control flow and nothing else. It does not author an artifact, does not judge
one's content, and does not decide whether a workflow may be accepted — `specs/0001` R21 reserves that
for a maintainer or a deterministic approval mechanism, so an orchestrator that accepted its own
workflow's output would be manufacturing the authority it is supposed to record.

Its choice is a table read. `specs/0001` R5 fixes this: a transition comes from a closed field, never
from interpreting prose. An orchestrator that has to read a narrative to decide what happens next is
evidence that the artifact it consumed is designed wrong — the repair belongs in that artifact's
schema, not in the orchestrator.

Because it is control flow rather than judgment, an orchestrator is a tested script and not a prompt.
`.claude/rules/claude-code-authoring.md` states where that logic belongs; the reason is that a
[transition guard](transition-guard.md) must be decidable the same way twice.

Whether `orchestrator` names a distinct component class the framework ships, or only a role that a
script fills, is not decided; `specs/0006` **Outstanding evidence** holds what would settle it.
