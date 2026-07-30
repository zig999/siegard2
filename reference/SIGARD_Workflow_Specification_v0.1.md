# SIGARD Workflow Specification

**Version:** 0.1 (Draft)

# 1. Purpose

This document defines how every Change Request flows through SIGARD
until acceptance.

The workflow is independent of technology and applies equally to
backend, frontend and full-stack projects.

# 2. Workflow Overview

``` text
Change Request
      │
      ▼
Knowledge Impact Analysis
      │
      ▼
Context Resolution
      │
      ▼
Specification
      │
      ▼
Execution Planning
      │
      ▼
Implementation
      │
      ▼
Deterministic Validation
      │
      ▼
Knowledge Contract Validation
      │
      ▼
Acceptance
```

# 3. Workflow Phases

## 3.1 Change Request

### Input

A requested change.

### Examples

-   New feature
-   Bug
-   Refactoring
-   Regulatory update

### Output

A normalized request suitable for analysis.

------------------------------------------------------------------------

## 3.2 Knowledge Impact Analysis

Purpose:

Determine whether permanent knowledge must evolve.

Possible outcomes:

### No Knowledge Impact

The request only changes implementation.

Examples:

-   Bug fix
-   Performance optimization
-   Missing test

### Knowledge Impact

The request changes business or architectural knowledge.

Examples:

-   New rule
-   New domain concept
-   Regulatory requirement

Outputs:

-   Existing KOs unchanged
-   Existing KOs updated
-   New KOs created

------------------------------------------------------------------------

## 3.3 Context Resolution

Consumes:

-   Change Request
-   Specification
-   Knowledge Graph

Produces:

-   Context Package

Rules:

-   Include only necessary ADRs.
-   Include only relevant KOs.
-   Exclude unrelated domains.
-   Keep deterministic ordering.

------------------------------------------------------------------------

## 3.4 Specification

The Specification describes only the requested change.

It MUST NOT duplicate permanent knowledge.

Instead, it references existing KOs.

Example:

Feature: Customer Registration

References:

-   KO Customer
-   KO CPF Validation

------------------------------------------------------------------------

## 3.5 Execution Planning

Transforms a specification into executable work.

Typical outputs:

-   Backend tasks
-   Frontend tasks
-   Database tasks
-   Test tasks
-   Documentation tasks

------------------------------------------------------------------------

## 3.6 Implementation

Workers consume the Execution Plan.

Implementation may produce:

-   Source code
-   Tests
-   Configuration
-   Documentation updates

Implementation MUST follow governing ADRs.

------------------------------------------------------------------------

## 3.7 Deterministic Validation

Validation uses objective mechanisms.

Examples:

-   Build
-   Unit tests
-   Integration tests
-   Lint
-   Static analysis
-   Hooks

Output:

Evidence package.

------------------------------------------------------------------------

## 3.8 Knowledge Contract Validation

Purpose:

Verify that implementation still satisfies impacted Knowledge Objects.

Questions answered:

-   Are all impacted KOs still true?
-   Were business rules preserved?
-   Was architectural intent maintained?

------------------------------------------------------------------------

## 3.9 Acceptance

Acceptance succeeds only when:

-   All deterministic validations passed.
-   Knowledge contracts remain valid.
-   Required evidence exists.

Outputs:

-   Accepted implementation
-   Evidence
-   Updated Knowledge Graph (when applicable)

# 4. Workflow Scenarios

## Scenario A --- First Implementation

Project starts with no code.

Flow:

1.  Discover domain concepts.
2.  Create initial KOs.
3.  Build first Specification.
4.  Resolve Context.
5.  Plan.
6.  Implement.
7.  Validate.
8.  Accept.

Result:

Knowledge Graph grows together with software.

------------------------------------------------------------------------

## Scenario B --- Small Bug Fix

Bug:

CPF validation incorrectly accepts invalid values.

Knowledge Impact Analysis concludes:

No knowledge change.

Flow:

Change Request → Context Resolution → Specification → Planning →
Implementation → Validation → Knowledge Contract Validation → Acceptance

No KO changes.

------------------------------------------------------------------------

## Scenario C --- New Business Rule

New regulation requires CPF to become mandatory.

Knowledge Impact Analysis:

Knowledge changed.

Flow:

Change Request → Update KO CPF Validation → Context Resolution →
Specification → Planning → Implementation → Validation → Knowledge
Contract Validation → Acceptance

Knowledge evolves before implementation.

------------------------------------------------------------------------

## Scenario D --- New Feature

Feature:

Customer Address History.

Flow:

-   Create new KO Address History.
-   Link to Customer.
-   Generate Specification.
-   Plan.
-   Implement.
-   Validate.

Knowledge Graph expands.

# 5. Artifact Flow

  Phase                       Reads           Produces
  --------------------------- --------------- -------------------
  Change Request              \-              Request
  Knowledge Impact Analysis   KO              KO Updates
  Context Resolution          ADR + KO        Context Package
  Specification               Context         Specification
  Planning                    Specification   Execution Plan
  Implementation              Plan            Code + Tests
  Validation                  Code            Evidence
  Knowledge Validation        Evidence + KO   Validation Result
  Acceptance                  All             Approved Change

# 6. Normative Rules

-   Every implementation MUST originate from a Change Request.
-   Specifications MUST reference permanent knowledge rather than
    duplicate it.
-   Knowledge Impact Analysis MUST execute before implementation.
-   Context Resolution MUST be deterministic.
-   Acceptance MUST require deterministic evidence.
-   Permanent knowledge MAY evolve only through explicit Knowledge
    Impact Analysis.
