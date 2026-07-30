# SIGARD Repository Layout & Conventions Specification

**Version:** 0.1 (Draft)

> Status: Normative Draft

# 1. Purpose

This specification defines the canonical repository organization for
SIGARD.

Its objective is to ensure deterministic navigation by AI agents and
humans while preserving clear ownership and traceability of every
artifact.

------------------------------------------------------------------------

# 2. Principles

The repository MUST be:

-   AI First
-   Deterministic
-   Traceable
-   Modular
-   Technology-agnostic

The directory structure MUST communicate artifact intent.

------------------------------------------------------------------------

# 3. Canonical Layout

``` text
repository/
├── architecture/
│   ├── adr/
│   ├── knowledge/
│   ├── glossary/
│   ├── validation/
│   └── diagrams/
├── specifications/
├── context/
├── plans/
├── evidence/
├── src/
├── tests/
├── docs/
└── .claude/
```

------------------------------------------------------------------------

# 4. Directory Responsibilities

-   architecture/: permanent knowledge
-   specifications/: change-specific specifications
-   context/: generated Context Packages
-   plans/: Execution Plans
-   evidence/: validation outputs
-   src/: implementation
-   tests/: automated verification
-   docs/: human-oriented documentation
-   .claude/: commands, workers, hooks and agent configuration

------------------------------------------------------------------------

# 5. Naming Conventions

Artifacts SHOULD follow stable identifiers.

Examples:

-   ADR-001
-   KO-015
-   SPEC-204
-   PLAN-204
-   CTX-204
-   EV-204

File names SHOULD remain stable across versions.

------------------------------------------------------------------------

# 6. Repository Rules

-   Permanent artifacts MUST NOT be stored with temporary artifacts.
-   Generated artifacts SHOULD be reproducible.
-   Source code MUST remain independent of generated context.
-   Temporary artifacts MAY be cleaned after workflow completion.

------------------------------------------------------------------------

# 7. AI Navigation

AI agents MUST navigate using artifact identifiers and repository
conventions.

Agents MUST NOT rely on arbitrary folder discovery.

------------------------------------------------------------------------

# 8. Version Control

Permanent artifacts SHOULD evolve through pull requests.

Generated artifacts MAY be regenerated instead of manually edited.

Evidence SHOULD remain immutable once accepted.

------------------------------------------------------------------------

# 9. Normative Rules

-   Every artifact MUST have a canonical location.
-   Every directory MUST have a single responsibility.
-   Repository structure MUST remain deterministic.
-   AI agents MUST follow repository conventions.
