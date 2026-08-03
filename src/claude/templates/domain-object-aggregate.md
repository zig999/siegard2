---
id: dm.aggregate.{{context}}.{{slug}}
type: aggregate
title: {{title}}
boundary: dm.context.{{context}}
root: dm.definition.{{context}}.{{root_slug}}
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

A {{title}} MUST {{invariant}} within one transaction.
