---
okf_version: "0.2"
---

# Siegard concepts

The authority for terms used normatively in `CLAUDE.md`, specifications, schemas, and rules. Add a
concept here before using a term normatively. A term used in a rule but absent from this bundle is an
interpretation waiting to drift.

This bundle is a Siegard concept bundle and a valid OKF v0.2 bundle. The frontmatter contract is
`schemas/concept.v1.json`; the decision and its one divergence from OKF are recorded in
`docs/adr/0005-okf-derived-concept-model.md`. Validate with `make validate`.

One concept per file. The filename is the concept `id` without its `concept.` prefix.

| Concept | Summary |
|---|---|
| [accepted](accepted.md) | The status of a specification or ADR whose decision binds. |
| [capability](capability.md) | A reusable framework behavior with a testable contract. |
| [contract version](contract-version.md) | The identifier a consumer reads to decide whether it can process an artifact. |
| [distribution](distribution.md) | The assembled release artifact under `dist/.claude/`. |
| [event log](event-log.md) | The append-only record of workflow facts. |
| [fixture](fixture.md) | A downstream-shaped case exercising a framework capability. |
| [framework source](framework-source.md) | The tree under `src/claude/` holding the components Siegard ships. |
| [projection](projection.md) | Current state derived by replaying the event log. |
| [provenance](provenance.md) | The recorded origin of a material decision. |
| [specialized agent](specialized-agent.md) | An agent with one declared role and minimum tools. |
| [transition guard](transition-guard.md) | The condition that must hold for a workflow to change state. |
