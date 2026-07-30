# SIGARD Artifact Specification

**Version:** 0.1 (Draft)

> Status: Normative Draft

# 1. Purpose

This document defines the canonical artifact model used throughout
SIGARD.

Artifacts are the only objects exchanged between phases, orchestrators
and workers.

Every artifact has a clearly defined lifecycle, ownership and
responsibility.

------------------------------------------------------------------------

# 2. Artifact Principles

Artifacts MUST be:

-   Explicit
-   Versionable
-   Traceable
-   Immutable once published (new versions replace old ones)
-   AI First
-   Independently identifiable

Every artifact MUST possess a unique identifier.

------------------------------------------------------------------------

# 3. Artifact Categories

## Permanent

Long-lived architectural knowledge.

Examples:

-   ADR
-   Knowledge Object
-   Glossary
-   Domain Model
-   Public Contracts

------------------------------------------------------------------------

## Temporary

Created to execute one Change Request.

Examples:

-   Specification
-   Execution Plan
-   Context Package
-   Evidence
-   Validation Report

------------------------------------------------------------------------

## Deliverables

Outputs that become part of the software.

Examples:

-   Source Code
-   Tests
-   Configuration
-   Documentation

------------------------------------------------------------------------

# 4. Artifact Catalog

  Artifact            Category      Producer             Consumer
  ------------------- ------------- -------------------- ------------
  ADR                 Permanent     Architect            Everyone
  Knowledge Object    Permanent     Architect / Domain   AI Agents
  Glossary            Permanent     Domain               Everyone
  Specification       Temporary     Planner              Workers
  Context Package     Temporary     Context Resolver     Workers
  Execution Plan      Temporary     Planner              Workers
  Source Code         Deliverable   Implementer          Runtime
  Tests               Deliverable   Implementer          Validation
  Evidence            Temporary     Validation           Acceptance
  Validation Report   Temporary     Validation           Acceptance

------------------------------------------------------------------------

# 5. Artifact Lifecycle

Permanent:

Draft → Review → Approved → Superseded → Archived

Temporary:

Created → Consumed → Closed

Deliverables:

Created → Modified → Released → Deprecated

------------------------------------------------------------------------

# 6. Common Metadata

Every artifact SHOULD expose:

``` yaml
id:
type:
title:
status:
version:
owner:
created_at:
updated_at:
references:
depends_on:
supersedes:
```

------------------------------------------------------------------------

# 7. Relationships

Artifacts MAY reference other artifacts.

Examples:

Specification → references Knowledge Objects

Execution Plan → derived_from Specification

Evidence → validates Execution Plan

Validation Report → references Evidence

------------------------------------------------------------------------

# 8. Traceability

SIGARD MUST support complete traceability.

Example chain:

Change Request → Specification → Execution Plan → Source Code → Tests →
Evidence → Acceptance

If permanent knowledge changed:

Change Request → Knowledge Object → Specification → Implementation

------------------------------------------------------------------------

# 9. Ownership

Each artifact has exactly one producer.

Consumers MAY be many.

Examples:

Planner produces Specifications.

Context Resolver produces Context Packages.

Workers produce Source Code.

Validation produces Evidence.

------------------------------------------------------------------------

# 10. Versioning

Permanent artifacts:

Semantic Versioning recommended.

Temporary artifacts:

Versioned only while active.

Deliverables:

Project versioning policy.

------------------------------------------------------------------------

# 11. Naming

Identifiers SHOULD remain stable.

Examples:

ADR-001

KO-023

SPEC-145

PLAN-145

CTX-145

EV-145

------------------------------------------------------------------------

# 12. Storage

Recommended repository:

architecture/ adr/ knowledge/ glossary/

specifications/

plans/

context/

evidence/

src/

tests/

------------------------------------------------------------------------

# 13. AI Consumption

AI agents MUST consume artifacts through their identifiers.

Agents SHOULD avoid reading unrelated artifacts.

Artifacts are authoritative.

Conversation history is not.

------------------------------------------------------------------------

# 14. Normative Rules

-   Every workflow phase MUST consume and produce artifacts.
-   Every artifact MUST be identifiable.
-   Permanent artifacts MUST preserve history.
-   Temporary artifacts MUST be disposable.
-   Deliverables MUST be traceable to a Specification.
-   Evidence MUST support Acceptance.
