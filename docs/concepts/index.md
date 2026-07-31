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

Each concept's `status` lives in its own frontmatter and is not repeated here. `docs/adr/README.md` states
when a concept crosses between the tiers: a concept becomes `accepted` when an artifact that binds uses the
term normatively, and one cited only by a `proposed` specification stays `proposed`. A `proposed` concept
names a term without binding its definition — see [accepted](accepted.md). The rule still governs a concept
added from here on, even though nothing in the bundle currently sits on the lower tier.

As of 2026-07-31 every entry is `accepted`. The bundle was promoted in one maintainer decision, together
with every specification and ADR that was still `proposed`, so the tier no longer distinguishes anything
here.

What that decision changed, and what it did not, is worth being exact about. The condition
`docs/adr/README.md` states for the crossing — a term used normatively by an artifact that binds — was
already satisfied for the entries citing `specs/0001-knowledge-object-driven-development.md`, and the
promotion recorded a fact for those. It was not satisfied for the vocabulary of
`specs/0004-generation-and-reproducibility.md` and the framework specifications: those documents were
accepted on the same authority and on the same day, with their own validation conditions open, so a
definition here binds a mechanism that in several cases does not exist yet. Each of those specifications
records that in its **What satisfied acceptance** section, and this bundle does not restate it per concept.

The consequence is the same one they carry: `.claude/rules/compatibility.md` now governs a change to any
definition here, and the first component built against one is the thing most likely to demand a change.

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
| [context package](context-package.md) | The manifest naming exactly the knowledge one run of context resolution puts in scope. |
| [contract version](contract-version.md) | The identifier a consumer reads to decide whether it can process an artifact. |
| [definition](definition.md) | The knowledge object type saying what a domain concept is and which attributes it holds. |
| [distribution](distribution.md) | The assembled release artifact under `dist/.claude/`. |
| [distribution manifest](distribution-manifest.md) | The record of what an installation carries, beside the plugin manifest the harness reads. |
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
| [placement decision](placement-decision.md) | The validated, frozen record of where a pack puts each artifact the manifest does not lock. |
| [process](process.md) | The knowledge object type holding an ordered sequence of steps that reference other objects by id. |
| [projection](projection.md) | A human-readable artifact generated from the knowledge graph, normative nowhere. |
| [provenance](provenance.md) | The recorded origin of a material decision. |
| [release record](release-record.md) | What changed between one framework version and the last. |
| [representation ratio](representation-ratio.md) | Permanent knowledge volume measured against the source volume it produces. |
| [rule](rule.md) | The knowledge object type stating one falsifiable condition; the only type an assertion binds to. |
| [skill](skill.md) | A distributable procedure or knowledge unit, invocable as `/name`. |
| [specialized agent](specialized-agent.md) | An agent with one declared role and minimum tools. |
| [specification](specification.md) | A normative document in `specs/`, the highest precedence source in this repository. |
| [specification delta](specification-delta.md) | The temporary artifact describing one requested change by reference. |
| [stack knowledge](stack-knowledge.md) | A fact whose change changes every system on the same technology, never held by the knowledge base. |
| [target pack](target-pack.md) | The distributable unit carrying one technology stack: the agents and templates producing the classes it declares. |
| [transition guard](transition-guard.md) | The condition that must hold for a workflow to change state. |
| [workflow state](workflow-state.md) | Current state of a workflow, derived from the record of what happened. |
