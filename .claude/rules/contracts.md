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

## Conforming example

A reviewer agent returns a verdict that an orchestrator uses to choose the next transition. Because
the verdict drives control flow, it needs a schema.

`schemas/review-verdict.v1.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://siegard.dev/schemas/review-verdict.v1.json",
  "type": "object",
  "additionalProperties": false,
  "required": ["contract_version", "verdict_id", "subject_id", "producer", "state", "evidence"],
  "properties": {
    "contract_version": { "const": "review-verdict/1" },
    "verdict_id": { "type": "string", "pattern": "^rv_[0-9a-z]{8}$" },
    "subject_id": { "type": "string", "description": "id of the artifact under review" },
    "producer": { "type": "string", "description": "agent name that produced this verdict" },
    "state": { "enum": ["accepted", "rejected", "blocked"] },
    "blocking_reason": {
      "type": "string",
      "description": "required when state is blocked; names the missing input"
    },
    "evidence": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["path", "claim"],
        "properties": {
          "path": { "type": "string" },
          "line": { "type": "integer", "minimum": 1 },
          "claim": { "type": "string" }
        }
      }
    }
  },
  "allOf": [
    {
      "if": { "properties": { "state": { "const": "blocked" } }, "required": ["state"] },
      "then": { "required": ["blocking_reason"] }
    }
  ]
}
```

A conforming instance:

```json
{
  "contract_version": "review-verdict/1",
  "verdict_id": "rv_7f3a91c0",
  "subject_id": "spec_workflow_events_v2",
  "producer": "spec-reviewer",
  "state": "rejected",
  "evidence": [
    {
      "path": "specs/workflow-events.md",
      "line": 42,
      "claim": "transition guard is stated in prose only and has no testable predicate"
    }
  ]
}
```

What makes it conforming, and what each element buys:

- `contract_version` — the consumer can reject an artifact it was not built to read;
- `verdict_id`, `subject_id` — traceability from a recorded event back to this artifact;
- `producer` — the named producer the rules above require;
- `state` as a closed enum — the orchestrator's transition is a lookup, not an interpretation;
- conditional `blocking_reason` — the failure outcome carries the reason mechanically;
- `evidence` with `minItems: 1` — a material decision cannot be recorded without support.

A prose review summary may accompany this artifact for a human reader. It is not the contract, and no
control flow may depend on it.
