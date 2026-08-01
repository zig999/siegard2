---
id: concept.event-log
type: term
title: event log
description: An append-only record of facts, kept by a repository rather than by the framework.
status: accepted
contract_version: concept/1
tags: [determinism, state]
generated: { by: claude-opus-5, at: 2026-07-31T21:30:00Z }
sources:
  - resource: foundation/0005-runtime-architecture.md
    title: Let Claude Code execute, and let the framework provide capabilities and contracts
---

# event log

An append-only record in which each entry states something that happened rather than the state that
resulted. State over such a record is computed by replaying it, so the two cannot disagree.

**The framework keeps none.** `foundation/0005` R23 states that Siegard refuses rather than sequences: it
ships no component that records where a run stands and none that resumes one. `foundation/0001` R8, which
required workflow state persisted outside the conversation, is retired for the same reason, and the
append-only log that satisfied it was removed —
`docs/adr/0016-remove-the-workflow-machinery.md`.

The term survives for two live uses, and both are about a log the framework does not own.

A governed repository may keep one, and `foundation/0005` R21 reaches it: a value that authenticates
something does not enter an artifact, an event log, or a report. A component that encounters a secret does
not carry it forward into a record the repository will keep.

And it names what would answer the one loss the removal is most likely to be asked about. Work interrupted
halfway leaves nothing that says where it stopped. Should that need answering, what returns is the
smallest durable record of what was already done — not the machinery that was removed, and not a component
that decides what runs next.

An earlier definition called this "the sole durable source for workflow history" and named the framework's
own append-only log as how the architecture satisfied a requirement. Both statements described a mechanism
this framework no longer has.
