---
paths:
  - "specs/**"
  - "schemas/**"
  - "src/claude/agents/**"
  - ".claude/agents/**"
---

# Inter-agent artifact contracts

An artifact passed between agents or between workflow phases must be consumable without human
interpretation.

## Required for every inter-agent artifact

- a named producer and a named consumer;
- valid states, transitions, and failure outcomes;
- a stable identifier for traceability;
- provenance or evidence references for material decisions;
- validation at the boundary, before consumption.

## Schema requirement by criticality

| What the artifact carries | Contract required |
|---|---|
| Control flow, transition guards, or persisted state | versioned schema in `schemas/`, validated at the boundary |
| Data a downstream agent parses to reach a decision | versioned schema in `schemas/` |
| Explanation, rationale, or narrative for a human | none; prose is the correct form |

Do not satisfy the first two rows with "some other equally testable contract". If an artifact drives
control flow or becomes recorded state, it gets a versioned schema file. If it only explains
something, do not schematize it — a schema around prose adds ceremony and no guarantee.

Prefer structured data for control flow. Use prose for explanation and for content that cannot be
represented meaningfully as a contract.

## What a conforming contract looks like

A reviewer agent returns a verdict an orchestrator uses to choose the next transition. Because the
verdict drives control flow, it needs a schema — and each element earns its place:

| Element | What it buys |
|---|---|
| `contract_version: { "const": "review-verdict/1" }` | the consumer rejects an artifact it was not built to read |
| `verdict_id`, `subject_id` | traceability from a recorded event back to this artifact |
| `producer` | the named producer the rules above require |
| `state: { "enum": [...] }` | the orchestrator's transition is a lookup, not an interpretation |
| `blocking_reason`, required by `if`/`then` when `state` is `blocked` | the failure outcome carries its reason mechanically |
| `evidence: { "minItems": 1 }` | a material decision cannot be recorded without support |

Plus `additionalProperties: false`, so a field the producer invented is rejected rather than ignored.
`schemas/impact-analysis.v1.json` and `schemas/workflow-event.v1.json` are worked examples in this
repository; read one before writing a new contract.

A prose summary may accompany such an artifact for a human reader. It is not the contract, and no control
flow may depend on it.
