# SIGARD Knowledge Graph Model Specification

**Version:** 0.1 (Draft)

> Status: Normative Draft

# 1. Purpose

This specification defines the canonical Knowledge Graph used by SIGARD.

The Knowledge Graph is the authoritative representation of permanent
knowledge and its explicit relationships.

------------------------------------------------------------------------

# 2. Objectives

The Knowledge Graph MUST:

-   Represent permanent knowledge.
-   Support deterministic traversal.
-   Minimize ambiguity.
-   Enable context resolution.
-   Preserve traceability.

------------------------------------------------------------------------

# 3. Graph Elements

## Nodes

Supported node types:

-   Knowledge Object
-   ADR
-   Glossary
-   Public Contract

Temporary artifacts MUST NOT become graph nodes.

## Edges

Supported relationships:

-   depends_on
-   references
-   extends
-   implements
-   supersedes

Relationships MUST be explicit.

------------------------------------------------------------------------

# 4. Canonical Rules

-   Every node MUST have a unique identifier.
-   Every edge MUST have a defined semantic.
-   Cycles SHOULD be avoided unless explicitly modeled.
-   Orphan nodes SHOULD be eliminated.

------------------------------------------------------------------------

# 5. Traversal

Traversal MUST:

1.  Start from one or more root nodes.
2.  Follow explicit edges only.
3.  Preserve deterministic ordering.
4.  Ignore unrelated branches.

Traversal output is a Context Package.

------------------------------------------------------------------------

# 6. Evolution

The graph evolves only when permanent knowledge changes.

Code changes alone MUST NOT modify the graph.

------------------------------------------------------------------------

# 7. Consistency

The graph MUST support:

-   Reachability checks
-   Duplicate detection
-   Broken reference detection
-   Cycle detection
-   Version compatibility

------------------------------------------------------------------------

# 8. AI Consumption

AI agents MUST:

-   Treat the graph as the source of truth.
-   Never infer missing relationships.
-   Request clarification when traversal cannot continue.

------------------------------------------------------------------------

# 9. Normative Rules

-   Every Knowledge Object MUST belong to the Knowledge Graph.
-   Every relationship MUST be explicit.
-   Context Resolution MUST traverse the graph deterministically.
-   The graph MUST represent permanent knowledge only.
