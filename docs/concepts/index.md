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

Each concept's `status` lives in its own frontmatter and is not repeated here. The bundle mixes the two
tiers on purpose, and `docs/adr/README.md` states when a concept crosses between them: a concept becomes
`accepted` when an artifact that binds uses the term normatively, and one cited only by a `proposed`
specification stays `proposed`. A `proposed` concept names a term without binding its definition — see
[accepted](accepted.md).

As of 2026-07-31 the split is 30 `accepted` and 16 `proposed`. Every remaining `proposed` entry is
vocabulary for `specs/0001-knowledge-object-driven-development.md` or
`specs/0004-generation-and-reproducibility.md`, neither of which is accepted, so promoting one would bind a
definition to a mechanism that does not exist. The tier is derivable rather than declared: read which
artifacts cite a concept, and read their status.

[orchestrator](orchestrator.md) is the first entry where that reasoning has started to come apart: its
mechanism now exists and is tested, while the specification that uses the term normatively is still
`proposed`. It stays `proposed` because the concept follows its source, and because whether an
orchestrator is a component class at all is still open — see `docs/bootstrap.md` open question 3.

| Concept | Summary |
|---|---|
| [accepted](accepted.md) | The status of a specification or ADR whose decision binds. |
| [amendment](amendment.md) | A recorded revision of part of an accepted decision, leaving the rest in force. |
| [artifact class](artifact-class.md) | What a produced artifact is, named independently of how any technology expresses it. |
| [artifact persistence](artifact-persistence.md) | Whether an artifact is committed, recomputed from committed inputs, or discarded with its run. |
| [assertion](assertion.md) | A mechanical check that rejects an implementation violating one knowledge object. |
| [boundary](boundary.md) | The knowledge object type holding a scope — a bounded context or an aggregate — with derived membership. |
| [capability](capability.md) | A reusable framework behavior with a testable contract. |
| [change request](change-request.md) | The recorded request that originates every change to a governed repository. |
| [context package](context-package.md) | The manifest naming exactly the knowledge one implementation task may read. |
| [contract version](contract-version.md) | The identifier a consumer reads to decide whether it can process an artifact. |
| [definition](definition.md) | The knowledge object type saying what a domain concept is and which attributes it holds. |
| [distribution](distribution.md) | The assembled release artifact under `dist/.claude/`. |
| [domain knowledge](domain-knowledge.md) | A fact whose change changes this system, and the only kind the knowledge base holds. |
| [escalation](escalation.md) | The insertion of workflow phases, decided by a predicate over a validated artifact. |
| [event log](event-log.md) | The append-only record of workflow facts. |
| [fail-soft](fail-soft.md) | Resolution degrades instead of blocking, and acceptance is evaluated independently. |
| [fixture](fixture.md) | A downstream-shaped case exercising a framework capability. |
| [framework source](framework-source.md) | The tree under `src/claude/` holding the components Siegard ships. |
| [generation manifest](generation-manifest.md) | The lock recording where each produced artifact went, so a later run reuses the placement. |
| [generation plan](generation-plan.md) | The derived, inspectable list of what one generation will produce, validated before any write. |
| [generation scope](generation-scope.md) | The closed, frozen set of knowledge objects one generation compiles. |
| [generation track](generation-track.md) | Whether an artifact class is produced by template expansion or by agent judgment. |
| [generative completeness](generative-completeness.md) | Whether a scope holds every domain fact production needs, as a blocking validation. |
| [impact analysis](impact-analysis.md) | The phase that decides whether a change request requires permanent knowledge to change. |
| [interface](interface.md) | The knowledge object type describing what a bounded context exposes to, or consumes from, another. |
| [knowledge base](knowledge-base.md) | The authored set of knowledge objects, distinct from the graph materialized from it. |
| [knowledge graph](knowledge-graph.md) | The graph of knowledge objects and their declared relationships, derived from frontmatter. |
| [knowledge object](knowledge-object.md) | One durable concept of a governed repository's knowledge. |
| [least privilege](least-privilege.md) | Only the tools and permissions a component's contract names. |
| [lifecycle](lifecycle.md) | The knowledge object type holding a definition's legal states and its total transition table. |
| [ontology](ontology.md) | The schema level of the knowledge model: node types, edges, cardinality, meaning. |
| [orchestrator](orchestrator.md) | The component that chooses a transition by lookup on a validated artifact's closed field. |
| [operative rule](operative-rule.md) | The imperative form of a rule, held by one artifact and separate from why it was decided. |
| [process](process.md) | The knowledge object type holding an ordered sequence of steps that reference other objects by id. |
| [projection](projection.md) | A human-readable artifact generated from the knowledge graph, normative nowhere. |
| [provenance](provenance.md) | The recorded origin of a material decision. |
| [representation ratio](representation-ratio.md) | Permanent knowledge volume measured against the source volume it produces. |
| [rule](rule.md) | The knowledge object type stating one falsifiable condition; the only type an assertion binds to. |
| [skill](skill.md) | A distributable procedure or knowledge unit, invocable as `/name`. |
| [specialized agent](specialized-agent.md) | An agent with one declared role and minimum tools. |
| [specification](specification.md) | A normative document in `specs/`, the highest precedence source in this repository. |
| [specification delta](specification-delta.md) | The temporary artifact describing one requested change by reference. |
| [stack knowledge](stack-knowledge.md) | A fact whose change changes every system on the same technology, never held by the knowledge base. |
| [target pack](target-pack.md) | The distributable unit carrying one technology stack: a specialized agent and its templates. |
| [transition guard](transition-guard.md) | The condition that must hold for a workflow to change state. |
| [workflow state](workflow-state.md) | Current state of a workflow, derived from the record of what happened. |
