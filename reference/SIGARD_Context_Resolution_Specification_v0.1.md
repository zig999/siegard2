# SIGARD Context Resolution Specification

**Version:** 0.1 (Draft)

> Status: Normative Draft

# 1. Purpose

This specification defines how SIGARD transforms a Change Request into
the minimum deterministic Context Package required by AI agents.

Context Resolution is responsible for reducing ambiguity, minimizing
token consumption and ensuring every implementation starts from the same
architectural knowledge.

------------------------------------------------------------------------

# 2. Objectives

The Context Resolver MUST:

-   Produce deterministic outputs.
-   Minimize context size.
-   Preserve architectural consistency.
-   Avoid unrelated knowledge.
-   Respect architectural decisions (ADRs).

------------------------------------------------------------------------

# 3. Definitions

## Context Package

A temporary collection of artifacts required for one implementation.

A Context Package MAY contain:

-   ADRs
-   Knowledge Objects
-   Specifications
-   Existing source code references
-   Public contracts
-   Existing tests

It MUST NOT contain unrelated artifacts.

------------------------------------------------------------------------

## Resolution Root

The initial artifact used to start traversal.

Usually:

-   Change Request
-   Specification

------------------------------------------------------------------------

# 4. Inputs

The resolver consumes:

-   Change Request
-   Specification
-   Knowledge Graph
-   ADR Repository
-   Project metadata

------------------------------------------------------------------------

# 5. Outputs

The resolver produces one Context Package.

The package SHOULD be immutable during execution.

------------------------------------------------------------------------

# 6. Resolution Algorithm

Step 1

Read Change Request.

Step 2

Identify referenced domains.

Step 3

Locate governing ADRs.

Step 4

Locate root KOs.

Step 5

Traverse dependencies.

Step 6

Remove unrelated nodes.

Step 7

Order artifacts deterministically.

Step 8

Produce Context Package.

------------------------------------------------------------------------

# 7. Traversal Rules

The resolver MUST traverse explicit relationships only.

Supported links include:

-   depends_on
-   references
-   implements
-   extends

Hidden relationships MUST NOT be inferred.

------------------------------------------------------------------------

# 8. Context Selection Rules

Always include:

-   Governing ADRs
-   Root KOs
-   Direct dependencies

Include only when necessary:

-   Neighboring KOs
-   Integration contracts
-   Existing implementation references

Never include:

-   Unrelated domains
-   Closed features
-   Deprecated knowledge
-   Historical discussions

------------------------------------------------------------------------

# 9. Determinism

Given identical:

-   Change Request
-   Knowledge Graph
-   ADR repository

The resolver MUST produce an identical Context Package.

Ordering MUST be deterministic.

------------------------------------------------------------------------

# 10. Context Package Structure

Recommended structure:

``` text
Context Package

Architecture
  ADR-001
  ADR-005

Knowledge
  KO Customer
  KO CPF Validation

Specification
  Feature Specification

Implementation
  Existing Repository

Validation
  Existing Tests
```

------------------------------------------------------------------------

# 11. Examples

## Example A

Request:

Implement Customer Registration.

Resolver returns:

-   ADR Authentication
-   ADR Validation
-   KO Customer
-   KO Registration
-   KO CPF Validation

Nothing else.

------------------------------------------------------------------------

## Example B

Bug:

Customer accepts invalid CPF.

Resolver returns:

-   KO CPF Validation
-   Existing validation tests
-   Related implementation

No marketing knowledge is included.

------------------------------------------------------------------------

## Example C

New billing rule.

Resolver returns:

-   Billing ADR
-   KO Invoice
-   KO Tax Rule
-   KO Payment

------------------------------------------------------------------------

# 12. Multi-domain Requests

If a request spans multiple domains, the resolver SHOULD produce one
unified Context Package.

The package MUST preserve dependency order.

------------------------------------------------------------------------

# 13. Failure Conditions

Resolution MUST fail when:

-   Root KO cannot be found.
-   Required ADR is missing.
-   Dependency cycle cannot be resolved.
-   Knowledge is contradictory.

Implementation MUST NOT begin until resolved.

------------------------------------------------------------------------

# 14. AI Agent Responsibilities

Agents MUST:

-   Consume only the Context Package.
-   Avoid loading unrelated documents.
-   Treat missing knowledge as an architectural gap.
-   Request clarification instead of guessing.

------------------------------------------------------------------------

# 15. Normative Rules

-   Context Resolution MUST execute before planning.
-   Every implementation MUST use a Context Package.
-   Context Packages MUST be deterministic.
-   The resolver MUST prefer explicit relationships.
-   The resolver MUST minimize token usage.
-   Context Packages MUST be reproducible.
