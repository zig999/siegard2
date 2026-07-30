# SIGARD Knowledge Object Specification

**Version:** 0.1 (Draft)

> Status: Normative Draft

# 1. Purpose

This document defines the normative model for Knowledge Objects (KOs),
the fundamental unit of knowledge in SIGARD.

A Knowledge Object is the primary mechanism used to capture, organize
and distribute architectural, business and technical knowledge to AI
agents.

------------------------------------------------------------------------

# 2. Design Principles

Every KO MUST satisfy the following principles:

-   Single Responsibility
-   AI First
-   Stable Knowledge
-   Explicit Relationships
-   Independent Understanding
-   Reusability
-   Versionability

A KO MUST describe one durable concept.

A KO MUST NOT describe an implementation task.

------------------------------------------------------------------------

# 3. What is a Knowledge Object?

A Knowledge Object represents one concept that is expected to remain
valid beyond a single implementation.

Examples:

-   Customer
-   Invoice
-   Authentication
-   CPF Validation
-   Payment Approval

Not KOs:

-   "Implement customer API"
-   "Fix bug #52"
-   "Refactor repository"

Those are implementation work.

------------------------------------------------------------------------

# 4. Single Responsibility

Each KO MUST answer exactly one question.

Examples:

KO: Customer

Question: What is a Customer?

KO: CPF Validation

Question: How is CPF validated?

If two independent questions exist, two KOs SHOULD exist.

------------------------------------------------------------------------

# 5. Knowledge Lifetime

Permanent:

-   Business concepts
-   Domain rules
-   Architectural decisions
-   Integration contracts

Temporary:

-   Specifications
-   Execution Plans
-   Evidence
-   Tasks

Temporary artifacts MUST NOT become KOs.

------------------------------------------------------------------------

# 6. Recommended Structure

``` yaml
id: KO-001
title: Customer
question: What is a Customer?
kind: domain
version: 1.0.0

summary: |
  Canonical customer definition.

answer: |
  ...

depends_on:
  - KO-010

references:
  - ADR-001

exports:
  - Customer Entity
  - Customer Identifier

tags:
  - sales
  - crm
```

Mandatory fields:

-   id
-   title
-   question
-   answer
-   version

------------------------------------------------------------------------

# 7. Relationships

Relationships MUST be explicit.

Supported relationships include:

-   depends_on
-   references
-   implements
-   extends
-   supersedes

Relationships MUST NOT be inferred from prose.

------------------------------------------------------------------------

# 8. Writing Guidelines

A KO SHOULD:

-   use short paragraphs;
-   avoid unnecessary narrative;
-   describe facts instead of opinions;
-   use canonical terminology;
-   define invariants before examples.

A KO MAY include:

-   Mermaid diagrams
-   Tables
-   JSON examples
-   Pseudocode

A KO SHOULD NOT duplicate another KO.

------------------------------------------------------------------------

# 9. Evolution Rules

A KO MAY evolve when:

-   business knowledge changes;
-   architecture changes;
-   regulation changes.

A KO MUST NOT evolve simply because code changes.

Implementation SHOULD adapt to knowledge, not the opposite.

------------------------------------------------------------------------

# 10. Versioning

Minor version:

-   clarifications
-   examples
-   formatting

Major version:

-   semantic rule changes
-   contract changes
-   incompatible knowledge

Every version MUST preserve traceability.

------------------------------------------------------------------------

# 11. Knowledge Graph Integration

Every KO is a node in the Knowledge Graph.

Nodes are connected only through explicit relationships.

The graph represents permanent knowledge only.

Specifications, code and evidence are external artifacts.

------------------------------------------------------------------------

# 12. AI Consumption Rules

AI agents MUST:

1.  Read only requested KOs.
2.  Respect governing ADRs.
3.  Treat KO content as normative.
4.  Never infer missing rules.
5.  Request architectural clarification when knowledge is insufficient.

------------------------------------------------------------------------

# 13. Examples

## Example A

KO Customer

Question:

What is a Customer?

Answer:

Defines the canonical representation of a customer used across the
platform.

------------------------------------------------------------------------

## Example B

KO CPF Validation

Question:

How is CPF validated?

Answer:

Defines canonical validation rules independently of implementation
language.

------------------------------------------------------------------------

# 14. Anti-patterns

The following are prohibited:

-   One KO describing multiple domains.
-   Implementation instructions inside KOs.
-   Temporary project decisions.
-   Duplicate concepts.
-   Hidden dependencies.
-   Ambiguous terminology.

------------------------------------------------------------------------

# 15. Normative Rules

-   Every KO MUST have a single responsibility.
-   Every KO MUST define one canonical question.
-   Every KO MUST be independently understandable.
-   Every KO MUST belong to the Knowledge Graph.
-   KOs SHOULD be reusable.
-   KOs MUST NOT contain implementation tasks.
-   KOs MUST evolve independently of source code whenever possible.
