# SIGARD Architecture Decision Model (ADR Specification)

**Version:** 0.1 (Draft)

## 1. Purpose

This document defines how architectural decisions are created, approved,
evolved and consumed within SIGARD.

Architectural Decisions (ADRs) are normative artifacts that govern
implementation.

------------------------------------------------------------------------

## 2. Principles

An ADR MUST:

-   record a durable architectural decision;
-   explain the rationale;
-   define consequences;
-   be traceable;
-   be immutable after approval (changes create a new version or
    successor).

------------------------------------------------------------------------

## 3. When an ADR is Required

An ADR SHOULD be created for:

-   architectural patterns;
-   technology selection;
-   cross-cutting concerns;
-   coding constraints;
-   integration strategies;
-   security decisions;
-   deployment decisions.

An ADR MUST NOT be created for implementation details.

------------------------------------------------------------------------

## 4. Lifecycle

Draft → Review → Approved → Superseded → Archived

------------------------------------------------------------------------

## 5. Recommended Structure

``` yaml
id: ADR-001
title:
status:
version:
decision:
context:
rationale:
consequences:
supersedes:
references:
```

------------------------------------------------------------------------

## 6. Relationships

ADRs MAY reference:

-   Knowledge Objects
-   Other ADRs
-   Specifications
-   Public Contracts

Knowledge Objects MAY reference governing ADRs.

------------------------------------------------------------------------

## 7. AI Consumption

AI agents MUST:

1.  Read governing ADRs before implementation.
2.  Treat ADRs as normative.
3.  Reject implementations that violate approved ADRs.
4.  Request clarification instead of inventing architecture.

------------------------------------------------------------------------

## 8. Evolution

Minor version: - wording - examples

Major version: - architectural behavior - incompatible decision

Superseded ADRs remain available for traceability.

------------------------------------------------------------------------

## 9. Normative Rules

-   Every architectural constraint SHOULD originate from an ADR.
-   Every Specification MUST comply with governing ADRs.
-   Every Context Package MUST include applicable ADRs.
-   Conflicting ADRs MUST be resolved before implementation.
