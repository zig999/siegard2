---
id: dm.definition.{{context}}.{{slug}}
type: definition
title: {{title}}
boundary: dm.aggregate.{{context}}.{{boundary_slug}}
ddd: {{ddd}}
attributes:
  - { name: {{attribute_name}}, type: string, max_length: {{attribute_max_length}}, required: true }
identity:
  attributes:
    - {{attribute_name}}
description: {{description}}
question: {{question}}
contract_version: domain-object/2
generated: { by: {{generated_by}}, at: "{{generated_at}}" }
origin: {{origin}}
out_of_scope:
  - {{out_of_scope}}
---

# {{title}}

## Answer

{{description}}

## Invariants

A {{title}} MUST {{invariant}}.
