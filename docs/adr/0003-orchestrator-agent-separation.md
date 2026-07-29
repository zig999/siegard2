---
id: "0003"
title: Separate orchestration from specialized agent work
status: proposed
contract_version: adr/1
---

# Separate orchestration from specialized agent work

## Context

A single agent that both advances a workflow and performs its semantic work has no boundary at which
state can be validated, and no place to restrict tools. Its context mixes workflow bookkeeping with
task content, and the same prompt ends up holding both the rule and its application.

## Decision

Split responsibilities across components, each with one authority:

- **commands** — thin user-facing entry points; validate input, start or resume a workflow, delegate;
- **orchestrators** — advance workflows and dispatch bounded work; own transitions, not task content;
- **specialized agents** — one declared role each, with the minimum tools that role requires;
- **skills** — reusable procedures and knowledge, loaded on demand;
- **hooks** — fast, objective enforcement at lifecycle events;
- **scripts** — durable orchestration, validation, transformation, and state derivation.

No component holds an authority another already holds. A prompt may instruct an agent how to apply a
rule but must not be the only place that rule lives when a specification, schema, or validator could
hold it.

## Consequences

- Each boundary becomes a validation point and a place to restrict tools.
- Context stays separated, so an agent's window holds its role's material and little else.
- More components to author, install, and version than a single capable agent would need.
- Cost accepted: orchestration overhead on workflows small enough that one agent would have sufficed.

## Validation required before acceptance

The component taxonomy is currently a design with nothing built against it. It binds nothing until:

1. one command, one orchestrator, and one specialized agent exist and complete a workflow together;
2. the orchestrator chooses its transition from a validated artifact's closed state field, with no
   interpretation of prose;
3. the specialized agent's tool grant is demonstrably the minimum its role requires;
4. a fixture exercises the path end to end.

If the thin path in `docs/bootstrap.md` shows some of these components are ceremony for the workflows
the framework actually runs, narrow the taxonomy before accepting it.
