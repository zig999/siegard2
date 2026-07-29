---
id: concept.event-log
type: term
title: event log
description: The append-only record of workflow facts, persisted outside the conversation.
status: accepted
contract_version: concept/1
tags: [determinism, state]
generated: { by: claude-opus-5, at: 2026-07-29T16:33:28Z }
sources:
  - resource: docs/adr/0001-event-sourced-workflow-state.md
    title: Derive workflow state from an append-only event log
---

# event log

The append-only record of workflow facts, persisted outside the conversation. Each entry states
something that happened, not the state that resulted.

It is the sole durable source for workflow history. Conversation history and auto memory are not: both
are context, both can be truncated or rewritten, and neither is normative.

The decision to model state this way is recorded in ADR-0001, which is `proposed` — see
[accepted](accepted.md). The term is defined here because rules reference it; the architecture it
implies binds nothing yet.
