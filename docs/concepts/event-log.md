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
  - resource: CLAUDE.md
    title: Siegard Code repository instructions
---

# event log

The append-only record of workflow facts, persisted outside the conversation. Each entry states
something that happened, not the state that resulted.

It is the sole durable source for workflow history. Conversation history and auto memory are not: both
are context, both can be truncated or rewritten, and neither is normative.

`CLAUDE.md` under **Determinism and state** requires workflow state to be persisted outside the
conversation; an append-only log is one way to satisfy that, and it is not yet decided. The term is
defined here because rules reference it; the architecture it implies binds nothing yet — see
`docs/bootstrap.md` for the stage that will settle it.
