---
# File: domain/{{context_slug}}/{{element_slug}}.md — the filename is the identity.
# Display name is derived: {{element_slug}} → {{PascalCase}}. Declare `display` only when the
# derivation miscases an acronym, and it must reduce back to the slug.
type: {{aggregate-root | entity | value-object | domain-service | enumeration}}

# entity only — the aggregate root that owns this entity, by slug. A value object never
# declares one.
aggregate: {{root_slug}}

# aggregate-root, entity, value-object. Attribute types are primitives (string, integer,
# decimal, boolean, date, datetime) or a value-object / enumeration element: its bare slug
# inside the same context, its full identity (domain/{{other_context}}/{{element_slug}})
# across contexts. A link to an entity or aggregate root is a relationship, never an
# attribute. `unknown` is forbidden — an undetermined type is a decision to make and log.
# `required: true` only where the material states the attribute is always present; absent
# means the material did not say. `many: true` only where the value repeats.
attributes:
  - name: {{snake_case_name}}
    type: {{primitive_or_element_reference}}
    required: true
    many: true

# aggregate-root, entity, value-object — optional. One declaration per fact, on the
# owning/navigating side.
# target is an entity or aggregate root: bare slug inside the same context, full identity
# across. type: composition | reference | association. cardinality states the target end (1,
# 0..1, 0..*, 1..*); the source end defaults to 1 for composition and 0..* otherwise —
# source-cardinality overrides it, only where it differs. role labels the edge; required when
# two relationships share the same target.
relationships:
  - target: {{element_reference}}
    type: {{composition | reference | association}}
    cardinality: "{{1 | 0..1 | 0..* | 1..*}}"
    source-cardinality: "{{1 | 0..1 | 0..* | 1..*}}"
    role: {{role_slug}}

# aggregate-root, entity (optional); domain-service (required). Names only, kebab-case verbs —
# parameters, returns and refusals live in the behavioral layers.
operations:
  - {{operation_slug}}

# enumeration only. kebab-case; code forms are derived.
values:
  - {{value_slug}}

# No provenance meta-fields (gaps, sources, rationale, proposal) — a fact the material does not
# state is decided by the analysis and disclosed in the decision log (SPEC-001), never marked
# here.
---

## Description

{{What the concept represents in the domain — never how it is implemented. One sentence per
line. `None.` if there is nothing to say.}}

## Responsibility

{{Why this concept exists in the domain — its one main responsibility, answering: why does
this concept exist? `None.` for value objects and enumerations with nothing beyond the
description.}}
