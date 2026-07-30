# SIGARD Core Architecture Specification

**Version:** 0.1 (Draft)

> **Status:** Normative Draft

# 1. Vision

## Purpose

SIGARD is an AI-FIRST framework for Specification-Driven Development
(SDD). Its purpose is not to generate software directly, but to provide
a deterministic architecture that enables AI agents to build software
consistently, traceably, and with minimal ambiguity.

The framework is based on five principles:

-   Knowledge is the primary source of truth.
-   Specifications describe changes, not the whole system.
-   AI consumes structured knowledge instead of free-form documentation.
-   Deterministic validation is preferred over subjective review.
-   Every software change is driven by an explicit Change Request.

## Scope

This document defines:

-   the architectural principles of SIGARD;
-   the core concepts;
-   the permanent artifacts;
-   the knowledge model;
-   the Knowledge Graph;
-   Context Resolution.

The operational workflow is intentionally defined in a separate
specification.

# 2. Architectural Principles

## AI FIRST

All artifacts MUST be designed primarily for machine consumption.

## Knowledge First

Business and architectural knowledge MUST exist independently of source
code.

## Specification First

Implementation MUST always be driven by an explicit specification
describing a requested change.

## Deterministic Validation

Whenever possible, validation MUST be performed through deterministic
mechanisms such as compilation, tests, linting and hooks.

## Small Context

AI agents SHOULD receive only the minimum context required to complete a
task.

## Separation of Concerns

Knowledge, specifications, implementation and evidence are independent
artifacts.

# 3. Core Concepts

## Change Request

Represents any requested change to the system.

Examples:

-   New feature
-   Bug fix
-   Refactoring
-   Regulatory change
-   Performance improvement

## Knowledge Object (KO)

A Knowledge Object represents exactly one durable concept.

A KO MUST answer one question only.

Examples:

-   Customer
-   Invoice
-   Payment Approval
-   CPF Validation

## Knowledge Graph

The permanent graph formed by all Knowledge Objects and their
relationships.

## Context Package

A temporary package containing only the artifacts required for one
implementation task.

## Specification

Describes the requested change.

Specifications are temporary.

## Execution Plan

Describes how the implementation will be performed.

## Evidence

Artifacts proving implementation correctness.

Examples:

-   test results
-   build logs
-   static analysis
-   validation reports

## Knowledge Contract

Every KO defines an architectural contract that implementation must
satisfy.

# 4. SIGARD Artifacts

  -------------------------------------------------------------------------
  Artifact            Lifetime          Producer          Consumer
  ------------------- ----------------- ----------------- -----------------
  ADR                 Permanent         Architects        Everyone

  Knowledge Object    Permanent         Architects /      AI Agents
                                        Domain experts    

  Specification       Temporary         Planner           Implementers

  Execution Plan      Temporary         Planner           Workers

  Source Code         Permanent         Implementers      Runtime

  Tests               Permanent         Implementers      Validation

  Evidence            Temporary         Validation        Acceptance
  -------------------------------------------------------------------------

Permanent artifacts define the architecture.

Temporary artifacts define a specific implementation.

# 5. Knowledge Model

## Single Responsibility

Each KO MUST represent one concept only.

## Stable Knowledge

KOs represent stable knowledge rather than implementation details.

## Reuse

Knowledge MUST be reusable across multiple specifications.

## Relationships

Knowledge Objects are connected using explicit relationships such as:

-   depends_on
-   references
-   implements
-   extends

## Recommended Structure

``` text
id:
title:
question:
answer:
depends_on:
references:
exports:
owner:
version:
```

The question field is mandatory because it defines the responsibility of
the KO.

# 6. Knowledge Graph

The Knowledge Graph is the permanent representation of architectural
knowledge.

Nodes represent Knowledge Objects.

Edges represent explicit relationships.

The graph evolves over time as new concepts emerge.

Specifications DO NOT belong to the graph.

Execution Plans DO NOT belong to the graph.

Evidence DOES NOT belong to the graph.

Only durable knowledge is stored.

# 7. Context Resolution

Context Resolution is responsible for producing a Context Package.

Input:

-   Change Request
-   Specification
-   Knowledge Graph

Output:

-   Minimal Context Package

Rules:

1.  Include only required KOs.
2.  Include governing ADRs.
3.  Exclude unrelated domains.
4.  Preserve deterministic ordering.
5.  Produce identical output for identical inputs.

Example:

Change Request:

"Implement customer registration."

Context Package:

-   ADR Authentication
-   ADR Validation
-   KO Customer
-   KO CPF Validation
-   KO Registration

# 8. General Architecture

The conceptual architecture is:

``` text
Change Request
        │
        ▼
Specification
        │
        ▼
Context Resolution
        │
        ▼
Context Package
        │
        ▼
Execution
        │
        ▼
Evidence
```

Knowledge remains permanent throughout the process while specifications
and execution artifacts are transient.

## Final Notes

This specification intentionally separates architecture from
implementation workflow.

Future documents define:

-   workflow
-   implementation phases
-   deterministic validation
-   knowledge impact analysis
-   operational scenarios
